#!/usr/bin/env python3
"""Aggregate parallel shards for frozen option-library composition gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.option_library_combo_runtime_v0 import summarize, V2_OPPONENTS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    inp = Path(args.input_dir)
    files = sorted(inp.rglob("OPTION_LIBRARY_COMBO_SHARD_*.json"))
    expected_keys = {x["key"] for x in V2_OPPONENTS}
    shards, rows, failures = {}, [], []

    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        key = d["opponent"]["key"]
        shards[key] = d
        rows.extend(d.get("rows") or [])
        if not d.get("mechanical_pass"):
            failures.append({"opponent": key, "failures": d.get("failures")})

    missing = sorted(expected_keys - set(shards))
    mechanical_pass = not failures and not missing and set(shards) == expected_keys
    overall = summarize(rows)
    by_opp = {k: shards[k]["summary"] for k in sorted(shards)}

    nonnegative_blocks = sum(
        1 for x in by_opp.values()
        if x and float(x.get("combo_vs_base_score_delta", 0.0)) >= 0.0
    )
    worst_block = min(
        (float(x.get("combo_vs_base_score_delta", 0.0)) for x in by_opp.values() if x),
        default=-1.0,
    )
    combo_delta = float(overall.get("combo_vs_base_score_delta", 0.0))
    combo_vs_best = float(overall.get("combo_vs_best_single_mean_score_delta", 0.0))

    if mechanical_pass and combo_delta > 0 and combo_vs_best >= 0 and nonnegative_blocks >= 6:
        decision = "OPTION_LIBRARY_COMBO_ADVANCE"
    elif mechanical_pass and combo_delta > 0 and worst_block >= -0.0625:
        decision = "OPTION_LIBRARY_COMBO_SAFE_BUT_NO_INCREMENT"
    elif mechanical_pass and combo_delta > 0:
        decision = "OPTION_LIBRARY_COMBO_HETEROGENEOUS"
    elif mechanical_pass:
        decision = "OPTION_LIBRARY_COMBO_NO_GAIN"
    else:
        decision = "OPTION_LIBRARY_COMBO_MECHANICS_INVALID"

    out = {
        "schema": "kculture-option-library-combo-runtime-v0-parallel-aggregate",
        "mechanical_pass": mechanical_pass,
        "missing_shards": missing,
        "failures": failures,
        "summary": overall,
        "by_opponent": by_opp,
        "gate_diagnostics": {
            "nonnegative_combo_blocks": nonnegative_blocks,
            "worst_combo_block_score_delta": worst_block,
        },
        "decision": decision,
        "contexts": len(rows),
        "shard_files": [str(p) for p in files],
        "automatic_kaggle_submission": False,
    }
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("OPTION_LIBRARY_COMBO_PARALLEL_RESULT", json.dumps({
        "decision": decision,
        "mechanical_pass": mechanical_pass,
        "summary": overall,
        "by_opponent": by_opp,
        "missing_shards": missing,
        "failures": failures,
    }, sort_keys=True), flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
