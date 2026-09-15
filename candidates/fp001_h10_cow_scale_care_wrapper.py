"""FP001 B4 — scale-aware CARE overlays on H10 compact COW scheduler.

The H10 threshold-6 scheduler owns all survival, fertilizer collection, harvest,
setup and liquidation work.  This wrapper spends only H10-idle main-farmer turns
on CARE and optional extra FEED, preserving the causal safety principle used in B3.
"""
from __future__ import annotations

from candidates.fp001_h10_cow_scale_module import (
    TARGET_POSITIONS,
    _count,
    _farm,
    _get,
    _is_shed,
    _move_toward,
    _nearest_shed,
    _tile,
    make_agent as make_h10_agent,
)


def _dist(a, b):
    return abs(int(a[0]) - int(b[0])) + abs(int(a[1]) - int(b[1]))


def make_agent(n_cows=3, mode="NONE"):
    n_cows = int(n_cows)
    mode = str(mode).upper()
    if not 1 <= n_cows <= len(TARGET_POSITIONS):
        raise ValueError(n_cows)
    if mode not in {"NONE", "SURVIVAL", "DAILY"}:
        raise ValueError(mode)

    base = make_h10_agent(n_cows, harvest_threshold=6)
    targets = TARGET_POSITIONS[:n_cows]

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

        cows = []
        for pos in targets:
            t = _tile(farm, pos)
            if not (isinstance(t, dict) and _get(t, "animal", None) == "COW"):
                return action  # H10 setup/survival remains authoritative.
            cows.append((pos, t))

        # First use free capacity to CARE cows already fed today. This is the
        # SURVIVAL treatment and costs no additional WHEAT.
        care_targets = [
            pos for pos, t in cows
            if bool(_get(t, "fed_today", False)) and not bool(_get(t, "cared_today", False))
        ]
        if care_targets:
            target = min(care_targets, key=lambda p: (_dist(farmer, p), targets.index(p)))
            action["farmer"] = ["CARE"] if farmer == tuple(target) else _move_toward(farmer, target)
            return action

        if mode != "DAILY":
            return action

        # DAILY treatment: use remaining idle capacity to feed cows that H10 did
        # not need to feed for survival today; a later idle turn can CARE them.
        feed_targets = [pos for pos, t in cows if not bool(_get(t, "fed_today", False))]
        if not feed_targets:
            return action

        if _count(inv, "WHEAT") <= 0:
            if _count(shed, "WHEAT") > 0:
                if _is_shed(farmer):
                    action["farmer"] = ["PICKUP", "WHEAT", min(n_cows, _count(shed, "WHEAT"))]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
            return action

        target = min(feed_targets, key=lambda p: (_dist(farmer, p), targets.index(p)))
        action["farmer"] = ["FEED"] if farmer == tuple(target) else _move_toward(farmer, target)
        return action

    return agent


agent = make_agent(6, "DAILY")
