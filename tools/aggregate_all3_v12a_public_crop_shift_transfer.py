#!/usr/bin/env python3
"""Aggregate V12A exact-ALL3 public crop-shift transfer census."""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter
from pathlib import Path

def stats(rr):
    if not rr:return {"support":0}
    return {
      "support":len(rr),
      "wins":sum(r["result"]=="W" for r in rr),
      "losses":sum(r["result"]=="L" for r in rr),
      "ties":sum(r["result"]=="T" for r in rr),
      "score_rate":statistics.fmean(float(r["score"]) for r in rr),
      "loss_rate":sum(r["result"]=="L" for r in rr)/len(rr),
      "mean_margin":statistics.fmean(float(r["margin"]) for r in rr),
      "families":sorted({r["family"] for r in rr}),
      "opponents":sorted({r["opponent"] for r in rr}),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    mech=(len(docs)==7 and len(rows)==112 and not failures and all(d.get("mechanical_pass") for d in docs))
    sig=[r for r in rows if r["opp_carrot_adv_any"]]
    nonsig=[r for r in rows if not r["opp_carrot_adv_any"]]
    strict=[r for r in rows if r["strict_any"]]
    s=stats(sig); ns=stats(nonsig); st=stats(strict)
    family_support=Counter(r["family"] for r in sig)
    qualifying_families=sorted(k for k,v in family_support.items() if v>=2)
    score_gap=(float(ns.get("score_rate",0))-float(s.get("score_rate",0))) if sig and nonsig else None

    if not mech:
        decision="V12A_MECHANICS_INVALID"
    elif len(sig)<8 or len(qualifying_families)<2:
        decision="V12A_PUBLIC_CROP_SHIFT_TRANSFER_SPARSE"
    elif (
      s["loss_rate"]>=0.75 and s["score_rate"]<=0.25
      and len(nonsig)>=16 and score_gap is not None and score_gap>=0.20
    ):
        decision="V12A_PUBLIC_CROP_SHIFT_TRANSFER_READY"
    else:
        decision="V12A_PUBLIC_CROP_SHIFT_NOT_DISCRIMINATIVE"

    by_opp={}
    for d in docs:
        by_opp[d["opponent"]]=d.get("summary",{})
    result={
      "schema":"kculture-v12a-public-crop-shift-transfer-v1",
      "mechanical_pass":mech,"decision":decision,
      "contexts":len(rows),"signal":s,"strict":st,"non_signal":ns,
      "signal_score_gap":score_gap,
      "family_signal_support":dict(sorted(family_support.items())),
      "qualifying_signal_families":qualifying_families,
      "by_opponent":by_opp,"rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,
      "runtime_identity_feature_allowed":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V12A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"contexts":len(rows),
      "signal":s,"strict":st,"non_signal":ns,"signal_score_gap":score_gap,
      "family_signal_support":dict(sorted(family_support.items())),
      "qualifying_signal_families":qualifying_families,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
