#!/usr/bin/env python3
"""
FP001 — first-principles market microsimulator for Kaggriculture.

Purpose
-------
Analyze mechanics-derived strategies without using competitor replays, notebooks,
team identity, ratings, EpisodeIds, hidden seeds, or future/private opponent state.

The price curves and BUY/SELL quote conventions mirror kaggle-environments 1.32.7.
This is a research tool, not an agent.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Dict, Tuple

PRICE_FLOOR = 1
HINGE_GAIN = 8.0

MARKET_PARAMS: Dict[str, dict] = {
    "WHEAT": {"base": 25, "I0": 10_000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10_000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10_000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10_000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10_000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10_000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10_000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10_000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10_000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}


def _shape(name: str, x: float, T: float) -> float:
    if name == "linear":
        return x
    if name == "sq":
        return x * x
    if name == "sqrt":
        return math.sqrt(x)
    if name == "log":
        return math.log1p(x)
    if name == "log10":
        return math.log10(1.0 + x)
    if name == "hinge":
        if T <= 0:
            return x
        u = x / T
        return u + HINGE_GAIN * max(0.0, u - 1.0) ** 2
    raise ValueError(f"unknown curve: {name}")


def market_price(item: str, inventory: int) -> int:
    p = MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        func = p["below_func"]
        amp = p["below_target"] * base / _shape(func, T, T)
        value = base + amp * _shape(func, I0 - inventory, T)
    else:
        func = p["above_func"]
        amp = p["above_target"] * base / _shape(func, T, T)
        value = base - amp * _shape(func, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(value)))


def buy_product(item: str, inventory: int, qty: int) -> Tuple[int, int]:
    """BUY_PRODUCT quote is at post-buy inventory."""
    total = 0
    for _ in range(qty):
        quote = market_price(item, inventory - 1)
        total += quote
        inventory -= 1
    return total, inventory


def sell(item: str, inventory: int, qty: int) -> Tuple[int, int]:
    """SELL quote is at pre-sell inventory; $1 sales do not add supply."""
    total = 0
    for _ in range(qty):
        quote = market_price(item, inventory)
        total += quote
        if quote > PRICE_FLOOR:
            inventory += 1
    return total, inventory


@dataclass(frozen=True)
class CarryResult:
    qty: int
    town_demand: int
    buy_cost: int
    sell_revenue: int
    pnl: int
    ending_inventory: int


def wheat_town_carry(start_inventory: int, qty: int, town_demand: int) -> CarryResult:
    """Buy before a known town pulse, let town consume, then sell next opportunity."""
    cost, inv = buy_product("WHEAT", start_inventory, qty)
    inv -= town_demand
    revenue, inv = sell("WHEAT", inv, qty)
    return CarryResult(qty, town_demand, cost, revenue, revenue - cost, inv)


def no_demand_round_trip(start_inventory: int, qty: int) -> int:
    cost, inv = buy_product("WHEAT", start_inventory, qty)
    revenue, _ = sell("WHEAT", inv, qty)
    return revenue - cost


def premium_sell_denial(item: str, start_inventory: int, our_qty: int, opponent_qty: int) -> dict:
    """Diagnostic only: our sale is processed before a later opponent sale."""
    opp_baseline, _ = sell(item, start_inventory, opponent_qty)
    our_revenue, after_us = sell(item, start_inventory, our_qty)
    opp_after, ending = sell(item, after_us, opponent_qty)
    denied = opp_baseline - opp_after
    return {
        "item": item,
        "our_qty": our_qty,
        "opponent_qty": opponent_qty,
        "our_revenue": our_revenue,
        "opponent_revenue_denied": denied,
        "immediate_gap_effect": our_revenue + denied,
        "ending_inventory": ending,
    }


def self_test() -> None:
    for inv in (9_800, 10_000, 10_200):
        for qty in (1, 10, 50, 100):
            assert no_demand_round_trip(inv, qty) == 0, (inv, qty)
    for demand in (1, 2, 4, 7, 20, 100):
        r = wheat_town_carry(10_000, 50, demand)
        assert r.pnl >= 0, r
    r = premium_sell_denial("STRAWBERRY", 10_000, 10, 50)
    assert r["opponent_revenue_denied"] > 0, r


def print_default_scenarios() -> None:
    print("FP001 Kaggriculture first-principles market microsim")
    print("\nNo-demand WHEAT round-trip PnL (must be 0):")
    for q in (10, 50, 90):
        print(f"  q={q:3d}: {no_demand_round_trip(10_000, q):+d}")
    print("\nWHEAT town-pulse carry from I0=10000:")
    for q in (25, 50, 90):
        vals = []
        for d in (1, 2, 4, 7):
            r = wheat_town_carry(10_000, q, d)
            vals.append(f"D={d}: {r.pnl:+d}")
        print(f"  q={q:3d}: " + ", ".join(vals))
    print("\nSequential premium-sale denial diagnostic (ours first, opponent later; opp qty=50):")
    for item in ("STRAWBERRY", "MELON", "MILK", "WOOL"):
        r = premium_sell_denial(item, 10_000, 10, 50)
        print(f"  {item:10s}: our_rev={r['our_revenue']:5d}, opp_denied={r['opponent_revenue_denied']:5d}, immediate_gap={r['immediate_gap_effect']:5d}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("PASS")
    else:
        self_test()
        print_default_scenarios()


if __name__ == "__main__":
    main()
