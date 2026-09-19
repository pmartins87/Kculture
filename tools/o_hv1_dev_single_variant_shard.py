#!/usr/bin/env python3
"""Execution-equivalent single-variant shard for O-HV1 development."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_hv1_dev_shard import (
    EXPECTED_ENGINE,BASE,SEEDS,CONFIGS,V2_OPPONENTS,
    acquire,run,parity,purge,
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--opponent",required=True)
    ap.add_argument("--variant",required=True,choices=sorted(CONFIGS))
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"hv1-single-{args.opponent}-{args.variant}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,provenance["opponent"]=acquire(spec,tmp/"opp")
        paths=[base_main,opp_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                purge(paths);b=run(base_main,opp_main,seed,seat,"BASE")
                purge(paths);t=run(base_main,opp_main,seed,seat,args.variant)
                p=parity(b,t)
                if not p["ok"]: raise RuntimeError(f"pre-HV parity failure {p}")
                rows.append({
                  "opponent":args.opponent,"family":spec["family"],"seed":seed,"seat":seat,
                  "variant":args.variant,"config":CONFIGS[args.variant],
                  "base_score":b["score"],"base_margin":b["margin"],"base_rewards":b["rewards"],
                  "score":t["score"],"margin":t["margin"],"rewards":t["rewards"],
                  "score_delta":t["score"]-b["score"],"margin_delta":t["margin"]-b["margin"],
                  "fire_count":t["fire_count"],
                  "first_fire":min((x["step"] for x in t["fire_meta"]),default=None),
                  "products":dict(__import__("collections").Counter(x["product"] for x in t["fire_meta"])),
                  "gross_added":sum(int(x["gross_value"]) for x in t["fire_meta"]),
                  "parity":p,
                })
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==8
    result={
      "schema":"kculture-o-hv1-dev-single-shard-v1",
      "opponent":args.opponent,"family":spec["family"],"variant":args.variant,
      "config":CONFIGS[args.variant],"seeds":SEEDS,
      "mechanical_pass":mech,"rows":rows,"failures":failures,
      "provenance":provenance,"seconds":time.perf_counter()-started,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_HV1_SINGLE_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"variant":args.variant,"mechanical_pass":mech,
      "contexts":len(rows),"failures":len(failures),
      "mean_score_delta":(__import__("statistics").fmean(x["score_delta"] for x in rows) if rows else None),
      "mean_margin_delta":(__import__("statistics").fmean(x["margin_delta"] for x in rows) if rows else None),
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
