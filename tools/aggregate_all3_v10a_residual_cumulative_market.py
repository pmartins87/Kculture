#!/usr/bin/env python3
"""Aggregate V10A cumulative residual market upper-bound contexts."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
MODES=("BASE","FULL_ALL","FULL_W2PLUS","STRUCT_W2PLUS","INSERT_W2PLUS","QTY_W2PLUS","REORDER_W2PLUS")
def summ(rows):
    if not rows:return {}
    pos=[r for r in rows if float(r["score_delta"])>0]
    return {
      "contexts":len(rows),
      "positive_score_contexts":len(pos),
      "positive_indices":sorted({int(r["index"]) for r in pos}),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
      "mean_substitutions":statistics.fmean(float(r["substitutions"]) for r in rows),
      "total_physical_fallbacks":sum(int(r["physical_fallbacks"]) for r in rows),
    }
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    by={m:summ([r for r in rows if r["mode"]==m]) for m in MODES}
    mech=len(docs)==4 and len(rows)==28 and not failures and all(d.get("mechanical_pass") for d in docs)
    full_all=by["FULL_ALL"].get("positive_score_contexts",0)
    full_w2=by["FULL_W2PLUS"].get("positive_score_contexts",0)
    struct=by["STRUCT_W2PLUS"].get("positive_score_contexts",0)
    if not mech:decision="V10A_MECHANICS_INVALID"
    elif full_all==0:decision="V10A_RESIDUAL_MARKET_UPPER_BOUND_CLOSED"
    elif full_w2==0:decision="V10A_EARLY_RESIDUAL_REQUIRED"
    elif struct>0:decision="V10A_W2PLUS_STRUCTURAL_HEADROOM"
    else:decision="V10A_W2PLUS_NONSTRUCTURAL_HEADROOM"
    result={"schema":"kculture-v10a-residual-cumulative-market-v1","mechanical_pass":mech,
      "decision":decision,"by_mode":by,"rows":rows,"failures":failures,
      "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V10A_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"by_mode":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
