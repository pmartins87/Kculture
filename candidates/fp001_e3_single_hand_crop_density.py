"""FP001 E3 — one daily hand servicing a compact STRAWBERRY/MELON block.

Frozen intent:
- main farmer remains entirely on the proven H10/B4 COW scheduler;
- at most one first-cost hand is hired per day;
- STRAWBERRY keeps the proven H11 fertilizer schedule (ages 9, 13);
- MELON uses no fertilizer: ordinary WATER can reach its six-unit cap;
- no late replant/rescue ladder.
"""
from __future__ import annotations

from candidates.fp001_h10_cow_scale_care_wrapper import make_agent as make_b4_agent
from candidates.fp001_h10_cow_scale_module import (
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
from candidates.fp001_e2_dedicated_strawberry_hand import (
    _fert_done,
    _filter_fertilizer_sales,
)

STRAWBERRY = "STRAWBERRY"
MELON = "MELON"
STRAW_FERT_AGES = (9, 13)
STRAW_LAST_PRODUCTIVE_AGE = 16
MELON_LAST_WATER_AGE = 12

# Compact snake, disjoint from COW5 positions
# (4,4),(3,4),(2,4),(1,4),(1,3).
CROP_POSITIONS = (
    (4, 3),
    (3, 3),
    (2, 3),
    (2, 2),
    (3, 2),
    (4, 2),
    (4, 1),
    (3, 1),
)


def _live_crop(farm, pos, crop):
    t = _tile(farm, pos)
    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop:
        return t
    return None


def _plan(n_strawberries, n_melons):
    n_s = max(0, int(n_strawberries))
    n_m = max(0, int(n_melons))
    if n_s + n_m > len(CROP_POSITIONS):
        raise ValueError((n_s, n_m))
    crops = [STRAWBERRY] * n_s + [MELON] * n_m
    return list(zip(CROP_POSITIONS[: len(crops)], crops))


def _hand_inventory(private, hand_index=0):
    invs = list(_get(private, "inventories", []) or [])
    idx = hand_index + 1
    return invs[idx] if idx < len(invs) and invs[idx] is not None else {}


def _nearest(pos, positions):
    return min(positions, key=lambda p: (_dist(pos, p), CROP_POSITIONS.index(p)))


def _remaining_straw_fert_need(farm, plan, day):
    need = 0
    for pos, crop in plan:
        if crop != STRAWBERRY:
            continue
        tile = _live_crop(farm, pos, crop)
        raw = _tile(farm, pos)
        if tile is None:
            if day <= 1 and (raw is None or (isinstance(raw, dict) and raw.get("kind") == "WEED")):
                need += len(STRAW_FERT_AGES)
            continue
        age = day - _ival(tile.get("planted_day", day))
        for a in STRAW_FERT_AGES:
            if age <= a and not _fert_done(tile, a):
                need += 1
    return need


def _needs_hand(farm, plan, day):
    for pos, crop in plan:
        raw = _tile(farm, pos)
        tile = _live_crop(farm, pos, crop)
        if tile is None:
            if day <= 1 and (raw is None or (isinstance(raw, dict) and raw.get("kind") == "WEED")):
                return True
            continue
        age = day - _ival(tile.get("planted_day", day))
        yld = _ival(tile.get("yield_units", 0))
        if crop == STRAWBERRY and (age <= STRAW_LAST_PRODUCTIVE_AGE or yld > 0):
            return True
        if crop == MELON and (age <= MELON_LAST_WATER_AGE or yld > 0):
            return True
    return False


def _pending_seed_buys(farm, private, plan, day):
    if day > 1:
        return []
    seeds = _get(private, "seeds", {}) or {}
    missing = {STRAWBERRY: 0, MELON: 0}
    for pos, crop in plan:
        raw = _tile(farm, pos)
        tile = _live_crop(farm, pos, crop)
        if tile is None and (raw is None or (isinstance(raw, dict) and raw.get("kind") == "WEED")):
            missing[crop] += 1
    out = []
    for crop in (STRAWBERRY, MELON):
        q = max(0, missing[crop] - _count(seeds, crop))
        if q > 0:
            out.append(["BUY_SEED", crop, q])
    return out


def _hand_action(farm, private, plan, day):
    hands = list(_get(farm, "hands", []) or [])
    if not hands:
        return ["PASS"]
    pos = tuple(hands[0])
    inv = _hand_inventory(private, 0)
    shed = _get(private, "shed", {}) or {}
    seeds = _get(private, "seeds", {}) or {}

    # On opening setup, WATER the crop we just planted before moving away.
    # Planting day starts at consecutive_unwatered=1, so failing to water it can
    # kill the tile at the first end-of-day refresh.
    if day <= 1:
        for p, crop in plan:
            if p != pos:
                continue
            t = _live_crop(farm, p, crop)
            if t is not None and not bool(t.get("watered_today", False)):
                return ["WATER"]

        # Clear an unexpected opening weed before planting; no late rescue.
        weeds = [p for p, _ in plan if isinstance(_tile(farm, p), dict) and _tile(farm, p).get("kind") == "WEED"]
        if weeds:
            target = _nearest(pos, weeds)
            return ["DIG"] if pos == target else _move_toward(pos, target)

        pending = []
        for p, crop in plan:
            if _tile(farm, p) is None and _count(seeds, crop) > 0:
                pending.append((p, crop))
        if pending:
            targets = [p for p, _ in pending]
            target = _nearest(pos, targets)
            crop = next(c for p, c in pending if p == target)
            return ["PLANT", crop] if pos == target else _move_toward(pos, target)

    # H11 fertilizer is only for STRAWBERRY and has priority on its exact due day.
    due = []
    for p, crop in plan:
        if crop != STRAWBERRY:
            continue
        t = _live_crop(farm, p, crop)
        if t is None:
            continue
        age = day - _ival(t.get("planted_day", day))
        if any(age == a and not _fert_done(t, a) for a in STRAW_FERT_AGES):
            due.append(p)

    if due:
        carried = _count(inv, "FERTILIZER")
        if carried <= 0:
            available = _count(shed, "FERTILIZER")
            if available > 0:
                if _is_shed(pos):
                    return ["PICKUP", "FERTILIZER", min(len(due), available)]
                return _move_toward(pos, _nearest_shed(pos))
        else:
            target = _nearest(pos, due)
            return ["FERTILIZE"] if pos == target else _move_toward(pos, target)

    # WATER all live crops before harvest. MELON ordinary watering reaches the
    # six-unit cap; fertilizer is intentionally not used for MELON in this gate.
    water = []
    for p, crop in plan:
        t = _live_crop(farm, p, crop)
        if t is None or bool(t.get("watered_today", False)):
            continue
        age = day - _ival(t.get("planted_day", day))
        if crop == STRAWBERRY and age <= STRAW_LAST_PRODUCTIVE_AGE:
            water.append(p)
        elif crop == MELON and age <= MELON_LAST_WATER_AGE:
            water.append(p)
    if water:
        target = _nearest(pos, water)
        return ["WATER"] if pos == target else _move_toward(pos, target)

    harvest = []
    for p, crop in plan:
        t = _live_crop(farm, p, crop)
        if t is None or _ival(t.get("yield_units", 0)) <= 0:
            continue
        age = day - _ival(t.get("planted_day", day))
        if crop == STRAWBERRY and age >= 10:
            harvest.append(p)
        elif crop == MELON and age >= 10:
            harvest.append(p)
    if harvest:
        target = _nearest(pos, harvest)
        return ["HARVEST"] if pos == target else _move_toward(pos, target)

    return ["PASS"]


def make_agent(n_cows=5, care_mode="DAILY", n_strawberries=0, n_melons=0):
    n_cows = int(n_cows)
    care_mode = str(care_mode).upper()
    plan = _plan(n_strawberries, n_melons)
    if not plan:
        return make_b4_agent(n_cows, care_mode)

    base = make_b4_agent(n_cows, care_mode)

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

        # Keep only fertilizer that the remaining STRAWBERRY H11 windows need.
        fert_need = _remaining_straw_fert_need(farm, plan, day)
        carried_fert = sum(_count(inv or {}, "FERTILIZER") for inv in invs)
        shed_fert = _count(shed, "FERTILIZER")
        reserve = max(0, fert_need - carried_fert)
        market = _filter_fertilizer_sales(market, max(0, shed_fert - reserve))

        # Preserve all base setup/animal orders before adding opening seeds.
        market.extend(_pending_seed_buys(farm, private, plan, day))

        for crop in (STRAWBERRY, MELON):
            q = _count(shed, crop)
            if q > 0:
                market.append(["SELL", crop, q])

        # At most the first hand of the day. It is placed first in market order so
        # its one-unit cost cannot be starved by later purchases.
        if not hands and hires_today == 0 and _needs_hand(farm, plan, day):
            market.insert(0, ["HIRE"])

        action["market"] = market[:10]
        if hands:
            action["hands"][0] = _hand_action(farm, private, plan, day)
        return action

    return agent


agent = make_agent(5, "DAILY", 0, 6)
