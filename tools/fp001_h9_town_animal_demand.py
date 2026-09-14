#!/usr/bin/env python3
"""FP001 H9 — town-conditioned animal-product demand model.

First-principles only. Derives deterministic/expected town pulls from official
shop mechanics. No competitor data.

The useful object is expected remaining demand conditional on the shops already
unlocked in the legal public observation. Future shop identities are integrated
under the official uniform-with-replacement draw distribution.
"""
from __future__ import annotations

from collections import defaultdict

TURNS_PER_DAY = 24
EPISODE_STEPS = 720
SHOP_UNLOCK_DAYS = tuple(range(3, 25, 3))  # 3,6,...,24 (8 copies max)
SHOP_SELL_INTERVAL = 4
CENTER_SELL_INTERVAL = 24

SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

ANIMAL_PRODUCTS = ("EGG", "MILK", "WOOL")


def shop_pull_per_tick(shop: str, product: str) -> int:
    products = SHOPS[shop]
    if product not in products:
        return 0
    return 2 if len(products) == 1 else 1


def ticks_from_step(first_step: int, interval: int, end_step: int = EPISODE_STEPS - 1) -> int:
    """Number of divisible-by-interval ticks in [first_step, end_step]."""
    first = first_step + ((-first_step) % interval)
    if first > end_step:
        return 0
    return (end_step - first) // interval + 1


def prior_full_season_expected():
    out = defaultdict(float)

    # Town center pulls one of every non-fertilizer product at step 0,24,...696.
    center_ticks = ticks_from_step(0, CENTER_SELL_INTERVAL)
    for p in ANIMAL_PRODUCTS:
        out[p] += center_ticks

    # Shop copy k is revealed at EOD immediately before day d begins, hence it
    # participates from step 24*d onward. Identity is uniform over 8 shop names.
    names = tuple(sorted(SHOPS))
    for day in SHOP_UNLOCK_DAYS:
        first_step = day * TURNS_PER_DAY
        ticks = ticks_from_step(first_step, SHOP_SELL_INTERVAL)
        for p in ANIMAL_PRODUCTS:
            expected_per_tick = sum(shop_pull_per_tick(s, p) for s in names) / len(names)
            out[p] += ticks * expected_per_tick

    return dict(out)


def expected_remaining(step: int, unlocked_shops: tuple[str, ...]):
    """Expected pulls at or after current step conditional on public town state."""
    step = max(0, int(step))
    out = defaultdict(float)

    # Known town-center future demand.
    center_ticks = ticks_from_step(step, CENTER_SELL_INTERVAL)
    for p in ANIMAL_PRODUCTS:
        out[p] += center_ticks

    # Every already-unlocked shop is known and keeps consuming independently.
    shop_ticks_now = ticks_from_step(step, SHOP_SELL_INTERVAL)
    for shop in unlocked_shops:
        for p in ANIMAL_PRODUCTS:
            out[p] += shop_ticks_now * shop_pull_per_tick(shop, p)

    # Unrevealed future copies retain the official uniform prior.
    names = tuple(sorted(SHOPS))
    revealed = len(unlocked_shops)
    future_days = SHOP_UNLOCK_DAYS[revealed:]
    for day in future_days:
        first_step = max(step, day * TURNS_PER_DAY)
        ticks = ticks_from_step(first_step, SHOP_SELL_INTERVAL)
        for p in ANIMAL_PRODUCTS:
            expected_per_tick = sum(shop_pull_per_tick(s, p) for s in names) / len(names)
            out[p] += ticks * expected_per_tick

    return dict(out)


def main():
    prior = prior_full_season_expected()
    print("H9_TOWN_ANIMAL_DEMAND_PASS")
    print("full_season_expected", {p: round(prior[p], 3) for p in ANIMAL_PRODUCTS})
    print("milk_minus_wool", round(prior["MILK"] - prior["WOOL"], 3))
    print("milk_over_wool", round(prior["MILK"] / prior["WOOL"], 5))

    # Exact algebraic expectations under the official default mechanics:
    # shop tick exposures = 162+144+126+108+90+72+54+36 = 792.
    # Expected pulls/tick: EGG=2/8=.25, MILK=3/8=.375, WOOL=2/8=.25
    # (YARN_STORE is single-product, therefore pulls 2 units).
    assert prior == {"EGG": 228.0, "MILK": 327.0, "WOOL": 228.0}, prior

    scenarios = {
        "day3_yarn": (72, ("YARN_STORE",)),
        "day3_pizza": (72, ("PIZZA_SHOP",)),
        "day6_yarn_yarn": (144, ("YARN_STORE", "YARN_STORE")),
        "day6_pizza_icecream": (144, ("PIZZA_SHOP", "ICE_CREAM_SHOP")),
    }
    for name, (step, shops) in scenarios.items():
        d = expected_remaining(step, shops)
        print(name, {p: round(d[p], 3) for p in ANIMAL_PRODUCTS})


if __name__ == "__main__":
    main()
