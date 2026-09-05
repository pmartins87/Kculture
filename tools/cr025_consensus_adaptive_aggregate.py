"""Aggregate the frozen CR025 vs CR024 fresh Stage-B comparison."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = sorted(glob.glob(args.input_glob, recursive=True))
    if not files:
        raise SystemExit("no shards")
    rows, errors, opponents = [], [], []
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        opponents.append(d.get("opponent"))
        errors.extend(d.get("errors") or [])
        rows.extend(d.get("rows") or [])

    expected = 168
    mechanical_pass = len(rows) == expected and not errors and len(set(opponents)) == 7
    base_score = sum(float(r["cr024"]["score"]) for r in rows)
    cand_score = sum(float(r["cr025"]["score"]) for r in rows)
    favorable = sum(float(r["cr025"]["score"]) > float(r["cr024"]["score"]) for r in rows)
    unfavorable = sum(float(r["cr025"]["score"]) < float(r["cr024"]["score"]) for r in rows)
    diffs = [float(r["cr025"]["delta"]) - float(r["cr024"]["delta"]) for r in rows]
    trigger_orders = sum(int((r["cr025"].get("overlay") or {}).get("triggered_orders", 0)) for r in rows)
    trigger_games = sum(1 for r in rows if int((r["cr025"].get("overlay") or {}).get("triggered_orders", 0)) > 0)
    carrot_orders = sum(int((((r["cr025"].get("overlay") or {}).get("items") or {}).get("CARROT", 0))) for r in rows)
    strawberry_orders = sum(int((((r["cr025"].get("overlay") or {}).get("items") or {}).get("STRAWBERRY", 0))) for r in rows)

    metrics = {
        "cr024_total_score": base_score,
        "cr025_total_score": cand_score,
        "score_gain": cand_score - base_score,
        "favorable_conversions": favorable,
        "unfavorable_conversions": unfavorable,
        "net_favorable_conversions": favorable - unfavorable,
        "mean_margin_gain": sum(diffs) / max(1, len(diffs)),
        "positive_margin_rows": sum(x > 0 for x in diffs),
        "negative_margin_rows": sum(x < 0 for x in diffs),
        "same_margin_rows": sum(x == 0 for x in diffs),
        "triggered_orders": trigger_orders,
        "triggered_games": trigger_games,
        "carrot_orders": carrot_orders,
        "strawberry_orders": strawberry_orders,
    }
    checks = {
        "mechanical_168_rows_zero_errors": mechanical_pass,
        "score_gain_ge_2": mechanical_pass and metrics["score_gain"] >= 2.0,
        "net_favorable_ge_2": mechanical_pass and metrics["net_favorable_conversions"] >= 2,
        "unfavorable_le_4": mechanical_pass and metrics["unfavorable_conversions"] <= 4,
        "mean_margin_positive": mechanical_pass and metrics["mean_margin_gain"] > 0.0,
        "overlay_fired": mechanical_pass and metrics["triggered_orders"] > 0,
    }
    passed = all(checks.values())
    decision = "CR025_PASS__PACKAGE" if passed else "CR025_FAIL__RETIRE_OVERLAY_ON_CONSENSUS"
    payload = {
        "experiment": "CR025_CONSENSUS_ADAPTIVE",
        "stage": "ADAPTIVE_OVERLAY_STAGE_B_RESERVED",
        "expected_rows": expected,
        "completed_rows": len(rows),
        "opponents": sorted(set(opponents)),
        "error_count": len(errors),
        "errors": errors,
        "metrics": metrics,
        "checks": checks,
        "decision": decision,
        "held_out_touched": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not mechanical_pass:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
