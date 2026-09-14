#!/usr/bin/env python3
"""FP001 E3 — deterministic-town single-hand crop-density causal gate."""
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
MODULE_PATH = ROOT / "candidates" / "fp001_e3_single_hand_crop_density.py"
SEEDS = (69501, 69502)
STARTING_MONEY = 3000.0
N_COWS = 5
CARE_MODE = "DAILY"

TREATMENTS = (
    ("BASE", 0, 0),
    ("S1", 1, 0),
    ("S2", 2, 0),
    ("S4", 4, 0),
    ("M1", 0, 1),
    ("M2", 0, 2),
    ("M4", 0, 4),
    ("M6", 0, 6),
    ("M4S2", 2, 4),
    ("M6S1", 1, 6),
)


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_e3_frozen", MODULE_PATH)
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


def _tile_at(tiles, pos):
    x, y = pos
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def instrument(fn):
    stats = Counter()
    state = {"max_hands": 0}

    def wrapped(obs, config=None):
        player = int(_get(obs, "player", 0) or 0)
        farms = _get(obs, "farms", []) or []
        farm = farms[player] if player < len(farms) else {}
        tiles = _get(farm, "tiles", []) or []
        farmer_pos = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])
        hand_pos = [tuple(p) for p in (_get(farm, "hands", []) or [])]
        state["max_hands"] = max(state["max_hands"], len(hand_pos))

        action = fn(obs, config)
        main = action.get("farmer", ["PASS"])
        mop = main[0] if isinstance(main, list) and main else "PASS"
        stats[f"main_{mop}"] += 1
        mt = _tile_at(tiles, farmer_pos)
        if isinstance(mt, dict) and mt.get("animal") == "COW":
            stats[f"main_cow_{mop}"] += 1

        for idx, ha in enumerate(list(action.get("hands") or [])):
            op = ha[0] if isinstance(ha, list) and ha else "PASS"
            stats[f"hand_{op}"] += 1
            if idx < len(hand_pos):
                ht = _tile_at(tiles, hand_pos[idx])
                crop = ht.get("crop") if isinstance(ht, dict) and ht.get("kind") == "PLANT" else None
                if op == "PLANT" and len(ha) >= 2:
                    stats[f"hand_crop_{ha[1]}_PLANT"] += 1
                elif crop in {"STRAWBERRY", "MELON"} and op in {"WATER", "FERTILIZE", "HARVEST"}:
                    stats[f"hand_crop_{crop}_{op}"] += 1

        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            op = order[0]
            if op == "HIRE":
                stats["market_HIRE_orders"] += 1
                continue
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

    return wrapped, stats, state


