#!/usr/bin/env python3
"""FP001 H8 Gate B2 — multi-animal full-engine logistics test.

Compares 2-3 animal portfolios and quantifies whether two cheap daily farm hands
actually improve realized money after movement, feeding, collection, harvest,
market impact, setup and hire cost.
"""
from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "candidates" / "fp001_h8_multi_animal_module.py"
SEEDS = list(range(64101, 64105))
STARTING_MONEY = 3000.0

ARCHS = {
    "COW2_H0": (("COW", "COW"), 0),
    "COW2_H2": (("COW", "COW"), 2),
    "COW3_H0": (("COW", "COW", "COW"), 0),
    "COW3_H2": (("COW", "COW", "COW"), 2),
    "COW2_SHEEP1_H2": (("COW", "COW", "SHEEP"), 2),
    "COW1_SHEEP2_H2": (("COW", "SHEEP", "SHEEP"), 2),
    "SHEEP3_H2": (("SHEEP", "SHEEP", "SHEEP"), 2),
}


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_h8_multi", MODULE_PATH)
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


def run_one(mod, species_tuple, hands_target, seed, seat):
    wrapped, stats = instrument(mod.make_agent(species_tuple, hands_target=hands_target))
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
    assert statuses == ["DONE", "DONE"], (species_tuple, hands_target, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY, (species_tuple, hands_target, seed, seat, rewards)

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    alive = []
    for idx, species in enumerate(species_tuple):
        x, y = mod.TARGET_POSITIONS[idx]
        tile = farm["tiles"][y][x]
        alive.append(isinstance(tile, dict) and tile.get("animal") == species)
    assert all(alive), (species_tuple, hands_target, seed, seat, alive, dict(stats))

    delta = rewards[seat] - STARTING_MONEY
    return delta, dict(stats)


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
    results = {}
    stats_by_arch = {}

    for name, (species_tuple, hands_target) in ARCHS.items():
        deltas = []
        total = Counter()
        for seed in SEEDS:
            for seat in (0, 1):
                delta, stats = run_one(mod, species_tuple, hands_target, seed, seat)
                deltas.append(delta)
                total.update(stats)
        results[name] = deltas
        stats_by_arch[name] = total

        assert min(deltas) > 0, (name, summary(deltas))
        assert total["unit_COLLECT_FERTILIZER"] > 0, (name, total)
        assert total["unit_FEED"] > 0, (name, total)
        for species, wanted in Counter(species_tuple).items():
            assert total[f"market_BUY_ANIMAL_{species}_qty"] == wanted * len(deltas), (name, total)
        if hands_target:
            assert total["market_HIRE__orders"] > 0, (name, total)

    print("H8_MULTI_ANIMAL_RUNTIME_PASS")
    for name in ARCHS:
        st = stats_by_arch[name]
        print(name, summary(results[name]))
        print("  key_stats", {
            "hire_orders": st.get("market_HIRE__orders", 0),
            "wheat_bought": st.get("market_BUY_PRODUCT_WHEAT_qty", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "wool_sold": st.get("market_SELL_WOOL_qty", 0),
            "feed": st.get("unit_FEED", 0),
            "fert_collect": st.get("unit_COLLECT_FERTILIZER", 0),
            "harvest": st.get("unit_HARVEST", 0),
            "moves": sum(st.get(f"unit_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
        })

    ranking = sorted(ARCHS, key=lambda n: mean(results[n]), reverse=True)
    print("mean_delta_ranking", [(n, mean(results[n])) for n in ranking])

    # Direct labor ablations: same portfolio, H2 minus H0.
    cow2_labor = mean(results["COW2_H2"]) - mean(results["COW2_H0"])
    cow3_labor = mean(results["COW3_H2"]) - mean(results["COW3_H0"])
    print("labor_value", {"COW2_H2_minus_H0": cow2_labor, "COW3_H2_minus_H0": cow3_labor})


if __name__ == "__main__":
    main()
