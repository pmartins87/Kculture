#!/usr/bin/env python3
"""Aggregate V27A rank-1 teacher Markov reconstructibility audit."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

CHECKPOINTS=(0,1,2,3,4,8,16,32,64,128,256,384,512,640,718)
SEEDS=(79701,79702,79703)
SEATS=(0,1)
TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"

def rate(xs,key):
    vals=[1.0 if bool(x[key]) else 0.0 for x in xs]
    return statistics.fmean(vals) if vals else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--snapshot-result",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    snap=json.loads(Path(args.snapshot_result).read_text())
    if snap.get("decision")!="V26A_FRONTIER_SNAPSHOT_READY" or not snap.get("mechanical_pass"):
        raise SystemExit("V26A snapshot not ready")
    sources=list(snap["selected_representatives"])
    expected={(str(s["main_sha256"]),seed,seat) for s in sources for seed in SEEDS for seat in SEATS}

    docs=[]
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v27a-rank1-markov-audit-shard-v1":
            docs.append(d)

    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    actual={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"])) for r in rows}
    samples=[s for r in rows for s in r["samples"]]

    mech=(
      len(docs)==4
      and all(bool(d.get("mechanical_pass")) for d in docs)
      and all(str(d.get("teacher_sha"))==TEACHER_SHA for d in docs)
      and all(bool(d.get("immutable_snapshot_used")) and not bool(d.get("live_kaggle_reacquisition_used")) for d in docs)
      and not failures
      and len(rows)==len(expected)
      and actual==expected
      and len(samples)==len(expected)*len(CHECKPOINTS)
    )

    overall={
      "complete_action_parity":rate(samples,"full_equal"),
      "market_parity":rate(samples,"market_equal"),
      "farmer_parity":rate(samples,"farmer_equal"),
      "hands_parity":rate(samples,"hands_equal"),
      "comparisons":len(samples),
    }

    by_source=[]
    for src in sources:
        sha=str(src["main_sha256"])
        ss=[s for r in rows if str(r["main_sha256"])==sha for s in r["samples"]]
        by_source.append({
          "rank":int(src["representative_rank"]),
          "ref":src["representative_ref"],
          "sha":sha,
          "comparisons":len(ss),
          "complete_action_parity":rate(ss,"full_equal"),
          "market_parity":rate(ss,"market_equal"),
          "farmer_parity":rate(ss,"farmer_equal"),
          "hands_parity":rate(ss,"hands_equal"),
        })

    by_checkpoint=[]
    for cp in CHECKPOINTS:
        ss=[s for s in samples if int(s["step"])==cp]
        by_checkpoint.append({
          "step":cp,
          "comparisons":len(ss),
          "complete_action_parity":rate(ss,"full_equal"),
          "market_parity":rate(ss,"market_equal"),
          "farmer_parity":rate(ss,"farmer_equal"),
          "hands_parity":rate(ss,"hands_equal"),
        })

    by_seed=[]
    for seed in SEEDS:
        ss=[s for r in rows if int(r["seed"])==seed for s in r["samples"]]
        by_seed.append({
          "seed":seed,
          "comparisons":len(ss),
          "complete_action_parity":rate(ss,"full_equal"),
          "market_parity":rate(ss,"market_equal"),
          "farmer_parity":rate(ss,"farmer_equal"),
          "hands_parity":rate(ss,"hands_equal"),
        })

    disagreements=[]
    for r in rows:
        for s in r["samples"]:
            if not s["full_equal"]:
                disagreements.append({
                  "source_rank":r["source_rank"],
                  "ref":r["ref"],
                  "sha":r["main_sha256"],
                  "seed":r["seed"],
                  "seat":r["seat"],
                  "step":s["step"],
                  "market_equal":s["market_equal"],
                  "farmer_equal":s["farmer_equal"],
                  "hands_equal":s["hands_equal"],
                  "ongoing":s["ongoing"],
                  "fresh":s["fresh"],
                })

    min_source=min((x["complete_action_parity"] for x in by_source),default=0.0)
    min_checkpoint=min((x["complete_action_parity"] for x in by_checkpoint),default=0.0)

    markov_gate=(
      mech
      and overall["complete_action_parity"]>=0.95
      and overall["market_parity"]>=0.98
      and overall["farmer_parity"]>=0.98
      and overall["hands_parity"]>=0.98
      and min_source>=0.90
      and min_checkpoint>=0.85
    )

    if not mech:
        decision="V27A_MECHANICS_INVALID"
    elif markov_gate:
        decision="V27A_MARKOV_DISTILLATION_VIABLE"
    elif overall["complete_action_parity"]>=0.70:
        decision="V27A_HISTORY_AWARE_DISTILLATION_REQUIRED"
    else:
        decision="V27A_TEACHER_TOO_STATEFUL_FOR_FAST_DISTILLATION"

    result={
      "schema":"kculture-v27a-rank1-markov-audit-v1",
      "mechanical_pass":mech,
      "decision":decision,
      "teacher_sha":TEACHER_SHA,
      "teacher_ref":"ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer",
      "episodes":len(rows),
      "overall":overall,
      "minimum_source_complete_action_parity":min_source,
      "minimum_checkpoint_complete_action_parity":min_checkpoint,
      "by_source":by_source,
      "by_checkpoint":by_checkpoint,
      "by_seed":by_seed,
      "disagreement_count":len(disagreements),
      "disagreements":disagreements,
      "markov_gate_pass":markov_gate,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }

    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V27A_RESULT",json.dumps({
      "decision":decision,
      "mechanical_pass":mech,
      "episodes":len(rows),
      "comparisons":len(samples),
      "complete_action_parity":overall["complete_action_parity"],
      "market_parity":overall["market_parity"],
      "farmer_parity":overall["farmer_parity"],
      "hands_parity":overall["hands_parity"],
      "minimum_source_complete_action_parity":min_source,
      "minimum_checkpoint_complete_action_parity":min_checkpoint,
      "disagreement_count":len(disagreements),
      "markov_gate_pass":markov_gate,
      "failures":len(failures),
    },sort_keys=True),flush=True)

    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
