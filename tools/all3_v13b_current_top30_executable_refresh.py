#!/usr/bin/env python3
"""V13B current Top-30 executable frontier refresh.

Downloads public notebook packages/sources transiently, deduplicates exact main.py bytes,
then removes Kaggle credentials from the process environment before executing any
third-party code. Only provenance + mechanical smoke metadata is persisted.
"""
from __future__ import annotations
import argparse,json,math,os,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    EXPECTED_ENGINE, acquire_public_main, load_public_agent, purge_package_modules, sha256_bytes
)

SEED=78001

def run_smoke(main_py:Path,seat:int)->dict:
    purge_package_modules(main_py.parent)
    agent=load_public_agent(main_py)
    entry=getattr(agent,"__name__",None)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":SEED},debug=False)
    t0=time.perf_counter()
    if seat==0:
        env.run([agent,"starter"])
    else:
        env.run(["starter",agent])
    secs=time.perf_counter()-t0
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    ok=(statuses==["DONE","DONE"] and len(rewards)==2 and steps>=720 and all(math.isfinite(x) for x in rewards))
    return {"seat":seat,"ok":ok,"entrypoint":entry,"statuses":statuses,"rewards":rewards,"steps":steps,"seconds":secs}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit(f"engine mismatch {getattr(kaggle_environments,'__version__',None)} != {EXPECTED_ENGINE}")

    cfg=json.loads(Path(args.config).read_text())
    refs=list(cfg.get("current_top30") or [])
    if len(refs)!=30 or [int(x.get("rank",0)) for x in refs]!=list(range(1,31)):
        raise SystemExit("V13B config must contain exact ranks 1..30")

    frozen=json.loads((ROOT/"data/programme_teacher/2026-09-18/PROGRAMME_CORPUS.json").read_text())
    frozen_by_sha={}
    for e in frozen.get("entries",[]):
        h=e.get("source_sha256")
        if h:
            frozen_by_sha.setdefault(h,[]).append({
              "rank":e.get("rank"),"ref":e.get("ref"),"title":e.get("title"),
              "programme_families":e.get("programme_families") or [],
              "license_markers":e.get("license_markers") or []
            })

    acquisitions=[]
    by_sha={}
    failures=[]
    started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v13b-current-frontier-") as td:
        tmp=Path(td)
        for row in refs:
            rank=int(row["rank"]);ref=str(row["ref"])
            try:
                main_py,receipt=acquire_public_main(ref,tmp/f"r{rank:02d}")
                h=sha256_bytes(main_py.read_bytes())
                rec={
                  "rank":rank,"ref":ref,"status":"ACQUIRED","main_sha256":h,
                  "main_bytes":main_py.stat().st_size,
                  "receipt":receipt,
                  "frozen_identity_matches":frozen_by_sha.get(h,[])
                }
                acquisitions.append(rec)
                by_sha.setdefault(h,{"main":main_py,"ranks":[],"refs":[]})
                by_sha[h]["ranks"].append(rank);by_sha[h]["refs"].append(ref)
                print("V13B_ACQUIRE",json.dumps({"rank":rank,"ref":ref,"main_sha256":h,"acquisition":receipt.get("acquisition")},sort_keys=True),flush=True)
            except Exception as exc:
                err={"rank":rank,"ref":ref,"status":"ACQUIRE_FAIL","error":f"{type(exc).__name__}: {exc}"}
                acquisitions.append(err);failures.append(err)
                print("V13B_ACQUIRE_FAIL",json.dumps(err,sort_keys=True),flush=True)

        # Third-party source execution starts only after all credential-bearing acquisition is over.
        removed={}
        for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
            if key in os.environ:
                removed[key]=True
                os.environ.pop(key,None)

        unique=[]
        for h,meta in sorted(by_sha.items(),key=lambda kv:min(kv[1]["ranks"])):
            main_py=meta["main"]
            smokes=[]
            smoke_error=None
            for seat in (0,1):
                try:
                    smokes.append(run_smoke(main_py,seat))
                except Exception as exc:
                    smoke_error=f"{type(exc).__name__}: {exc}"
                    smokes.append({"seat":seat,"ok":False,"error":smoke_error})
                finally:
                    purge_package_modules(main_py.parent)
            pass_both=len(smokes)==2 and all(bool(x.get("ok")) for x in smokes)
            old=frozen_by_sha.get(h,[])
            row={
              "main_sha256":h,
              "ranks":sorted(meta["ranks"]),
              "refs":meta["refs"],
              "representative_rank":min(meta["ranks"]),
              "representative_ref":meta["refs"][meta["ranks"].index(min(meta["ranks"]))],
              "source_bytes":main_py.stat().st_size,
              "frozen_identity_matches":old,
              "smoke":smokes,
              "smoke_pass_both_seats":pass_both,
              "smoke_error":smoke_error,
            }
            unique.append(row)
            print("V13B_UNIQUE_SMOKE",json.dumps({
              "main_sha256":h,"ranks":row["ranks"],"refs":row["refs"],
              "pass_both":pass_both,"smoke":smokes
            },sort_keys=True),flush=True)

        acquired=[x for x in acquisitions if x.get("status")=="ACQUIRED"]
        pass_sha={x["main_sha256"] for x in unique if x["smoke_pass_both_seats"]}
        top10_pass=sum(1 for x in acquired if int(x["rank"])<=10 and x["main_sha256"] in pass_sha)
        mech={
          "refs_requested":30,
          "refs_acquired":len(acquired),
          "refs_failed":30-len(acquired),
          "unique_sources_acquired":len(unique),
          "unique_sources_both_seat_smoke_pass":len(pass_sha),
          "top10_refs_on_smoke_pass_source":top10_pass,
        }
        ready=(
          mech["refs_acquired"]>=24
          and mech["unique_sources_acquired"]>=12
          and mech["unique_sources_both_seat_smoke_pass"]>=10
          and top10_pass>=5
        )
        if ready:
            decision="V13B_EXECUTABLE_FRONTIER_READY"
        elif mech["refs_acquired"]>=24 and mech["unique_sources_acquired"]>=12:
            decision="V13B_EXECUTABLE_FRONTIER_PARTIAL"
        else:
            decision="V13B_FRONTIER_REFRESH_INCOMPLETE"

        result={
          "schema":"kculture-all3-v13b-current-top30-executable-refresh-v1",
          "engine":EXPECTED_ENGINE,
          "config":args.config,
          "seed":SEED,
          "decision":decision,
          "mechanics":mech,
          "acquisitions":acquisitions,
          "unique_sources":unique,
          "acquisition_failures":failures,
          "credentials_removed_before_third_party_execution":sorted(removed),
          "third_party_code_persisted":False,
          "automatic_kaggle_submission":False,
          "local_smoke_wl_is_strategically_meaningless":True,
          "seconds":time.perf_counter()-started,
        }
        out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V13B_RESULT",json.dumps({
          "decision":decision,"mechanics":mech,
          "acquire_failures":len(failures),
          "unique_pass_representatives":[
            {"rank":x["representative_rank"],"ref":x["representative_ref"],"sha":x["main_sha256"]}
            for x in unique if x["smoke_pass_both_seats"]
          ]
        },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
