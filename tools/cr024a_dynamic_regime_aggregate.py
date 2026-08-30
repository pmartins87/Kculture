"""Aggregate CR024A dynamic Stage-A shards and rank simple public-state guards."""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import defaultdict
from pathlib import Path


def safe_float(x):
    try:
        y = float(x)
        return y if math.isfinite(y) else None
    except Exception:
        return None


def metrics(rows, feature, threshold, direction):
    tp=tn=fp=fn=0; caught_seeds=set(); caught_opps=set(); false_seeds=set(); false_opps=set()
    for r in rows:
        x=safe_float(r["features"].get(feature))
        if x is None: continue
        pred = x <= threshold if direction == "le" else x >= threshold
        y=bool(r["unfavorable"])
        if pred and y:
            tp+=1; caught_seeds.add(r["seed"]); caught_opps.add(r["opponent"])
        elif pred and not y:
            fp+=1; false_seeds.add(r["seed"]); false_opps.add(r["opponent"])
        elif not pred and y: fn+=1
        else: tn+=1
    recall=tp/max(1,tp+fn); specificity=tn/max(1,tn+fp); precision=tp/max(1,tp+fp)
    return {
        "tp":tp,"tn":tn,"fp":fp,"fn":fn,
        "recall":recall,"specificity":specificity,"precision":precision,
        "balanced_accuracy":0.5*(recall+specificity),
        "caught_harmful_seed_count":len(caught_seeds),
        "caught_harmful_opponent_count":len(caught_opps),
        "false_positive_seed_count":len(false_seeds),
        "false_positive_opponent_count":len(false_opps),
    }


def rank_rules(rows):
    names=sorted({k for r in rows for k in r["features"] if k not in {"clock","step","day"}})
    out=[]
    for name in names:
        vals=sorted({safe_float(r["features"].get(name)) for r in rows} - {None})
        if len(vals)<2: continue
        mids=[(a+b)/2.0 for a,b in zip(vals,vals[1:]) if a!=b]
        # Limit pathological high-cardinality scans deterministically.
        if len(mids)>80:
            idxs=sorted({round(i*(len(mids)-1)/79) for i in range(80)})
            mids=[mids[i] for i in idxs]
        for th in mids:
            for direction in ("le","ge"):
                m=metrics(rows,name,th,direction)
                if m["tp"]==0: continue
                out.append({"feature":name,"threshold":th,"direction":direction,**m})
    out.sort(key=lambda d:(
        -d["caught_harmful_seed_count"],
        -d["recall"],
        d["fp"],
        -d["balanced_accuracy"],
        d["feature"],d["threshold"]
    ))
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-glob",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    files=sorted(glob.glob(args.input_glob,recursive=True))
    if not files: raise SystemExit("no shards")
    episodes=[]; errors=[]
    for p in files:
        d=json.load(open(p,encoding="utf-8")); errors.extend(d.get("errors") or [])
        for r in d.get("rows") or []:
            episodes.append(r)
    if errors: raise SystemExit(f"shard errors: {len(errors)}")
    # Exact W/L conversions are re-derived here; shard labels are not trusted blindly.
    unfavorable=[]
    favorable=[]
    by_clock=defaultdict(list)
    for r in episodes:
        c=float(r["control"]["score"]); t=float(r["top19"]["score"])
        unf=t<c; fav=t>c
        if unf: unfavorable.append({"seed":r["seed"],"seat":r["seat"],"opponent":r["opponent"],"control":r["control"],"top19":r["top19"]})
        if fav: favorable.append({"seed":r["seed"],"seat":r["seat"],"opponent":r["opponent"],"control":r["control"],"top19":r["top19"]})
        for cp in r.get("checkpoints") or []:
            by_clock[int(cp["clock"])].append({
                "seed":r["seed"],"seat":r["seat"],"opponent":r["opponent"],
                "unfavorable":unf,"features":cp["features"],
            })
    clock_reports=[]
    for clk in sorted(by_clock):
        rows=by_clock[clk]
        # A checkpoint is only comparable if essentially all 216 episodes reached it.
        if len(rows) < int(0.98*len(episodes)): continue
        rules=rank_rules(rows)
        clock_reports.append({"clock":clk,"row_count":len(rows),"top_rules":rules[:20]})
    # Promotion candidate: early/simple rule catching harmful outcomes from >=2 harmful
    # seeds, recall >= 0.60 and safe-state false-positive rate <= 0.10.  Stage A only;
    # even a passing rule is merely freeze-eligible and must face untouched Stage B.
    eligible=[]
    total_unf=len(unfavorable); total_safe=len(episodes)-total_unf
    for cr in clock_reports:
        for rule in cr["top_rules"]:
            fpr=rule["fp"]/max(1,total_safe)
            if (rule["caught_harmful_seed_count"]>=2 and rule["recall"]>=0.60 and fpr<=0.10 and rule["precision"]>=0.20):
                eligible.append({"clock":cr["clock"],"false_positive_rate":fpr,**rule})
    eligible.sort(key=lambda d:(d["clock"],-d["recall"],d["false_positive_rate"],-d["precision"]))
    payload={
        "experiment":"CR024A",
        "stage":"DYNAMIC_REGIME_DIAGNOSTIC_STAGE_A_ONLY",
        "shard_count":len(files),
        "episode_rows":len(episodes),
        "unfavorable_conversion_count":len(unfavorable),
        "favorable_conversion_count":len(favorable),
        "unfavorable_conversions":unfavorable,
        "favorable_conversions":favorable,
        "harmful_seed_set":sorted({r["seed"] for r in unfavorable}),
        "harmful_opponent_set":sorted({r["opponent"] for r in unfavorable}),
        "stage_b_touched":False,
        "held_out_touched":False,
        "runtime_identity_features_used":False,
        "runtime_seed_feature_allowed":False,
        "clock_reports":clock_reports,
        "eligible_simple_guards":eligible[:50],
        "freeze_recommendation":eligible[0] if eligible else None,
        "decision":"FREEZE_GUARD_FOR_STAGE_B" if eligible else "NO_SIMPLE_DYNAMIC_GUARD__BUILD_CONSENSUS_BACKBONE",
        "policy":"No Stage-A rule is promoted directly. Freeze first, then test once on untouched raw Stage B. If no simple guard exists, use consensus/shrinkage backbone rather than inventing a threshold.",
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("episode_rows","unfavorable_conversion_count","favorable_conversion_count","harmful_seed_set","harmful_opponent_set","decision","freeze_recommendation")},indent=2,sort_keys=True))

if __name__=="__main__": main()
