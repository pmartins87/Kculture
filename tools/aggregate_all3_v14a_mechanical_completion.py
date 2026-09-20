#!/usr/bin/env python3
"""Mechanically complete V14A from original shard artifacts plus exact 429 supplement."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

MODES=("BASE","MARKET_ALL","MARKET_W2PLUS","PHYSICAL_ALL","PHYSICAL_W2PLUS","FULL_ALL")
EXPECTED_MISSING={"v13c_hard_14","v13c_hard_16","v13c_hard_18"}

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
    return bool(s) and (
      s["improved_score_contexts"]>=4
      and s["improved_sources"]>=2
      and s["mean_score_delta"]>0
      and s["regressed_score_contexts"]<=s["improved_score_contexts"]/2
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-dir",required=True)
    ap.add_argument("--supplement",required=True)
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    cfg=json.loads(Path(args.hard_config).read_text())
    contexts=list(cfg.get("hard_contexts") or [])
    if len(contexts)!=24:raise RuntimeError(f"expected 24 hard contexts, got {len(contexts)}")
    cids={c["context_id"] for c in contexts}

    docs=[json.loads(p.read_text()) for p in sorted(Path(args.original_dir).rglob("*.json"))]
    if len(docs)!=4:raise RuntimeError(f"expected 4 original shard docs, got {len(docs)}")

    original_rows=[r for d in docs for r in d.get("rows",[])]
    original_failures=[f for d in docs for f in d.get("failures",[])]
    if len(original_rows)!=126:
        raise RuntimeError(f"expected 126 valid original rows, got {len(original_rows)}")
    if len(original_failures)!=3:
        raise RuntimeError(f"expected exactly 3 original failures, got {original_failures}")
    seen_fail_ids={str(f.get("context_id")) for f in original_failures}
    if seen_fail_ids!=EXPECTED_MISSING:
        raise RuntimeError(f"unexpected missing contexts {seen_fail_ids}")
    for f in original_failures:
        if f.get("phase")!="teacher_acquire" or "429" not in str(f.get("error")):
            raise RuntimeError(f"original failure not pure 429 acquisition: {f}")

    sup=json.loads(Path(args.supplement).read_text())
    if not sup.get("mechanical_pass"):
        raise RuntimeError(f"supplement mechanical fail: {sup.get('failures')}")
    sup_rows=list(sup.get("rows") or [])
    if len(sup_rows)!=18:
        raise RuntimeError(f"expected 18 supplement rows, got {len(sup_rows)}")
    if {r["context_id"] for r in sup_rows}!=EXPECTED_MISSING:
        raise RuntimeError("supplement context set mismatch")

    rows=original_rows+sup_rows
    expected={(c["context_id"],m) for c in contexts for m in MODES}
    actual=[(r["context_id"],r["mode"]) for r in rows]
    aset=set(actual)
    if len(rows)!=144 or len(aset)!=144:
        raise RuntimeError(f"combined row count/uniqueness fail rows={len(rows)} unique={len(aset)}")
    missing=sorted(expected-aset);extra=sorted(aset-expected)
    if missing or extra:
        raise RuntimeError(f"combined key grid mismatch missing={missing} extra={extra}")

    by={m:summary([r for r in rows if r["mode"]==m]) for m in MODES}
    market_modes=[m for m in ("MARKET_ALL","MARKET_W2PLUS") if passes(by[m])]
    physical_modes=[m for m in ("PHYSICAL_ALL","PHYSICAL_W2PLUS") if passes(by[m])]
    full=by["FULL_ALL"]
    full_pass=(full.get("improved_score_contexts",0)>=4 and full.get("improved_sources",0)>=2 and full.get("mean_score_delta",0)>0)

    if market_modes and not physical_modes:
        decision="V14A_MARKET_DOMAIN_HEADROOM"
    elif physical_modes and not market_modes:
        decision="V14A_PHYSICAL_DOMAIN_HEADROOM"
    elif market_modes and physical_modes:
        decision="V14A_BOTH_DOMAINS_HEADROOM"
    elif full_pass:
        decision="V14A_CROSS_DOMAIN_INTERACTION_HEADROOM"
    else:
        decision="V14A_SHADOW_UPPER_BOUND_NOT_REUSABLE"

    result={
      "schema":"kculture-all3-v14a-domain-upper-bound-complete-v1",
      "mechanical_pass":True,
      "decision":decision,
      "hard_contexts":24,
      "rows":rows,
      "by_mode":by,
      "passing_market_modes":market_modes,
      "passing_physical_modes":physical_modes,
      "full_all_ceiling_pass":full_pass,
      "original_workflow":35525689199,
      "original_valid_rows":126,
      "original_429_contexts":sorted(EXPECTED_MISSING),
      "supplement_rows":18,
      "strategic_population_changed":False,
      "strategic_gate_changed":False,
      "automatic_kaggle_submission":False,
      "opponent_identity_runtime_feature_allowed":False,
      "failures":[]
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V14A_COMPLETE_RESULT",json.dumps({
      "mechanical_pass":True,"decision":decision,"by_mode":by,
      "passing_market_modes":market_modes,"passing_physical_modes":physical_modes,
      "full_all_ceiling_pass":full_pass
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
