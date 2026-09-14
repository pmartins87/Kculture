"""FP001 H8 — mechanics-derived multi-animal runtime scheduler.

Gate purpose: scale the proven H8 animal/fertilizer mechanism from one animal to
2-3 animals while charging real movement and optional daily HIRE costs.

This module is zero-lineage: fixed target tiles and all decisions come from
official mechanics/current own observation, never competitor replay routes.
"""
from __future__ import annotations

from collections import Counter

ANIMAL_META = {
    "GOOSE": {"structure": "COOP", "product": "EGG"},
    "COW": {"structure": "PASTURE", "product": "MILK"},
    "SHEEP": {"structure": "PASTURE", "product": "WOOL"},
}

# All are in the initially unlocked NW quadrant on the default 10x10 board.
# (4,4) is also shed-adjacent; the others deliberately introduce pathing.
TARGET_POSITIONS = ((4, 4), (3, 4), (4, 3))
SHED_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError, IndexError):
            return default


def _ival(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _farm(obs):
    player = max(0, _ival(_get(obs, "player", 0)))
    farms = _get(obs, "farms", []) or []
    return farms[player] if player < len(farms) else {}


def _step(obs, config):
    raw = _get(obs, "step", None)
    if raw is not None:
        return max(0, _ival(raw))
    turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
    return max(0, _ival(_get(obs, "day", 0))) * turns + max(0, _ival(_get(obs, "hour", 0)))


def _inventories(private):
    return list(_get(private, "inventories", []) or [])


def _unit_inv(private, idx):
    invs = _inventories(private)
    return invs[idx] if idx < len(invs) and invs[idx] is not None else {}


def _tile(farm, pos):
    x, y = pos
    tiles = _get(farm, "tiles", []) or []
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def _manhattan(a, b):
    return abs(_ival(a[0]) - _ival(b[0])) + abs(_ival(a[1]) - _ival(b[1]))


def _move_toward(pos, target):
    x, y = _ival(pos[0]), _ival(pos[1])
    tx, ty = _ival(target[0]), _ival(target[1])
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _is_shed_adjacent(pos):
    return tuple(pos) in SHED_ACCESS


def _nearest_shed(pos):
    return min(SHED_ACCESS, key=lambda p: _manhattan(pos, p))


def _positive_count(d, key):
    return max(0, _ival(_get(d, key, 0)))


def _base_action(farm):
    hands = list(_get(farm, "hands", []) or [])
    return {
        "farmer": ["PASS"],
        "hands": [["PASS"] for _ in hands],
        "market": [],
    }


def _placed_counts(farm, species_tuple):
    counts = Counter()
    for idx, species in enumerate(species_tuple):
        tile = _tile(farm, TARGET_POSITIONS[idx])
        if isinstance(tile, dict) and _get(tile, "animal", None) == species:
            counts[species] += 1
    return counts


def make_agent(species_tuple=("COW", "COW", "COW"), hands_target=2):
    species_tuple = tuple(species_tuple)
    if not (1 <= len(species_tuple) <= len(TARGET_POSITIONS)):
        raise ValueError("species_tuple must contain 1..3 animals")
    if any(s not in ANIMAL_META for s in species_tuple):
        raise ValueError(species_tuple)
    hands_target = max(0, min(2, int(hands_target)))
    desired = Counter(species_tuple)
    products = tuple(sorted({ANIMAL_META[s]["product"] for s in species_tuple}))

    def agent(obs, config=None):
        config = config or {}
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        action = _base_action(farm)

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = episode_steps - 1 - step

        farmer_pos = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])
        hands = [tuple(p) for p in (_get(farm, "hands", []) or [])]
        positions = [farmer_pos, *hands]
        invs = [_unit_inv(private, i) for i in range(len(positions))]

        market = []

        # Liquidate realized output.  Animal products wait for hour 1 so the
        # deterministic town-center pulse at hour 0 happens first. Fertilizer
        # has no town demand, so it is sold as soon as it reaches the shed.
        fert_shed = _positive_count(shed, "FERTILIZER")
        if fert_shed:
            market.append(["SELL", "FERTILIZER", fert_shed])
        for product in products:
            qty = _positive_count(shed, product)
            if qty and (hour == 1 or remaining <= 8):
                market.append(["SELL", product, qty])

        # Count animals across placed tiles, shed and every worker inventory so
        # setup BUYs cannot duplicate animals that are merely in transit.
        placed = _placed_counts(farm, species_tuple)
        available = Counter(placed)
        for species in desired:
            available[species] += _positive_count(shed, species)
            for inv in invs:
                available[species] += _positive_count(inv, species)
        for species, want in desired.items():
            missing = max(0, want - available[species])
            if missing:
                market.append(["BUY_ANIMAL", species, missing])

        # Keep a modest shared wheat buffer. This charges real market prices but
        # avoids pretending feed appears inside worker inventories for free.
        wheat_total = _positive_count(shed, "WHEAT") + sum(_positive_count(inv, "WHEAT") for inv in invs)
        wheat_floor = max(4, 2 * len(species_tuple))
        wheat_target = max(8, 6 * len(species_tuple))
        if wheat_total < wheat_floor and remaining > turns:
            market.append(["BUY_PRODUCT", "WHEAT", wheat_target - wheat_total])

        # -------- Setup gate: main farmer only; no cheap-labor advantage yet. --------
        incomplete = None
        for idx, species in enumerate(species_tuple):
            tile = _tile(farm, TARGET_POSITIONS[idx])
            if not (isinstance(tile, dict) and _get(tile, "animal", None) == species):
                incomplete = (idx, species, TARGET_POSITIONS[idx], tile)
                break

        if incomplete is not None:
            idx, species, target, target_tile = incomplete
            structure = ANIMAL_META[species]["structure"]
            build_op = "BUILD_COOP" if structure == "COOP" else "BUILD_PASTURE"
            main_inv = invs[0] if invs else {}

            # Build/clear the target first.
            target_ready = isinstance(target_tile, dict) and _get(target_tile, "kind", None) == structure and _get(target_tile, "animal", None) is None
            if not target_ready:
                if tuple(farmer_pos) != tuple(target):
                    action["farmer"] = _move_toward(farmer_pos, target)
                elif target_tile is None:
                    action["farmer"] = [build_op]
                elif isinstance(target_tile, dict) and _get(target_tile, "animal", None) is None:
                    action["farmer"] = ["DIG"]
                else:
                    action["farmer"] = ["PASS"]
                action["market"] = market[:10]
                return action

            # Structure is ready: fetch one animal from shed, then return/place.
            if _positive_count(main_inv, species) > 0:
                if tuple(farmer_pos) == tuple(target):
                    action["farmer"] = ["PLACE", species]
                else:
                    action["farmer"] = _move_toward(farmer_pos, target)
            elif _positive_count(shed, species) > 0:
                if _is_shed_adjacent(farmer_pos):
                    action["farmer"] = ["PICKUP", species, 1]
                else:
                    action["farmer"] = _move_toward(farmer_pos, _nearest_shed(farmer_pos))
            action["market"] = market[:10]
            return action

        # -------- Operational phase. --------
        current_hands = len(hands)
        hires_today = max(0, _ival(_get(farm, "hires_today", 0)))
        if hands_target > current_hands and hires_today < hands_target and remaining > turns:
            for _ in range(hands_target - current_hands):
                market.append(["HIRE"])

        # Terminal liquidation: stop opening new tasks early enough to return
        # carried output to the shed, then the next turn's market can sell it.
        if remaining <= 8:
            for unit_idx, pos in enumerate(positions):
                inv = invs[unit_idx]
                positive_inv = any(_positive_count(inv, k) > 0 for k in ("FERTILIZER", *products))
                if positive_inv:
                    if _is_shed_adjacent(pos):
                        unit_action = ["DROP"]
                    else:
                        unit_action = _move_toward(pos, _nearest_shed(pos))
                    if unit_idx == 0:
                        action["farmer"] = unit_action
                    else:
                        action["hands"][unit_idx - 1] = unit_action
            action["market"] = market[:10]
            return action

        # New hands spawn at shed access. Give empty workers a small wheat load
        # before assigning animal tasks. Reserve shed stock sequentially so two
        # workers cannot both assume the same wheat unit.
        reserved_units = set()
        shed_wheat_available = _positive_count(shed, "WHEAT")
        for unit_idx, pos in enumerate(positions):
            if shed_wheat_available <= 0:
                break
            if _is_shed_adjacent(pos) and _positive_count(invs[unit_idx], "WHEAT") == 0:
                take = min(2, shed_wheat_available)
                unit_action = ["PICKUP", "WHEAT", take]
                if unit_idx == 0:
                    action["farmer"] = unit_action
                else:
                    action["hands"][unit_idx - 1] = unit_action
                reserved_units.add(unit_idx)
                shed_wheat_available -= take

        # Generate simultaneous legal tasks from current own state.
        tasks = []
        for idx, species in enumerate(species_tuple):
            pos = TARGET_POSITIONS[idx]
            tile = _tile(farm, pos)
            if not (isinstance(tile, dict) and _get(tile, "animal", None) == species):
                continue
            if max(0, _ival(_get(tile, "consecutive_unfed", 0))) >= 1 and not bool(_get(tile, "fed_today", False)):
                tasks.append((100, "FEED", pos, species))
            if bool(_get(tile, "fertilizer_available", False)):
                tasks.append((70, "COLLECT_FERTILIZER", pos, species))
            yld = max(0, _ival(_get(tile, "yield_units", 0)))
            if yld > 0:
                tasks.append((50 + min(10, yld), "HARVEST", pos, species))
        tasks.sort(key=lambda t: (-t[0], t[2][1], t[2][0], t[1]))

        free_units = [i for i in range(len(positions)) if i not in reserved_units]
        assignments = {}
        for priority, op, target, species in tasks:
            if not free_units:
                break
            def cost(unit_idx):
                c = _manhattan(positions[unit_idx], target)
                if op == "FEED" and _positive_count(invs[unit_idx], "WHEAT") <= 0:
                    c += 5
                return (c, unit_idx)
            unit_idx = min(free_units, key=cost)
            free_units.remove(unit_idx)
            assignments[unit_idx] = (op, target)

        for unit_idx, (op, target) in assignments.items():
            pos = positions[unit_idx]
            inv = invs[unit_idx]
            if op == "FEED" and _positive_count(inv, "WHEAT") <= 0:
                shed_target = _nearest_shed(pos)
                if _is_shed_adjacent(pos) and _positive_count(shed, "WHEAT") > 0:
                    unit_action = ["PICKUP", "WHEAT", 1]
                else:
                    unit_action = _move_toward(pos, shed_target)
            elif tuple(pos) == tuple(target):
                unit_action = [op]
            else:
                unit_action = _move_toward(pos, target)

            if unit_idx == 0:
                action["farmer"] = unit_action
            else:
                action["hands"][unit_idx - 1] = unit_action

        action["market"] = market[:10]
        return action

    return agent


agent = make_agent(("COW", "COW", "COW"), hands_target=2)
