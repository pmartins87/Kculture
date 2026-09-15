"""FP001 E5 — compact elite-informed COW/SHEEP + M6S1 integration.

This keeps the proven H10 compact path, batching and CARE priority, but allows
the five pasture positions to hold a frozen COW/SHEEP composition.  The crop
layer is the exact E3 one-hand M6S1 scheduler; no opponent-derived runtime
feature is used.
"""
from __future__ import annotations

from collections import Counter

from candidates.fp001_h10_cow_scale_module import (
    TARGET_POSITIONS,
    _count,
    _dist,
    _farm,
    _get,
    _is_shed,
    _ival,
    _move_toward,
    _nearest_shed,
    _step,
    _tile,
)
from candidates.fp001_e3_single_hand_crop_density import (
    _filter_fertilizer_sales,
    _hand_action,
    _needs_hand,
    _pending_seed_buys,
    _plan,
    _remaining_straw_fert_need,
)

ANIMAL_META = {
    "COW": {"product": "MILK"},
    "SHEEP": {"product": "WOOL"},
}


def make_compact_animal_agent(species_tuple, harvest_threshold=6):
    species_tuple = tuple(str(x).upper() for x in species_tuple)
    harvest_threshold = max(1, min(6, int(harvest_threshold)))
    if len(species_tuple) != 5 or any(x not in ANIMAL_META for x in species_tuple):
        raise ValueError(species_tuple)
    targets = TARGET_POSITIONS[: len(species_tuple)]
    desired = Counter(species_tuple)
    products = tuple(sorted({ANIMAL_META[x]["product"] for x in species_tuple}))

    def agent(obs, config=None):
        config = config or {}
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        invs = list(_get(private, "inventories", []) or [])
        inv = invs[0] if invs else {}
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = episode_steps - 1 - step

        action = {"farmer": ["PASS"], "hands": [], "market": []}
        market = []

        fert = _count(shed, "FERTILIZER")
        if fert:
            market.append(["SELL", "FERTILIZER", fert])
        for product in products:
            qty = _count(shed, product)
            if qty and (hour == 1 or remaining <= 8):
                market.append(["SELL", product, qty])

        placed = Counter()
        correct = 0
        for pos, species in zip(targets, species_tuple):
            tile = _tile(farm, pos)
            if isinstance(tile, dict) and _get(tile, "animal", None) == species:
                placed[species] += 1
                correct += 1

        owned = Counter(placed)
        for species in desired:
            owned[species] += _count(shed, species) + _count(inv, species)
            missing = max(0, desired[species] - owned[species])
            if missing:
                market.append(["BUY_ANIMAL", species, missing])

        wheat_total = _count(shed, "WHEAT") + _count(inv, "WHEAT")
        wheat_floor = 2 * len(species_tuple)
        wheat_target = 3 * len(species_tuple)
        if wheat_total < wheat_floor and remaining > turns:
            market.append(["BUY_PRODUCT", "WHEAT", wheat_target - wheat_total])

        if correct < len(species_tuple):
            carried_animals = sum(_count(inv, species) for species in desired)
            if carried_animals == 0:
                for species in species_tuple:
                    shed_qty = _count(shed, species)
                    if shed_qty > 0:
                        if _is_shed(farmer):
                            action["farmer"] = ["PICKUP", species, shed_qty]
                        else:
                            action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                        action["market"] = market[:10]
                        return action

            target = None
            target_tile = None
            target_species = None
            for pos, species in zip(targets, species_tuple):
                tile = _tile(farm, pos)
                if not (isinstance(tile, dict) and _get(tile, "animal", None) == species):
                    target, target_tile, target_species = pos, tile, species
                    break

            if target is not None:
                if farmer != tuple(target):
                    action["farmer"] = _move_toward(farmer, target)
                elif target_tile is None:
                    action["farmer"] = ["BUILD_PASTURE"]
                elif (
                    isinstance(target_tile, dict)
                    and _get(target_tile, "kind", None) == "PASTURE"
                    and _get(target_tile, "animal", None) is None
                    and _count(inv, target_species) > 0
                ):
                    action["farmer"] = ["PLACE", target_species]
                elif isinstance(target_tile, dict) and _get(target_tile, "animal", None) is None:
                    action["farmer"] = ["DIG"]
                action["market"] = market[:10]
                return action

        animals = []
        for pos, species in zip(targets, species_tuple):
            tile = _tile(farm, pos)
            if isinstance(tile, dict) and _get(tile, "animal", None) == species:
                animals.append((pos, tile))

        terminal_harvest = remaining <= 2 * turns
        urgent_feed = [
            (pos, tile) for pos, tile in animals
            if _ival(_get(tile, "consecutive_unfed", 0)) >= 1
            and not bool(_get(tile, "fed_today", False))
        ]
        if urgent_feed and _count(inv, "WHEAT") <= 0:
            if _count(shed, "WHEAT") > 0:
                if _is_shed(farmer):
                    action["farmer"] = ["PICKUP", "WHEAT", min(len(species_tuple), _count(shed, "WHEAT"))]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                action["market"] = market[:10]
                return action

        tasks = []
        for pos, tile in animals:
            if (
                _ival(_get(tile, "consecutive_unfed", 0)) >= 1
                and not bool(_get(tile, "fed_today", False))
            ):
                tasks.append((100, "FEED", pos))
            if bool(_get(tile, "fertilizer_available", False)):
                tasks.append((80, "COLLECT_FERTILIZER", pos))
            yld = _ival(_get(tile, "yield_units", 0))
            if yld >= harvest_threshold or (terminal_harvest and yld > 0):
                tasks.append((50, "HARVEST", pos))

        if tasks:
            here = [task for task in tasks if tuple(task[2]) == farmer]
            if here:
                _, op, _ = max(here, key=lambda x: x[0])
                if op == "FEED" and _count(inv, "WHEAT") <= 0:
                    if _is_shed(farmer) and _count(shed, "WHEAT") > 0:
                        action["farmer"] = ["PICKUP", "WHEAT", min(len(species_tuple), _count(shed, "WHEAT"))]
                    else:
                        action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                else:
                    action["farmer"] = [op]
            else:
                best_priority = max(x[0] for x in tasks)
                choices = [x for x in tasks if x[0] == best_priority]
                _, _, target = min(choices, key=lambda x: (_dist(farmer, x[2]), targets.index(x[2])))
                action["farmer"] = _move_toward(farmer, target)

        action["market"] = market[:10]
        return action

    return agent


