#!/usr/bin/env python3
"""FP001 H10 — paired COW scale + batch-harvest runtime gate.

Separates three effects on fresh seed/seat pairs:
1) B2 COW3/H0 -> new compact scheduler with the same harvest threshold 1;
2) threshold 1 -> threshold 6 at n=3 (pure batch-harvest effect within H10);
3) n=3 -> 4 -> 5 -> 6 under the same threshold-6 scheduler (scale effect).

No competitor data is used.  PASS is the opponent so the gate measures realized
own-economy mechanics/logistics.  Animal loss is recorded rather than hidden by a
hard assertion, allowing scale saturation to appear as evidence instead of merely
turning the workflow red.
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

B2_PATH = ROOT / "candidates" / "fp001_h8_multi_animal_module.py"
H10_PATH = ROOT / "candidates" / "fp001_h10_cow_scale_module.py"
SEEDS = list(range(66101, 66105))
STARTING_MONEY = 3000.0

ARCHS = {
    "B2_COW3": ("b2", 3, 1),
    "H10_COW3_T1": ("h10", 3, 1),
    "H10_COW3_T6": ("h10", 3, 6),
    "H10_COW4_T6": ("h10", 4, 6),
    "H10_COW5_T6": ("h10", 5, 6),
    "H10_COW6_T6": ("h10", 6, 6),
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
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
        for ua in units:
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


def make_arch_agent(b2, h10, kind, n, threshold):
    if kind == "b2":
        return b2.make_agent(tuple("COW" for _ in range(n)), hands_target=0), b2.TARGET_POSITIONS[:n]
    return h10.make_agent(n, harvest_threshold=threshold), h10.TARGET_POSITIONS[:n]


def run_one(b2, h10, arch_name, spec_tuple, seed, seat):
    kind, n, threshold = spec_tuple
    base, targets = make_arch_agent(b2, h10, kind, n, threshold)
    wrapped, stats = instrument(base)
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
    assert statuses == ["DONE", "DONE"], (arch_name, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY, (arch_name, seed, seat, rewards)

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    alive = 0
    for x, y in targets:
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            alive += 1

    private = env.state[seat].observation.private
    shed = private.get("shed", {}) if hasattr(private, "get") else {}
    stranded = {
        "MILK": int(shed.get("MILK", 0) or 0),
        "FERTILIZER": int(shed.get("FERTILIZER", 0) or 0),
        "WHEAT": int(shed.get("WHEAT", 0) or 0),
    }
    return {
        "delta": rewards[seat] - STARTING_MONEY,
        "alive": alive,
        "target": n,
        "stranded": stranded,
        "stats": dict(stats),
    }


def summary(xs):
    return {
        "n": len(xs),
        "mean": mean(xs),
        "median": median(xs),
        "min": min(xs),
        "max": max(xs),
    }


def paired(values, a, b):
    keys = sorted(set(values[a]) & set(values[b]))
    diffs = [values[a][k]["delta"] - values[b][k]["delta"] for k in keys]
    return {
        "mean": mean(diffs),
        "median": median(diffs),
        "min": min(diffs),
        "max": max(diffs),
        "wins": sum(d > 0 for d in diffs),
        "ties": sum(d == 0 for d in diffs),
        "losses": sum(d < 0 for d in diffs),
    }


def main():
    b2 = load_module("fp001_b2", B2_PATH)
    h10 = load_module("fp001_h10", H10_PATH)

    values = {name: {} for name in ARCHS}
    totals = {name: Counter() for name in ARCHS}

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for name, spec_tuple in ARCHS.items():
                out = run_one(b2, h10, name, spec_tuple, seed, seat)
                values[name][key] = out
                totals[name].update(out["stats"])

    print("H10_COW_SCALE_RUNTIME_COMPLETE")
    for name, (_, target_n, threshold) in ARCHS.items():
        rows = list(values[name].values())
        deltas = [r["delta"] for r in rows]
        alive_counts = [r["alive"] for r in rows]
        st = totals[name]
        full_survival = sum(r["alive"] == r["target"] for r in rows)
        positive = sum(r["delta"] > 0 for r in rows)
        print(name, summary(deltas), {
            "target_cows": target_n,
            "harvest_threshold": threshold,
            "full_survival": f"{full_survival}/{len(rows)}",
            "min_alive": min(alive_counts),
            "positive": f"{positive}/{len(rows)}",
            "per_cow_mean_delta": round(mean(deltas) / target_n, 3),
        })
        print("  key_stats", {
            "cow_bought": st.get("market_BUY_ANIMAL_COW_qty", 0),
            "wheat_bought": st.get("market_BUY_PRODUCT_WHEAT_qty", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "feed": st.get("unit_FEED", 0),
            "fert_collect": st.get("unit_COLLECT_FERTILIZER", 0),
            "harvest": st.get("unit_HARVEST", 0),
            "pickup": st.get("unit_PICKUP", 0),
            "build": st.get("unit_BUILD_PASTURE", 0),
            "place": st.get("unit_PLACE", 0),
            "moves": sum(st.get(f"unit_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
        })

    print("paired_H10_COW3_T1_minus_B2_COW3", paired(values, "H10_COW3_T1", "B2_COW3"))
    print("paired_H10_COW3_T6_minus_T1", paired(values, "H10_COW3_T6", "H10_COW3_T1"))
    print("paired_H10_COW4_minus_COW3", paired(values, "H10_COW4_T6", "H10_COW3_T6"))
    print("paired_H10_COW5_minus_COW4", paired(values, "H10_COW5_T6", "H10_COW4_T6"))
    print("paired_H10_COW6_minus_COW5", paired(values, "H10_COW6_T6", "H10_COW5_T6"))

    ranking = sorted(ARCHS, key=lambda n: mean([r["delta"] for r in values[n].values()]), reverse=True)
    print("mean_delta_ranking", [(n, mean([r["delta"] for r in values[n].values()])) for n in ranking])


if __name__ == "__main__":
    main()
