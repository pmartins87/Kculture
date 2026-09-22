#!/usr/bin/env python3
"""Aggregate V27C bounded-history behavioral-distillation census."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter,defaultdict
from pathlib import Path

COMPONENTS=("complete","market","farmer","hands")

def entropy(counter):
    n=sum(counter.values())
    if n<=0:return 0.0
    out=0.0
    for v in counter.values():
        p=v/n
        out-=p*math.log2(p)
    return out

def conflict_metrics(rows,component):
    by=defaultdict(Counter)
    for r in rows:
        by[r["feature_hash"]][r[component]]+=1
    conflict_hashes={h:c for h,c in by.items() if len(c)>1}
    conflict_rows=sum(sum(c.values()) for c in conflict_hashes.values())
    return {
      "unique_feature_hashes":len(by),
      "conflicting_feature_hashes":len(conflict_hashes),
      "conflict_rows":conflict_rows,
      "conflict_row_rate":conflict_rows/len(rows) if rows else None,
      "max_labels_per_feature_hash":max((len(c) for c in by.values()),default=0),
    },by

def modal_by_step(train,component):
    counts=defaultdict(Counter)
    for r in train:
        counts[int(r["step"])][r[component]]+=1
    return {step:sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))[0][0] for step,c in counts.items()}

def modal_accuracy(rows,modal,component):
    usable=[r for r in rows if int(r["step"]) in modal]
    if not usable:return None
    return sum(r[component]==modal[int(r["step"])] for r in usable)/len(usable)

def exact_match_metrics(train,rows,component):
    by=defaultdict(Counter)
    for r in train:by[r["feature_hash"]][r[component]]+=1
    matched=[r for r in rows if r["feature_hash"] in by]
    if not matched:
        return {"matched_rows":0,"match_rate":0.0,"label_agreement":None}
    correct=0
    for r in matched:
        c=by[r["feature_hash"]]
        pred=sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))[0][0]
        correct+=pred==r[component]
    return {
      "matched_rows":len(matched),
      "match_rate":len(matched)/len(rows) if rows else None,
      "label_agreement":correct/len(matched),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    docs=[]
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v27c-bounded-history-census-shard-v1":
            docs.append(d)

    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    shard_counts={int(d.get("num_shards",-1)) for d in docs}
    expected_shards=next(iter(shard_counts)) if len(shard_counts)==1 else -1
    shard_ids={int(d.get("shard_index",-1)) for d in docs}
    episodes={(r["source_sha"],int(r["seed"]),int(r["seat"])) for r in rows}
    mech=(
      expected_shards==12
      and len(docs)==12
      and shard_ids==set(range(12))
      and all(bool(d.get("mechanical_pass")) for d in docs)
      and not failures
      and len(episodes)==96
      and len(rows)>=60000
    )

    train=[r for r in rows if r["split"]=="train"]
    val=[r for r in rows if r["split"]=="validation"]
    test=[r for r in rows if r["split"]=="test"]

    label_stats={}
    conflicts={}
    exact_matches={}
    modal={}
    for comp in COMPONENTS:
        train_labels={r[comp] for r in train}
        val_labels={r[comp] for r in val}
        test_labels={r[comp] for r in test}
        label_stats[comp]={
          "unique_all":len({r[comp] for r in rows}),
          "unique_train":len(train_labels),
          "unique_validation":len(val_labels),
          "unique_test":len(test_labels),
          "unseen_validation_labels":len(val_labels-train_labels),
          "unseen_test_labels":len(test_labels-train_labels),
        }
        cm,_=conflict_metrics(rows,comp)
        conflicts[comp]=cm
        m=modal_by_step(train,comp)
        modal[comp]={
          "validation_accuracy":modal_accuracy(val,m,comp),
          "test_accuracy":modal_accuracy(test,m,comp),
        }
        exact_matches[comp]={
          "validation":exact_match_metrics(train,val,comp),
          "test":exact_match_metrics(train,test,comp),
        }

    train_sets={c:{r[c] for r in train} for c in COMPONENTS}
    def decomposable_coverage(split_rows):
        if not split_rows:return None
        good=0
        for r in split_rows:
            ok=(
              r["complete"] in train_sets["complete"]
              or (
                r["market"] in train_sets["market"]
                and r["farmer"] in train_sets["farmer"]
                and r["hands"] in train_sets["hands"]
              )
            )
            good+=ok
        return good/len(split_rows)

    step_entropy={}
    for comp in COMPONENTS:
        by=defaultdict(Counter)
        for r in rows:by[int(r["step"])][r[comp]]+=1
        vals=[entropy(c) for c in by.values()]
        step_entropy[comp]={
          "mean":statistics.fmean(vals) if vals else None,
          "max":max(vals) if vals else None,
          "steps_with_nonzero_entropy":sum(v>0 for v in vals),
        }

    source_rows=defaultdict(list)
    for r in rows:source_rows[r["source_sha"]].append(r)
    source_support=[]
    for sha,rr in sorted(source_rows.items()):
        source_support.append({
          "sha":sha,
          "rows":len(rr),
          "unique_complete_labels":len({x["complete"] for x in rr}),
          "test_rows":sum(x["split"]=="test" for x in rr),
        })

    val_decomp=decomposable_coverage(val)
    test_decomp=decomposable_coverage(test)

    gate=(
      mech
      and conflicts["farmer"]["conflict_row_rate"]<=0.005
      and conflicts["hands"]["conflict_row_rate"]<=0.02
      and conflicts["market"]["conflict_row_rate"]<=0.05
      and conflicts["complete"]["conflict_row_rate"]<=0.06
      and val_decomp>=0.98
      and test_decomp>=0.98
      and modal["complete"]["test_accuracy"]>=0.70
    )

    if not mech:
        decision="V27C_MECHANICS_INVALID"
    elif gate:
        decision="V27C_BEHAVIORAL_DISTILLATION_DATA_VIABLE"
    else:
        decision="V27C_BEHAVIORAL_DISTILLATION_DATA_TOO_COMPLEX"

    result={
      "schema":"kculture-v27c-bounded-history-census-v1",
      "mechanical_pass":mech,
      "decision":decision,
      "rows":len(rows),
      "episodes":len(episodes),
      "split_rows":{"train":len(train),"validation":len(val),"test":len(test)},
      "history_window":256,
      "feature_dim":docs[0].get("feature_dim") if docs else None,
      "label_stats":label_stats,
      "conflicts":conflicts,
      "step_modal":modal,
      "exact_feature_match":exact_matches,
      "validation_decomposable_coverage":val_decomp,
      "test_decomposable_coverage":test_decomp,
      "step_entropy":step_entropy,
      "source_support":source_support,
      "gate_pass":gate,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V27C_RESULT",json.dumps({
      "decision":decision,
      "mechanical_pass":mech,
      "rows":len(rows),
      "episodes":len(episodes),
      "unique_complete_labels":label_stats["complete"]["unique_all"],
      "complete_conflict_rate":conflicts["complete"]["conflict_row_rate"],
      "market_conflict_rate":conflicts["market"]["conflict_row_rate"],
      "farmer_conflict_rate":conflicts["farmer"]["conflict_row_rate"],
      "hands_conflict_rate":conflicts["hands"]["conflict_row_rate"],
      "validation_decomposable_coverage":val_decomp,
      "test_decomposable_coverage":test_decomp,
      "step_modal_complete_test_accuracy":modal["complete"]["test_accuracy"],
      "gate_pass":gate,
      "failures":len(failures),
    },sort_keys=True))
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
