#!/usr/bin/env python3
"""Aggregate dormant V18A fixed-window temporal localization."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

MODES=("BASE","MARKET_W2A_ONLY","MARKET_W2B_ONLY","MARKET_W2C_ONLY","MARKET_W2AB","MARKET_W2BC","MARKET_W2ABC")
SINGLES=("MARKET_W2A_ONLY","MARKET_W2B_ONLY","MARKET_W2C_ONLY")
ADJ=("MARKET_W2AB","MARKET_W2BC")

def summarize(rows):
    if not rows:return {}
    ltw=[r for r in rows if float(r["base_score"])<1 and float(r["treatment_score"])==1]
    pos=[r for r in rows if float(r["score_delta"])>0]
    neg=[r for r in rows if float(r["score_delta"])<0]
    return {
      "contexts":len(rows),"loss_to_win":len(ltw),"loss_to_win_sources":len({r["main_sha256"] for r in ltw}),
      "positive_score_contexts":len(pos),"negative_score_contexts":len(neg),
      "improved_sources":len({r["main_sha256"] for r in pos}),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
    }

def passes(s):
    return bool(s) and s["loss_to_win"]>=4 and s["loss_to_win_sources"]>=2 and s["mean_score_delta"]>0 and s["mean_margin_delta"]>0

def choose(modes,by):
    good=[m for m in modes if passes(by[m])]
    good.sort(key=lambda m:(-by[m]["loss_to_win"],-by[m]["improved_sources"],-by[m]["mean_score_delta"],m))
    return good[0] if good else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    mech=(len(docs)==4 and len(rows)==24*len(MODES) and not failures and all(d.get("mechanical_pass") for d in docs))
    by={m:summarize([r for r in rows if r["mode"]==m]) for m in MODES}
    single=choose(SINGLES,by);adj=choose(ADJ,by)
    if not mech:decision="V18A_MECHANICS_INVALID";selected=None
    elif single:decision="V18A_SINGLE_W2_WINDOW_HEADROOM";selected=single
    elif adj:decision="V18A_ADJACENT_W2_WINDOWS_HEADROOM";selected=adj
    elif passes(by["MARKET_W2ABC"]):decision="V18A_DISTRIBUTED_W2_HEADROOM";selected="MARKET_W2ABC"
    else:decision="V18A_V14A_REPLICATION_FAILURE";selected=None
    result={"schema":"kculture-all3-v18a-w2-temporal-v1","mechanical_pass":mech,"decision":decision,
      "selected_mode":selected,"by_mode":by,"rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18A_RESULT",json.dumps({"decision":decision,"selected_mode":selected,"by_mode":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
