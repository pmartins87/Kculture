"""Aggregate parallel shards using the frozen CR-015 evaluator semantics."""
from __future__ import annotations

import argparse
import glob
import json
import statistics
from pathlib import Path

import cr015_preregistered_evaluation as E

ROOT = E.ROOT
OPP_CFG = ROOT / "configs/cr015_current_meta_opponents_v1.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    seed_cfg = json.loads(E.CONFIG.read_text(encoding="utf-8"))
    seeds = seed_cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]
    opp_cfg = json.loads(OPP_CFG.read_text(encoding="utf-8"))
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
        if payload.get("stage") != args.stage.upper():
            raise RuntimeError(f"stage mismatch in {path}")
        if payload.get("seeds") != seeds:
            raise RuntimeError(f"seed mismatch in {path}")
        seen.append(payload["opponent"])
        rows.extend(payload.get("rows") or [])
        errors.extend(payload.get("errors") or [])

    if sorted(seen) != sorted(expected_opponents):
        raise RuntimeError(f"opponent shard mismatch: seen={sorted(seen)} expected={sorted(expected_opponents)}")

    expected_pairs = len(seeds) * len(expected_opponents) * 2
    ordered = sorted(rows, key=lambda r: abs(r["r4b"]["delta"]))
    close = ordered[: min(args.close_target, len(ordered))]

    broad_r4b = E.contrast(rows, "cr015", "r4b")
    broad_cr011 = E.contrast(rows, "cr015", "cr011")
    close_r4b = E.contrast(close, "cr015", "r4b")
    close_cr011 = E.contrast(close, "cr015", "cr011")

    # Exact gate copied from the preregistered evaluator; contrast/score are
    # imported from that frozen file to avoid semantic drift.
    no_net_harm = (
        broad_r4b["mean_score_gain"] >= 0
        and broad_cr011["mean_score_gain"] >= 0
        and close_r4b["unfavorable_outcome_changes"] <= close_r4b["favorable_outcome_changes"]
        and close_cr011["unfavorable_outcome_changes"] <= close_cr011["favorable_outcome_changes"]
    )
    outcome_signal = (
        close_r4b["favorable_outcome_changes"] > close_r4b["unfavorable_outcome_changes"]
        or close_cr011["favorable_outcome_changes"] > close_cr011["unfavorable_outcome_changes"]
        or broad_r4b["mean_score_gain"] > 0
        or broad_cr011["mean_score_gain"] > 0
    )
    relative_supported = broad_r4b["mean_relative_gain"] > 0
    stage_a_supported = (
        args.stage == "a"
        and not errors
        and len(rows) == expected_pairs
        and no_net_harm
        and outcome_signal
        and relative_supported
    )

    payload = {
        "experiment": "CR-015",
        "stage": args.stage.upper(),
        "execution": "parallel-shards-equivalent-to-frozen-evaluator",
        "candidate": "candidates/cr015_liquidation_phase_early_order.py",
        "seed_config": str(E.CONFIG.relative_to(ROOT)),
        "opponent_config": str(OPP_CFG.relative_to(ROOT)),
        "seeds": seeds,
        "opponents": expected_opponents,
        "expected_pairs": expected_pairs,
        "completed_pairs": len(rows),
        "errors": errors,
        "close_selection": {
            "rule": "smallest absolute frozen R4B terminal money delta only",
            "target": args.close_target,
            "selected": len(close),
            "mean_abs_r4b_delta": statistics.mean(abs(r["r4b"]["delta"]) for r in close) if close else None,
        },
        "broad": {
            "cr015_vs_r4b": broad_r4b,
            "cr015_vs_cr011": broad_cr011,
        },
        "close": {
            "cr015_vs_r4b": close_r4b,
            "cr015_vs_cr011": close_cr011,
        },
        "stage_a_gate": {
            "zero_errors": not errors,
            "no_net_wl_harm": no_net_harm,
            "outcome_conversion_signal": outcome_signal,
            "mean_relative_gain_vs_r4b_positive": relative_supported,
            "supported": stage_a_supported,
        },
        "policy": "Stage B may run only for the unchanged frozen candidate if Stage A supported=true. No candidate code/threshold changes between stages.",
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    compact["error_count"] = len(errors)
    print(json.dumps(compact, indent=2, sort_keys=True))

    if errors or len(rows) != expected_pairs:
        raise SystemExit(3)
    if args.stage == "a" and not stage_a_supported:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
