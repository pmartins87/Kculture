#!/usr/bin/env python3
"""FP001 H8 Gate B1 — full-engine single-animal logistics proof.

Runs the zero-lineage single-animal module for GOOSE/COW/SHEEP, both seats and
fresh seeds.  PASS opponent isolates whether a complete legal logistics chain
can realize positive money after setup, feed, collection, harvest and sale.

This is not a population-strength test.
"""
from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "candidates" / "fp001_h8_single_animal_module.py"
SEEDS = list(range(63001, 63005))
SPECIES = ("GOOSE", "COW", "SHEEP")
STARTING_MONEY = 3000.0


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_h8_single", MODULE_PATH)
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
        farmer = action.get("farmer", ["PASS"])
        if isinstance(farmer, list) and farmer:
            stats[f"unit_{farmer[0]}"] += 1
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


def run_one(mod, species: str, seed: int, seat: int):
    wrapped, stats = instrument(mod.make_agent(species))
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
    assert statuses == ["DONE", "DONE"], (species, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY, (species, seed, seat, rewards)

    s = env.state[seat]
    obs = s.observation
    farm = obs.farms[seat]
    private = obs.private
    x, y = farm["farmer"]
    tile = farm["tiles"][y][x]
    alive = isinstance(tile, dict) and tile.get("animal") == species
    assert alive, (species, seed, seat, tile, dict(stats))

    # Final carried inventory should have been dropped/liquidated by the terminal
    # sequence; allow WHEAT=0 and other zero-valued dict entries only.
    main_inv = private["inventories"][0] if private.get("inventories") else {}
    stranded = {k: int(v) for k, v in main_inv.items() if int(v) > 0}
    assert not stranded, (species, seed, seat, stranded)

    delta = rewards[seat] - STARTING_MONEY
    return delta, dict(stats), dict(private["shed"])


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
    by_species = {}
    aggregate_stats = {}
    final_sheds = {}

    for species in SPECIES:
        deltas = []
        stats_total = Counter()
        sheds = []
        for seed in SEEDS:
            for seat in (0, 1):
                delta, stats, shed = run_one(mod, species, seed, seat)
                deltas.append(delta)
                stats_total.update(stats)
                sheds.append(shed)
        by_species[species] = deltas
        aggregate_stats[species] = dict(stats_total)
        final_sheds[species] = sheds

        assert min(deltas) > 0, (species, summary(deltas))
        assert stats_total[f"market_BUY_ANIMAL_{species}_qty"] == len(deltas), stats_total
        assert stats_total["unit_PLACE"] == len(deltas), stats_total
        assert stats_total["unit_COLLECT_FERTILIZER"] > 0, stats_total
        assert stats_total["unit_FEED"] > 0, stats_total

    print("H8_SINGLE_ANIMAL_RUNTIME_PASS")
    for species in SPECIES:
        print(species, summary(by_species[species]))
        st = aggregate_stats[species]
        keys = [
            f"market_BUY_ANIMAL_{species}_qty",
            "market_BUY_PRODUCT_WHEAT_qty",
            "market_SELL_FERTILIZER_qty",
            f"market_SELL_{mod.ANIMAL_META[species]['product']}_qty",
            "unit_COLLECT_FERTILIZER",
            "unit_HARVEST",
            "unit_PICKUP",
            "unit_FEED",
            "unit_DROP",
        ]
        print("  actions/orders", {k: st.get(k, 0) for k in keys})
        positive_final = []
        for shed in final_sheds[species]:
            positive_final.append({k: int(v) for k, v in shed.items() if int(v) > 0})
        print("  final_positive_shed", positive_final[:2])

    ranking = sorted(SPECIES, key=lambda s: mean(by_species[s]), reverse=True)
    print("runtime_mean_delta_ranking", [(s, mean(by_species[s])) for s in ranking])


if __name__ == "__main__":
    main()
