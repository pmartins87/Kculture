#!/usr/bin/env python3
"""V8D-E1 fresh extension shard. O-LQ3C is unchanged."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_lq3c_v8d_validation_shard import (
    EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire,Candidate,run,parity,purge
)

SEED_BLOCKS={
 "D":[76013,76014,76015,76016],
 "E":[76017,76018,76019,76020],
 "F":[76021,76022,76023,76024],
}
ALLOWED={"v48","v47_mirror","ready_stock"}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--block",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    if args.opponent not in ALLOWED:raise SystemExit("bad opponent")
    if args.block not in SEED_BLOCKS:raise SystemExit("bad block")
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};paths=[];started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v8d-e1-{args.opponent}-{args.block}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main;provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");provenance["opponent"]={**rec,"family":spec["family"]}
        paths=[base_main,opp_main]
        for seed in SEED_BLOCKS[args.block]:
          for seat in (0,1):
            key={"opponent":args.opponent,"family":spec["family"],"block":args.block,"seed":seed,"seat":seat}
            try:
                purge(paths);b=run(base_main,opp_main,seed,seat,False)
                purge(paths);t=run(base_main,opp_main,seed,seat,True)
                if not parity(b,t):raise RuntimeError("pre-fire parity failure")
                row={**key,
                     "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                     "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                     "fire_count":t["fire_count"],"fire_turns":[int(x["turn"]) for x in t["fire_meta"]]}
                rows.append(row)
                print("V8D_E1_PAIR",json.dumps(row,sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==8
    result={"schema":"kculture-v8d-e1-lq3c-shard-v1","mechanical_pass":mech,
            "opponent":args.opponent,"block":args.block,"seeds":SEED_BLOCKS[args.block],
            "rows":rows,"failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started,
            "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8D_E1_SHARD_RESULT",json.dumps({"opponent":args.opponent,"block":args.block,"mechanical_pass":mech,
      "rows":len(rows),"fire_contexts":sum(r["fire_count"]>0 for r in rows),
      "positive_score_contexts":sum(r["score_delta"]>0 for r in rows),
      "negative_score_contexts":sum(r["score_delta"]<0 for r in rows),
      "mean_score_delta":sum(r["score_delta"] for r in rows)/len(rows) if rows else 0,
      "mean_margin_delta":sum(r["margin_delta"] for r in rows)/len(rows) if rows else 0,
      "failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