def run_one(mod, treatment, seed, seat):
    label, n_s, n_m = treatment
    fn = mod.make_agent(N_COWS, CARE_MODE, n_s, n_m)
    wrapped, stats, state = instrument(fn)
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make(
        "kaggriculture",
        configuration={
            "episodeSteps": 720,
            "startingMoney": 3000,
            "seed": seed,
            "weedSpawnChance": 0,
            "townShopUnlockInterval": 999,
        },
        debug=True,
    )
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = [float(x) for x in j["rewards"]]
    assert statuses == ["DONE", "DONE"], (label, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS
    alive = 0
    for x, y in TARGET_POSITIONS[:N_COWS]:
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            alive += 1

    d = dict(stats)
    main_moves = sum(d.get(f"main_{x}", 0) for x in ("NORTH", "SOUTH", "EAST", "WEST"))
    hand_moves = sum(d.get(f"hand_{x}", 0) for x in ("NORTH", "SOUTH", "EAST", "WEST"))
    return {
        "delta": rewards[seat] - STARTING_MONEY,
        "alive": alive,
        "max_hands": state["max_hands"],
        "main_feed": d.get("main_FEED", 0),
        "main_care": d.get("main_CARE", 0),
        "main_moves": main_moves,
        "milk_sold": d.get("market_SELL_MILK_qty", 0),
        "fert_sold": d.get("market_SELL_FERTILIZER_qty", 0),
        "straw_sold": d.get("market_SELL_STRAWBERRY_qty", 0),
        "melon_sold": d.get("market_SELL_MELON_qty", 0),
        "straw_seed_bought": d.get("market_BUY_SEED_STRAWBERRY_qty", 0),
        "melon_seed_bought": d.get("market_BUY_SEED_MELON_qty", 0),
        "hires": d.get("market_HIRE_orders", 0),
        "hand_moves": hand_moves,
        "hand_pass": d.get("hand_PASS", 0),
        "hand_water": d.get("hand_WATER", 0),
        "hand_fertilize": d.get("hand_FERTILIZE", 0),
        "hand_harvest": d.get("hand_HARVEST", 0),
        "stats": d,
    }


def summary(xs):
    return {"n": len(xs), "mean": mean(xs), "median": median(xs), "min": min(xs), "max": max(xs)}


def paired(values, treatment, control="BASE"):
    keys = sorted(set(values[treatment]) & set(values[control]))
    rows = [(k, values[treatment][k]["delta"] - values[control][k]["delta"]) for k in keys]
    ds = [d for _, d in rows]
    return {
        "mean": mean(ds), "median": median(ds), "min": min(ds), "max": max(ds),
        "wins": sum(d > 0 for d in ds), "ties": sum(d == 0 for d in ds), "losses": sum(d < 0 for d in ds),
        "cases": [{"seed": k[0], "seat": k[1], "delta": d} for k, d in rows],
    }


def animal_fingerprint(row):
    return (row["main_feed"], row["main_care"], row["main_moves"], row["milk_sold"])


def main():
    mod = load_module()
    values = {label: {} for label, _, _ in TREATMENTS}

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for treatment in TREATMENTS:
                label = treatment[0]
                row = run_one(mod, treatment, seed, seat)
                values[label][key] = row
                print("CASE", label, seed, seat, row["delta"], "S", row["straw_sold"], "M", row["melon_sold"])

    print("E3_DENSITY_COMPLETE")
    for label, n_s, n_m in TREATMENTS:
        rows = list(values[label].values())
        print(label, summary([r["delta"] for r in rows]), {
            "full_cow_survival": f"{sum(r['alive'] == N_COWS for r in rows)}/{len(rows)}",
            "max_hands": max(r["max_hands"] for r in rows),
            "straw_sold_per_case": mean([r["straw_sold"] for r in rows]),
            "melon_sold_per_case": mean([r["melon_sold"] for r in rows]),
            "milk_sold_per_case": mean([r["milk_sold"] for r in rows]),
            "fert_sold_per_case": mean([r["fert_sold"] for r in rows]),
            "hires_per_case": mean([r["hires"] for r in rows]),
            "main_feed_per_case": mean([r["main_feed"] for r in rows]),
            "main_care_per_case": mean([r["main_care"] for r in rows]),
            "main_moves_per_case": mean([r["main_moves"] for r in rows]),
            "hand_moves_per_case": mean([r["hand_moves"] for r in rows]),
            "hand_pass_per_case": mean([r["hand_pass"] for r in rows]),
            "hand_water_per_case": mean([r["hand_water"] for r in rows]),
            "hand_fertilize_per_case": mean([r["hand_fertilize"] for r in rows]),
            "hand_harvest_per_case": mean([r["hand_harvest"] for r in rows]),
            "theoretical_straw": 8 * n_s,
            "theoretical_melon": 6 * n_m,
        })

    base = values["BASE"]
    eligible = []
    for label, n_s, n_m in TREATMENTS:
        if label == "BASE":
            continue
        p = paired(values, label)
        same_animal = all(animal_fingerprint(values[label][k]) == animal_fingerprint(base[k]) for k in base)
        survival = all(r["alive"] == N_COWS and r["max_hands"] <= 1 for r in values[label].values())
        print("PAIRED", label, p, "animal_exact", same_animal, "mechanical", survival)
        if p["losses"] == 0 and p["wins"] == len(base) and same_animal and survival:
            eligible.append((p["mean"], label, n_s + n_m))

    assert all(r["alive"] == N_COWS for rows in values.values() for r in rows.values())
    assert all(r["max_hands"] <= 1 for rows in values.values() for r in rows.values())

    eligible.sort(reverse=True)
    print("ELIGIBLE_RANKING", eligible)
    if eligible:
        print("E3_SELECTED_CAUSAL", eligible[0][1], eligible[0][0])
    else:
        print("E3_NO_ELIGIBLE_TREATMENT")
    print("E3_MECHANICAL_PASS")


if __name__ == "__main__":
    main()
