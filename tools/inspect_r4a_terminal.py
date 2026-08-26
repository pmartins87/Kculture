"""Inspect the frozen R4A COK route tails without modifying the policy."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/public_opponents/cok_v8_779caae.py"
OUTPUT = ROOT / "artifacts/r4a_terminal_inspection.json"


def load_module():
    spec = importlib.util.spec_from_file_location("kculture_r4a_inspect", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compact(action):
    action = action or {}
    return {
        "farmer": action.get("farmer"),
        "hands": action.get("hands"),
        "market": action.get("market"),
    }


def summarize_window(actions, start, end):
    summary = {
        "steps": 0,
        "market": {},
        "unit_ops": {},
    }
    for step in range(max(0, start), min(len(actions), end + 1)):
        action = actions[step] or {}
        summary["steps"] += 1
        for order in list(action.get("market") or []):
            if not isinstance(order, list) or not order:
                continue
            key = str(order[0])
            if len(order) >= 2:
                key += ":" + str(order[1])
            quantity = order[2] if len(order) >= 3 and isinstance(order[2], (int, float)) else 1
            summary["market"][key] = summary["market"].get(key, 0) + quantity
        units = [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]
        for unit in units:
            if not isinstance(unit, list) or not unit:
                continue
            op = str(unit[0])
            summary["unit_ops"][op] = summary["unit_ops"].get(op, 0) + 1
    return summary


def main():
    module = load_module()
    payload = {"source": str(SOURCE.relative_to(ROOT)), "routes": {}}
    checkpoints = [600, 624, 648, 672, 680, 684, 688, 692, 695, 696, 697, 698, 700, 704, 708, 712, 716, 717, 718]
    for family_name, routes in (
        ("current", module._V7_CURRENT_ROUTES),
        ("legacy", module._V7_LEGACY_ROUTES),
    ):
        family = {}
        for label, actions in routes.items():
            n = len(actions)
            interesting = sorted({s for s in checkpoints if 0 <= s < n} | {max(0, n - 5), max(0, n - 4), max(0, n - 3), max(0, n - 2), max(0, n - 1)})
            tail = {str(step): compact(actions[step]) for step in interesting if 0 <= step < n}
            terminal_market = list((actions[-1] or {}).get("market") or []) if n else []
            family[label] = {
                "length": n,
                "last_index": n - 1,
                "tail": tail,
                "window_day28_672_695": summarize_window(actions, 672, 695),
                "window_day29_696_718": summarize_window(actions, 696, 718),
                "last_market_orders": terminal_market,
                "last_sell_orders": [
                    order for order in terminal_market
                    if isinstance(order, list) and order and order[0] == "SELL"
                ],
                "last_drop_actions": [
                    order
                    for order in [
                        (actions[-1] or {}).get("farmer") or ["PASS"],
                        *list((actions[-1] or {}).get("hands") or []),
                    ]
                    if isinstance(order, list) and order and order[0] == "DROP"
                ] if n else [],
            }
        payload["routes"][family_name] = family
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
