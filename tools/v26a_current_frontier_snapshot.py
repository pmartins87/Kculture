#!/usr/bin/env python3
"""V26A current-frontier immutable snapshot discovery."""
from __future__ import annotations
import argparse,json,math,os,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.kaggle_meta_scout_cli import csv_rows,normkey
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE

TOP_N=30
MAX_REPS=12
MIN_REPS=8
SMOKE_SEED=79500

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
    refs=[];seen=set()
    for row in rows:
        ref=ref_value(row)
        if ref and ref not in seen:
            seen.add(ref);refs.append(ref)
        if len(refs)>=TOP_N:
            break
    if len(refs)!=TOP_N:
        raise RuntimeError(f"expected Top-{TOP_N}, got {len(refs)}")
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

def run_smoke(main_py,seat):
    purge_package_modules(main_py.parent)
    agent=load_public_agent(main_py)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":SMOKE_SEED},debug=False)
    if seat==0:env.run([agent,"starter"])
    else:env.run(["starter",agent])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    return {"seat":seat,"ok":statuses==["DONE","DONE"] and len(rewards)==2 and steps>=720 and all(math.isfinite(x) for x in rewards),"statuses":statuses,"rewards":rewards,"steps":steps}

def snapshot_package(main_py,dest):
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(main_py.parent,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    snap=dest/"main.py"
    if not snap.exists():snap.write_bytes(main_py.read_bytes())
    return snap

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--raw",required=True)
    ap.add_argument("--snapshot-dir",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    outp=Path(args.out);rawp=Path(args.raw);snaproot=Path(args.snapshot_dir)
    outp.parent.mkdir(parents=True,exist_ok=True);rawp.parent.mkdir(parents=True,exist_ok=True);snaproot.mkdir(parents=True,exist_ok=True)

    refs,raw=list_current_top30();rawp.write_text(raw,encoding="utf-8")
    acquisitions=[];unavailable=[];unique_rows=[];smoke_failures=[]

    with tempfile.TemporaryDirectory(prefix="v26a-frontier-") as td:
        tmp=Path(td);by_sha={}
        for rank,ref in enumerate(refs,start=1):
            try:
                main,sha,receipt=acquire_retry(ref,tmp/f"rank{rank:02d}")
                acquisitions.append({"rank":rank,"ref":ref,"status":"ACQUIRED","main_sha256":sha,"receipt":receipt})
                meta=by_sha.setdefault(sha,{"main":main,"ranks":[],"refs":[]})
                meta["ranks"].append(rank);meta["refs"].append(ref)
                print("V26A_ACQUIRE",json.dumps({"rank":rank,"ref":ref,"sha":sha},sort_keys=True),flush=True)
            except Exception as exc:
                rec={"rank":rank,"ref":ref,"status":"UNAVAILABLE","error":f"{type(exc).__name__}: {exc}"}
                acquisitions.append(rec);unavailable.append(rec)
                print("V26A_UNAVAILABLE",json.dumps(rec,sort_keys=True),flush=True)

        for sha,meta in sorted(by_sha.items(),key=lambda kv:min(kv[1]["ranks"])):
            smokes=[]
            for seat in (0,1):
                try:smokes.append(run_smoke(meta["main"],seat))
                except Exception as exc:smokes.append({"seat":seat,"ok":False,"error":f"{type(exc).__name__}: {exc}"})
                finally:purge_package_modules(meta["main"].parent)
            pass_both=len(smokes)==2 and all(bool(x.get("ok")) for x in smokes)
            rr=min(meta["ranks"]);ref=meta["refs"][meta["ranks"].index(rr)]
            row={"main_sha256":sha,"ranks":sorted(meta["ranks"]),"refs":list(meta["refs"]),"representative_rank":rr,"representative_ref":ref,"smoke":smokes,"smoke_pass_both_seats":pass_both,"is_v47_identity":sha==BASE["expected_main_sha256"]}
            unique_rows.append(row)
            if not pass_both:smoke_failures.append({"sha":sha,"ref":ref})
            print("V26A_SMOKE",json.dumps({"sha":sha,"rank":rr,"ref":ref,"pass_both":pass_both,"is_v47_identity":row["is_v47_identity"]},sort_keys=True),flush=True)

        eligible=[x for x in unique_rows if x["smoke_pass_both_seats"] and not x["is_v47_identity"]]
        eligible.sort(key=lambda x:(int(x["representative_rank"]),x["main_sha256"]))
        selected=eligible[:MAX_REPS]

        manifest_sources=[]
        for rep in selected:
            src=by_sha[rep["main_sha256"]]["main"]
            snap=snapshot_package(src,snaproot/"sources"/rep["main_sha256"])
            got=sha256_bytes(snap.read_bytes())
            if got!=rep["main_sha256"]:raise RuntimeError(f"snapshot SHA mismatch {got} != {rep['main_sha256']}")
            manifest_sources.append({"sha":got,"representative_rank":rep["representative_rank"],"representative_ref":rep["representative_ref"],"path":f"sources/{got}/main.py"})

        manifest={"schema":"kculture-v26a-current-frontier-snapshot-v1","sources":manifest_sources}
        (snaproot/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")

    mechanical_pass=(len(refs)==TOP_N and len(selected)>=MIN_REPS and len(manifest_sources)==len(selected) and all(x["smoke_pass_both_seats"] for x in selected))
    decision="V26A_FRONTIER_SNAPSHOT_READY" if mechanical_pass else "V26A_FRONTIER_SNAPSHOT_INVALID"
    result={"schema":"kculture-v26a-frontier-snapshot-result-v1","decision":decision,"mechanical_pass":mechanical_pass,"top30_refs":refs,"acquisitions":acquisitions,"unavailable_refs":unavailable,"unique_sources":len(unique_rows),"selected_representatives":selected,"selected_representative_count":len(selected),"smoke_failures":smoke_failures,"snapshot_manifest":"MANIFEST.json","automatic_kaggle_submission":False}
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V26A_SNAPSHOT_RESULT",json.dumps({"decision":decision,"mechanical_pass":mechanical_pass,"selected_representatives":len(selected),"unavailable_refs":len(unavailable),"smoke_failures":len(smoke_failures)},sort_keys=True),flush=True)
    if not mechanical_pass:raise SystemExit(2)

if __name__=="__main__":
    main()
