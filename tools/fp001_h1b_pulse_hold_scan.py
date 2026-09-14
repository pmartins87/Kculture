#!/usr/bin/env python3
"""FP001 H1B — first-principles scan for delaying sale across town demand.

Compare two counterfactuals with identical starting market inventory and own
quantity, no opponent market intervention between them:

A) SELL now, then town consumes D.
B) Town consumes D, then SELL next turn.

When sell prices are above the $1 floor, both paths end with the same market
inventory.  Any revenue difference is therefore pure timing value from the
exogenous town pulse, not a changed terminal market state.
"""
from __future__ import annotations

from fp001_market_microsim import MARKET_PARAMS, PRICE_FLOOR, sell

PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")


def pulse_hold_gain(item: str, start_inventory: int, qty: int, demand: int) -> dict:
    immediate_revenue, immediate_after_sale = sell(item, start_inventory, qty)
    immediate_end = immediate_after_sale - demand

    depleted_inventory = start_inventory - demand
    delayed_revenue, delayed_end = sell(item, depleted_inventory, qty)

    return {
        "item": item,
        "start_inventory": start_inventory,
        "qty": qty,
        "demand": demand,
        "immediate_revenue": immediate_revenue,
        "delayed_revenue": delayed_revenue,
        "gain": delayed_revenue - immediate_revenue,
        "immediate_end_inventory": immediate_end,
        "delayed_end_inventory": delayed_end,
    }


def main() -> None:
    rows = []
    for item in PRODUCTS:
        I0 = MARKET_PARAMS[item]["I0"]
        for qty in (5, 10, 25, 50):
            for demand in (1, 2, 4, 7):
                r = pulse_hold_gain(item, I0, qty, demand)
                # Around I0 all quoted prices are well above the $1 floor, so
                # the two timing paths must converge to the same market state.
                assert r["immediate_end_inventory"] == r["delayed_end_inventory"], r
                assert r["gain"] >= 0, r
                rows.append(r)

    canonical = {(r["item"], r["qty"], r["demand"]): r for r in rows}
    assert canonical[("MILK", 25, 4)]["gain"] == 241
    assert canonical[("STRAWBERRY", 25, 4)]["gain"] == 224
    assert canonical[("WHEAT", 25, 4)]["gain"] == 18

    print("H1B_PULSE_HOLD_SCAN_PASS")
    print("canonical_q25_d4")
    for item in sorted(PRODUCTS, key=lambda x: canonical[(x, 25, 4)]["gain"], reverse=True):
        r = canonical[(item, 25, 4)]
        print(f"  {item:10s} gain={r['gain']:4d} immediate={r['immediate_revenue']:5d} delayed={r['delayed_revenue']:5d}")
    print("top_cases")
    for r in sorted(rows, key=lambda x: x["gain"], reverse=True)[:12]:
        print(f"  {r['item']:10s} q={r['qty']:2d} D={r['demand']:1d} gain={r['gain']:4d}")


if __name__ == "__main__":
    main()
