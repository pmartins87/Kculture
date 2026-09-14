#!/usr/bin/env python3
"""FP001 FP0: exact mechanics parity against kaggle-environments==1.32.7.

This test deliberately imports the installed Kaggriculture engine and compares our
standalone microsimulator against it.  No competitor replay data is used.
"""
from __future__ import annotations

from types import SimpleNamespace

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS as ENGINE_MARKET_PARAMS,
    _commit_unit,
    _new_farm,
    _new_market,
    _new_private,
    _town_consume,
    market_price as engine_market_price,
)

from fp001_market_microsim import (
    MARKET_PARAMS,
    buy_product,
    market_price,
    no_demand_round_trip,
    sell,
    wheat_town_carry,
)


def engine_buy(item: str, start_inventory: int, qty: int):
    farm = _new_farm(10, 10_000_000)
    private = _new_private()
    market = _new_market()
    market["inventory"][item] = start_inventory
    money0 = farm["money"]
    for _ in range(qty):
        quote = engine_market_price(item, market["inventory"][item] - 1)
        ok = _commit_unit("BUY_PRODUCT", item, quote, farm, private, market, shed_capacity=100_000)
        assert ok
    return int(money0 - farm["money"]), market["inventory"][item], private


def engine_sell(item: str, start_inventory: int, qty: int):
    farm = _new_farm(10, 0)
    private = _new_private()
    private["shed"][item] = qty
    market = _new_market()
    market["inventory"][item] = start_inventory
    for _ in range(qty):
        quote = engine_market_price(item, market["inventory"][item])
        ok = _commit_unit("SELL", item, quote, farm, private, market, shed_capacity=100_000)
        assert ok
    return int(farm["money"]), market["inventory"][item]


def engine_round_trip(item: str, start_inventory: int, qty: int) -> int:
    farm = _new_farm(10, 10_000_000)
    private = _new_private()
    market = _new_market()
    market["inventory"][item] = start_inventory
    money0 = farm["money"]
    for _ in range(qty):
        quote = engine_market_price(item, market["inventory"][item] - 1)
        assert _commit_unit("BUY_PRODUCT", item, quote, farm, private, market, shed_capacity=100_000)
    for _ in range(qty):
        quote = engine_market_price(item, market["inventory"][item])
        assert _commit_unit("SELL", item, quote, farm, private, market, shed_capacity=100_000)
    return int(farm["money"] - money0)


def engine_wheat_town_carry(start_inventory: int, qty: int, demand: int):
    farm = _new_farm(10, 10_000_000)
    private = _new_private()
    market = _new_market()
    market["inventory"]["WHEAT"] = start_inventory
    money0 = farm["money"]

    for _ in range(qty):
        quote = engine_market_price("WHEAT", market["inventory"]["WHEAT"] - 1)
        assert _commit_unit("BUY_PRODUCT", "WHEAT", quote, farm, private, market, shed_capacity=100_000)

    # Each BAKERY instance consumes exactly one WHEAT when a shop pulse fires.
    # Use step=1 so the artificially huge town-center interval does not fire.
    obs = SimpleNamespace(market=market, town={"unlocked_shops": ["BAKERY"] * demand})
    state = [SimpleNamespace(observation=obs)]
    env = SimpleNamespace(configuration={"townShopSellInterval": 1, "townCenterSellInterval": 999_999})
    _town_consume(env, state, step=1)

    for _ in range(qty):
        quote = engine_market_price("WHEAT", market["inventory"]["WHEAT"])
        assert _commit_unit("SELL", "WHEAT", quote, farm, private, market, shed_capacity=100_000)

    return int(farm["money"] - money0), market["inventory"]["WHEAT"]


def main() -> None:
    assert MARKET_PARAMS == ENGINE_MARKET_PARAMS, "market parameter drift"

    price_cases = 0
    tx_cases = 0
    for item, p in ENGINE_MARKET_PARAMS.items():
        I0, T = p["I0"], p["T"]
        inventories = sorted({0, 1, I0 - 3 * T, I0 - T, I0 - T // 2, I0 - 1, I0, I0 + 1, I0 + T // 2, I0 + T, I0 + 3 * T, I0 * 2})
        for inv in inventories:
            assert market_price(item, inv) == engine_market_price(item, inv), (item, inv)
            price_cases += 1

    for item in ("WHEAT", "FERTILIZER"):
        for inv in (9_800, 10_000, 10_200):
            for qty in (1, 10, 50, 90):
                local_cost, local_inv = buy_product(item, inv, qty)
                eng_cost, eng_inv, _ = engine_buy(item, inv, qty)
                assert (local_cost, local_inv) == (eng_cost, eng_inv), (item, inv, qty)

                local_rev, local_sell_inv = sell(item, inv, qty)
                eng_rev, eng_sell_inv = engine_sell(item, inv, qty)
                assert (local_rev, local_sell_inv) == (eng_rev, eng_sell_inv), (item, inv, qty)

                if item == "WHEAT":
                    assert no_demand_round_trip(inv, qty) == 0
                    assert engine_round_trip(item, inv, qty) == 0
                tx_cases += 1

    carry_cases = []
    for inv in (9_900, 10_000, 10_100):
        for qty in (1, 10, 25, 50, 90):
            for demand in (0, 1, 2, 4, 7, 12):
                local = wheat_town_carry(inv, qty, demand)
                eng_pnl, eng_inv = engine_wheat_town_carry(inv, qty, demand)
                assert local.pnl == eng_pnl, (inv, qty, demand, local.pnl, eng_pnl)
                assert local.ending_inventory == eng_inv, (inv, qty, demand, local.ending_inventory, eng_inv)
                if demand == 0:
                    assert eng_pnl == 0
                carry_cases.append((inv, qty, demand, eng_pnl))

    positives = [x for x in carry_cases if x[2] > 0 and x[3] > 0]
    assert positives, "town pulse never created positive carry"

    print("FP0_ENGINE_PARITY_PASS")
    print(f"price_cases={price_cases}")
    print(f"transaction_cases={tx_cases}")
    print(f"town_carry_cases={len(carry_cases)} positive={len(positives)}")
    print("sample_i0_q90_d7=", next(x[3] for x in carry_cases if x[:3] == (10_000, 90, 7)))


if __name__ == "__main__":
    main()
