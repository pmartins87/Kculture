#!/usr/bin/env python3
"""FP001 E2 — paired labor revaluation with one dedicated STRAWBERRY hand."""
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
MODULE_PATH = ROOT / "candidates" / "fp001_e2_dedicated_strawberry_hand.py"
SEEDS = list(range(69201, 69205))
STARTING_MONEY = 3000.0
# n_cows, care_mode, strawberry, dedicated_hand
ARCHS = (
    (4, "DAILY", False, False),
    (4, "DAILY", True, False),
    (4, "DAILY", True, True),
    (5, "SURVIVAL", False, False),
    (5, "SURVIVAL", True, False),
    (5, "SURVIVAL", True, True),
    (5, "DAILY", False, False),
    (5, "DAILY", True, False),
    (5, "DAILY", True, True),
)


def load_module():
    spec = importlib.util.spec_from_file_location("fp001_e2", MODULE_PATH)
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


def instrument(fn, crop_pos):
    stats = Counter()
    crop_seen = False
    crop_failed = False

    def wrapped(obs, config=None):
        nonlocal crop_seen, crop_failed
        player = int(_get(obs, "player", 0) or 0)
        farms = _get(obs, "farms", []) or []
        farm = farms[player] if player < len(farms) else {}
        tiles = _get(farm, "tiles", []) or []
        farmer_pos = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])
        hand_pos = [tuple(p) for p in (_get(farm, "hands", []) or [])]

        ct = _tile_at(tiles, crop_pos)
        if isinstance(ct, dict) and ct.get("kind") == "PLANT" and ct.get("crop") == "STRAWBERRY":
            crop_seen = True
        elif crop_seen and isinstance(ct, dict) and ct.get("kind") == "WEED":
            crop_failed = True

        action = fn(obs, config)

        # Main-farmer actions: this should remain the animal backbone.
        ua = action.get("farmer", ["PASS"])
        op = ua[0] if isinstance(ua, list) and ua else "PASS"
        stats[f"main_{op}"] += 1
        mtile = _tile_at(tiles, farmer_pos)
        if op in {"FEED", "CARE", "HARVEST", "COLLECT_FERTILIZER"} and isinstance(mtile, dict) and mtile.get("animal") == "COW":
            stats[f"cow_{op}"] += 1

        # Hand actions and crop attribution based on each hand's current tile.
        hand_actions = list(action.get("hands") or [])
        for idx, ha in enumerate(hand_actions):
            hop = ha[0] if isinstance(ha, list) and ha else "PASS"
            stats[f"hand_{hop}"] += 1
            if idx >= len(hand_pos):
                continue
            htile = _tile_at(tiles, hand_pos[idx])
            if hop == "PLANT" and len(ha) >= 2 and ha[1] == "STRAWBERRY":
                stats["crop_PLANT"] += 1
            elif hop in {"WATER", "FERTILIZE", "HARVEST"}:
                if isinstance(htile, dict) and htile.get("kind") == "PLANT" and htile.get("crop") == "STRAWBERRY":
                    stats[f"crop_{hop}"] += 1

        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            mop = order[0]
            if mop == "HIRE":
                stats["market_HIRE_orders"] += 1
                continue
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

    def flags():
        return crop_seen, crop_failed

    return wrapped, stats, flags


def run_one(mod, arch, seed, seat):
    n_cows, mode, strawberry, hand = arch
    wrapped, stats, flags = instrument(mod.make_agent(*arch), mod.CROP_POS)
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
    assert statuses == ["DONE", "DONE"], (arch, seed, seat, statuses)
    assert rewards[1 - seat] == STARTING_MONEY

    obs = env.state[seat].observation
    farm = obs.farms[seat]
    from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS
    alive = 0
    for x, y in TARGET_POSITIONS[:n_cows]:
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict) and tile.get("animal") == "COW":
            alive += 1

    seen, failed = flags()
    return {
        "delta": rewards[seat] - STARTING_MONEY,
        "alive": alive,
        "crop_seen": int(seen),
        "crop_failed": int(failed),
        "stats": dict(stats),
    }


def summary(xs):
    return {"n": len(xs), "mean": mean(xs), "median": median(xs), "min": min(xs), "max": max(xs)}


def paired(values, treatment, control):
    keys = sorted(set(values[treatment]) & set(values[control]))
    ds = [values[treatment][k]["delta"] - values[control][k]["delta"] for k in keys]
    return {
        "mean": mean(ds),
        "median": median(ds),
        "min": min(ds),
        "max": max(ds),
        "wins": sum(x > 0 for x in ds),
        "ties": sum(x == 0 for x in ds),
        "losses": sum(x < 0 for x in ds),
    }


def name(a):
    n, mode, strawberry, hand = a
    return f"COW{n}_{mode}_S{int(strawberry)}H{int(hand)}"


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

    print("E2_DEDICATED_HAND_RUNTIME_COMPLETE")
    for arch in ARCHS:
        n_cows, _, _, _ = arch
        rows = list(values[arch].values())
        st = totals[arch]
        ds = [r["delta"] for r in rows]
        print(name(arch), summary(ds), {
            "full_cow_survival": f"{sum(r['alive'] == n_cows for r in rows)}/{len(rows)}",
            "crop_seen": sum(r["crop_seen"] for r in rows),
            "crop_failed": sum(r["crop_failed"] for r in rows),
            "hire_orders": st.get("market_HIRE_orders", 0),
            "berries_sold": st.get("market_SELL_STRAWBERRY_qty", 0),
            "crop_plant": st.get("crop_PLANT", 0),
            "crop_water": st.get("crop_WATER", 0),
            "crop_fertilize": st.get("crop_FERTILIZE", 0),
            "crop_harvest": st.get("crop_HARVEST", 0),
            "fert_sold": st.get("market_SELL_FERTILIZER_qty", 0),
            "milk_sold": st.get("market_SELL_MILK_qty", 0),
            "main_feed": st.get("main_FEED", 0),
            "main_care": st.get("main_CARE", 0),
            "main_moves": sum(st.get(f"main_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
            "hand_moves": sum(st.get(f"hand_{d}", 0) for d in ("NORTH", "SOUTH", "EAST", "WEST")),
            "hand_pass": st.get("hand_PASS", 0),
        })

    # For each backbone: labor effect within crop treatment, then total module vs animal control.
    backbones = ((4, "DAILY"), (5, "SURVIVAL"), (5, "DAILY"))
    for n_cows, mode in backbones:
        base = (n_cows, mode, False, False)
        no_hand = (n_cows, mode, True, False)
        with_hand = (n_cows, mode, True, True)
        print(f"paired_{name(with_hand)}_minus_{name(no_hand)}", paired(values, with_hand, no_hand))
        print(f"paired_{name(with_hand)}_minus_{name(base)}", paired(values, with_hand, base))
        print(f"paired_{name(no_hand)}_minus_{name(base)}", paired(values, no_hand, base))

    # Mechanical gate: every architecture must preserve all expected cows.
    for arch in ARCHS:
        n_cows, _, _, _ = arch
        assert all(r["alive"] == n_cows for r in values[arch].values()), (arch, values[arch])

    print("E2_DEDICATED_HAND_MECHANICAL_PASS")


if __name__ == "__main__":
    main()
