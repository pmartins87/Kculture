"""CR022C Stage B: evaluate only the frozen q25 winner versus exact q100/CR008.

This runner intentionally does not evaluate q50/q75 on Stage-B seeds.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr022c_quantity_shard import play

CONFIG = ROOT / "configs/cr022c_quantity_preregistered_seeds_v1.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    seeds = cfg["stage_b_seeds"]
    opponent = Path(args.opponent)
    if not opponent.is_absolute():
        opponent = ROOT / opponent

    rows = []
    errors = []
    for seed in seeds:
        for seat in (0, 1):
            row = {"seed": int(seed), "opponent": args.opponent_id, "seat": seat}
            for arm in ("q100", "q25"):
                try:
                    row[arm] = play(arm, opponent, int(seed), seat)
                except Exception as exc:
                    errors.append({
                        "seed": int(seed),
                        "opponent": args.opponent_id,
                        "seat": seat,
                        "arm": arm,
                        "error": repr(exc),
                    })
                    row[arm] = None
                    break
            if row.get("q100") is not None and row.get("q25") is not None:
                rows.append(row)

    payload = {
        "experiment": "CR022C",
        "stage": "B",
        "candidate": "q25",
        "control": "q100",
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
    print(json.dumps({
        "experiment": "CR022C",
        "stage": "B",
        "candidate": "q25",
        "opponent": args.opponent_id,
        "expected_pairs": payload["expected_pairs"],
        "completed_pairs": payload["completed_pairs"],
        "error_count": len(errors),
    }, indent=2, sort_keys=True))
    if errors or len(rows) != len(seeds) * 2:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
