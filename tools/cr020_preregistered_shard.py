"""Mechanical shard runner for the frozen CR-020 preregistered protocol.

One invocation evaluates one exact frozen opponent over every seed and both
seats for a requested stage.  R4B and frozen CR-015 are the controls.  The
candidate is CR-020 monotone append latch.  Gate logic lives only in the
aggregator and is frozen before Stage A is run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cr015_preregistered_evaluation as E

CONFIG = ROOT / "configs/cr020_preregistered_seeds_v1.json"
R4B = ROOT / "candidates/r4b_ablation_market_only.py"
PREDECESSOR = ROOT / "candidates/cr015_liquidation_phase_early_order.py"
CANDIDATE = ROOT / "candidates/cr020_monotone_append_latch.py"


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
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = cfg["stage_a_seeds" if args.stage == "a" else "stage_b_seeds"]

    rows = []
    errors = []
    for seed in seeds:
        for seat in (0, 1):
            row = {"seed": int(seed), "opponent": args.opponent_id, "seat": seat}
            for key, path in (
                ("r4b", R4B),
                ("cr015", PREDECESSOR),
                ("cr020", CANDIDATE),
            ):
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
                        "seed": int(seed),
                        "opponent": args.opponent_id,
                        "seat": seat,
                        "arm": key,
                        "error": repr(exc),
                    })
                    row[key] = None
                    break
            if all(row.get(k) is not None for k in ("r4b", "cr015", "cr020")):
                rows.append(row)

    payload = {
        "experiment": "CR-020",
        "runner": "parallel-shard-v1",
        "stage": args.stage.upper(),
        "opponent": args.opponent_id,
        "seed_config": str(CONFIG.relative_to(ROOT)),
        "seeds": seeds,
        "expected_pairs": len(seeds) * 2,
        "completed_pairs": len(rows),
        "errors": errors,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    compact = {k: v for k, v in payload.items() if k not in ("rows", "errors")}
    compact["error_count"] = len(errors)
    print(json.dumps(compact, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
