#!/usr/bin/env python3
"""Execution-equivalent O-PC1 shard for one opponent x one seed."""
from __future__ import annotations
import argparse,json,statistics,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire,run,parity,purge

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--opponent",required=True)
    ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"pc1-{args.opponent}-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,provenance["opponent"]=acquire(spec,tmp/"opp")
        paths=[base_main,opp_main]

        for seat in (0,1):
            try:
                purge(paths);b=run(base_main,opp_main,args.seed,seat,False)
                purge(paths);t=run(base_main,opp_main,args.seed,seat,True)
                p=parity(b,t)
                if not p["ok"]: raise RuntimeError(f"pre-PC1 parity failure {p}")
                rows.append({
                  "opponent":args.opponent,"family":spec["family"],"seed":args.seed,"seat":seat,
                  "base_score":b["score"],"treatment_score":t["score"],"score_delta":t["score"]-b["score"],
                  "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":t["margin"]-b["margin"],
                  "base_rewards":b["rewards"],"treatment_rewards":t["rewards"],
                  "fire_count":t["fire_count"],
                  "first_fire":min((x["step"] for x in t["fire_meta"]),default=None),
                  "plant_replacements":sum(int(x["plant_replacements"]) for x in t["fire_meta"]),
                  "seed_units_redirected":sum(int(x["seed_units_redirected"]) for x in t["fire_meta"]),
                  "max_value_edge":max((int(x["carrot_value"])-int(x["wheat_value"]) for x in t["fire_meta"]),default=None),
                  "parity":p,
                })
            except Exception as exc:
                failures.append({"seed":args.seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==2
    result={
      "schema":"kculture-o-pc1-dev-seed-shard-v1","opponent":args.opponent,"family":spec["family"],
      "seed":args.seed,"mechanical_pass":mech,"rows":rows,"failures":failures,
      "provenance":provenance,"seconds":time.perf_counter()-started,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_PC1_SEED_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"seed":args.seed,"mechanical_pass":mech,
      "contexts":len(rows),"failures":len(failures),
      "mean_score_delta":statistics.fmean(r["score_delta"] for r in rows) if rows else None,
      "mean_margin_delta":statistics.fmean(r["margin_delta"] for r in rows) if rows else None,
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
