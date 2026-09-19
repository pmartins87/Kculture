#!/usr/bin/env python3
"""Aggregate 12 O-PC1 opponent x seed shards with frozen gate."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

OPPS=("v47_mirror","v48","ready_stock")
SEEDS=(74901,74902,74903,74904)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[]
    for s in shards: rows+=s.get("rows",[]);failures+=s.get("failures",[])
    expected={(o,s) for o in OPPS for s in SEEDS}
    actual={(s.get("opponent"),int(s.get("seed"))) for s in shards if s.get("opponent") and s.get("seed") is not None}
    mech=len(shards)==12 and len(rows)==24 and not failures and all(s.get("mechanical_pass") for s in shards) and actual==expected

    sd=[float(r["score_delta"]) for r in rows];md=[float(r["margin_delta"]) for r in rows]
    summary={
      "contexts":len(rows),
      "mean_score_delta":statistics.fmean(sd) if sd else None,
      "mean_margin_delta":statistics.fmean(md) if md else None,
      "positive_score_contexts":sum(x>0 for x in sd),
      "negative_score_contexts":sum(x<0 for x in sd),
      "fire_contexts":sum(int(r["fire_count"])>0 for r in rows),
      "mean_fire_count":statistics.fmean(int(r["fire_count"]) for r in rows) if rows else None,
      "plant_replacements":sum(int(r["plant_replacements"]) for r in rows),
      "seed_units_redirected":sum(int(r["seed_units_redirected"]) for r in rows),
    }
    by={}
    for opp in OPPS:
        xs=[r for r in rows if r["opponent"]==opp]
        by[opp]={
          "contexts":len(xs),
          "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in xs) if xs else None,
          "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in xs) if xs else None,
          "positive_score_contexts":sum(float(r["score_delta"])>0 for r in xs),
          "negative_score_contexts":sum(float(r["score_delta"])<0 for r in xs),
          "fire_contexts":sum(int(r["fire_count"])>0 for r in xs),
        }

    if mech and summary["mean_score_delta"]>0 and summary["negative_score_contexts"]==0 and summary["mean_margin_delta"]>0 and summary["fire_contexts"]>=4:
        decision="O_PC1_DEV_PASS"
    elif mech and summary["mean_score_delta"]==0 and summary["negative_score_contexts"]==0 and summary["mean_margin_delta"]>0 and summary["fire_contexts"]>=4:
        decision="O_PC1_DEV_SAFE_MARGIN"
    elif mech:
        decision="O_PC1_DEV_CLOSE"
    else:
        decision="O_PC1_DEV_MECHANICS_INVALID"

    result={
      "schema":"kculture-o-pc1-development-parallel-v1","mechanical_pass":mech,
      "decision":decision,"summary":summary,"by_opponent":by,"rows":rows,
      "failures":failures,"automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_PC1_DEV_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"summary":summary,
      "by_opponent":by,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
