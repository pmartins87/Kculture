"""CR-020: monotone append latch for adaptive market-sale placement.

This refinement is derived only from the frozen pre-CR020 CR-014/014B/014C
trajectory diagnostics.  Prediction models, thresholds, eligible products and
sale quantities remain identical to CR-008/CR-011/CR-015.

Placement starts with the CR-015 rule:
- if the frozen R4B base queue begins with SELL, prepend adaptive sales;
- otherwise append adaptive sales.

The sole CR-020 change is monotonicity: once an actual adaptive intervention is
appended in an episode, that player's episode becomes append-locked.  All later
adaptive interventions are appended even if the altered trajectory later
presents a SELL-first base queue.  Thus prefix -> append is allowed, while the
trajectory-sensitive append -> prefix transition is forbidden.

The latch is identity-free, seed-free and outcome-free.  It is set only when an
adaptive sale is actually emitted; turns without an adaptive sale do not alter
it.
"""
from __future__ import annotations

from candidates import cr008_adaptive_frontrun as C

_HISTORY = {0: {}, 1: {}}
_LAST_STEP = {0: -1, 1: -1}
_APPEND_LOCKED = {0: False, 1: False}


def _reset_if_needed(player, step):
    if step == 0 or step < _LAST_STEP[player]:
        _HISTORY[player].clear()
        _APPEND_LOCKED[player] = False
    _LAST_STEP[player] = step


def _remember(player, step, obs):
    _HISTORY[player][step] = C._snapshot(obs)
    cutoff = step - 30
    for k in list(_HISTORY[player]):
        if k < cutoff:
            del _HISTORY[player][k]


def _base_starts_with_sell(market):
    if not market:
        return False
    first = market[0]
    return (
        isinstance(first, list)
        and len(first) >= 2
        and first[0] == "SELL"
    )


def _monotone_adaptive_sales(obs, action, player, step):
    prev = _HISTORY[player].get(step - 24)
    if prev is None:
        return action
    feat = C._public_features(obs, prev, player)
    if not feat:
        return action

    names = C._MODELS["feature_names"]
    market = list(action.get("market") or [])
    already = {
        o[1]
        for o in market
        if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"
    }
    shed = C._get(C._get(obs, "private", {}) or {}, "shed", {}) or {}
    adaptive = []
    capacity = max(0, 10 - len(market))

    # Preserve the frozen adaptive-sale multiset logic exactly.
    for target, item in C.TARGET_TO_ITEM.items():
        if len(adaptive) >= capacity:
            break
        if item in already:
            continue
        try:
            qty = max(0, int(C._get(shed, item, 0) or 0))
        except Exception:
            qty = 0
        if qty <= 0:
            continue
        prob = C._tree_prob(C._MODELS["models"][target], feat, names)
        threshold = float(C._MODELS["thresholds"][target])
        if prob >= threshold:
            adaptive.append(["SELL", item, qty])
            already.add(item)

    if adaptive:
        if _APPEND_LOCKED[player]:
            action["market"] = market + adaptive
        elif _base_starts_with_sell(market):
            action["market"] = adaptive + market
        else:
            action["market"] = market + adaptive
            _APPEND_LOCKED[player] = True
    return action


def agent(obs, config=None):
    player = int(C._get(obs, "player", 0) or 0)
    step = C._clock_step(obs)
    _reset_if_needed(player, step)
    action = C._BASE.agent(obs, config)
    action = _monotone_adaptive_sales(obs, action, player, step)
    _remember(player, step, obs)
    return action
