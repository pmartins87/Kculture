#!/usr/bin/env python3
"""FP001 E1 — paired one-STRAWBERRY marginal hybrid gate.

Controls and hybrids share identical seeds/seats. The only treatment is one early
STRAWBERRY using otherwise-idle main-farmer turns plus reservation/conversion of at
most two fertilizer units. This locates which B4 backbone has useful action headroom.
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
MODULE_PATH = ROOT / "candidates" / "fp001_e1_strawberry_hybrid.py"
SEEDS = list(range(68101, 68105))
STARTING_MONEY = 3000.0
ARCHS = (
    (4, "DAILY", 0),
    (4, "DAILY", 1),
    (5, "SURVIVAL", 0),
    (5, "SURVIVAL", 1),
    (5, "DAILY", 0),
    (5, "DAILY", 1),
)


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_e1", MODULE_PATH)
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


def instrument(fn, crop_positions):
    stats = Counter()
    crop_seen = {tuple(p): False for p in crop_positions}
    crop_failed = {tuple(p): False for p in crop_positions}

    def wrapped(obs, config=None):
        player = int(_get(obs, "player", 0) or 0)
        farms = _get(obs, "farms", []) or []
        farm = farms[player] if player < len(farms) else {}
        tiles = _get(farm, "tiles", []) or []
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        for pos in crop_seen:
            x, y = pos
            tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
                crop_seen[pos] = True
            elif crop_seen[pos] and isinstance(tile, dict) and tile.get("kind") == "WEED":
                crop_failed[pos] = True

        action = fn(obs, config)
        ua = action.get("farmer", ["PASS"])
        op = ua[0] if isinstance(ua, list) and ua else "PASS"
        stats[f"unit_{op}"] += 1

        fx, fy = farmer
        current_tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None
        if op == "PLANT" and len(ua) >= 2 and ua[1] == "STRAWBERRY":
            stats["crop_PLANT"] += 1
        elif op in {"WATER", "FERTILIZE", "HARVEST"}:
            if isinstance(current_tile, dict) and current_tile.get("kind") == "PLANT" and current_tile.get("crop") == "STRAWBERRY":
                stats[f"crop_{op}"] += 1
            elif isinstance(current_tile, dict) and current_tile.get("animal") == "COW":
                stats[f"cow_{op}"] += 1

        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            mop = order[0]
            item = order[1] if len(order) >= 2 else ""
            qty = 1
            if len(order) >= 3:
                try:
                    qty = int(order[2])
                except Exception:
                    qty = 0
            stats[f"market_{mop}_{item}_orders"] += 1
            stats[f"market_{mop}_{item}_qty"] += qty
        return action

    return wrapped, stats, crop_seen, crop_failed


def run_one(mod, arch, seed, seat):
    n_cows, mode, berries = arch
    crop_positions = mod.CROP_POSITIONS[:berries]
    wrapped, stats, seen, failed = instrument(mod.make_agent(*arch), crop_positions)
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed}, debug=True)
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = [float(x) for x in j["rewards"]]
    assert statuses == ["DONE", "DONE"], (arch, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    alive = 0
    from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS
    for x, y in TARGET_POSITIONS[:n_cows]:
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            alive += 1

    return {
        "delta": rewards[seat] - STARTING_MONEY,
        "alive": alive,
        "crop_seen": sum(bool(v) for v in seen.values()),
        "crop_failed": sum(bool(v) for v in failed.values()),
        "stats": dict(stats),
    }


def summary(xs):
    return {"n": len(xs), "mean": mean(xs), "median": median(xs), "min": min(xs), "max": max(xs)}


def paired(values, treatment, control):
    keys = sorted(set(values[treatment]) & set(values[control]))
    ds = [values[treatment][k]["delta"] - values[control][k]["delta"] for k in keys]
    return {
        "mean": mean(ds), "median": median(ds), "min": min(ds), "max": max(ds),
        "wins": sum(x > 0 for x in ds), "ties": sum(x == 0 for x in ds), "losses": sum(x < 0 for x in ds),
    }


def name(a):
    n, mode, berries = a
    return f"COW{n}_{mode}_S{berries}"


def main():
    mod = load_module()
    values = {a: {} for a in ARCHS}
    totals = {a: Counter() for a in ARCHS}

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for arch in ARCHS:
                out = run_one(mod, arch, seed, seat)
                values[arch][key] = out
                totals[arch].update(out["stats"])

    print("E1_STRAWBERRY_RUNTIME_COMPLETE")
    for arch in ARCHS:
        n_cows, mode, berries = arch
        rows = list(values[arch].values())
        ds = [r["delta"] for r in rows]
        st = totals[arch]
        print(name(arch), summary(ds), {
            "full_cow_survival": f"{sum(r['alive'] == n_cows for r in rows)}/{len(rows)}",
            "crop_seen": sum(r["crop_seen"] for r in rows),
            "crop_failed": sum(r["crop_failed"] for r in rows),
            "berries_sold": st.get("market_SELL_STRAWBERRY_qty", 0),
            "crop_plant": st.get("crop_PLANT", 0),
            "crop_water": st.get("crop_WATER", 0),
            "crop_fertilize": st.get("crop_FERTILIZE", 0),
            "crop_harvest": st.get("crop_HARVEST", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "feed": st.get("unit_FEED", 0),
            "care": st.get("unit_CARE", 0),
            "idle_pass": st.get("unit_PASS", 0),
            "moves": sum(st.get(f"unit_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
        })

    pairs = (
        ((4, "DAILY", 1), (4, "DAILY", 0)),
        ((5, "SURVIVAL", 1), (5, "SURVIVAL", 0)),
        ((5, "DAILY", 1), (5, "DAILY", 0)),
    )
    for treatment, control in pairs:
        print(f"paired_{name(treatment)}_minus_{name(control)}", paired(values, treatment, control))

    # Gate is informational: a treatment may lose because that is exactly the
    # action-headroom question. Mechanical validity and cow survival are required.
    for arch in ARCHS:
        n_cows, _, _ = arch
        assert all(r["alive"] == n_cows for r in values[arch].values()), (arch, values[arch])
    print("E1_STRAWBERRY_MECHANICAL_PASS")


if __name__ == "__main__":
    main()
