#!/usr/bin/env python3
"""FP001 H11 — exact-engine fertilizer conversion audit.

Question: once H8 animals generate fertilizer, is one unit worth more sold directly
or converted into incremental crop output?

This is a mechanics-layer audit, not yet a routing policy.  It brute-forces daily
FERTILIZE schedules for one already-planted crop while holding an otherwise
identical optimal-survival watering/harvest schedule fixed.  Plant transitions are
executed by kaggriculture==1.32.7 internal engine helpers, not a hand-written crop
model.
"""
from __future__ import annotations

from itertools import combinations

from kaggle_environments.envs.kaggriculture import kaggriculture as kg

CROPS = tuple(kg.CROPS)
TPD = 24


def fresh(crop):
    farm = kg._new_farm(10, 1_000_000)
    private = kg._new_private()
    pos = tuple(farm["farmer"])
    x, y = pos
    farm["tiles"][y][x] = kg._new_plant(crop, 0, TPD)
    private["inventories"][0]["FERTILIZER"] = 100
    return farm, private, pos


def tile_at(farm, pos):
    x, y = pos
    return farm["tiles"][y][x]


def inv_count(private, item):
    return int(private["inventories"][0].get(item, 0))


def simulate(crop, fert_days):
    """Return produced units/actions using exact plant helpers.

    Ongoing crops are harvested at the beginning of each day before WATER, avoiding
    the tile's max-held cap from masking fertilizer output. Non-ongoing crops are
    kept until the end of their yield window and harvested once.
    """
    cd = kg.CROPS[crop]
    farm, private, pos = fresh(crop)
    fert_days = set(fert_days)
    water_actions = 0
    fert_actions = 0
    harvest_actions = 0

    # Long enough to pass all ongoing production events or the non-ongoing window.
    if cd["ongoing"]:
        last_prod_current_day = cd["first_yield_day"] - 1 + (cd["max_yield"] - 1) * cd["interval"]
        last_day = last_prod_current_day + 1  # one extra day to harvest final EOD output
    else:
        last_day = cd["max_yield_day"]

    for day in range(last_day + 1):
        tile = tile_at(farm, pos)
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
            break

        # Harvest prior production first for ongoing crops; this keeps yield_units
        # below cap and measures actual total production capacity.
        if cd["ongoing"] and tile.get("yield_units", 0) > 0:
            kg._apply_unit_action(farm, private, 0, ["HARVEST"], 10, day, TPD, 1000)
            harvest_actions += 1
            tile = tile_at(farm, pos)

        if day <= last_day - (1 if cd["ongoing"] else 0):
            kg._apply_unit_action(farm, private, 0, ["WATER"], 10, day, TPD, 1000)
            water_actions += 1
            if day in fert_days:
                before = inv_count(private, "FERTILIZER")
                kg._apply_unit_action(farm, private, 0, ["FERTILIZE"], 10, day, TPD, 1000)
                after = inv_count(private, "FERTILIZER")
                if after == before - 1:
                    fert_actions += 1

            kg._daily_refresh_plants(farm, day, TPD)

    # Final harvest for any remaining product.
    tile = tile_at(farm, pos)
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("yield_units", 0) > 0:
        day = last_day + 1
        kg._apply_unit_action(farm, private, 0, ["HARVEST"], 10, day, TPD, 1000)
        harvest_actions += 1

    produced = inv_count(private, crop)
    used = 100 - inv_count(private, "FERTILIZER")
    return {
        "product": produced,
        "fert_used": used,
        "water_actions": water_actions,
        "fert_actions": fert_actions,
        "harvest_actions": harvest_actions,
        "actions": water_actions + fert_actions + harvest_actions,
    }


def candidate_days(crop):
    cd = kg.CROPS[crop]
    if cd["ongoing"]:
        last_prod_current_day = cd["first_yield_day"] - 1 + (cd["max_yield"] - 1) * cd["interval"]
        # Only days that can cover at least one production event matter.
        return tuple(range(max(0, cd["first_yield_day"] - 3), last_prod_current_day + 1))
    return tuple(range(0, cd["max_yield_day"] + 1))


def pareto_schedules(crop):
    days = candidate_days(crop)
    rows = []
    # Enumerate all subsets; longest day range here is small (MELON 13 => 8192).
    for r in range(len(days) + 1):
        for comb in combinations(days, r):
            out = simulate(crop, comb)
            rows.append((comb, out))

    # For each fertilizer count retain max product, then minimum action count.
    best = {}
    for comb, out in rows:
        f = out["fert_used"]
        key = (out["product"], -out["actions"])
        if f not in best or key > (best[f][1]["product"], -best[f][1]["actions"]):
            best[f] = (comb, out)
    return best


def sequential_sale_revenue(item, qty, start_inventory):
    inv = int(start_inventory)
    total = 0
    for _ in range(int(qty)):
        price = kg.market_price(item, inv)
        total += price
        if price > 1:
            inv += 1
    return total


def fertilizer_sale_value(qty, start_inventory):
    return sequential_sale_revenue("FERTILIZER", qty, start_inventory)


def money_delta(crop, extra_units, fert_used, product_start, fert_start):
    # Incremental product units are sold after the baseline product amount, so the
    # caller passes the market inventory at the incremental-sale margin.
    crop_gain = sequential_sale_revenue(crop, extra_units, product_start)
    fert_opp = fertilizer_sale_value(fert_used, fert_start)
    return crop_gain - fert_opp, crop_gain, fert_opp


def main():
    print("H11_FERTILIZER_CONVERSION_AUDIT")
    product_offsets = (0, -50, -150)   # negative = town-created scarcity
    fert_offsets = (0, 50, 150)       # positive = our fertilizer supply glut

    all_best = {}
    for crop in CROPS:
        base = simulate(crop, ())
        frontier = pareto_schedules(crop)
        all_best[crop] = (base, frontier)
        print("crop", crop, "baseline", base)
        for f in sorted(frontier):
            comb, out = frontier[f]
            extra = out["product"] - base["product"]
            if f == 0 or extra > 0:
                nominal = extra * kg.MARKET_PARAMS[crop]["base"] - f * kg.MARKET_PARAMS["FERTILIZER"]["base"]
                print("  f", f, "days", comb, "product", out["product"], "extra", extra, "actions", out["actions"], "nominal_conversion_delta", nominal)

    print("market_sensitivity")
    for crop in CROPS:
        base, frontier = all_best[crop]
        for f, (comb, out) in sorted(frontier.items()):
            extra = out["product"] - base["product"]
            if f <= 0 or extra <= 0:
                continue
            for po in product_offsets:
                for fo in fert_offsets:
                    delta, gain, opp = money_delta(
                        crop,
                        extra,
                        f,
                        kg.MARKET_PARAMS[crop]["I0"] + po,
                        kg.MARKET_PARAMS["FERTILIZER"]["I0"] + fo,
                    )
                    if delta > 0:
                        print("  profitable", crop, "f", f, "extra", extra, "prod_off", po, "fert_off", fo, "delta", delta, "crop_gain", gain, "fert_opp", opp, "days", comb)

    # Mechanics sanity: fertilizer must create incremental output for at least one
    # ongoing premium crop, otherwise the hypothesized conversion channel is absent.
    straw_base, straw_front = all_best["STRAWBERRY"]
    straw_extra = max(out["product"] - straw_base["product"] for _, out in straw_front.values())
    assert straw_extra > 0, (straw_base, straw_front)
    print("H11_FERTILIZER_CONVERSION_MECHANIC_PASS", {"strawberry_max_extra": straw_extra})


if __name__ == "__main__":
    main()
