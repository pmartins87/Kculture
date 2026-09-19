#!/usr/bin/env python3
"""Aggregate 12 O-HV1 config×opponent shards using frozen selection rule."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

CONFIGS={
 "D1":{"min_step":240,"min_price":175},
 "D2":{"min_step":240,"min_price":200},
 "D3":{"min_step":336,"min_price":175},
 "D4":{"min_step":336,"min_price":200},
}
OPPS=("v47_mirror","v48","ready_stock")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[]
    flat=[]
    for s in shards:
        failures+=s.get("failures",[])
        flat+=s.get("rows",[])
    mech=(
      len(shards)==12 and len(flat)==96 and not failures
      and all(s.get("mechanical_pass") for s in shards)
      and {(s.get("opponent"),s.get("variant")) for s in shards}
         == {(o,v) for o in OPPS for v in CONFIGS}
    )

    summary={};eligible=[]
    for v,cfg in CONFIGS.items():
        vals=[x for x in flat if x["variant"]==v]
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
          "by_opponent":{
            o:{
              "mean_score_delta":statistics.fmean(float(x["score_delta"]) for x in vals if x["opponent"]==o),
              "mean_margin_delta":statistics.fmean(float(x["margin_delta"]) for x in vals if x["opponent"]==o),
              "negative_score_contexts":sum(float(x["score_delta"])<0 for x in vals if x["opponent"]==o),
            } for o in OPPS
          },
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
      "schema":"kculture-o-hv1-development-parallel-v1",
      "mechanical_pass":mech,"decision":decision,
      "selected":selected,"selected_config":CONFIGS.get(selected),
      "eligible":eligible,"summary":summary,"rows":flat,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_HV1_DEV_RESULT",json.dumps({
      "mechanical_pass":mech,"decision":decision,"selected":selected,
      "selected_config":CONFIGS.get(selected),"eligible":eligible,
      "summary":summary,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
