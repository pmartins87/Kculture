#!/usr/bin/env python3
"""V23A immutable-snapshot current-frontier refresh."""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.kaggle_meta_scout_cli import csv_rows, normkey
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE, acquire_public_main, load_public_agent, purge_package_modules, sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action, score
from tools.first_party_option_host_v1 import OptionHostState, apply_option_host

DISCOVERY_SEEDS=(79301,79302,79303,79304,79305,79306)
SEATS=(0,1)
TOP_N=30
MAX_REPS=12
MIN_REPS=8
SMOKE_SEED=79300


def ref_value(row):
    for k,v in row.items():
        if normkey(k)=="ref" and str(v).strip():
            return str(v).strip()
    for _k,v in row.items():
        s=str(v or "").strip()
        if "/" in s and " " not in s:
            return s
    return None


def list_current_top30():
    cmd=["kaggle","kernels","list","--competition","kaggriculture","--sort-by","scoreDescending","--page-size","100","-v"]
    p=subprocess.run(cmd,text=True,capture_output=True,check=False)
    if p.returncode!=0:
        raise RuntimeError(f"kaggle kernels list failed rc={p.returncode}: {p.stderr[-4000:]}")
    rows=csv_rows(p.stdout)
    refs=[]; seen=set()
    for row in rows:
        ref=ref_value(row)
        if ref and ref not in seen:
            seen.add(ref); refs.append(ref)
        if len(refs)>=TOP_N:
            break
    if len(refs)!=TOP_N:
        raise RuntimeError(f"expected current Top-{TOP_N}, got {len(refs)}")
    return refs,p.stdout


def acquire_retry(ref,target,attempts=8):
    last=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,target/f"a{i}")
            return main,sha256_bytes(main.read_bytes()),receipt
        except Exception as exc:
            last=exc
            if i+1<attempts:
                time.sleep(min(60.0,5.0*(2**i)))
    raise last


def acquire_expected_retry(ref,expected,target,attempts=8):
    last=None
    for i in range(attempts):
        try:
            main,sha,receipt=acquire_retry(ref,target/f"outer{i}",attempts=1)
            if sha!=expected:
                raise RuntimeError(f"source SHA drift {sha} != {expected}")
            return main,receipt
        except Exception as exc:
            last=exc
            if i+1<attempts:
                time.sleep(min(60.0,5.0*(2**i)))
    raise last


def run_smoke(main_py,seat):
    purge_package_modules(main_py.parent)
    agent=load_public_agent(main_py)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":SMOKE_SEED},debug=False)
    if seat==0: env.run([agent,"starter"])
    else: env.run(["starter",agent])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    return {
        "seat":seat,
        "ok":statuses==["DONE","DONE"] and len(rewards)==2 and steps>=720 and all(math.isfinite(x) for x in rewards),
        "statuses":statuses,"rewards":rewards,"steps":steps,
    }


class All3:
    def __init__(self,base_main):
        self.agent=load_public_agent(base_main)
        self.state=OptionHostState()
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        return apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)


def run_all3(base_main,opp_main,seed,seat):
    purge_package_modules(base_main.parent)
    purge_package_modules(opp_main.parent)
    cand=All3(base_main)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"result":"W" if margin>0 else ("L" if margin<0 else "T"),"rewards":rewards,"steps":steps}


