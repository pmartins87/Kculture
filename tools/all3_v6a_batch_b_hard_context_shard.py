#!/usr/bin/env python3
"""V6A Batch B hard-context census shard for one V2 opponent family."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.all3_v6a_hard_context_shard import (
    EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire,purge_paths,run,
)

SEEDS=list(range(75109,75117))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v6b-{args.opponent}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec.get("family"),"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp")
            provenance["opponent"]={**rec,"family":spec.get("family")}
        paths=[base_main,opp_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                purge_paths(paths)
                r=run(base_main,opp_main,seed,seat)
                rows.append({
                  "opponent":args.opponent,"family":spec.get("family"),"seed":seed,"seat":seat,
                  "reward":r["reward"],"opponent_reward":r["opponent_reward"],
                  "margin":r["margin"],"score":r["score"],"steps":r["steps"],
                })
                print("V6B_CONTEXT",json.dumps(rows[-1],sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge_paths(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==16
    result={
      "schema":"kculture-all3-v6a-hard-context-batch-b-shard-v1",
      "opponent":args.opponent,"family":spec.get("family"),"seeds":SEEDS,
      "mechanical_pass":mech,"rows":rows,"failures":failures,
      "provenance":provenance,"seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V6B_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),
      "wins":sum(r["score"]==1 for r in rows),"ties":sum(r["score"]==0.5 for r in rows),
      "losses":sum(r["score"]==0 for r in rows),
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__":main()
