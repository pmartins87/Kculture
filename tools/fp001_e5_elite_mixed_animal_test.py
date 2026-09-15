#!/usr/bin/env python3
"""FP001 E5 — fixed elite COW/SHEEP composition transfer gate."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median, stdev

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates.fp001_e5_elite_mixed_animal import make_agent
from candidates.fp001_e3_single_hand_crop_density import make_agent as make_e4_agent
from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS

SEEDS = tuple(range(69701, 69733))
STARTING_MONEY = 3000.0
FAMILIES = {
    "C5": ("COW", "COW", "COW", "COW", "COW"),
    "C3S2": ("COW", "COW", "COW", "SHEEP", "SHEEP"),
    "C2S3": ("COW", "COW", "SHEEP", "SHEEP", "SHEEP"),
}
POLICIES = {
    f"{family}_{suffix}": (species, crop)
    for family, species in FAMILIES.items()
    for suffix, crop in (("BASE", False), ("M6S1", True))
}


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
        main = action.get("farmer", ["PASS"])
        op = main[0] if isinstance(main, list) and main else "PASS"
        stats[f"main_{op}"] += 1
        for hand in list(action.get("hands") or []):
            hop = hand[0] if isinstance(hand, list) and hand else "PASS"
            stats[f"hand_{hop}"] += 1
        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            mop = order[0]
            if mop == "HIRE":
                stats["market_HIRE_orders"] += 1
                continue
            item = order[1] if len(order) >= 2 else ""
            try:
                qty = int(order[2]) if len(order) >= 3 else 1
            except Exception:
                qty = 0
            stats[f"market_{mop}_{item}_qty"] += qty
        return action

    return wrapped, stats


def run_one(label, species, crop, seed, seat):
    wrapped, stats = instrument(make_agent(species, "DAILY", 1 if crop else 0, 6 if crop else 0))
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed},
        debug=True,
    )
    env.run(agents)
    payload = env.toJSON()
    statuses = list(payload["statuses"])
    rewards = [float(x) for x in payload["rewards"]]
    ok = statuses == ["DONE", "DONE"]

    correct = 0
    if ok:
        farm = env.state[seat].observation.farms[seat]
        for pos, wanted in zip(TARGET_POSITIONS[:5], species):
            x, y = pos
            tile = farm["tiles"][y][x]
            if isinstance(tile, dict) and tile.get("animal") == wanted:
                correct += 1

    d = dict(stats)
    main_moves = sum(d.get(f"main_{x}", 0) for x in ("NORTH", "SOUTH", "EAST", "WEST"))
    return {
        "ok": ok,
        "statuses": statuses,
        "delta": rewards[seat] - STARTING_MONEY if ok else float("nan"),
        "correct_animals": correct,
        "main_feed": d.get("main_FEED", 0),
        "main_care": d.get("main_CARE", 0),
        "main_moves": main_moves,
        "milk_sold": d.get("market_SELL_MILK_qty", 0),
        "wool_sold": d.get("market_SELL_WOOL_qty", 0),
        "fert_sold": d.get("market_SELL_FERTILIZER_qty", 0),
        "melon_sold": d.get("market_SELL_MELON_qty", 0),
        "straw_sold": d.get("market_SELL_STRAWBERRY_qty", 0),
        "hires": d.get("market_HIRE_orders", 0),
    }


def trace_one(fn, seed, seat):
    actions = []

    def traced(obs, config=None):
        action = fn(obs, config)
        actions.append(json.loads(json.dumps(action)))
        return action

    agents = [traced, pass_agent] if seat == 0 else [pass_agent, traced]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed},
        debug=True,
    )
    env.run(agents)
    payload = env.toJSON()
    return {
        "actions": actions,
        "statuses": list(payload["statuses"]),
        "rewards": [float(x) for x in payload["rewards"]],
    }


def percentile(xs, q):
    vals = sorted(float(x) for x in xs)
    pos = (len(vals) - 1) * float(q)
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def summary(xs):
    vals = list(xs)
    return {
        "n": len(vals), "mean": mean(vals), "median": median(vals),
        "p10": percentile(vals, 0.10), "p25": percentile(vals, 0.25),
        "p75": percentile(vals, 0.75), "p90": percentile(vals, 0.90),
        "min": min(vals), "max": max(vals),
    }


def comparison(a, b):
    diffs = [x - y for x, y in zip(a, b)]
    se = stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) > 1 else 0.0
    return {
        "summary": summary(diffs),
        "ci95": (mean(diffs) - 1.96 * se, mean(diffs) + 1.96 * se),
        "signs": {"wins": sum(x > 0 for x in diffs), "ties": sum(x == 0 for x in diffs), "losses": sum(x < 0 for x in diffs)},
    }


def main():
    # The generic species scheduler must preserve the exact frozen E4 COW5
    # behavior before any mixed-species result is admissible.
    parity = 0
    for crop in (False, True):
        for seat in (0, 1):
            old = trace_one(make_e4_agent(5, "DAILY", 1 if crop else 0, 6 if crop else 0), 69700, seat)
            new = trace_one(make_agent(FAMILIES["C5"], "DAILY", 1 if crop else 0, 6 if crop else 0), 69700, seat)
            ok = old == new
            parity += int(ok)
            print("E5_C5_PARITY_CASE", {"crop": crop, "seat": seat, "exact": ok})
    print("E5_C5_PARITY", {"exact": parity, "total": 4})
    if parity != 4:
        print("E5_DECISION INFRASTRUCTURE_FAIL_C5_NOT_E4_EXACT")
        return

    rows = {label: {} for label in POLICIES}
    failures = 0
    for seed in SEEDS:
        for seat in (0, 1):
            for label, (species, crop) in POLICIES.items():
                row = run_one(label, species, crop, seed, seat)
                rows[label][(seed, seat)] = row
                failures += int(not row["ok"])
                print("CASE", label, seed, seat, "ok", row["ok"], "delta", row["delta"], "animals", row["correct_animals"], "milk", row["milk_sold"], "wool", row["wool_sold"], "M", row["melon_sold"], "S", row["straw_sold"])

    if failures:
        print("E5_MECHANICAL_FAILURES", failures)
        print("E5_DECISION STRONG_FAIL")
        return

    seed_values = {label: [] for label in POLICIES}
    for label in POLICIES:
        for seed in SEEDS:
            seed_values[label].append(mean(rows[label][(seed, seat)]["delta"] for seat in (0, 1)))
        print("E5_DISTRIBUTION", label, summary(seed_values[label]))

    mechanics = {}
    transfer = {}
    for family in FAMILIES:
        base_label, hybrid_label = f"{family}_BASE", f"{family}_M6S1"
        correct = crop_full = fingerprint = 0
        for seed in SEEDS:
            for seat in (0, 1):
                base = rows[base_label][(seed, seat)]
                hybrid = rows[hybrid_label][(seed, seat)]
                correct += int(hybrid["correct_animals"] == 5)
                crop_full += int(hybrid["melon_sold"] == 36 and hybrid["straw_sold"] == 8)
                base_fp = (base["main_feed"], base["main_care"], base["main_moves"], base["milk_sold"], base["wool_sold"])
                hybrid_fp = (hybrid["main_feed"], hybrid["main_care"], hybrid["main_moves"], hybrid["milk_sold"], hybrid["wool_sold"])
                fingerprint += int(base_fp == hybrid_fp)
        mechanics[family] = {"correct_animals": correct, "crop_full": crop_full, "fingerprint": fingerprint, "total": len(SEEDS) * 2}
        transfer[family] = comparison(seed_values[hybrid_label], seed_values[base_label])
        transfer[family]["p10_gap"] = summary(seed_values[hybrid_label])["p10"] - summary(seed_values[base_label])["p10"]
        print("E5_MECHANICS", family, mechanics[family])
        print("E5_CROP_TRANSFER", family, transfer[family])

    versus_c5 = {}
    for family in ("C3S2", "C2S3"):
        versus_c5[family] = comparison(seed_values[f"{family}_M6S1"], seed_values["C5_M6S1"])
        versus_c5[family]["p10_gap"] = summary(seed_values[f"{family}_M6S1"])["p10"] - summary(seed_values["C5_M6S1"])["p10"]
        print("E5_MIXED_VS_C5", family, versus_c5[family])

    total = len(SEEDS) * 2
    eligible = {}
    transfer_pass = {}
    for family in ("C3S2", "C2S3"):
        m = mechanics[family]
        t = transfer[family]
        eligible[family] = m["correct_animals"] == total and m["crop_full"] == total and m["fingerprint"] == total
        transfer_pass[family] = (
            eligible[family]
            and t["summary"]["mean"] >= 2000.0
            and t["summary"]["median"] > 0.0
            and t["ci95"][0] > 0.0
            and t["p10_gap"] >= -2000.0
        )

    economic = [
        family for family in ("C3S2", "C2S3")
        if transfer_pass[family]
        and versus_c5[family]["summary"]["mean"] > 0.0
        and versus_c5[family]["summary"]["median"] > 0.0
        and versus_c5[family]["ci95"][0] > 0.0
    ]
    if economic:
        best = max(economic, key=lambda family: summary(seed_values[f"{family}_M6S1"])["mean"])
        decision = f"PROMOTE_{best}_PRIMARY"
    else:
        retain = [
            family for family in ("C3S2", "C2S3")
            if transfer_pass[family]
            and versus_c5[family]["summary"]["mean"] >= -4000.0
            and versus_c5[family]["summary"]["median"] >= -4000.0
            and versus_c5[family]["p10_gap"] >= -5000.0
        ]
        if retain:
            best = max(retain, key=lambda family: summary(seed_values[f"{family}_M6S1"])["mean"])
            decision = f"RETAIN_{best}_POPULATION_CHALLENGER"
        else:
            decision = "MIXED_FIXED_FAIL_KEEP_C5_M6S1"

    print("E5_ELIGIBLE", eligible)
    print("E5_TRANSFER_PASS", transfer_pass)
    print("E5_DECISION", decision)
    print("E5_COMPLETE")


if __name__ == "__main__":
    main()
