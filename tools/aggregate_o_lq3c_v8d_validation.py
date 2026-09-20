#!/usr/bin/env python3
"""Aggregate frozen O-LQ3C V8D fresh paired validation."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

OPPS=("v48","v47_mirror","ready_stock")
def summarize(rows):
    if not rows:return {}
    return {
      "contexts":len(rows),
      "fire_contexts":sum(int(r["fire_count"])>0 for r in rows),
      "total_fires":sum(int(r["fire_count"]) for r in rows),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
      "positive_score_contexts":sum(float(r["score_delta"])>0 for r in rows),
      "negative_score_contexts":sum(float(r["score_delta"])<0 for r in rows),
      "nonwin_to_win":sum(float(r["base_score"])<1 and float(r["treatment_score"])==1 for r in rows),
      "win_to_nonwin":sum(float(r["base_score"])==1 and float(r["treatment_score"])<1 for r in rows),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    by={o:summarize([r for r in rows if r["opponent"]==o]) for o in OPPS}
    overall=summarize(rows)
    mech=(len(docs)==9 and len(rows)==72 and not failures and all(d.get("mechanical_pass") for d in docs))
    coverage=mech and by["v48"].get("fire_contexts",0)>=4 and (by["v47_mirror"].get("fire_contexts",0)+by["ready_stock"].get("fire_contexts",0))>=2
    regression=overall.get("win_to_nonwin",0)>0 or by["v47_mirror"].get("negative_score_contexts",0)>0 or by["ready_stock"].get("negative_score_contexts",0)>0
    pass_gate=(coverage and not regression and by["v48"].get("mean_score_delta",0)>0 and by["v48"].get("positive_score_contexts",0)>=1)
    if not mech:decision="V8D_MECHANICS_INVALID"
    elif not coverage:decision="V8D_CONDITIONAL_ORDER_UNDERPOWERED"
    elif regression:decision="V8D_CONDITIONAL_ORDER_REGRESSION_CLOSE"
    elif pass_gate:decision="V8D_CONDITIONAL_ORDER_FRESH_PASS"
    else:decision="V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION"
    result={"schema":"kculture-v8d-lq3c-validation-v1","mechanical_pass":mech,"coverage_pass":coverage,
            "decision":decision,"overall":overall,"by_opponent":by,"rows":rows,"shards":docs,"failures":failures,
            "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8D_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"coverage_pass":coverage,
      "overall":overall,"by_opponent":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
