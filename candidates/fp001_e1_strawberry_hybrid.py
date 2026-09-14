"""FP001 E1 — marginal STRAWBERRY hybrid over proven H10/B4 animal controls.

Purpose
-------
Measure whether one early premium crop can add value to the animal-only controls
without silently rewriting the proven animal scheduler.  The crop layer:

* preserves the H10/B4 animal action whenever it is not PASS;
* uses only otherwise-idle main-farmer turns for crop physical work;
* reserves at most two animal-generated fertilizer units for the H11-optimal
  STRAWBERRY fertilizer ages 9 and 13; excess fertilizer is still sold;
* plants only in the opening (day 0/1), so a failed/dead crop is not secretly
  rescued by a later replant;
* sells realized STRAWBERRY from the shed without changing the animal product
  timing rules.

This is deliberately a causal marginal-value gate, not yet the final integrated
elite farm.  Labor and larger crop blocks are separate follow-up treatments.
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
CROP_POSITIONS = ((4, 3), (3, 3))
FERT_AGES = (9, 13)


def _crop_tile(farm, pos):
    tile = _tile(farm, pos)
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == CROP:
        return tile
    return None


def _fert_done(tile, fert_age):
    planted = _ival(tile.get("planted_day", 0))
    # FERTILIZE on age a sets fertilized_until_day to planted+a+2.
    return _ival(tile.get("fertilized_until_day", -1), -1) >= planted + fert_age + 2


def _remaining_fert_need(farm, day, crop_count):
    need = 0
    for pos in CROP_POSITIONS[:crop_count]:
        tile = _crop_tile(farm, pos)
        if tile is None:
            # Reserve only while an opening plant is still feasible.
            if day <= 1:
                need += len(FERT_AGES)
            continue
        age = day - _ival(tile.get("planted_day", day))
        if age <= FERT_AGES[-1]:
            need += sum(0 if _fert_done(tile, a) else 1 for a in FERT_AGES)
    return need


def _filter_fertilizer_sales(market, sellable_qty):
    out = []
    remaining_sellable = max(0, int(sellable_qty))
    for order in list(market or []):
        if not (isinstance(order, list) and len(order) >= 2 and order[0] == "SELL" and order[1] == "FERTILIZER"):
            out.append(order)
            continue
        requested = _ival(order[2], 1) if len(order) >= 3 else 1
        q = min(max(0, requested), remaining_sellable)
        if q > 0:
            out.append(["SELL", "FERTILIZER", q])
            remaining_sellable -= q
    return out


def make_agent(n_cows=4, care_mode="DAILY", strawberry_count=1):
    n_cows = int(n_cows)
    care_mode = str(care_mode).upper()
    strawberry_count = int(strawberry_count)
    if not 0 <= strawberry_count <= len(CROP_POSITIONS):
        raise ValueError(strawberry_count)

    base = make_b4_agent(n_cows, care_mode)
    if strawberry_count == 0:
        return base

    crop_positions = CROP_POSITIONS[:strawberry_count]

    def agent(obs, config=None):
        config = config or {}
        action = base(obs, config)
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        seeds = _get(private, "seeds", {}) or {}
        invs = list(_get(private, "inventories", []) or [])
        inv = invs[0] if invs else {}
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        day = step // turns
        remaining = episode_steps - 1 - step

        # ---- Market layer: buy only the missing opening seed(s). ----
        live_or_planted = sum(1 for pos in crop_positions if _crop_tile(farm, pos) is not None)
        empty_targets = sum(1 for pos in crop_positions if _tile(farm, pos) is None)
        opening_missing = max(0, strawberry_count - live_or_planted - _count(seeds, CROP))
        market = list(action.get("market") or [])
        if day <= 1 and opening_missing > 0 and empty_targets > 0:
            market.append(["BUY_SEED", CROP, opening_missing])

        # Keep exactly the fertilizer still useful to the planned H11 schedule.
        fert_need = _remaining_fert_need(farm, day, strawberry_count)
        inv_fert = _count(inv, "FERTILIZER")
        shed_fert = _count(shed, "FERTILIZER")
        reserve_in_shed = max(0, fert_need - inv_fert)
        sellable_fert = max(0, shed_fert - reserve_in_shed)
        market = _filter_fertilizer_sales(market, sellable_fert)

        # Liquidate realized crop output.  Timing optimization is intentionally
        # deferred so E1 measures the physical/fertilizer hybrid first.
        berries = _count(shed, CROP)
        if berries > 0:
            market.append(["SELL", CROP, berries])
        action["market"] = market[:10]

        # Physical crop work is a marginal overlay: never overwrite a non-PASS
        # animal action in this first causal gate.
        farmer_action = action.get("farmer", ["PASS"])
        if farmer_action != ["PASS"]:
            return action

        # 1) Existing crop tasks. HARVEST before WATER avoids yield-cap loss;
        # WATER before other optional tasks protects the plant from becoming weed.
        crop_rows = []
        for idx, pos in enumerate(crop_positions):
            tile = _crop_tile(farm, pos)
            if tile is None:
                continue
            age = day - _ival(tile.get("planted_day", day))
            crop_rows.append((idx, pos, tile, age))

        harvestable = [(i, p, t, a) for i, p, t, a in crop_rows if _ival(t.get("yield_units", 0)) > 0]
        if harvestable:
            _, pos, _, _ = min(harvestable, key=lambda r: abs(farmer[0]-r[1][0]) + abs(farmer[1]-r[1][1]))
            action["farmer"] = ["HARVEST"] if farmer == tuple(pos) else _move_toward(farmer, pos)
            return action

        dry = [(i, p, t, a) for i, p, t, a in crop_rows if not bool(t.get("watered_today", False))]
        if dry:
            _, pos, _, _ = min(dry, key=lambda r: abs(farmer[0]-r[1][0]) + abs(farmer[1]-r[1][1]))
            action["farmer"] = ["WATER"] if farmer == tuple(pos) else _move_toward(farmer, pos)
            return action

        # 2) Exact H11 fertilizer ages 9 and 13. Prefetch one day before the first
        # required age so shed travel does not consume the only useful turn.
        fert_due = []
        for idx, pos, tile, age in crop_rows:
            for fert_age in FERT_AGES:
                if age == fert_age and not _fert_done(tile, fert_age):
                    fert_due.append((idx, pos, tile, age))
                    break
        if fert_due:
            if _count(inv, "FERTILIZER") <= 0:
                if shed_fert > 0:
                    if _is_shed(farmer):
                        action["farmer"] = ["PICKUP", "FERTILIZER", min(fert_need, shed_fert)]
                    else:
                        action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                return action
            _, pos, _, _ = min(fert_due, key=lambda r: abs(farmer[0]-r[1][0]) + abs(farmer[1]-r[1][1]))
            action["farmer"] = ["FERTILIZE"] if farmer == tuple(pos) else _move_toward(farmer, pos)
            return action

        if any(age >= 8 and age <= FERT_AGES[-1] for _, _, _, age in crop_rows) and fert_need > inv_fert:
            if shed_fert > 0:
                if _is_shed(farmer):
                    action["farmer"] = ["PICKUP", "FERTILIZER", min(fert_need - inv_fert, shed_fert)]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                return action

        # 3) Opening setup only. Weed can be cleared day0/1, but there is no late
        # replant rescue after the causal treatment has failed.
        if day <= 1:
            for pos in crop_positions:
                tile = _tile(farm, pos)
                if _crop_tile(farm, pos) is not None:
                    continue
                if farmer != tuple(pos):
                    action["farmer"] = _move_toward(farmer, pos)
                    return action
                if isinstance(tile, dict) and tile.get("kind") == "WEED":
                    action["farmer"] = ["DIG"]
                    return action
                if tile is None and _count(seeds, CROP) > 0:
                    action["farmer"] = ["PLANT", CROP]
                    return action

        return action

    return agent


agent = make_agent(4, "DAILY", 1)
