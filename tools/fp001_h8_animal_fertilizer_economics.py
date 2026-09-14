#!/usr/bin/env python3
"""FP001 H8 — exact-engine animal/fertilizer economics audit.

Goal: test the first-principles hypothesis that animals should be valued partly
as fertilizer-producing capital, not only for EGG/MILK/WOOL.

This is deliberately a mechanics/economics audit, not a routed farm agent.
It uses exact kaggle-environments==1.32.7 helpers and excludes competitor data.

Conservative simplifications for output valuation:
- no town demand is credited to animal products;
- no CARE bonus is used;
- fertilizer is sold rather than credited at an optimistic crop-use value;
- feed WHEAT is priced as exact market purchases;
- movement/hire costs are not hidden: we report a minimum unit-action count and
  the maximum shadow value per action the raw economics could tolerate.
"""
from __future__ import annotations

from dataclasses import dataclass

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    ANIMALS,
    MARKET_PARAMS,
    _apply_unit_action,
    _commit_unit,
    _daily_refresh_animals,
    _new_animal,
    _new_farm,
    _new_market,
    _new_private,
    market_price,
)

ANIMAL_TYPES = ("GOOSE", "COW", "SHEEP")


@dataclass
class OneAnimal:
    animal: str
    days: int
    feed_units: int
    fertilizer_units: int
    product_units: int
    recurring_actions: int
    survived: bool


def simulate_one(animal: str, days: int) -> OneAnimal:
    """Exact state evolution with minimum-survival feeding and daily collection.

    The farmer is placed on the animal tile and each helper call represents a
    separate legal turn. Movement is excluded but actions are counted.
    """
    farm = _new_farm(10, 0)
    private = _new_private()
    x, y = farm["farmer"]
    farm["tiles"][y][x] = _new_animal(animal, 0)
    product = ANIMALS[animal]["product"]

    feed_units = 0
    recurring_actions = 0

    for day in range(days):
        tile = farm["tiles"][y][x]
        if not (isinstance(tile, dict) and tile.get("animal") == animal):
            break

        # Collect yesterday's fertilizer before the next daily refresh so the
        # boolean availability flag can generate a new unit every surviving day.
        if tile.get("fertilizer_available", False):
            _apply_unit_action(farm, private, 0, ["COLLECT_FERTILIZER"], 10, day, 24, 100_000)
            recurring_actions += 1

        # Harvest any accumulated base product; no CARE bonus is assumed.
        if tile.get("yield_units", 0) > 0:
            _apply_unit_action(farm, private, 0, ["HARVEST"], 10, day, 24, 100_000)
            recurring_actions += 1

        # Feed only when one more unfed end-of-day would cause escape.
        if tile.get("consecutive_unfed", 0) >= 1:
            private["inventories"][0]["WHEAT"] = private["inventories"][0].get("WHEAT", 0) + 1
            _apply_unit_action(farm, private, 0, ["FEED"], 10, day, 24, 100_000)
            recurring_actions += 1
            feed_units += 1

        _daily_refresh_animals(farm, day)

    # Collect final end-of-horizon inventory/fertilizer once; this is executable
    # on a subsequent turn when the horizon is used as an economic slice.
    tile = farm["tiles"][y][x]
    survived = isinstance(tile, dict) and tile.get("animal") == animal
    if survived:
        if tile.get("fertilizer_available", False):
            _apply_unit_action(farm, private, 0, ["COLLECT_FERTILIZER"], 10, days, 24, 100_000)
            recurring_actions += 1
        if tile.get("yield_units", 0) > 0:
            _apply_unit_action(farm, private, 0, ["HARVEST"], 10, days, 24, 100_000)
            recurring_actions += 1

    fert = int(private["inventories"][0].get("FERTILIZER", 0))
    prod = int(private["inventories"][0].get(product, 0))
    return OneAnimal(animal, days, feed_units, fert, prod, recurring_actions, survived)


def exact_buy_cost(item: str, qty: int) -> int:
    if qty <= 0:
        return 0
    farm = _new_farm(10, 100_000_000)
    private = _new_private()
    market = _new_market()
    start = farm["money"]
    for _ in range(qty):
        quote = market_price(item, market["inventory"][item] - 1)
        assert _commit_unit("BUY_PRODUCT", item, quote, farm, private, market, 1_000_000)
    return int(start - farm["money"])


