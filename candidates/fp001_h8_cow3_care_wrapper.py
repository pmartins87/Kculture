"""FP001 H8 B3 — CARE overlays for the proven COW3/H0 physical backbone.

Uses the zero-lineage COW3 scheduler as the safety baseline.  CARE work is added
only in otherwise idle main-farmer turns, so survival/collection/harvest tasks
from the proven B2 scheduler keep priority.

Modes:
- NONE: exact B2 COW3/H0 baseline.
- SURVIVAL: CARE after baseline survival FEED whenever an idle turn is available.
- DAILY: in idle turns, additionally FEED + CARE every cow each day to bank more
  bonus for the next fed production tick.
"""
from __future__ import annotations

from candidates.fp001_h8_multi_animal_module import (
    TARGET_POSITIONS,
    _farm,
    _get,
    _is_shed_adjacent,
    _move_toward,
    _nearest_shed,
    _positive_count,
    _tile,
    make_agent as make_base_agent,
)


def make_agent(mode="NONE"):
    mode = str(mode).upper()
    if mode not in {"NONE", "SURVIVAL", "DAILY"}:
        raise ValueError(mode)

    base = make_base_agent(("COW", "COW", "COW"), hands_target=0)

    def agent(obs, config=None):
        action = base(obs, config)
        if mode == "NONE":
            return action

        # Never steal a turn from the B2 safety scheduler.
        if action.get("farmer") != ["PASS"]:
            return action

        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        invs = list(_get(private, "inventories", []) or [])
        inv = invs[0] if invs else {}
        farmer_pos = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        cows = []
        for pos in TARGET_POSITIONS[:3]:
            tile = _tile(farm, pos)
            if not (isinstance(tile, dict) and _get(tile, "animal", None) == "COW"):
                return action  # setup still incomplete; baseline owns the turn.
            cows.append((pos, tile))

        # 1) CARE already-fed cows first.  This never spends extra WHEAT and
        # converts an otherwise idle turn into a banked production bonus.
        care_targets = [
            pos for pos, tile in cows
            if bool(_get(tile, "fed_today", False)) and not bool(_get(tile, "cared_today", False))
        ]
        if care_targets:
            target = min(care_targets, key=lambda p: abs(farmer_pos[0] - p[0]) + abs(farmer_pos[1] - p[1]))
            action["farmer"] = ["CARE"] if farmer_pos == tuple(target) else _move_toward(farmer_pos, target)
            return action

        if mode != "DAILY":
            return action

        # 2) DAILY mode uses remaining idle capacity to feed cows that have not
        # yet been fed today, so a later idle turn can CARE them.  We deliberately
        # do not replace fertilizer/harvest/survival work.
        feed_targets = [pos for pos, tile in cows if not bool(_get(tile, "fed_today", False))]
        if not feed_targets:
            return action

        # Need WHEAT in the main inventory.  Base scheduler maintains a shared
        # WHEAT buffer; retrieve it from shed when necessary.
        if _positive_count(inv, "WHEAT") <= 0:
            if _positive_count(shed, "WHEAT") > 0:
                if _is_shed_adjacent(farmer_pos):
                    action["farmer"] = ["PICKUP", "WHEAT", min(3, _positive_count(shed, "WHEAT"))]
                else:
                    action["farmer"] = _move_toward(farmer_pos, _nearest_shed(farmer_pos))
            return action

        target = min(feed_targets, key=lambda p: abs(farmer_pos[0] - p[0]) + abs(farmer_pos[1] - p[1]))
        action["farmer"] = ["FEED"] if farmer_pos == tuple(target) else _move_toward(farmer_pos, target)
        return action

    return agent


agent = make_agent("DAILY")
