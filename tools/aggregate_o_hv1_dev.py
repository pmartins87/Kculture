#!/usr/bin/env python3
"""Aggregate frozen O-HV1 development matrix and select one config."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

CONFIGS={
 "D1":{"min_step":240,"min_price":175},
 "D2":{"min_step":240,"min_price":200},
 "D3":{"min_step":336,"min_price":175},
 "D4":{"min_step":336,"min_price":200},
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[]
    for s in shards: rows+=s.get("rows",[]);failures+=s.get("failures",[])
    mech=len(shards)==3 and len(rows)==24 and not failures and all(s.get("mechanical_pass") for s in shards)

    summary={}
    eligible=[]
    for v,cfg in CONFIGS.items():
        vals=[r["variants"][v] for r in rows]
        sd=[float(x["score_delta"]) for x in vals]
        md=[float(x["margin_delta"]) for x in vals]
        fire_contexts=sum(int(x["fire_count"])>0 for x in vals)
        rec={
          "config":cfg,"contexts":len(vals),
          "mean_score_delta":statistics.fmean(sd) if sd else None,
          "mean_margin_delta":statistics.fmean(md) if md else None,
          "positive_score_contexts":sum(x>0 for x in sd),
          "negative_score_contexts":sum(x<0 for x in sd),
          "fire_contexts":fire_contexts,
          "mean_fire_count":statistics.fmean(int(x["fire_count"]) for x in vals) if vals else None,
          "gross_added":sum(int(x["gross_added"]) for x in vals),
        }
        summary[v]=rec
        if mech and rec["negative_score_contexts"]==0 and rec["mean_score_delta"]>=0 and rec["mean_margin_delta"]>0 and fire_contexts>=4:
            eligible.append(v)

    selected=None
    if eligible:
        selected=max(
          eligible,
          key=lambda v:(
            summary[v]["mean_score_delta"],
            summary[v]["positive_score_contexts"],
            summary[v]["mean_margin_delta"],
            CONFIGS[v]["min_price"],
            CONFIGS[v]["min_step"],
          )
        )
        decision="O_HV1_DEV_FREEZE_"+selected
    else:
        decision="O_HV1_DEV_CLOSE" if mech else "O_HV1_DEV_MECHANICS_INVALID"

    result={
      "schema":"kculture-o-hv1-development-v1",
      "mechanical_pass":mech,"decision":decision,
      "selected":selected,"selected_config":CONFIGS.get(selected),
      "eligible":eligible,"summary":summary,"rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_HV1_DEV_RESULT",json.dumps({
      "mechanical_pass":mech,"decision":decision,"selected":selected,
      "selected_config":CONFIGS.get(selected),"eligible":eligible,"summary":summary,
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
