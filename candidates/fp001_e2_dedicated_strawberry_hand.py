"""FP001 E2 — dedicated farm-hand STRAWBERRY overlay.

The main farmer remains fully controlled by the proven H10/B4 animal scheduler.
A single cheap daily hand is hired only while one opening STRAWBERRY has useful
work remaining.  This isolates whether labor unlocks H11 crop/fertilizer value
without stealing FEED/CARE/harvest turns from the animal backbone.
"""
from __future__ import annotations

from candidates.fp001_h10_cow_scale_care_wrapper import make_agent as make_b4_agent
from candidates.fp001_h10_cow_scale_module import (
    _count,
    _farm,
    _get,
    _is_shed,
    _ival,
    _move_toward,
    _nearest_shed,
    _step,
    _tile,
)

CROP = "STRAWBERRY"
CROP_POS = (4, 3)
FERT_AGES = (9, 13)
LAST_PRODUCTIVE_AGE = 16


def _crop_tile(farm):
    tile = _tile(farm, CROP_POS)
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == CROP:
        return tile
    return None


def _fert_done(tile, fert_age):
    planted = _ival(tile.get("planted_day", 0))
    return _ival(tile.get("fertilized_until_day", -1), -1) >= planted + fert_age + 2


def _remaining_fert_need(farm, day):
    tile = _crop_tile(farm)
    if tile is None:
        return len(FERT_AGES) if day <= 1 else 0
    age = day - _ival(tile.get("planted_day", day))
    if age > FERT_AGES[-1]:
        return 0
    return sum(0 if _fert_done(tile, a) else 1 for a in FERT_AGES)


def _filter_fertilizer_sales(market, sellable_qty):
    out = []
    remaining = max(0, int(sellable_qty))
    for order in list(market or []):
        if not (
            isinstance(order, list)
            and len(order) >= 2
            and order[0] == "SELL"
            and order[1] == "FERTILIZER"
        ):
            out.append(order)
            continue
        requested = _ival(order[2], 1) if len(order) >= 3 else 1
        q = min(max(0, requested), remaining)
        if q > 0:
            out.append(["SELL", "FERTILIZER", q])
            remaining -= q
    return out


def _needs_hand(farm, day, seeds):
    tile = _crop_tile(farm)
    raw = _tile(farm, CROP_POS)
    if tile is None:
        # Opening treatment only. If seed is not yet purchased, the HIRE and
        # BUY_SEED can occur in the same market phase; the hand acts next turn.
        return day <= 1 and (raw is None or (isinstance(raw, dict) and raw.get("kind") == "WEED"))
    age = day - _ival(tile.get("planted_day", day))
    return age <= LAST_PRODUCTIVE_AGE or _ival(tile.get("yield_units", 0)) > 0


def _hand_inventory(private, hand_index):
    invs = list(_get(private, "inventories", []) or [])
    idx = hand_index + 1  # inventory[0] belongs to the main farmer
    return invs[idx] if idx < len(invs) and invs[idx] is not None else {}


