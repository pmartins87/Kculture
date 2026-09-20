#!/usr/bin/env python3
"""Aggregate V8C one-shot conditional SELL-order value atlas."""
from __future__ import annotations
import argparse, json, statistics
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input-dir", required=True); ap.add_argument("--out", required=True); args = ap.parse_args()
    docs = [json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures = [f for d in docs for f in d.get("failures", [])]
    rows = [r for d in docs for r in d.get("branches", [])]
    expected_branch_states = sum(int(d.get("event_count", 0)) for d in docs)
    mech = len(docs) == 4 and not failures and all(d.get("mechanical_pass") for d in docs) and expected_branch_states > 0 and len(rows) == expected_branch_states

    positive = [r for r in rows if float(r["margin_delta"]) > 0]
    negative = [r for r in rows if float(r["margin_delta"]) < 0]
    flips = [r for r in rows if float(r["base_score"]) == 0.0 and float(r["treatment_score"]) == 1.0]
    regress = [r for r in rows if float(r["base_score"]) == 1.0 and float(r["treatment_score"]) < 1.0]
    pos_contexts = sorted({int(r["index"]) for r in positive})
    flip_contexts = sorted({int(r["index"]) for r in flips})

    by_turn = defaultdict(list)
    for r in rows: by_turn[int(r["turn"])].append(r)
    turn_summary = []
    for turn, rr in sorted(by_turn.items()):
        turn_summary.append({
            "turn": turn, "states": len(rr),
            "mean_margin_delta": statistics.fmean(float(x["margin_delta"]) for x in rr),
            "positive_margin_states": sum(float(x["margin_delta"]) > 0 for x in rr),
            "negative_margin_states": sum(float(x["margin_delta"]) < 0 for x in rr),
            "loss_to_win_flips": sum(float(x["base_score"]) == 0.0 and float(x["treatment_score"]) == 1.0 for x in rr),
            "contexts": sorted({int(x["index"]) for x in rr}),
        })

    if not mech:
        decision = "V8C_MECHANICS_INVALID"
    elif len(flip_contexts) >= 2:
        decision = "V8C_CONDITIONAL_ORDER_HEADROOM_REPEATABLE"
    elif flips and len(pos_contexts) >= 2:
        decision = "V8C_CONDITIONAL_ORDER_HEADROOM_NARROW"
    elif len(pos_contexts) >= 2:
        decision = "V8C_CONDITIONAL_ORDER_MARGIN_HETEROGENEOUS"
    else:
        decision = "V8C_CONDITIONAL_ORDER_NO_REUSABLE_HEADROOM"

    top_pos = sorted(positive, key=lambda r: (float(r["score_delta"]), float(r["margin_delta"])), reverse=True)[:12]
    top_neg = sorted(negative, key=lambda r: (float(r["score_delta"]), float(r["margin_delta"])))[:12]
    result = {
        "schema": "kculture-v8c-local-priority-value-atlas-v1",
        "mechanical_pass": mech, "decision": decision,
        "branch_states": len(rows), "expected_branch_states": expected_branch_states, "loss_to_win_flips": len(flips), "win_to_nonwin_regressions": len(regress),
        "positive_margin_states": len(positive), "negative_margin_states": len(negative),
        "positive_margin_contexts": pos_contexts, "flip_contexts": flip_contexts,
        "mean_margin_delta": statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0,
        "median_margin_delta": statistics.median(float(r["margin_delta"]) for r in rows) if rows else 0.0,
        "turn_summary": turn_summary, "top_positive": top_pos, "top_negative": top_neg,
        "rows": rows, "context_docs": docs, "failures": failures,
        "automatic_kaggle_submission": False,
        "interpretation_rule": (
            "Discovery only. Do not retune O-LQ3 globally. If repeatable/narrow headroom exists, derive at most one compact "
            "opponent-identity-free public-state condition, freeze it before any fresh-seed V8D validation."
        ),
    }
    p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("V8C_RESULT", json.dumps({
        "decision": decision, "mechanical_pass": mech, "branch_states": len(rows), "expected_branch_states": expected_branch_states,
        "loss_to_win_flips": len(flips), "positive_margin_states": len(positive), "negative_margin_states": len(negative),
        "positive_margin_contexts": pos_contexts, "flip_contexts": flip_contexts,
        "mean_margin_delta": result["mean_margin_delta"], "turn_summary": turn_summary,
        "top_positive": [{k:r[k] for k in ("index","opponent","seed","seat","turn","score_delta","margin_delta")} for r in top_pos],
        "failures": len(failures),
    }, sort_keys=True), flush=True)
    if not mech: raise SystemExit(2)


if __name__ == "__main__":
    main()
