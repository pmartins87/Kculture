#!/usr/bin/env python3
"""FP001 B4 — paired scale x CARE runtime gate.

Tests n=3..6 with NONE/SURVIVAL/DAILY on identical fresh seed/seat pairs.  This
locates the action-capacity frontier of one main farmer after H10 batching removed
avoidable harvest work.
"""
from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODULE_PATH = ROOT / "candidates" / "fp001_h10_cow_scale_care_wrapper.py"
SEEDS = list(range(67101, 67105))
STARTING_MONEY = 3000.0
SCALES = (3, 4, 5, 6)
MODES = ("NONE", "SURVIVAL", "DAILY")


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_b4", MODULE_PATH)
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
        for ua in [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]:
            if isinstance(ua, list) and ua:
                stats[f"unit_{ua[0]}"] += 1
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


def run_one(mod, n_cows, mode, seed, seat):
    wrapped, stats = instrument(mod.make_agent(n_cows, mode))
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed}, debug=True)
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = [float(x) for x in j["rewards"]]
    assert statuses == ["DONE", "DONE"], (n_cows, mode, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    alive = 0
    for x, y in mod.TARGET_POSITIONS[:n_cows]:
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            alive += 1
    return {"delta": rewards[seat] - STARTING_MONEY, "alive": alive, "stats": dict(stats)}


def summary(xs):
    return {"n": len(xs), "mean": mean(xs), "median": median(xs), "min": min(xs), "max": max(xs)}


def paired(values, a, b):
    keys = sorted(set(values[a]) & set(values[b]))
    ds = [values[a][k]["delta"] - values[b][k]["delta"] for k in keys]
    return {"mean": mean(ds), "median": median(ds), "min": min(ds), "max": max(ds),
            "wins": sum(x > 0 for x in ds), "ties": sum(x == 0 for x in ds), "losses": sum(x < 0 for x in ds)}


def main():
    mod = load_module()
    archs = [(n, mode) for n in SCALES for mode in MODES]
    values = {a: {} for a in archs}
    totals = {a: Counter() for a in archs}

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for a in archs:
                n, mode = a
                out = run_one(mod, n, mode, seed, seat)
                values[a][key] = out
                totals[a].update(out["stats"])

    print("B4_SCALE_CARE_RUNTIME_COMPLETE")
    for a in archs:
        n, mode = a
        rows = list(values[a].values())
        ds = [r["delta"] for r in rows]
        full = sum(r["alive"] == n for r in rows)
        st = totals[a]
        print(f"COW{n}_{mode}", summary(ds), {
            "full_survival": f"{full}/{len(rows)}",
            "min_alive": min(r["alive"] for r in rows),
            "per_cow_mean": round(mean(ds) / n, 3),
        })
        print("  key_stats", {
            "care": st.get("unit_CARE", 0),
            "feed": st.get("unit_FEED", 0),
            "wheat_bought": st.get("market_BUY_PRODUCT_WHEAT_qty", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "harvest": st.get("unit_HARVEST", 0),
            "moves": sum(st.get(f"unit_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
        })

    for n in SCALES:
        print(f"paired_COW{n}_SURVIVAL_minus_NONE", paired(values, (n, "SURVIVAL"), (n, "NONE")))
        print(f"paired_COW{n}_DAILY_minus_NONE", paired(values, (n, "DAILY"), (n, "NONE")))
        print(f"paired_COW{n}_DAILY_minus_SURVIVAL", paired(values, (n, "DAILY"), (n, "SURVIVAL")))

    for mode in MODES:
        for n in SCALES[1:]:
            print(f"paired_{mode}_COW{n}_minus_COW{n-1}", paired(values, (n, mode), (n - 1, mode)))

    ranking = sorted(archs, key=lambda a: mean([r["delta"] for r in values[a].values()]), reverse=True)
    print("mean_delta_ranking", [(f"COW{n}_{mode}", mean([r["delta"] for r in values[(n, mode)].values()])) for n, mode in ranking])


if __name__ == "__main__":
    main()