def _hand_action(farm, private, hand_index, day):
    hands = list(_get(farm, "hands", []) or [])
    if hand_index >= len(hands):
        return ["PASS"]
    pos = tuple(hands[hand_index])
    inv = _hand_inventory(private, hand_index)
    shed = _get(private, "shed", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    raw = _tile(farm, CROP_POS)
    tile = _crop_tile(farm)

    # Opening setup: no late replant rescue.
    if tile is None:
        if day > 1:
            return ["PASS"]
        if pos != CROP_POS:
            return _move_toward(pos, CROP_POS)
        if isinstance(raw, dict) and raw.get("kind") == "WEED":
            return ["DIG"]
        if raw is None and _count(seeds, CROP) > 0:
            return ["PLANT", CROP]
        return ["PASS"]

    age = day - _ival(tile.get("planted_day", day))

    # H11 fertilizer schedule has first priority on exact due days.  A fresh
    # daily hand begins near the shed, so pickup/travel/fertilize all fit well
    # within the 24-turn day without requiring cross-day carried inventory.
    due = next((a for a in FERT_AGES if age == a and not _fert_done(tile, a)), None)
    if due is not None:
        if _count(inv, "FERTILIZER") <= 0:
            if _count(shed, "FERTILIZER") > 0:
                if _is_shed(pos):
                    return ["PICKUP", "FERTILIZER", 1]
                return _move_toward(pos, _nearest_shed(pos))
            # No fertilizer physically available yet: continue crop survival;
            # do not buy fertilizer in this causal gate.
        else:
            if pos == CROP_POS:
                return ["FERTILIZE"]
            return _move_toward(pos, CROP_POS)

    # Water on every productive day. This prevents the E1 failure mode in which
    # residual animal work starved crop maintenance.
    if age <= LAST_PRODUCTIVE_AGE and not bool(tile.get("watered_today", False)):
        if pos == CROP_POS:
            return ["WATER"]
        return _move_toward(pos, CROP_POS)

    # Harvest after today's mandatory maintenance. Yield then rides the hand's
    # inventory until automatic end-of-day shed drop; it is sold next turn.
    if _ival(tile.get("yield_units", 0)) > 0:
        if pos == CROP_POS:
            return ["HARVEST"]
        return _move_toward(pos, CROP_POS)

    return ["PASS"]


def make_agent(n_cows=5, care_mode="DAILY", strawberry=True, dedicated_hand=True):
    n_cows = int(n_cows)
    care_mode = str(care_mode).upper()
    strawberry = bool(strawberry)
    dedicated_hand = bool(dedicated_hand)

    if not strawberry:
        return make_b4_agent(n_cows, care_mode)
    if not dedicated_hand:
        # Preserve the exact E1 no-hand treatment for matched attribution.
        from candidates.fp001_e1_strawberry_hybrid import make_agent as make_e1_agent
        return make_e1_agent(n_cows, care_mode, 1)

    base = make_b4_agent(n_cows, care_mode)

    def agent(obs, config=None):
        config = config or {}
        action = base(obs, config)
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        seeds = _get(private, "seeds", {}) or {}
        invs = list(_get(private, "inventories", []) or [])

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns
        hands = list(_get(farm, "hands", []) or [])
        hires_today = max(0, _ival(_get(farm, "hires_today", 0)))

        # Base scheduler never owns hand actions. Explicit PASS slots make the
        # action shape valid for all currently existing hands.
        action["hands"] = [["PASS"] for _ in hands]
        market = list(action.get("market") or [])

        # Buy only the one opening seed if still missing.
        live = _crop_tile(farm) is not None
        raw = _tile(farm, CROP_POS)
        if day <= 1 and not live and raw is None and _count(seeds, CROP) <= 0:
            market.append(["BUY_SEED", CROP, 1])

        # Preserve animal-generated fertilizer for remaining H11 applications.
        fert_need = _remaining_fert_need(farm, day)
        carried_fert = sum(_count(inv or {}, "FERTILIZER") for inv in invs)
        shed_fert = _count(shed, "FERTILIZER")
        reserve_in_shed = max(0, fert_need - carried_fert)
        market = _filter_fertilizer_sales(market, max(0, shed_fert - reserve_in_shed))

        berries = _count(shed, CROP)
        if berries > 0:
            market.append(["SELL", CROP, berries])

        # One bounded daily HIRE. Put it first so the one-unit labor cost is paid
        # before other purchases; this avoids a low-cash market order starving the
        # causal treatment. The rest of the base market order remains unchanged.
        if not hands and hires_today == 0 and _needs_hand(farm, day, seeds):
            market.insert(0, ["HIRE"])

        action["market"] = market[:10]

        # A hand hired this market phase does not have an action slot until the
        # next observation. Once present, only hand 0 receives crop work.
        if hands:
            action["hands"][0] = _hand_action(farm, private, 0, day)

        return action

    return agent


agent = make_agent(5, "DAILY", True, True)