def make_care_agent(species_tuple, mode="DAILY"):
    species_tuple = tuple(str(x).upper() for x in species_tuple)
    mode = str(mode).upper()
    if mode not in {"NONE", "SURVIVAL", "DAILY"}:
        raise ValueError(mode)
    targets = TARGET_POSITIONS[: len(species_tuple)]
    base = make_compact_animal_agent(species_tuple, harvest_threshold=6)

    def agent(obs, config=None):
        action = base(obs, config)
        if mode == "NONE" or action.get("farmer") != ["PASS"]:
            return action

        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        invs = list(_get(private, "inventories", []) or [])
        inv = invs[0] if invs else {}
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        animals = []
        for pos, species in zip(targets, species_tuple):
            tile = _tile(farm, pos)
            if not (isinstance(tile, dict) and _get(tile, "animal", None) == species):
                return action
            animals.append((pos, tile))

        care_targets = [
            pos for pos, tile in animals
            if bool(_get(tile, "fed_today", False))
            and not bool(_get(tile, "cared_today", False))
        ]
        if care_targets:
            target = min(care_targets, key=lambda p: (_dist(farmer, p), targets.index(p)))
            action["farmer"] = ["CARE"] if farmer == tuple(target) else _move_toward(farmer, target)
            return action

        if mode != "DAILY":
            return action
        feed_targets = [pos for pos, tile in animals if not bool(_get(tile, "fed_today", False))]
        if not feed_targets:
            return action
        if _count(inv, "WHEAT") <= 0:
            if _count(shed, "WHEAT") > 0:
                if _is_shed(farmer):
                    action["farmer"] = ["PICKUP", "WHEAT", min(len(species_tuple), _count(shed, "WHEAT"))]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
            return action
        target = min(feed_targets, key=lambda p: (_dist(farmer, p), targets.index(p)))
        action["farmer"] = ["FEED"] if farmer == tuple(target) else _move_toward(farmer, target)
        return action

    return agent


def make_agent(species_tuple=("COW", "COW", "COW", "SHEEP", "SHEEP"), care_mode="DAILY", n_strawberries=1, n_melons=6):
    species_tuple = tuple(str(x).upper() for x in species_tuple)
    plan = _plan(n_strawberries, n_melons)
    base = make_care_agent(species_tuple, care_mode)
    if not plan:
        return base

    def agent(obs, config=None):
        config = config or {}
        action = base(obs, config)
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        invs = list(_get(private, "inventories", []) or [])

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns
        hands = list(_get(farm, "hands", []) or [])
        hires_today = max(0, _ival(_get(farm, "hires_today", 0)))

        action["hands"] = [["PASS"] for _ in hands]
        market = list(action.get("market") or [])

        fert_need = _remaining_straw_fert_need(farm, plan, day)
        carried_fert = sum(_count(inv or {}, "FERTILIZER") for inv in invs)
        shed_fert = _count(shed, "FERTILIZER")
        reserve = max(0, fert_need - carried_fert)
        market = _filter_fertilizer_sales(market, max(0, shed_fert - reserve))
        market.extend(_pending_seed_buys(farm, private, plan, day))

        for crop in ("STRAWBERRY", "MELON"):
            qty = _count(shed, crop)
            if qty > 0:
                market.append(["SELL", crop, qty])

        if not hands and hires_today == 0 and _needs_hand(farm, plan, day):
            market.insert(0, ["HIRE"])

        action["market"] = market[:10]
        if hands:
            action["hands"][0] = _hand_action(farm, private, plan, day)
        return action

    return agent


agent = make_agent()
