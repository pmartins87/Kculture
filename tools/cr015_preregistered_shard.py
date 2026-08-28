"""Mechanical shard runner for the frozen CR-015 preregistered protocol.

One invocation evaluates exactly one frozen opponent over every seed and both
seats for a requested stage. The final gate is applied only by the aggregator
using functions from the already-frozen candidate-agnostic evaluator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cr015_preregistered_evaluation as E

ROOT = E.ROOT
CANDIDATE = ROOT / "candidates/cr015_liquidation_phase_early_order.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--stage", choices=("a", "b"), required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    opponent = Path(args.opponent)
    if not opponent.is_absolute():
        opponent = ROOT / opponent
    cfg = json.loads(E.CONFIG.read_text(encoding="utf-8"))
    seeds = cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]

    rows = []
    errors = []
    for seed in seeds:
        for seat in (0, 1):
            row = {"seed": int(seed), "opponent": args.opponent_id, "seat": seat}
            for key, path in (("r4b", E.R4B), ("cr011", E.CR011), ("cr015", CANDIDATE)):
                try:
                    self_reward, opp_reward, delta = E.play(path, opponent, seed, seat)
                    row[key] = {
                        "self": self_reward,
                        "opp": opp_reward,
                        "delta": delta,
                        "score": E.score(delta),
                    }
                except Exception as exc:
                    errors.append({
                        "seed": int(seed), "opponent": args.opponent_id,
                        "seat": seat, "arm": key, "error": repr(exc),
                    })
                    row[key] = None
                    break
            if all(row.get(k) is not None for k in ("r4b", "cr011", "cr015")):
                rows.append(row)

    payload = {
        "experiment": "CR-015",
        "runner": "parallel-shard-v1",
        "stage": args.stage.upper(),
        "opponent": args.opponent_id,
        "seeds": seeds,
        "expected_pairs": len(seeds) * 2,
        "completed_pairs": len(rows),
        "errors": errors,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("rows", "errors")} | {"error_count": len(errors)}, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
