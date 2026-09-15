#!/usr/bin/env python3
"""CR090 Phase 1 — H9 public-shop adaptive fifth-animal causal gate."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, stdev

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates.fp001_h9_adaptive_fifth_animal import (
    choose_h9_fifth,
    expected_remaining,
    first_shop,
    make_agent,
)
from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS, _get

SEEDS = tuple(range(90201, 90265))
STARTING_MONEY = 3000.0
MODES = ("DELAY_COW", "DELAY_SHEEP", "H9_ADAPT")
MILK_SHOPS = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}


def pass_agent(obs, config=None):
    player = int(_get(obs, "player", 0) or 0)
    farms = _get(obs, "farms", []) or []
    hands_n = len(_get(farms[player], "hands", []) or []) if player < len(farms) else 0
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hands_n)], "market": []}


def stable_hash(actions):
    payload = json.dumps(actions, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def intended_fifth(mode, shop):
    if mode == "DELAY_COW":
        return "COW"
    if mode == "DELAY_SHEEP":
        return "SHEEP"
    return choose_h9_fifth(shop)


def run_one(mode, seed, seat):
    fn = make_agent(mode)
    prefix = []
    full = []
    seen_shop = None
    orders = Counter()

    def wrapped(obs, config=None):
        nonlocal seen_shop
        shop = first_shop(obs)
        if shop is not None and seen_shop is None:
            seen_shop = shop

        action = fn(obs, config)
        frozen = json.loads(json.dumps(action))
        full.append(frozen)
        if len(prefix) < 72:
            prefix.append(frozen)

        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            op = str(order[0])
            item = str(order[1]) if len(order) >= 2 else ""
            try:
                qty = int(order[2]) if len(order) >= 3 else 1
            except Exception:
                qty = 0
            orders[f"{op}_{item}"] += qty
        return action

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

    fifth = None
    if ok:
        farm = env.state[seat].observation.farms[seat]
        x, y = TARGET_POSITIONS[4]
        tile = farm["tiles"][y][x]
        if isinstance(tile, dict):
            fifth = tile.get("animal")

    expected = intended_fifth(mode, seen_shop) if seen_shop is not None else None
    return {
        "ok": ok,
        "statuses": statuses,
        "delta": rewards[seat] - STARTING_MONEY if ok else float("nan"),
        "first_shop": seen_shop,
        "expected_fifth": expected,
        "final_fifth": fifth,
        "prefix_hash": stable_hash(prefix),
        "full_hash": stable_hash(full),
        "prefix_len": len(prefix),
        "buy_cow_qty": orders.get("BUY_ANIMAL_COW", 0),
        "buy_sheep_qty": orders.get("BUY_ANIMAL_SHEEP", 0),
        "sell_milk_qty": orders.get("SELL_MILK", 0),
        "sell_wool_qty": orders.get("SELL_WOOL", 0),
    }


def pct(xs, q):
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    pos = (len(vals) - 1) * float(q)
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def summarize(xs):
    vals = [float(x) for x in xs]
    if not vals:
        return {"n": 0}
    return {
        "n": len(vals),
        "mean": mean(vals),
        "median": median(vals),
        "p10": pct(vals, 0.10),
        "p25": pct(vals, 0.25),
        "p75": pct(vals, 0.75),
        "p90": pct(vals, 0.90),
        "min": min(vals),
        "max": max(vals),
    }


def compare(rows, left, right, keys):
    diffs = [rows[left][key]["delta"] - rows[right][key]["delta"] for key in keys]
    if not diffs:
        return {"summary": {"n": 0}, "signs": {"wins": 0, "ties": 0, "losses": 0}, "positive_rate": None, "ci95": None}
    se = stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) > 1 else 0.0
    mu = mean(diffs)
    wins = sum(x > 0 for x in diffs)
    ties = sum(x == 0 for x in diffs)
    losses = sum(x < 0 for x in diffs)
    return {
        "summary": summarize(diffs),
        "signs": {"wins": wins, "ties": ties, "losses": losses},
        "positive_rate": wins / len(diffs),
        "ci95": [mu - 1.96 * se, mu + 1.96 * se],
    }


def regime(shop):
    if shop == "YARN_STORE":
        return "YARN"
    if shop in MILK_SHOPS:
        return "MILK"
    return "NEUTRAL"


def main():
    rows = {mode: {} for mode in MODES}
    failures = 0

    for seed in SEEDS:
        for seat in (0, 1):
            key = (seed, seat)
            for mode in MODES:
                row = run_one(mode, seed, seat)
                rows[mode][key] = row
                failures += int(not row["ok"])
                print(
                    "CR090_CASE", mode, seed, seat,
                    "ok", row["ok"],
                    "shop", row["first_shop"],
                    "expected5", row["expected_fifth"],
                    "final5", row["final_fifth"],
                    "delta", row["delta"],
                )

    keys = [(seed, seat) for seed in SEEDS for seat in (0, 1)]
    regime_keys = defaultdict(list)
    shop_counts = Counter()
    prefix_parity = 0
    shop_parity = 0
    selector_exact = 0
    mechanics_exact = 0

    for key in keys:
        trio = [rows[mode][key] for mode in MODES]
        shops = [row["first_shop"] for row in trio]
        prefixes = [row["prefix_hash"] for row in trio]
        shop_ok = len(set(shops)) == 1 and shops[0] is not None
        prefix_ok = len(set(prefixes)) == 1 and all(row["prefix_len"] == 72 for row in trio)
        shop_parity += int(shop_ok)
        prefix_parity += int(prefix_ok)

        shop = shops[0] if shop_ok else None
        if shop is not None:
            shop_counts[shop] += 1
            regime_keys[regime(shop)].append(key)

        adapt = rows["H9_ADAPT"][key]
        if shop is not None:
            expected_mode = "DELAY_SHEEP" if choose_h9_fifth(shop) == "SHEEP" else "DELAY_COW"
            selector_exact += int(adapt["full_hash"] == rows[expected_mode][key]["full_hash"])

        all_mech = all(row["ok"] and row["expected_fifth"] == row["final_fifth"] for row in trio)
        mechanics_exact += int(all_mech)

    all_n = len(keys)
    first_shop_scores = {
        shop: expected_remaining(72, (shop,)) for shop in sorted(shop_counts)
    }

    yarn_vs_cow = compare(rows, "H9_ADAPT", "DELAY_COW", regime_keys["YARN"])
    milk_vs_sheep = compare(rows, "H9_ADAPT", "DELAY_SHEEP", regime_keys["MILK"])
    neutral_vs_sheep = compare(rows, "H9_ADAPT", "DELAY_SHEEP", regime_keys["NEUTRAL"])
    all_vs_cow = compare(rows, "H9_ADAPT", "DELAY_COW", keys)
    all_vs_sheep = compare(rows, "H9_ADAPT", "DELAY_SHEEP", keys)

    distributions = {
        mode: summarize([rows[mode][key]["delta"] for key in keys])
        for mode in MODES
    }

    mechanics_pass = (
        failures == 0
        and prefix_parity == all_n
        and shop_parity == all_n
        and selector_exact == all_n
        and mechanics_exact == all_n
    )
    support_pass = len(regime_keys["YARN"]) >= 8 and len(regime_keys["MILK"]) >= 16

    y = yarn_vs_cow
    m = milk_vs_sheep
    causal_pass = (
        mechanics_pass
        and support_pass
        and y["summary"].get("mean", float("-inf")) > 0.0
        and y["summary"].get("median", float("-inf")) > 0.0
        and (y["positive_rate"] or 0.0) >= 0.65
        and m["summary"].get("mean", float("-inf")) > 0.0
        and m["summary"].get("median", float("-inf")) > 0.0
        and (m["positive_rate"] or 0.0) >= 0.65
    )

    robustness_pass = (
        causal_pass
        and all_vs_cow["summary"].get("mean", float("-inf")) > 0.0
        and all_vs_cow["summary"].get("median", float("-inf")) >= 0.0
        and all_vs_sheep["summary"].get("mean", float("-inf")) > 0.0
    )

    if not causal_pass:
        decision = "CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION"
    elif not robustness_pass:
        decision = "CR090_H9_CAUSAL_PASS_NATURAL_FAIL_MOVE_HIERARCHICAL"
    else:
        decision = "CR090_H9_PHASE1_PASS_ADVANCE_M6S1_RETENTION"

    result = {
        "schema": "cr090-h9-adaptive-fifth-phase1-v1",
        "seeds": [SEEDS[0], SEEDS[-1]],
        "cases_per_policy": all_n,
        "policies": list(MODES),
        "failures": failures,
        "shop_counts": dict(sorted(shop_counts.items())),
        "regime_counts": {name: len(regime_keys[name]) for name in ("YARN", "MILK", "NEUTRAL")},
        "first_shop_expected_remaining": first_shop_scores,
        "checks": {
            "prefix_parity": [prefix_parity, all_n],
            "shop_parity": [shop_parity, all_n],
            "selector_exact_full_trajectory": [selector_exact, all_n],
            "mechanics_exact": [mechanics_exact, all_n],
            "mechanics_pass": mechanics_pass,
            "support_pass": support_pass,
            "causal_pass": causal_pass,
            "natural_robustness_pass": robustness_pass,
        },
        "distributions": distributions,
        "comparisons": {
            "YARN_adapt_minus_delayed_cow": yarn_vs_cow,
            "MILK_adapt_minus_delayed_sheep": milk_vs_sheep,
            "NEUTRAL_adapt_minus_delayed_sheep": neutral_vs_sheep,
            "ALL_adapt_minus_delayed_cow": all_vs_cow,
            "ALL_adapt_minus_delayed_sheep": all_vs_sheep,
        },
        "decision": decision,
        "automatic_submission": False,
        "held_out_touched": False,
    }

    outdir = ROOT / "artifacts"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "cr090_h9_phase1_result.json"
    outpath.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("CR090_H9_RESULT", json.dumps(result, sort_keys=True))
    print("CR090_H9_DECISION", decision)
    print("CR090_H9_COMPLETE")

    if failures or not mechanics_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
