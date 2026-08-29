"""Aggregate CR-020 shards and apply the gate frozen before Stage-A outcomes.

The close subset is selected only from absolute frozen R4B terminal delta.
Promotion evidence is outcome-aware: money-margin improvement alone is not
enough.  Stage B may run only for the exact unchanged candidate if Stage A
passes this file's frozen gate.
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cr015_preregistered_evaluation as E

CONFIG = ROOT / "configs/cr020_preregistered_seeds_v1.json"
OPP_CONFIG = ROOT / "configs/cr015_current_meta_opponents_v1.json"
CANDIDATE = "candidates/cr020_monotone_append_latch.py"
PREDECESSOR = "candidates/cr015_liquidation_phase_early_order.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    seed_cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = seed_cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]
    opp_cfg = json.loads(OPP_CONFIG.read_text(encoding="utf-8"))
    expected_opponents = [x["id"] for x in opp_cfg["opponents"]]

    paths = sorted(Path(p) for p in glob.glob(args.input_glob, recursive=True))
    if not paths:
        raise SystemExit("no shard reports found")

    rows = []
    errors = []
    seen = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("runner") != "parallel-shard-v1":
            continue
        if payload.get("experiment") != "CR-020":
            raise RuntimeError(f"experiment mismatch in {path}")
        if payload.get("stage") != args.stage.upper():
            raise RuntimeError(f"stage mismatch in {path}")
        if payload.get("seeds") != seeds:
            raise RuntimeError(f"seed mismatch in {path}")
        seen.append(payload["opponent"])
        rows.extend(payload.get("rows") or [])
        errors.extend(payload.get("errors") or [])

    if sorted(seen) != sorted(expected_opponents):
        raise RuntimeError(
            f"opponent shard mismatch: seen={sorted(seen)} "
            f"expected={sorted(expected_opponents)}"
        )

    expected_pairs = len(seeds) * len(expected_opponents) * 2
    ordered = sorted(rows, key=lambda r: abs(r["r4b"]["delta"]))
    close = ordered[: min(args.close_target, len(ordered))]

    broad_r4b = E.contrast(rows, "cr020", "r4b")
    broad_prev = E.contrast(rows, "cr020", "cr015")
    close_r4b = E.contrast(close, "cr020", "r4b")
    close_prev = E.contrast(close, "cr020", "cr015")

    zero_errors = not errors and len(rows) == expected_pairs
    no_net_wl_harm = (
        broad_r4b["mean_score_gain"] >= 0
        and broad_prev["mean_score_gain"] >= 0
        and close_r4b["unfavorable_outcome_changes"] <= close_r4b["favorable_outcome_changes"]
        and close_prev["unfavorable_outcome_changes"] <= close_prev["favorable_outcome_changes"]
    )
    outcome_conversion_signal = (
        close_r4b["favorable_outcome_changes"] > close_r4b["unfavorable_outcome_changes"]
        or close_prev["favorable_outcome_changes"] > close_prev["unfavorable_outcome_changes"]
        or broad_r4b["mean_score_gain"] > 0
        or broad_prev["mean_score_gain"] > 0
    )
    gain_vs_r4b = broad_r4b["mean_relative_gain"] > 0
    no_margin_regression_vs_predecessor = broad_prev["mean_relative_gain"] >= 0

    stage_a_supported = (
        args.stage == "a"
        and zero_errors
        and no_net_wl_harm
        and outcome_conversion_signal
        and gain_vs_r4b
        and no_margin_regression_vs_predecessor
    )

    payload = {
        "experiment": "CR-020",
        "stage": args.stage.upper(),
        "execution": "parallel-shards-frozen-before-stage-a",
        "candidate": CANDIDATE,
        "predecessor": PREDECESSOR,
        "seed_config": str(CONFIG.relative_to(ROOT)),
        "opponent_config": str(OPP_CONFIG.relative_to(ROOT)),
        "seeds": seeds,
        "opponents": expected_opponents,
        "expected_pairs": expected_pairs,
        "completed_pairs": len(rows),
        "errors": errors,
        "close_selection": {
            "rule": "smallest absolute frozen R4B terminal money delta only",
            "target": args.close_target,
            "selected": len(close),
            "mean_abs_r4b_delta": (
                statistics.mean(abs(r["r4b"]["delta"]) for r in close)
                if close else None
            ),
        },
        "broad": {
            "cr020_vs_r4b": broad_r4b,
            "cr020_vs_cr015": broad_prev,
        },
        "close": {
            "cr020_vs_r4b": close_r4b,
            "cr020_vs_cr015": close_prev,
        },
        "stage_a_gate": {
            "zero_errors_and_complete": zero_errors,
            "no_net_wl_harm": no_net_wl_harm,
            "outcome_conversion_signal": outcome_conversion_signal,
            "mean_relative_gain_vs_r4b_positive": gain_vs_r4b,
            "no_mean_relative_regression_vs_cr015": no_margin_regression_vs_predecessor,
            "supported": stage_a_supported,
        },
        "policy": (
            "Stage B may run only for this exact unchanged CR-020 candidate if "
            "Stage A supported=true. Money-margin improvement without an outcome "
            "conversion signal is insufficient. Held-out 32/32 remains sealed."
        ),
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    compact["error_count"] = len(errors)
    print(json.dumps(compact, indent=2, sort_keys=True))

    if not zero_errors:
        raise SystemExit(3)
    if args.stage == "a" and not stage_a_supported:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
