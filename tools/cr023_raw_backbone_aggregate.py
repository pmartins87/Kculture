"""CR023 raw-backbone Stage-A aggregate and frozen preregistered gate."""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from pathlib import Path

CONTROL = "cr008"
ROUTES = ("top11_openloop", "top16_openloop", "top19_openloop")


def cvar10(values):
    xs = sorted(float(x) for x in values)
    if not xs:
        return 0.0
    n = max(1, math.ceil(0.10 * len(xs)))
    return statistics.mean(xs[:n])


def metrics(rows, route):
    relative = [float(r[route]["delta"]) - float(r[CONTROL]["delta"]) for r in rows]
    own = [float(r[route]["self"]) - float(r[CONTROL]["self"]) for r in rows]
    scores = [float(r[route]["score"]) - float(r[CONTROL]["score"]) for r in rows]
    favorable = sum(x > 0 for x in scores)
    unfavorable = sum(x < 0 for x in scores)
    return {
        "pairs": len(rows),
        "mean_score_gain": statistics.mean(scores) if scores else 0.0,
        "favorable_outcome_changes": favorable,
        "unfavorable_outcome_changes": unfavorable,
        "net_outcome_changes": favorable - unfavorable,
        "mean_relative_gain": statistics.mean(relative) if relative else 0.0,
        "median_relative_gain": statistics.median(relative) if relative else 0.0,
        "mean_self_gain": statistics.mean(own) if own else 0.0,
        "positive_relative_fraction": sum(x > 0 for x in relative) / len(relative) if relative else 0.0,
        "cvar10_relative_gain": cvar10(relative),
        "min_relative_gain": min(relative) if relative else 0.0,
        "max_relative_gain": max(relative) if relative else 0.0,
    }


def eligible(broad, close):
    return (
        broad["unfavorable_outcome_changes"] <= broad["favorable_outcome_changes"]
        and close["unfavorable_outcome_changes"] <= close["favorable_outcome_changes"]
        and broad["mean_score_gain"] > 0
        and broad["favorable_outcome_changes"] > 0
        and broad["mean_relative_gain"] > 0
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
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    paths = sorted(glob.glob(args.input_glob, recursive=True))
    shards = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows = [r for shard in shards for r in shard.get("rows", [])]
    errors = [e for shard in shards for e in shard.get("errors", [])]
    expected = sum(int(shard.get("expected_pairs", 0)) for shard in shards)
    opponents = sorted({str(r["opponent"]) for r in rows})

    ordered = sorted(rows, key=lambda r: abs(float(r[CONTROL]["delta"])))
    close = ordered[: min(args.close_target, len(ordered))]

    results = {}
    for route in ROUTES:
        broad = metrics(rows, route)
        close_metrics = metrics(close, route)
        results[route] = {
            "broad": broad,
            "close": close_metrics,
            "eligible": eligible(broad, close_metrics),
            "selection_tuple": list(selection_tuple(broad, close_metrics)),
        }

    winner = None
    if not errors and len(rows) == expected:
        candidates = [route for route in ROUTES if results[route]["eligible"]]
        if candidates:
            winner = max(candidates, key=lambda route: selection_tuple(results[route]["broad"], results[route]["close"]))

    payload = {
        "experiment": "CR023",
        "stage": "RAW_A",
        "control": CONTROL,
        "shards": len(shards),
        "opponents": opponents,
        "expected_pairs": expected,
        "completed_pairs": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "close_selection": {
            "rule": "smallest absolute CR008 terminal relative delta only",
            "target": args.close_target,
            "selected": len(close),
            "mean_abs_cr008_delta": statistics.mean(abs(float(r[CONTROL]["delta"])) for r in close) if close else None,
        },
        "results": results,
        "raw_stage_a_winner": winner,
        "raw_stage_a_supported": bool(winner),
        "policy": "At most one eligible raw tape advances unchanged to disjoint raw Stage B. No second-place substitution or route editing after Stage A.",
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    print(json.dumps(compact, indent=2, sort_keys=True))

    if errors or len(rows) != expected:
        raise SystemExit(3)
    if not winner:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
