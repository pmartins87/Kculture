#!/usr/bin/env python3
"""Aggregate V14A domain upper-bound shards under frozen gate."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

MODES=("BASE","MARKET_ALL","MARKET_W2PLUS","PHYSICAL_ALL","PHYSICAL_W2PLUS","FULL_ALL")

def summary(rows):
    if not rows:return {}
    imp=[r for r in rows if float(r["score_delta"])>0]
    reg=[r for r in rows if float(r["score_delta"])<0]
    return {
      "contexts":len(rows),
      "improved_score_contexts":len(imp),
      "regressed_score_contexts":len(reg),
      "improved_source_shas":sorted({r["main_sha256"] for r in imp}),
      "improved_sources":len({r["main_sha256"] for r in imp}),
      "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rows),
      "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rows),
    }

def passes(s):
    if not s:return False
    return (
      s["improved_score_contexts"]>=4
      and s["improved_sources"]>=2
      and s["mean_score_delta"]>0
      and s["regressed_score_contexts"]<=s["improved_score_contexts"]/2
    )

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--hard-config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    cfg=json.loads(Path(args.hard_config).read_text());nctx=len(cfg.get("hard_contexts") or [])
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    mech=(len(docs)==4 and len(rows)==nctx*len(MODES) and not failures and all(d.get("mechanical_pass") for d in docs))
    by={m:summary([r for r in rows if r["mode"]==m]) for m in MODES}
    market_modes=[m for m in ("MARKET_ALL","MARKET_W2PLUS") if passes(by[m])]
    physical_modes=[m for m in ("PHYSICAL_ALL","PHYSICAL_W2PLUS") if passes(by[m])]
    full=by["FULL_ALL"]
    full_pass=(full.get("improved_score_contexts",0)>=4 and full.get("improved_sources",0)>=2 and full.get("mean_score_delta",0)>0)
    if not mech:decision="V14A_MECHANICS_INVALID"
    elif market_modes and not physical_modes:decision="V14A_MARKET_DOMAIN_HEADROOM"
    elif physical_modes and not market_modes:decision="V14A_PHYSICAL_DOMAIN_HEADROOM"
    elif market_modes and physical_modes:decision="V14A_BOTH_DOMAINS_HEADROOM"
    elif full_pass:decision="V14A_CROSS_DOMAIN_INTERACTION_HEADROOM"
    else:decision="V14A_SHADOW_UPPER_BOUND_NOT_REUSABLE"
    result={"schema":"kculture-all3-v14a-domain-upper-bound-v1","mechanical_pass":mech,"decision":decision,
      "hard_contexts":nctx,"by_mode":by,"passing_market_modes":market_modes,"passing_physical_modes":physical_modes,
      "full_all_ceiling_pass":full_pass,"rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,"opponent_identity_runtime_feature_allowed":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V14A_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"hard_contexts":nctx,
      "by_mode":by,"passing_market_modes":market_modes,"passing_physical_modes":physical_modes,
      "full_all_ceiling_pass":full_pass,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
