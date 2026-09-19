#!/usr/bin/env python3
"""Aggregate O-LQ2 fresh causal shards using frozen gate."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    files=sorted(Path(args.input_dir).rglob("*.json"))
    shards=[json.loads(p.read_text()) for p in files]
    rows=[];failures=[]
    for s in shards: rows.extend(s.get("rows",[]));failures.extend(s.get("failures",[]))
    mech=(len(shards)==8 and len(rows)==16 and not failures and all(s.get("mechanical_pass") for s in shards))
    sd=[float(r["score_delta"]) for r in rows]; md=[float(r["margin_delta"]) for r in rows]
    summary={
      "pairs":len(rows),
      "base_score_rate":statistics.mean(float(r["base_score"]) for r in rows) if rows else None,
      "treatment_score_rate":statistics.mean(float(r["treatment_score"]) for r in rows) if rows else None,
      "mean_score_delta":statistics.mean(sd) if sd else None,
      "mean_margin_delta":statistics.mean(md) if md else None,
      "median_margin_delta":statistics.median(md) if md else None,
      "positive_score_contexts":sum(x>0 for x in sd),
      "negative_score_contexts":sum(x<0 for x in sd),
      "loss_to_tie":sum(r["base_score"]==0 and r["treatment_score"]==0.5 for r in rows),
      "loss_to_win":sum(r["base_score"]==0 and r["treatment_score"]==1 for r in rows),
      "win_to_nonwin":sum(r["base_score"]==1 and r["treatment_score"]<1 for r in rows),
      "mean_fire_count":statistics.mean(r["fire_count"] for r in rows) if rows else None,
      "total_changed_slots":sum(r["changed_slots"] for r in rows),
      "total_merged_runs":sum(r["merged_runs"] for r in rows),
    }
    if mech and summary["mean_score_delta"]>=0.125 and summary["positive_score_contexts"]>=4 and summary["negative_score_contexts"]==0 and summary["mean_margin_delta"]>0:
        decision="O_LQ2_V48_CAUSAL_PASS"
    elif mech and summary["mean_score_delta"]>0:
        decision="O_LQ2_V48_CAUSAL_WEAK"
    elif mech and summary["mean_margin_delta"]>0:
        decision="O_LQ2_V48_CAUSAL_MARGIN_ONLY"
    elif mech:
        decision="O_LQ2_V48_CAUSAL_FAIL"
    else:
        decision="O_LQ2_V48_CAUSAL_MECHANICS_INVALID"
    result={"schema":"kculture-o-lq2-v48-causal-v1","mechanical_pass":mech,"summary":summary,"decision":decision,"rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ2_V48_CAUSAL_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"summary":summary,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
