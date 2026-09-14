#!/usr/bin/env python3
"""FP001 H8 Gate A — exact animal-control Pareto frontier.

Enumerates legal daily decisions using exact kaggle-environments==1.32.7 animal
state transitions.  It does NOT assume alternating-day feed, daily collection,
or daily harvest.  The frontier decides among:

- collect / defer fertilizer;
- harvest / defer accumulated animal product;
- no feed / FEED / FEED+CARE.

Records are Pareto-pruned on feed, unit-action count, collected fertilizer and
collected product.  This keeps the result valid under any non-negative market
revenue curve and any non-negative action shadow price.

Competitor data is not used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    ANIMALS,
    _apply_unit_action,
    _daily_refresh_animals,
    _new_animal,
    _new_farm,
    _new_private,
)

from fp001_h8_animal_fertilizer_economics import exact_buy_cost, exact_sell_revenue

ANIMAL_TYPES = ("GOOSE", "COW", "SHEEP")
HORIZONS = (5, 10, 15, 20, 25, 30)
PORTFOLIOS = (1, 3, 5)
ACTION_SHADOWS = (0, 10, 20, 30, 40, 50, 60, 80)


@dataclass(frozen=True)
class Metrics:
    feed: int
    actions: int
    fertilizer: int
    product: int
    schedule: str


def _animal_state(tile: dict) -> Tuple[int, int, int, int]:
    return (
        int(tile.get("consecutive_unfed", 0)),
        int(tile.get("pending_care_bonus", 0)),
        int(tile.get("yield_units", 0)),
        int(bool(tile.get("fertilizer_available", False))),
    )


def _tile_from_state(animal: str, day: int, state: Tuple[int, int, int, int]) -> dict:
    consecutive_unfed, pending, yield_units, fert = state
    t = _new_animal(animal, 0)
    t["consecutive_unfed"] = consecutive_unfed
    t["pending_care_bonus"] = pending
    t["yield_units"] = yield_units
    t["fertilizer_available"] = bool(fert)
    t["fed_today"] = False
    t["cared_today"] = False
    return t


def _dominates(a: Metrics, b: Metrics) -> bool:
    weak = (
        a.feed <= b.feed
        and a.actions <= b.actions
        and a.fertilizer >= b.fertilizer
        and a.product >= b.product
    )
    strict = (
        a.feed < b.feed
        or a.actions < b.actions
        or a.fertilizer > b.fertilizer
        or a.product > b.product
    )
    return weak and strict


def _prune(records: Iterable[Metrics]) -> List[Metrics]:
    # Collapse identical numeric outcomes first; keep the lexicographically
    # smallest schedule only for deterministic reporting.
    unique: Dict[Tuple[int, int, int, int], Metrics] = {}
    for r in records:
        key = (r.feed, r.actions, r.fertilizer, r.product)
        old = unique.get(key)
        if old is None or r.schedule < old.schedule:
            unique[key] = r
    vals = list(unique.values())
    keep: List[Metrics] = []
    for i, r in enumerate(vals):
        if any(i != j and _dominates(other, r) for j, other in enumerate(vals)):
            continue
        keep.append(r)
    return keep


def _step_record(
    animal: str,
    day: int,
    state: Tuple[int, int, int, int],
    record: Metrics,
    collect: bool,
    harvest: bool,
    mode: str,
):
    farm = _new_farm(10, 0)
    private = _new_private()
    x, y = farm["farmer"]
    farm["tiles"][y][x] = _tile_from_state(animal, day, state)
    tile = farm["tiles"][y][x]

    actions = record.actions
    fertilizer = record.fertilizer
    product = record.product
    feed = record.feed
    code = []

    if collect and tile.get("fertilizer_available", False):
        before = int(private["inventories"][0].get("FERTILIZER", 0))
        _apply_unit_action(farm, private, 0, ["COLLECT_FERTILIZER"], 10, day, 24, 100_000)
        gained = int(private["inventories"][0].get("FERTILIZER", 0)) - before
        if gained:
            fertilizer += gained
            actions += 1
            code.append("F")

    if harvest and int(tile.get("yield_units", 0)) > 0:
        item = ANIMALS[animal]["product"]
        before = int(private["inventories"][0].get(item, 0))
        _apply_unit_action(farm, private, 0, ["HARVEST"], 10, day, 24, 100_000)
        gained = int(private["inventories"][0].get(item, 0)) - before
        if gained:
            product += gained
            actions += 1
            code.append("H")

    if mode in ("D", "C"):
        private["inventories"][0]["WHEAT"] = 1
        _apply_unit_action(farm, private, 0, ["FEED"], 10, day, 24, 100_000)
        actions += 1
        feed += 1
        code.append("D")
        if mode == "C":
            _apply_unit_action(farm, private, 0, ["CARE"], 10, day, 24, 100_000)
            actions += 1
            code.append("C")

    _daily_refresh_animals(farm, day)
    next_tile = farm["tiles"][y][x]
    if not (isinstance(next_tile, dict) and next_tile.get("animal") == animal):
        return None

    next_state = _animal_state(next_tile)
    token = "".join(code) if code else "-"
    return next_state, Metrics(feed, actions, fertilizer, product, record.schedule + token + "/")


def frontier(animal: str, days: int) -> List[Metrics]:
    initial = _animal_state(_new_animal(animal, 0))
    dp: Dict[Tuple[int, int, int, int], List[Metrics]] = {
        initial: [Metrics(0, 0, 0, 0, "")]
    }

    for day in range(days):
        nxt: Dict[Tuple[int, int, int, int], List[Metrics]] = {}
        for state, records in dp.items():
            fert_available = bool(state[3])
            yield_available = state[2] > 0
            collect_options = (False, True) if fert_available else (False,)
            harvest_options = (False, True) if yield_available else (False,)
            for r in records:
                for collect in collect_options:
                    for harvest in harvest_options:
                        for mode in ("N", "D", "C"):
                            out = _step_record(animal, day, state, r, collect, harvest, mode)
                            if out is None:
                                continue
                            ns, nr = out
                            nxt.setdefault(ns, []).append(nr)
        dp = {state: _prune(records) for state, records in nxt.items()}

    # Terminal collection/harvest decisions.  There is no need to feed/care
    # after the final refresh because no later day is valued in this slice.
    terminal: List[Metrics] = []
    for state, records in dp.items():
        fert_available = bool(state[3])
        yield_units = state[2]
        for r in records:
            # keep uncollected terminal state (may be optimal at huge action shadow)
            terminal.append(r)
            if fert_available:
                terminal.append(Metrics(r.feed, r.actions + 1, r.fertilizer + 1, r.product, r.schedule + "TF/"))
            if yield_units > 0:
                terminal.append(Metrics(r.feed, r.actions + 1, r.fertilizer, r.product + yield_units, r.schedule + "TH/"))
            if fert_available and yield_units > 0:
                terminal.append(Metrics(r.feed, r.actions + 2, r.fertilizer + 1, r.product + yield_units, r.schedule + "TFH/"))
    return _prune(terminal)


def value_record(animal: str, r: Metrics, n: int, action_shadow: float) -> dict:
    product = ANIMALS[animal]["product"]
    animal_cost = ANIMALS[animal]["cost"] * n
    feed_cost = exact_buy_cost("WHEAT", r.feed * n)
    fert_revenue = exact_sell_revenue("FERTILIZER", r.fertilizer * n)
    product_revenue = exact_sell_revenue(product, r.product * n)

    # Setup lower bound: one structure build + one PLACE per animal and one
    # batched PICKUP of purchased animals.  BUY_ANIMAL itself is a market order.
    setup_actions = 2 * n + (1 if n > 0 else 0)
    actions = r.actions * n + setup_actions
    raw = fert_revenue + product_revenue - animal_cost - feed_cost
    objective = raw - action_shadow * actions
    return {
        "animal": animal,
        "n": n,
        "feed_per_animal": r.feed,
        "fert_per_animal": r.fertilizer,
        "product_per_animal": r.product,
        "actions_per_animal": r.actions,
        "total_actions_lb": actions,
        "raw_pnl": raw,
        "objective": objective,
        "schedule": r.schedule,
    }


def best_for(animal: str, days: int, n: int, action_shadow: float, rows: List[Metrics]) -> dict:
    scored = [value_record(animal, r, n, action_shadow) for r in rows]
    return max(scored, key=lambda x: (x["objective"], x["raw_pnl"], -x["total_actions_lb"]))


def main() -> None:
    cache: Dict[Tuple[str, int], List[Metrics]] = {}
    for animal in ANIMAL_TYPES:
        for days in HORIZONS:
            rows = frontier(animal, days)
            assert rows, (animal, days)
            cache[(animal, days)] = rows

    # Exact survival sanity: there must be at least one 30-day plan for every species.
    for animal in ANIMAL_TYPES:
        assert cache[(animal, 30)]

    print("H8_CONTROL_FRONTIER_PASS")
    for animal in ANIMAL_TYPES:
        print(f"frontier {animal} d30 size={len(cache[(animal, 30)])}")

    print("\nBEST_N3_BY_ACTION_SHADOW")
    for days in (10, 20, 30):
        print(f"days={days}")
        for shadow in ACTION_SHADOWS:
            candidates = [best_for(a, days, 3, shadow, cache[(a, days)]) for a in ANIMAL_TYPES]
            best = max(candidates, key=lambda x: x["objective"])
            print(
                f"  shadow={shadow:>3} best={best['animal']:5s} obj={best['objective']:8.1f} "
                f"raw={best['raw_pnl']:6d} act={best['total_actions_lb']:3d} "
                f"feed={best['feed_per_animal']:2d} fert={best['fert_per_animal']:2d} "
                f"prod={best['product_per_animal']:2d} unitact={best['actions_per_animal']:2d}"
            )

    print("\nDAY30_SPECIES_N3")
    for animal in ANIMAL_TYPES:
        rows = cache[(animal, 30)]
        for shadow in (0, 20, 40, 60):
            b = best_for(animal, 30, 3, shadow, rows)
            print(
                f"  {animal:5s} sh={shadow:2d} obj={b['objective']:8.1f} raw={b['raw_pnl']:6d} "
                f"act={b['total_actions_lb']:3d} feed={b['feed_per_animal']:2d} "
                f"fert={b['fert_per_animal']:2d} prod={b['product_per_animal']:2d}"
            )

    # Print concise exact policies for the production-relevant n=3/day30 cases.
    print("\nDAY30_POLICY_EXAMPLES")
    for shadow in (0, 40, 60):
        candidates = [best_for(a, 30, 3, shadow, cache[(a, 30)]) for a in ANIMAL_TYPES]
        best = max(candidates, key=lambda x: x["objective"])
        print(f"shadow={shadow} animal={best['animal']} schedule={best['schedule']}")


if __name__ == "__main__":
    main()
