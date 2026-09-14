#!/usr/bin/env python3
"""FP001 H1B exact-engine proof: delay an owned sale across known town demand.

Two counterfactual paths start from identical legal engine state with identical
owned shed inventory:

A. SELL product now, then town consumes.
B. Town consumes first, SELL same product next.

Around I0 and above the $1 floor both paths end at the same market inventory, so
revenue difference is pure timing value caused by exogenous town demand.
No competitor replay data is used.
"""
from __future__ import annotations

from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS,
    _commit_unit,
    _new_farm,
    _new_market,
    _new_private,
    _town_consume,
    market_price,
)

from fp001_h1b_pulse_hold_scan import pulse_hold_gain

SHOP_FOR_ITEM = {
    "WHEAT": "BAKERY",
    "CARROT": "PET_CAFE",          # consumes 2 per duplicate instance
    "TOMATO": "PIZZA_SHOP",
    "STRAWBERRY": "BRUNCH_SPOT",
    "EGG": "BAKERY",
    "MILK": "PIZZA_SHOP",
    "WOOL": "YARN_STORE",         # consumes 2 per duplicate instance
}


def sell_owned(item: str, start_inventory: int, qty: int):
    farm = _new_farm(10, 0)
    private = _new_private()
    private["shed"][item] = qty
    market = _new_market()
    market["inventory"][item] = start_inventory
    for _ in range(qty):
        quote = market_price(item, market["inventory"][item])
        assert _commit_unit("SELL", item, quote, farm, private, market, shed_capacity=100_000)
    return int(farm["money"]), market["inventory"][item]


def town_consume_item(item: str, market: dict, desired_demand: int):
    """Create exact shop demand when possible; town-center is disabled."""
    shop = SHOP_FOR_ITEM[item]
    multiplier = 2 if shop in ("PET_CAFE", "YARN_STORE") else 1
    assert desired_demand % multiplier == 0, (item, desired_demand)
    copies = desired_demand // multiplier
    obs = SimpleNamespace(market=market, town={"unlocked_shops": [shop] * copies})
    state = [SimpleNamespace(observation=obs)]
    env = SimpleNamespace(configuration={"townShopSellInterval": 1, "townCenterSellInterval": 999_999})
    _town_consume(env, state, step=1)


def engine_paths(item: str, qty: int, demand: int):
    I0 = MARKET_PARAMS[item]["I0"]

    # Path A: sell then town consumes.
    rev_a, after_sale = sell_owned(item, I0, qty)
    market_a = _new_market()
    market_a["inventory"][item] = after_sale
    town_consume_item(item, market_a, demand)
    end_a = market_a["inventory"][item]

    # Path B: town consumes then sell.
    market_b = _new_market()
    market_b["inventory"][item] = I0
    town_consume_item(item, market_b, demand)
    farm_b = _new_farm(10, 0)
    private_b = _new_private()
    private_b["shed"][item] = qty
    for _ in range(qty):
        quote = market_price(item, market_b["inventory"][item])
        assert _commit_unit("SELL", item, quote, farm_b, private_b, market_b, shed_capacity=100_000)
    rev_b = int(farm_b["money"])
    end_b = market_b["inventory"][item]

    return rev_a, rev_b, end_a, end_b


def main() -> None:
    # Use product/demand combinations exactly representable by one or more shops.
    cases = []
    for item in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "EGG", "MILK", "WOOL"):
        demands = (2, 4, 6) if item in ("CARROT", "WOOL") else (1, 2, 4, 7)
        for qty in (5, 10, 25, 50):
            for demand in demands:
                eng_a, eng_b, end_a, end_b = engine_paths(item, qty, demand)
                local = pulse_hold_gain(item, MARKET_PARAMS[item]["I0"], qty, demand)
                assert eng_b - eng_a == local["gain"], (item, qty, demand, eng_a, eng_b, local)
                assert end_a == end_b == local["immediate_end_inventory"], (item, qty, demand, end_a, end_b, local)
                assert eng_b >= eng_a, (item, qty, demand, eng_a, eng_b)
                cases.append((item, qty, demand, eng_b - eng_a))

    canonical = {(i, q, d): g for i, q, d, g in cases}
    assert canonical[("MILK", 25, 4)] == 241
    assert canonical[("STRAWBERRY", 25, 4)] == 224
    assert canonical[("WHEAT", 25, 4)] == 18

    print("H1B_EXACT_ENGINE_PASS")
    print(f"cases={len(cases)} positive={sum(g > 0 for _,_,_,g in cases)}")
    print("canonical_milk_q25_d4=", canonical[("MILK", 25, 4)])
    print("canonical_strawberry_q25_d4=", canonical[("STRAWBERRY", 25, 4)])
    print("canonical_wheat_q25_d4=", canonical[("WHEAT", 25, 4)])
    print("top_cases")
    for item, qty, demand, gain in sorted(cases, key=lambda x: x[3], reverse=True)[:15]:
        print(f"  {item:10s} q={qty:2d} D={demand:1d} gain={gain:4d}")


if __name__ == "__main__":
    main()
