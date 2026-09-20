#!/usr/bin/env python3
"""Aggregate V8B pairwise SELL-order transposition oracle."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    mech=len(docs)==4 and not failures and all(d.get("mechanical_pass") for d in docs)
    rows=[]
    for d in docs:
        b=d["base"];best=d["best"];ctx=d["context"]
        rows.append({
          "index":d["index"],"opponent":ctx["opponent"],"family":ctx.get("family"),
          "seed":ctx["seed"],"seat":ctx["seat"],
          "base_score":b["score"],"base_margin":b["margin"],
          "best_score":best["score"],"best_margin":best["margin"],
          "score_delta":float(best["score"])-float(b["score"]),
          "margin_delta":float(best["margin"])-float(b["margin"]),
          "best":best,
          "winning_branch_count":sum(float(x["score"])==1.0 for x in d.get("branches",[])),
        })
    flips=[r for r in rows if float(r["base_score"])<1 and float(r["best_score"])==1]
    mean_delta=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    if not mech:decision="V8B_ORDER_MECHANICS_INVALID"
    elif len(flips)>=2:decision="V8B_ORDER_HEADROOM_REPEATABLE"
    elif len(flips)==1:decision="V8B_ORDER_HEADROOM_NARROW"
    elif mean_delta>0:decision="V8B_ORDER_MARGIN_ONLY"
    else:decision="V8B_ORDER_NO_HEADROOM"
    result={
      "schema":"kculture-v8b-lq2-order-oracle-v1","mechanical_pass":mech,
      "decision":decision,"flipped_to_win":len(flips),"mean_best_margin_delta":mean_delta,
      "rows":rows,"flips":flips,"context_docs":docs,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8B_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"flipped_to_win":len(flips),
      "mean_best_margin_delta":mean_delta,"rows":rows,"flips":flips,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
