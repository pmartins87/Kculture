#!/usr/bin/env python3
"""FP001 H8 B3 — paired full-engine CARE overlay test on COW3/H0.

Same fresh seed/seat pairs for NONE, SURVIVAL and DAILY.  The comparison isolates
whether idle-turn CARE/feed investment adds realized money to the proven B2
physical backbone.
"""
from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "candidates" / "fp001_h8_cow3_care_wrapper.py"
SEEDS = list(range(65101, 65109))
MODES = ("NONE", "SURVIVAL", "DAILY")
STARTING_MONEY = 3000.0


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_h8_cow3_care", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def pass_agent(obs, config=None):
    player = int(_get(obs, "player", 0) or 0)
    farms = _get(obs, "farms", []) or []
    hands_n = len(_get(farms[player], "hands", []) or []) if player < len(farms) else 0
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hands_n)], "market": []}


def instrument(fn):
    stats = Counter()

    def wrapped(obs, config=None):
        action = fn(obs, config)
        units = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
        for unit_action in units:
            if isinstance(unit_action, list) and unit_action:
                stats[f"unit_{unit_action[0]}"] += 1
        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            op = order[0]
            item = order[1] if len(order) >= 2 else ""
            qty = 1
            if len(order) >= 3:
                try:
                    qty = int(order[2])
                except Exception:
                    qty = 0
            stats[f"market_{op}_{item}_orders"] += 1
            stats[f"market_{op}_{item}_qty"] += qty
        return action

    return wrapped, stats


def run_one(mod, mode, seed, seat):
    wrapped, stats = instrument(mod.make_agent(mode))
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed},
        debug=True,
    )
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = [float(x) for x in j["rewards"]]
    assert statuses == ["DONE", "DONE"], (mode, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY, (mode, seed, seat, rewards)

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    for pos in mod.TARGET_POSITIONS[:3]:
        x, y = pos
        tile = farm["tiles"][y][x]
        assert isinstance(tile, dict) and tile.get("animal") == "COW", (mode, seed, seat, pos, tile)

    return rewards[seat] - STARTING_MONEY, dict(stats)


def summary(xs):
    return {
        "n": len(xs),
        "mean": mean(xs),
        "median": median(xs),
        "min": min(xs),
        "max": max(xs),
    }


def main():
    mod = load_module()
    values = {m: {} for m in MODES}
    totals = {m: Counter() for m in MODES}

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for mode in MODES:
                delta, stats = run_one(mod, mode, seed, seat)
                values[mode][key] = delta
                totals[mode].update(stats)
                assert delta > 0, (mode, key, delta)

    print("H8_COW3_CARE_RUNTIME_STABLE")
    for mode in MODES:
        xs = list(values[mode].values())
        st = totals[mode]
        print(mode, summary(xs))
        print("  key_stats", {
            "care": st.get("unit_CARE", 0),
            "feed": st.get("unit_FEED", 0),
            "wheat_bought": st.get("market_BUY_PRODUCT_WHEAT_qty", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "moves": sum(st.get(f"unit_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
        })

    base = values["NONE"]
    for mode in ("SURVIVAL", "DAILY"):
        diffs = [values[mode][k] - base[k] for k in sorted(base)]
        print(f"paired_{mode}_minus_NONE", {
            "mean": mean(diffs),
            "median": median(diffs),
            "min": min(diffs),
            "max": max(diffs),
            "wins": sum(d > 0 for d in diffs),
            "ties": sum(d == 0 for d in diffs),
            "losses": sum(d < 0 for d in diffs),
        })

    sd = [values["DAILY"][k] - values["SURVIVAL"][k] for k in sorted(base)]
    print("paired_DAILY_minus_SURVIVAL", {
        "mean": mean(sd), "median": median(sd), "min": min(sd), "max": max(sd),
        "wins": sum(d > 0 for d in sd), "ties": sum(d == 0 for d in sd), "losses": sum(d < 0 for d in sd),
    })


if __name__ == "__main__":
    main()