def exact_sell_revenue(item: str, qty: int) -> int:
    if qty <= 0:
        return 0
    farm = _new_farm(10, 0)
    private = _new_private()
    private["shed"][item] = qty
    market = _new_market()
    for _ in range(qty):
        quote = market_price(item, market["inventory"][item])
        assert _commit_unit("SELL", item, quote, farm, private, market, 1_000_000)
    return int(farm["money"])


def portfolio(animal: str, n: int, days: int) -> dict:
    one = simulate_one(animal, days)
    assert one.survived, one
    feed = one.feed_units * n
    fert = one.fertilizer_units * n
    prod = one.product_units * n
    product = ANIMALS[animal]["product"]

    animal_cost = ANIMALS[animal]["cost"] * n
    feed_cost = exact_buy_cost("WHEAT", feed)
    fert_revenue = exact_sell_revenue("FERTILIZER", fert)
    product_revenue = exact_sell_revenue(product, prod)
    raw_pnl = fert_revenue + product_revenue - animal_cost - feed_cost

    # Lower-bound setup actions: one BUILD structure + one PLACE per animal,
    # plus one batched PICKUP of purchased animals. Actual routing adds movement.
    setup_actions_lb = 2 * n + (1 if n > 0 else 0)
    action_lb = setup_actions_lb + one.recurring_actions * n
    max_shadow_per_action = raw_pnl / action_lb if action_lb else 0.0

    return {
        "animal": animal,
        "n": n,
        "days": days,
        "feed": feed,
        "fert": fert,
        "product": product,
        "product_units": prod,
        "animal_cost": animal_cost,
        "feed_cost": feed_cost,
        "fert_revenue": fert_revenue,
        "product_revenue": product_revenue,
        "raw_pnl": raw_pnl,
        "setup_actions_lb": setup_actions_lb,
        "recurring_actions": one.recurring_actions * n,
        "action_lb": action_lb,
        "max_shadow_per_action": max_shadow_per_action,
        "raw_pnl_per_tile": raw_pnl / n,
    }


def main() -> None:
    # First prove the exact survival/generation mechanism for a single animal.
    for animal in ANIMAL_TYPES:
        x = simulate_one(animal, 30)
        assert x.survived
        assert x.fertilizer_units == 30, x
        # Minimal-survival schedule feeds on alternate days after first unfed day.
        assert x.feed_units == 15, x

    rows = []
    for days in (5, 10, 15, 20, 25, 30):
        for animal in ANIMAL_TYPES:
            for n in (1, 3, 5, 8):
                rows.append(portfolio(animal, n, days))

    print("H8_ANIMAL_FERTILIZER_ENGINE_AUDIT_PASS")
    print("single_animal_30d")
    for animal in ANIMAL_TYPES:
        x = simulate_one(animal, 30)
        print(
            f"  {animal:5s} feed={x.feed_units:2d} fertilizer={x.fertilizer_units:2d} "
            f"product={x.product_units:2d} recurring_actions={x.recurring_actions:2d}"
        )

    print("\nportfolios_n3")
    for days in (5, 10, 15, 20, 25, 30):
        subset = [r for r in rows if r["n"] == 3 and r["days"] == days]
        for r in sorted(subset, key=lambda z: z["raw_pnl"], reverse=True):
            print(
                f"  d={days:2d} {r['animal']:5s} pnl={r['raw_pnl']:6d} "
                f"fert_rev={r['fert_revenue']:5d} prod_rev={r['product_revenue']:5d} "
                f"feed_cost={r['feed_cost']:4d} actions_lb={r['action_lb']:3d} "
                f"max_action_shadow={r['max_shadow_per_action']:6.1f}"
            )

    print("\ntop_raw_pnl")
    for r in sorted(rows, key=lambda z: z["raw_pnl"], reverse=True)[:15]:
        print(
            f"  {r['animal']:5s} n={r['n']} d={r['days']:2d} pnl={r['raw_pnl']:6d} "
            f"per_tile={r['raw_pnl_per_tile']:7.1f} action_shadow={r['max_shadow_per_action']:6.1f}"
        )


if __name__ == "__main__":
    main()