def snapshot_package(main_py,dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(main_py.parent,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    snap_main=dest/"main.py"
    if not snap_main.exists():
        # Preserve canonical filename for downstream loader.
        snap_main.write_bytes(main_py.read_bytes())
    return snap_main


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--raw",required=True)
    ap.add_argument("--snapshot-dir",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    outp=Path(args.out); rawp=Path(args.raw); snaproot=Path(args.snapshot_dir)
    outp.parent.mkdir(parents=True,exist_ok=True); rawp.parent.mkdir(parents=True,exist_ok=True); snaproot.mkdir(parents=True,exist_ok=True)

    refs,raw=list_current_top30()
    rawp.write_text(raw,encoding="utf-8")

    acquisitions=[]; acquisition_failures=[]; smoke_failures=[]; episode_failures=[]; rows=[]; unique_rows=[]
    base_receipt=None
    with tempfile.TemporaryDirectory(prefix="v23a-frontier-") as td:
        tmp=Path(td); by_sha={}

        for rank,ref in enumerate(refs,start=1):
            try:
                main,sha,receipt=acquire_retry(ref,tmp/f"rank{rank:02d}")
                acquisitions.append({"rank":rank,"ref":ref,"status":"ACQUIRED","main_sha256":sha,"receipt":receipt})
                meta=by_sha.setdefault(sha,{"main":main,"ranks":[],"refs":[]})
                meta["ranks"].append(rank); meta["refs"].append(ref)
                print("V23A_ACQUIRE",json.dumps({"rank":rank,"ref":ref,"main_sha256":sha},sort_keys=True),flush=True)
            except Exception as exc:
                rec={"rank":rank,"ref":ref,"status":"UNAVAILABLE","error":f"{type(exc).__name__}: {exc}"}
                acquisitions.append(rec); acquisition_failures.append(rec)
                print("V23A_UNAVAILABLE",json.dumps(rec,sort_keys=True),flush=True)

        base_main,base_receipt=acquire_expected_retry(BASE["handle"],BASE["expected_main_sha256"],tmp/"base")

        removed=[]
        for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
            if key in os.environ:
                removed.append(key); os.environ.pop(key,None)

        for sha,meta in sorted(by_sha.items(),key=lambda kv:min(kv[1]["ranks"])):
            smokes=[]
            for seat in SEATS:
                try: smokes.append(run_smoke(meta["main"],seat))
                except Exception as exc: smokes.append({"seat":seat,"ok":False,"error":f"{type(exc).__name__}: {exc}"})
                finally: purge_package_modules(meta["main"].parent)
            pass_both=len(smokes)==2 and all(bool(x.get("ok")) for x in smokes)
            rep_rank=min(meta["ranks"]); rep_ref=meta["refs"][meta["ranks"].index(rep_rank)]
            ur={"main_sha256":sha,"ranks":sorted(meta["ranks"]),"refs":list(meta["refs"]),"representative_rank":rep_rank,"representative_ref":rep_ref,"smoke":smokes,"smoke_pass_both_seats":pass_both,"is_v47_base_identity":sha==BASE["expected_main_sha256"]}
            unique_rows.append(ur)
            if not pass_both: smoke_failures.append({"sha":sha,"representative_ref":rep_ref})
            print("V23A_SMOKE",json.dumps({"sha":sha,"rank":rep_rank,"ref":rep_ref,"pass_both":pass_both},sort_keys=True),flush=True)

        eligible=[x for x in unique_rows if x["smoke_pass_both_seats"] and not x["is_v47_base_identity"]]
        eligible.sort(key=lambda x:(int(x["representative_rank"]),x["main_sha256"]))
        selected=eligible[:MAX_REPS]

        # Immutable snapshot before discovery episodes.
        base_snap=snapshot_package(base_main,snaproot/"base")
        if sha256_bytes(base_snap.read_bytes())!=BASE["expected_main_sha256"]:
            raise RuntimeError("base snapshot SHA mismatch")

        selected_paths={}
        snapshot_manifest=[]
        for rep in selected:
            src=by_sha[rep["main_sha256"]]["main"]
            dest=snaproot/"sources"/rep["main_sha256"]
            snap_main=snapshot_package(src,dest)
            got=sha256_bytes(snap_main.read_bytes())
            if got!=rep["main_sha256"]:
                raise RuntimeError(f"snapshot SHA mismatch {got} != {rep['main_sha256']}")
            selected_paths[rep["main_sha256"]]=snap_main
            snapshot_manifest.append({"sha":got,"representative_rank":rep["representative_rank"],"representative_ref":rep["representative_ref"],"path":f"sources/{got}/main.py"})
        (snaproot/"MANIFEST.json").write_text(json.dumps({"schema":"kculture-v23-immutable-source-snapshot-v1","base":{"sha":BASE["expected_main_sha256"],"path":"base/main.py"},"sources":snapshot_manifest},indent=2,sort_keys=True)+"\n")

        if len(selected)>=MIN_REPS:
            for rep in selected:
                opp=selected_paths[rep["main_sha256"]]
                for seed in DISCOVERY_SEEDS:
                    for seat in SEATS:
                        try:
                            rr=run_all3(base_snap,opp,seed,seat)
                            row={"rank":int(rep["representative_rank"]),"ref":rep["representative_ref"],"main_sha256":rep["main_sha256"],"seed":int(seed),"seat":int(seat),**rr}
                            rows.append(row)
                            print("V23A_EPISODE",json.dumps({k:row[k] for k in ("rank","ref","main_sha256","seed","seat","result","score","margin")},sort_keys=True),flush=True)
                        except Exception as exc:
                            fail={"rank":int(rep["representative_rank"]),"ref":rep["representative_ref"],"sha":rep["main_sha256"],"seed":int(seed),"seat":int(seat),"error":f"{type(exc).__name__}: {exc}"}
                            episode_failures.append(fail)
                            print("V23A_EPISODE_FAIL",json.dumps(fail,sort_keys=True),flush=True)
                        finally:
                            purge_package_modules(base_snap.parent); purge_package_modules(opp.parent)

    expected=len(selected)*len(DISCOVERY_SEEDS)*len(SEATS)
    keys={(r["main_sha256"],r["seed"],r["seat"]) for r in rows}
    hard=[r for r in rows if float(r["score"])<1.0]
    hard_shas=sorted({r["main_sha256"] for r in hard}); hard_seeds=sorted({int(r["seed"]) for r in hard})
    selected_snapshot_ok=(snaproot/"MANIFEST.json").exists() and len(snapshot_manifest)==len(selected)
    mechanical_pass=(
        len(refs)==TOP_N and len(selected)>=MIN_REPS and expected>=96 and len(rows)==expected and len(keys)==expected
        and not episode_failures and selected_snapshot_ok
    )
    if not mechanical_pass: decision="V23A_MECHANICS_INVALID"
    elif len(hard)>=12 and len(hard_shas)>=4 and len(hard_seeds)>=3: decision="V23A_IMMUTABLE_HARD_POPULATION_READY"
    else: decision="V23A_FRONTIER_TOO_EASY_REFRESH_LATER"

    result={
      "schema":"kculture-all3-v23a-immutable-frontier-v1","engine":EXPECTED_ENGINE,"decision":decision,"mechanical_pass":mechanical_pass,
      "current_top30_refs":refs,"discovery_seeds":list(DISCOVERY_SEEDS),"seats":list(SEATS),
      "acquisitions":acquisitions,"unavailable_refs":acquisition_failures,
      "unique_sources_acquired":len(unique_rows),"smoke_failures":smoke_failures,
      "selected_representatives":selected,"selected_representative_count":len(selected),
      "snapshot_manifest":"MANIFEST.json","snapshot_source_count":len(snapshot_manifest),
      "base":{"handle":BASE["handle"],"expected_main_sha256":BASE["expected_main_sha256"],"receipt":base_receipt},
      "expected_games":expected,"completed_games":len(rows),"hard_contexts":len(hard),"hard_source_shas":hard_shas,"hard_seeds":hard_seeds,
      "hard_rows":hard,"rows":rows,"episode_failures":episode_failures,
      "credentials_removed_before_third_party_execution":removed,
      "selected_sources_persisted_to_ephemeral_artifact":True,
      "opponent_identity_runtime_feature":False,"automatic_kaggle_submission":False,
    }
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V23A_RESULT",json.dumps({"decision":decision,"mechanical_pass":mechanical_pass,"selected_representatives":len(selected),"expected_games":expected,"completed_games":len(rows),"hard_contexts":len(hard),"hard_sources":len(hard_shas),"hard_seeds":len(hard_seeds),"unavailable_refs":len(acquisition_failures),"episode_failures":len(episode_failures)},sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)

if __name__=="__main__":
    main()
