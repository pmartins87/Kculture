"""CR022C aggregate/gate for preregistered fractional adaptive-sale quantity sweep."""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from pathlib import Path

ARMS = ("q25", "q50", "q75")
CONTROL = "q100"


def score_gain(row, arm):
    return float(row[arm]["score"]) - float(row[CONTROL]["score"])


def cvar10(values):
    if not values:
        return 0.0
    xs = sorted(float(x) for x in values)
    n = max(1, math.ceil(0.10 * len(xs)))
    return statistics.mean(xs[:n])


def contrast(rows, arm):
    rel = [float(r[arm]["delta"]) - float(r[CONTROL]["delta"]) for r in rows]
    own = [float(r[arm]["self"]) - float(r[CONTROL]["self"]) for r in rows]
    sg = [score_gain(r, arm) for r in rows]
    fav = sum(x > 0 for x in sg)
    bad = sum(x < 0 for x in sg)
    return {
        "pairs": len(rows),
        "mean_relative_gain": statistics.mean(rel) if rel else 0.0,
        "median_relative_gain": statistics.median(rel) if rel else 0.0,
        "mean_self_gain": statistics.mean(own) if own else 0.0,
        "mean_score_gain": statistics.mean(sg) if sg else 0.0,
        "favorable_outcome_changes": fav,
        "unfavorable_outcome_changes": bad,
        "net_outcome_changes": fav - bad,
        "unchanged_outcomes": len(rows) - fav - bad,
        "positive_relative_fraction": sum(x > 0 for x in rel) / len(rel) if rel else 0.0,
        "cvar10_relative_gain": cvar10(rel),
        "min_relative_gain": min(rel) if rel else 0.0,
        "max_relative_gain": max(rel) if rel else 0.0,
    }


def eligible(broad, close):
    positive_signal = (
        broad["net_outcome_changes"] > 0
        or close["net_outcome_changes"] > 0
        or broad["mean_relative_gain"] > 0
    )
    return (
        broad["unfavorable_outcome_changes"] <= broad["favorable_outcome_changes"]
        and close["unfavorable_outcome_changes"] <= close["favorable_outcome_changes"]
        and broad["mean_score_gain"] >= 0
        and positive_signal
    )


def selection_tuple(broad, close):
    return (
        broad["net_outcome_changes"],
        close["net_outcome_changes"],
        broad["mean_score_gain"],
        close["mean_score_gain"],
        broad["mean_relative_gain"],
        broad["cvar10_relative_gain"],
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    paths = sorted(glob.glob(args.input_glob, recursive=True))
    shards = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows = [r for s in shards for r in s.get("rows", [])]
    errors = [e for s in shards for e in s.get("errors", [])]
    opponents = sorted({str(r["opponent"]) for r in rows})
    expected = sum(int(s.get("expected_pairs", 0)) for s in shards)

    ordered = sorted(rows, key=lambda r: abs(float(r[CONTROL]["delta"])))
    close = ordered[: min(args.close_target, len(ordered))]
    results = {}
    for arm in ARMS:
        b = contrast(rows, arm)
        c = contrast(close, arm)
        results[arm] = {
            "broad": b,
            "close": c,
            "eligible": eligible(b, c) if args.stage == "a" else None,
            "selection_tuple": list(selection_tuple(b, c)),
        }

    winner = None
    if args.stage == "a" and not errors and len(rows) == expected:
        candidates = [a for a in ARMS if results[a]["eligible"]]
        if candidates:
            winner = max(candidates, key=lambda a: selection_tuple(results[a]["broad"], results[a]["close"]))

    payload = {
        "experiment": "CR022C",
        "stage": args.stage.upper(),
        "control": CONTROL,
        "shards": len(shards),
        "opponents": opponents,
        "expected_pairs": expected,
        "completed_pairs": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "close_selection": {
            "rule": "smallest absolute q100 terminal relative delta only",
            "target": args.close_target,
            "selected": len(close),
            "mean_abs_q100_delta": statistics.mean(abs(float(r[CONTROL]["delta"])) for r in close) if close else None,
        },
        "results": results,
        "stage_a_winner": winner,
        "stage_a_supported": bool(winner) if args.stage == "a" else None,
        "policy": "At most one eligible Stage-A arm advances unchanged to disjoint Stage B; no rescue tuning on Stage-A seeds.",
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    print(json.dumps(compact, indent=2, sort_keys=True))
    if errors or len(rows) != expected:
        raise SystemExit(3)
    if args.stage == "a" and not winner:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
