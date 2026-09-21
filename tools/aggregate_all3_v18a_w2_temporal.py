#!/usr/bin/env python3
"""Aggregate V18A full MARKET_W2PLUS temporal localization and enforce V14A exact replication."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

MODES=("BASE","MARKET_P1_ONLY","MARKET_P2_ONLY","MARKET_P3_ONLY","MARKET_P12","MARKET_P23","MARKET_P123")
SINGLES=("MARKET_P1_ONLY","MARKET_P2_ONLY","MARKET_P3_ONLY")
ADJ=("MARKET_P12","MARKET_P23")

def summarize(rows):
    if not rows:return {}
    pos=[r for r in rows if float(r["score_delta"])>0]
    neg=[r for r in rows if float(r["score_delta"])<0]
    return {
      "contexts":len(rows),
      "positive_score_contexts":len(pos),
      "negative_score_contexts":len(neg),
      "improved_sources":len({r["main_sha256"] for r in pos}),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
    }

def passes(s):
    return bool(s) and s["positive_score_contexts"]>=4 and s["improved_sources"]>=2 and s["mean_score_delta"]>0 and s["mean_margin_delta"]>0

def choose(modes,by):
    chronology={"MARKET_P1_ONLY":0,"MARKET_P2_ONLY":1,"MARKET_P3_ONLY":2,"MARKET_P12":0,"MARKET_P23":1}
    good=[m for m in modes if passes(by[m])]
    good.sort(key=lambda m:(-by[m]["positive_score_contexts"],-by[m]["improved_sources"],-by[m]["mean_score_delta"],chronology[m]))
    return good[0] if good else None

def v14a_expected(path):
    d=json.loads(Path(path).read_text())
    rows=[r for r in d.get("rows",[]) if r.get("mode")=="MARKET_W2PLUS"]
    if len(rows)!=24:
        raise RuntimeError(f"expected 24 binding V14A MARKET_W2PLUS rows, got {len(rows)}")
    return {
      str(r["context_id"]):{
        "score":float(r["treatment_score"]),
        "margin":float(r["treatment_margin"]),
        "main_sha256":str(r["main_sha256"]),
        "seed":int(r["seed"]),
        "seat":int(r["seat"]),
      } for r in rows
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--v14a-binding",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    mech=(len(docs)==4 and len(rows)==24*len(MODES) and not failures and all(d.get("mechanical_pass") for d in docs))
    by={m:summarize([r for r in rows if r["mode"]==m]) for m in MODES}

    expected=v14a_expected(args.v14a_binding)
    p123=[r for r in rows if r["mode"]=="MARKET_P123"]
    replication_mismatches=[]
    if len(p123)!=24:
        replication_mismatches.append({"reason":"p123_count","actual":len(p123),"expected":24})
    else:
        for r in p123:
            cid=str(r["context_id"]);e=expected.get(cid)
            if e is None:
                replication_mismatches.append({"context_id":cid,"reason":"missing_v14a_expected"});continue
            if str(r["main_sha256"])!=e["main_sha256"] or int(r["seed"])!=e["seed"] or int(r["seat"])!=e["seat"]:
                replication_mismatches.append({"context_id":cid,"reason":"identity_mismatch"})
                continue
            if float(r["treatment_score"])!=e["score"] or float(r["treatment_margin"])!=e["margin"]:
                replication_mismatches.append({
                  "context_id":cid,"reason":"outcome_mismatch",
                  "actual_score":r["treatment_score"],"expected_score":e["score"],
                  "actual_margin":r["treatment_margin"],"expected_margin":e["margin"],
                })
    replication_pass=(len(replication_mismatches)==0)

    single=choose(SINGLES,by);adj=choose(ADJ,by)
    if not mech:
        decision="V18A_MECHANICS_INVALID";selected=None
    elif not replication_pass:
        decision="V18A_V14A_REPLICATION_FAILURE";selected=None
    elif single:
        decision="V18A_SINGLE_PARTITION_HEADROOM";selected=single
    elif adj:
        decision="V18A_ADJACENT_PARTITIONS_HEADROOM";selected=adj
    elif passes(by["MARKET_P123"]):
        decision="V18A_DISTRIBUTED_HEADROOM";selected="MARKET_P123"
    else:
        decision="V18A_V14A_REPLICATION_FAILURE";selected=None

    result={
      "schema":"kculture-all3-v18a-w2plus-temporal-v2",
      "mechanical_pass":mech,
      "v14a_replication_pass":replication_pass,
      "replication_mismatches":replication_mismatches,
      "decision":decision,
      "selected_mode":selected,
      "by_mode":by,
      "rows":rows,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18A_RESULT",json.dumps({
      "decision":decision,"selected_mode":selected,"mechanical_pass":mech,
      "v14a_replication_pass":replication_pass,
      "replication_mismatches":replication_mismatches,
      "by_mode":by,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
