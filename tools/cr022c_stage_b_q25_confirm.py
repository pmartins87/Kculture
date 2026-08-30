"""CR022C Stage-B aggregate for frozen q25 versus exact q100 control."""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from pathlib import Path


def cvar10(values):
    xs = sorted(float(x) for x in values)
    if not xs:
        return 0.0
    n = max(1, math.ceil(0.10 * len(xs)))
    return statistics.mean(xs[:n])


def contrast(rows):
    rel = [float(r["q25"]["delta"]) - float(r["q100"]["delta"]) for r in rows]
    own = [float(r["q25"]["self"]) - float(r["q100"]["self"]) for r in rows]
    sg = [float(r["q25"]["score"]) - float(r["q100"]["score"]) for r in rows]
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
        "positive_relative_fraction": sum(x > 0 for x in rel) / len(rel) if rel else 0.0,
        "cvar10_relative_gain": cvar10(rel),
        "min_relative_gain": min(rel) if rel else 0.0,
        "max_relative_gain": max(rel) if rel else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--close-target", type=int, default=40)
    args = ap.parse_args()

    paths = sorted(glob.glob(args.input_glob, recursive=True))
    shards = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows = [r for s in shards for r in s.get("rows", [])]
    errors = [e for s in shards for e in s.get("errors", [])]
    expected = sum(int(s.get("expected_pairs", 0)) for s in shards)
    close = sorted(rows, key=lambda r: abs(float(r["q100"]["delta"])))[:min(args.close_target, len(rows))]
    broad = contrast(rows)
    close_metrics = contrast(close)

    confirmed = (
        not errors
        and len(rows) == expected == 216
        and broad["unfavorable_outcome_changes"] <= broad["favorable_outcome_changes"]
        and close_metrics["unfavorable_outcome_changes"] <= close_metrics["favorable_outcome_changes"]
        and broad["mean_score_gain"] >= 0.0
        and (broad["net_outcome_changes"] > 0 or broad["mean_relative_gain"] > 0.0)
    )

    payload = {
        "experiment": "CR022C",
        "stage": "B",
        "candidate": "q25",
        "control": "q100_exact_cr008",
        "shards": len(shards),
        "expected_pairs": expected,
        "completed_pairs": len(rows),
        "error_count": len(errors),
        "broad": broad,
        "close": close_metrics,
        "close_selection": {
            "rule": "smallest absolute q100 terminal relative delta only",
            "target": args.close_target,
            "selected": len(close),
        },
        "confirmed": confirmed,
        "policy": "Frozen q25 either confirms unchanged or is rejected; no Stage-B rescue tuning or alternative fraction substitution.",
        "errors": errors,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "errors"}, indent=2, sort_keys=True))
    if errors or len(rows) != expected:
        raise SystemExit(3)
    if not confirmed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
