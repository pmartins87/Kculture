#!/usr/bin/env python3
"""Aggregate V8D-E1 extension. Cumulative decision is applied against the prior binding V8D result."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
OPPS=("v48","v47_mirror","ready_stock")
def s(rows):
    if not rows:return {}
    return {"contexts":len(rows),"fire_contexts":sum(int(r["fire_count"])>0 for r in rows),
      "total_fires":sum(int(r["fire_count"]) for r in rows),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
      "positive_score_contexts":sum(float(r["score_delta"])>0 for r in rows),
      "negative_score_contexts":sum(float(r["score_delta"])<0 for r in rows),
      "nonwin_to_win":sum(float(r["base_score"])<1 and float(r["treatment_score"])==1 for r in rows),
      "win_to_nonwin":sum(float(r["base_score"])==1 and float(r["treatment_score"])<1 for r in rows)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    by={o:s([r for r in rows if r["opponent"]==o]) for o in OPPS};overall=s(rows)
    mech=len(docs)==9 and len(rows)==72 and not failures and all(d.get("mechanical_pass") for d in docs)
    result={"schema":"kculture-v8d-e1-extension-v1","mechanical_pass":mech,
      "decision":"V8D_E1_EXTENSION_COMPLETE" if mech else "V8D_E1_MECHANICS_INVALID",
      "overall":overall,"by_opponent":by,"rows":rows,"shards":docs,"failures":failures,
      "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8D_E1_RESULT",json.dumps({"decision":result["decision"],"mechanical_pass":mech,
      "overall":overall,"by_opponent":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
