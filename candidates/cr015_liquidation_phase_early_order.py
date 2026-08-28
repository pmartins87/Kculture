"""CR-015: selective early-order adaptation only in base liquidation phase.

Frozen refinement derived from CR-014/014B/014C plus official Kaggriculture
market semantics. Prediction model, thresholds, eligible products and adaptive
quantities are identical to CR-008/CR-011. The only new decision is placement:

- if the frozen R4B base market queue already begins with SELL, prepend the
  adaptive sale(s), as CR-011 does;
- otherwise append them, as CR-008 does.

Rationale: prepending a sale to a spending-first queue can inject cash before
HIRE/BUY actions and shifts every base order to a later market position. Both
are high-leverage side effects. A SELL-first base queue is already in a
liquidation phase, so CR-015 permits the proven front-run only there.

No opponent identity, opponent package, seed, tuned price cutoff or terminal
outcome is used by this gate.
"""
from __future__ import annotations

import copy
from candidates import cr008_adaptive_frontrun as C

_HISTORY = {0: {}, 1: {}}
_LAST_STEP = {0: -1, 1: -1}


def _reset_if_needed(player, step):
    if step == 0 or step < _LAST_STEP[player]:
        _HISTORY[player].clear()
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


def _selective_adaptive_sales(obs, action, player, step):
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

    # Preserve frozen CR-008/CR-011 target iteration and adaptive multiset.
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
        if _base_starts_with_sell(market):
            action["market"] = adaptive + market
        else:
            action["market"] = market + adaptive
    return action


def agent(obs, config=None):
    player = int(C._get(obs, "player", 0) or 0)
    step = C._clock_step(obs)
    _reset_if_needed(player, step)
    action = C._BASE.agent(obs, config)
    action = _selective_adaptive_sales(obs, action, player, step)
    _remember(player, step, obs)
    return action
