#!/usr/bin/env python3
"""FP001 E4 — normal-environment robustness of frozen M6S1 vs COW5_DAILY."""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median, stdev

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates.fp001_e3_single_hand_crop_density import make_agent

SEEDS = tuple(range(69601, 69641))
STARTING_MONEY = 3000.0
POLICIES = {
    "BASE": (0, 0),
    "M6S1": (1, 6),
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
        for ha in list(action.get("hands") or []):
            hop = ha[0] if isinstance(ha, list) and ha else "PASS"
            stats[f"hand_{hop}"] += 1
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
            stats[f"market_{mop}_{item}_qty"] += qty
            stats[f"market_{mop}_{item}_orders"] += 1
        return action

    return wrapped, stats


def run_one(label, n_s, n_m, seed, seat):
    wrapped, stats = instrument(make_agent(5, "DAILY", n_s, n_m))
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make(
        "kaggriculture",
        configuration={
            "episodeSteps": 720,
            "startingMoney": 3000,
            "seed": seed,
        },
        debug=True,
    )
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = [float(x) for x in j["rewards"]]
    ok = statuses == ["DONE", "DONE"]

    alive = 0
    if ok:
        obs = env.state[seat].observation
        farm = obs.farms[seat]
        from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS
        for x, y in TARGET_POSITIONS[:5]:
            tile = farm["tiles"][y][x]
            if isinstance(tile, dict) and tile.get("animal") == "COW":
                alive += 1

    d = dict(stats)
    main_moves = sum(d.get(f"main_{x}", 0) for x in ("NORTH", "SOUTH", "EAST", "WEST"))
    return {
        "ok": ok,
        "statuses": statuses,
        "delta": (rewards[seat] - STARTING_MONEY) if ok else float("nan"),
        "alive": alive,
        "main_feed": d.get("main_FEED", 0),
        "main_care": d.get("main_CARE", 0),
        "main_moves": main_moves,
        "milk_sold": d.get("market_SELL_MILK_qty", 0),
        "fert_sold": d.get("market_SELL_FERTILIZER_qty", 0),
        "straw_sold": d.get("market_SELL_STRAWBERRY_qty", 0),
        "melon_sold": d.get("market_SELL_MELON_qty", 0),
        "hires": d.get("market_HIRE_orders", 0),
        "hand_pass": d.get("hand_PASS", 0),
    }


def percentile(xs, q):
    vals = sorted(float(x) for x in xs)
    if not vals:
        return float("nan")
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * float(q)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def dist_summary(xs):
    vals = list(xs)
    return {
        "n": len(vals),
        "mean": mean(vals),
        "median": median(vals),
        "p10": percentile(vals, 0.10),
        "p25": percentile(vals, 0.25),
        "p75": percentile(vals, 0.75),
        "p90": percentile(vals, 0.90),
        "min": min(vals),
        "max": max(vals),
    }


def main():
    values = {name: {} for name in POLICIES}
    failure_count = 0

    for seed in SEEDS:
        for seat in (0, 1):
            for label, (n_s, n_m) in POLICIES.items():
                row = run_one(label, n_s, n_m, seed, seat)
                values[label][(seed, seat)] = row
                if not row["ok"]:
                    failure_count += 1
                print(
                    "CASE", label, seed, seat,
                    "ok", row["ok"],
                    "delta", row["delta"],
                    "alive", row["alive"],
                    "milk", row["milk_sold"],
                    "M", row["melon_sold"],
                    "S", row["straw_sold"],
                )

    if failure_count:
        print("E4_MECHANICAL_FAILURES", failure_count)
        print("E4_DECISION STRONG_FAIL")
        return

    # Average both seats first: one episode seed is the statistical unit.
    seed_values = {label: {} for label in POLICIES}
    for label in POLICIES:
        for seed in SEEDS:
            rows = [values[label][(seed, 0)], values[label][(seed, 1)]]
            seed_values[label][seed] = mean(r["delta"] for r in rows)

    base_x = list(seed_values["BASE"].values())
    cand_x = list(seed_values["M6S1"].values())
    diffs = [seed_values["M6S1"][s] - seed_values["BASE"][s] for s in SEEDS]

    base_summary = dist_summary(base_x)
    cand_summary = dist_summary(cand_x)
    diff_summary = dist_summary(diffs)
    se = stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) > 1 else 0.0
    ci95 = (mean(diffs) - 1.96 * se, mean(diffs) + 1.96 * se)

    animal_exact_cases = 0
    candidate_survival_cases = 0
    crop_full_cases = 0
    for seed in SEEDS:
        for seat in (0, 1):
            b = values["BASE"][(seed, seat)]
            c = values["M6S1"][(seed, seat)]
            bf = (b["main_feed"], b["main_care"], b["main_moves"], b["milk_sold"])
            cf = (c["main_feed"], c["main_care"], c["main_moves"], c["milk_sold"])
            animal_exact_cases += int(bf == cf)
            candidate_survival_cases += int(c["alive"] == 5)
            crop_full_cases += int(c["melon_sold"] == 36 and c["straw_sold"] == 8)

    total_cases = len(SEEDS) * 2
    p10_gap = cand_summary["p10"] - base_summary["p10"]
    wins = sum(d > 0 for d in diffs)
    ties = sum(d == 0 for d in diffs)
    losses = sum(d < 0 for d in diffs)

    print("E4_BASE_DISTRIBUTION", base_summary)
    print("E4_M6S1_DISTRIBUTION", cand_summary)
    print("E4_SEED_LEVEL_DIFF", diff_summary)
    print("E4_DIFF_CI95", {"se": se, "lo": ci95[0], "hi": ci95[1]})
    print("E4_DIFF_SIGNS", {"wins": wins, "ties": ties, "losses": losses})
    print("E4_P10_GAP", p10_gap)
    print("E4_MECHANICS", {
        "candidate_survival": f"{candidate_survival_cases}/{total_cases}",
        "animal_exact_fingerprint": f"{animal_exact_cases}/{total_cases}",
        "full_crop_output": f"{crop_full_cases}/{total_cases}",
    })

    strong_pass = (
        candidate_survival_cases == total_cases
        and animal_exact_cases == total_cases
        and mean(diffs) >= 2000.0
        and median(diffs) > 0.0
        and ci95[0] > 0.0
        and p10_gap >= -2000.0
    )
    strong_fail = (
        mean(diffs) <= 0.0
        or median(diffs) <= -2000.0
        or candidate_survival_cases < total_cases
    )

    if strong_pass:
        decision = "STRONG_PASS"
    elif strong_fail:
        decision = "STRONG_FAIL"
    else:
        decision = "INCONCLUSIVE_EXTEND_TO_96"
    print("E4_DECISION", decision)
    print("E4_COMPLETE")


if __name__ == "__main__":
    main()
