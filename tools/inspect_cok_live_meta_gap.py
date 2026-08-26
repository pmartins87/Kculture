"""Static audit of frozen COK V8 route tapes against live-meta lifecycle signals.

Imports the exact fetched COK V8 source and summarizes every _ACTIONS_* route,
with special attention to the final 119 turns. This is observational and does
not mutate any strategy.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
from pathlib import Path

WINDOWS = ((0, 215), (216, 599), (600, 671), (672, 695), (696, 718))
MOVE = {"NORTH", "SOUTH", "EAST", "WEST"}


def load(path: Path):
    spec = importlib.util.spec_from_file_location("cok_live_meta_gap", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def summarize_window(actions, start: int, end: int) -> dict:
    unit = collections.Counter()
    market_ops = collections.Counter()
    market_qty = collections.Counter()
    for i in range(start, min(end + 1, len(actions))):
        a = actions[i]
        if not isinstance(a, dict):
            continue
        for op in [a.get("farmer")] + list(a.get("hands") or []):
            if isinstance(op, list) and op:
                unit[str(op[0])] += 1
        for order in a.get("market", []) or []:
            if not isinstance(order, list) or not order:
                continue
            market_ops[str(order[0])] += 1
            if len(order) >= 3:
                try:
                    market_qty[f"{order[0]}_{order[1]}"] += int(order[2])
                except (TypeError, ValueError):
                    pass
    return {
        "unit_actions": dict(sorted(unit.items())),
        "market_orders": dict(sorted(market_ops.items())),
        "market_quantities": dict(sorted(market_qty.items())),
        "feed": unit["FEED"],
        "care": unit["CARE"],
        "harvest": unit["HARVEST"],
        "drop": unit["DROP"],
        "pass": unit["PASS"],
        "movement": sum(unit[x] for x in MOVE),
        "buy_seed": {k[9:]: v for k, v in sorted(market_qty.items()) if k.startswith("BUY_SEED_")},
        "sell": {k[5:]: v for k, v in sorted(market_qty.items()) if k.startswith("SELL_")},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    mod = load(Path(args.source))
    routes = {}
    for name in sorted(vars(mod)):
        if not name.startswith("_ACTIONS_"):
            continue
        actions = getattr(mod, name)
        if not isinstance(actions, list) or len(actions) < 700:
            continue
        routes[name] = {
            "length": len(actions),
            "windows": {
                f"{a}_{b}": summarize_window(actions, a, b) for a, b in WINDOWS
            },
        }
    if not routes:
        raise RuntimeError("no route tapes found")
    report = {"schema_version": "cok-live-meta-gap-v1", "source": args.source, "routes": routes}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
