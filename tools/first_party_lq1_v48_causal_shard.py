#!/usr/bin/env python3
"""Parallel-equivalent shard for O-LQ1 fresh V48 causal gate."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.first_party_late_queue_sanitation_causal_gate import (
    EXPECTED_ENGINE,BASE,V48,acquire,run,pretrigger_parity,purge,
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")
    rows=[]; failures=[]; provenance={}; started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"o-lq1-shard-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
        paths=[base_main,v48_main]
        for seat in (0,1):
          try:
            purge(paths); b=run(base_main,v48_main,args.seed,seat,False)
            purge(paths); t=run(base_main,v48_main,args.seed,seat,True)
            parity=pretrigger_parity(b,t)
            if not parity["ok"]:
                raise RuntimeError(f"pretrigger parity failure {parity}")
            row={
                "seed":args.seed,"seat":seat,
                "base_score":b["score"],"treatment_score":t["score"],
                "score_delta":t["score"]-b["score"],
                "base_margin":b["margin"],"treatment_margin":t["margin"],
                "margin_delta":t["margin"]-b["margin"],
                "base_rewards":b["rewards"],"treatment_rewards":t["rewards"],
                "fire_count":t["fire_count"],
                "first_fire":min(t["fire_steps"]) if t["fire_steps"] else None,
                "last_fire":max(t["fire_steps"]) if t["fire_steps"] else None,
                "changed_slots":t["changed_slots"],
                "cleared_slots":t["cleared_slots"],
                "qty_down_slots":t["qty_down_slots"],
                "parity":parity,
            }
            rows.append(row)
            print("O_LQ1_SHARD_PAIR",json.dumps(row,sort_keys=True),flush=True)
          except Exception as exc:
            failures.append({"seed":args.seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
          finally:
            purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==2 and all(r["parity"]["ok"] for r in rows)
    result={
        "schema":"kculture-o-lq1-v48-causal-shard-v1",
        "seed":args.seed,"mechanical_pass":mech,
        "rows":rows,"failures":failures,"provenance":provenance,
        "seconds":time.perf_counter()-started,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ1_SHARD_RESULT",json.dumps({
        "seed":args.seed,"mechanical_pass":mech,"contexts":len(rows),
        "failures":len(failures),"seconds":result["seconds"]
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
