"""Apply the frozen CR024_CONSENSUS_V1 reserved-block promotion gate."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def paired_metrics(rows, arm, control):
    arm_score = sum(float(r[arm]["score"]) for r in rows)
    control_score = sum(float(r[control]["score"]) for r in rows)
    favorable = sum(float(r[arm]["score"]) > float(r[control]["score"]) for r in rows)
    unfavorable = sum(float(r[arm]["score"]) < float(r[control]["score"]) for r in rows)
    margin_diffs = [float(r[arm]["delta"]) - float(r[control]["delta"]) for r in rows]
    return {
        "arm_total_score": arm_score,
        "control_total_score": control_score,
        "score_gain": arm_score - control_score,
        "favorable_conversions": favorable,
        "unfavorable_conversions": unfavorable,
        "net_favorable_conversions": favorable - unfavorable,
        "mean_margin_gain": sum(margin_diffs) / max(1, len(margin_diffs)),
        "positive_margin_rows": sum(x > 0 for x in margin_diffs),
        "negative_margin_rows": sum(x < 0 for x in margin_diffs),
        "same_margin_rows": sum(x == 0 for x in margin_diffs),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = sorted(glob.glob(args.input_glob, recursive=True))
    if not files:
        raise SystemExit("no shards")
    rows, errors = [], []
    opponents = []
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        opponents.append(d.get("opponent"))
        errors.extend(d.get("errors") or [])
        rows.extend(d.get("rows") or [])

    expected = 168
    mechanical_pass = len(rows) == expected and not errors and len(set(opponents)) == 7
    vs_cr008 = paired_metrics(rows, "consensus", "cr008") if rows else {}
    vs_top19 = paired_metrics(rows, "consensus", "top19") if rows else {}

    checks = {
        "mechanical_168_rows_zero_errors": mechanical_pass,
        "vs_cr008_score_gain_ge_12": bool(rows) and vs_cr008["score_gain"] >= 12.0,
        "vs_cr008_net_favorable_ge_12": bool(rows) and vs_cr008["net_favorable_conversions"] >= 12,
        "vs_cr008_mean_margin_positive": bool(rows) and vs_cr008["mean_margin_gain"] > 0.0,
        "vs_cr008_unfavorable_le_10": bool(rows) and vs_cr008["unfavorable_conversions"] <= 10,
        "vs_top19_score_difference_ge_minus_2": bool(rows) and vs_top19["score_gain"] >= -2.0,
        "vs_top19_mean_margin_difference_ge_minus_500": bool(rows) and vs_top19["mean_margin_gain"] >= -500.0,
        "vs_top19_additional_unfavorable_le_4": bool(rows) and vs_top19["unfavorable_conversions"] <= 4,
    }
    passed = all(checks.values())
    decision = "CR024_CONSENSUS_V1_PASS__BUILD_PACKAGE" if passed else "CR024_CONSENSUS_V1_FAIL__DO_NOT_SUBMIT"
    payload = {
        "experiment": "CR024_CONSENSUS_V1",
        "stage": "FRESH_ADAPTIVE_OVERLAY_STAGE_A_RESERVED",
        "shard_count": len(files),
        "opponents": sorted(set(opponents)),
        "expected_rows": expected,
        "completed_rows": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "vs_cr008": vs_cr008,
        "vs_top19": vs_top19,
        "checks": checks,
        "decision": decision,
        "adaptive_overlay_stage_b_touched": False,
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
