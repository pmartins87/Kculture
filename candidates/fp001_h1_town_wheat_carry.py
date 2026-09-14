"""FP001 H1 — town-pulse WHEAT carry, first-principles causal probe.

This is intentionally NOT a production farm policy.  It uses PASS for every
physical action and only trades WHEAT around mechanically known town-consumption
pulses.  The purpose is to isolate whether the market mechanism can be captured
by a legal runtime agent.

No competitor replay, identity, rating, EpisodeId, hidden seed, future state, or
opponent-private state is used.
"""
from __future__ import annotations

import math

TARGET_QTY = 50
PRICE_FLOOR = 1
WHEAT_SHOPS = {
    "BAKERY",
    "PIZZA_SHOP",
    "BRUNCH_SPOT",
    "ICE_CREAM_SHOP",
    "FARMERS_MARKET",
}

DEFAULT_WHEAT_PARAMS = {
    "base": 25,
    "I0": 10_000,
    "T": 400,
    "below_func": "sqrt",
    "below_target": 0.80,
    "above_func": "log",
    "above_target": 0.20,
}


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default


def _int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _step(obs, config) -> int:
    raw = _get(obs, "step", None)
    if raw is not None:
        return max(0, _int(raw, 0))
    turns = max(1, _int(_get(config, "turnsPerDay", 24), 24))
    day = max(0, _int(_get(obs, "day", 0), 0))
    hour = max(0, _int(_get(obs, "hour", 0), 0))
    return day * turns + hour


def _shape(name: str, x: float, T: float) -> float:
    x = max(0.0, x)
    if name == "linear":
        return x
    if name == "sq":
        return x * x
    if name == "sqrt":
        return math.sqrt(x)
    if name == "log":
        return math.log1p(x)
    if name == "log10":
        return math.log10(1.0 + x)
    if name == "hinge":
        if T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _wheat_params(config):
    p = dict(DEFAULT_WHEAT_PARAMS)
    overrides = _get(config, "marketParams", {}) or {}
    patch = _get(overrides, "WHEAT", {}) or {}
    if isinstance(patch, dict):
        p.update(patch)
    else:
        for key in tuple(p):
            value = _get(patch, key, None)
            if value is not None:
                p[key] = value
    return p


def _wheat_price(inventory: int, config) -> int:
    p = _wheat_params(config)
    base = float(p["base"])
    I0 = int(p["I0"])
    T = float(p["T"])
    if inventory < I0:
        f = p["below_func"]
        denom = _shape(f, T, T)
        amp = 0.0 if denom == 0 else float(p["below_target"]) * base / denom
        value = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        denom = _shape(f, T, T)
        amp = 0.0 if denom == 0 else float(p["above_target"]) * base / denom
        value = base - amp * _shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(value)))


def _town_wheat_demand(step: int, obs, config) -> int:
    demand = 0
    shop_interval = max(1, _int(_get(config, "townShopSellInterval", 4), 4))
    center_interval = max(1, _int(_get(config, "townCenterSellInterval", 24), 24))

    if step % shop_interval == 0:
        town = _get(obs, "town", {}) or {}
        for shop in list(_get(town, "unlocked_shops", []) or []):
            if shop in WHEAT_SHOPS:
                demand += 1
    if step % center_interval == 0:
        demand += 1
    return demand


def _pass_action(obs):
    player = max(0, _int(_get(obs, "player", 0), 0))
    farms = _get(obs, "farms", []) or []
    hands_n = 0
    if player < len(farms):
        hands_n = len(_get(farms[player], "hands", []) or [])
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hands_n)], "market": []}


def _affordable_buy_qty(obs, config, target: int) -> int:
    player = max(0, _int(_get(obs, "player", 0), 0))
    farms = _get(obs, "farms", []) or []
    if player >= len(farms):
        return 0
    money = float(_get(farms[player], "money", 0) or 0)

    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    capacity = max(1, _int(_get(config, "shedCapacity", 100), 100))
    used = 0
    try:
        used = sum(max(0, int(v or 0)) for v in shed.values())
    except AttributeError:
        used = 0
    free = max(0, capacity - used)
    target = min(max(0, int(target)), free)
    if target <= 0:
        return 0

    market = _get(obs, "market", {}) or {}
    invs = _get(market, "inventory", {}) or {}
    inv = _int(_get(invs, "WHEAT", 10_000), 10_000)

    spent = 0
    qty = 0
    for _ in range(target):
        quote = _wheat_price(inv - 1, config)
        if spent + quote > money:
            break
        spent += quote
        inv -= 1
        qty += 1
    return qty


def agent(obs, config=None):
    config = config or {}
    action = _pass_action(obs)
    step = _step(obs, config)
    episode_steps = max(1, _int(_get(config, "episodeSteps", 720), 720))

    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    carried = max(0, _int(_get(shed, "WHEAT", 0), 0))

    # Close the previous pulse trade first.  In the default environment town
    # pulses are not consecutive, so no same-step sell/rebuy is needed for H1.
    if step > 0 and _town_wheat_demand(step - 1, obs, config) > 0 and carried > 0:
        action["market"] = [["SELL", "WHEAT", carried]]
        return action

    # Do not initiate a carry that cannot be closed before terminal reward.
    if step + 1 >= episode_steps:
        return action

    demand = _town_wheat_demand(step, obs, config)
    if demand <= 0 or carried > 0:
        return action

    qty = _affordable_buy_qty(obs, config, TARGET_QTY)
    if qty > 0:
        action["market"] = [["BUY_PRODUCT", "WHEAT", qty]]
    return action
