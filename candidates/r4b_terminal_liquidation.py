"""Kculture R4B: terminal-capacity liquidation wrapper over frozen COK V8.

Research-only candidate. The wrapped base is fetched and SHA-256 verified by
``tools/fetch_public_opponents.py`` before evaluation. This file is not yet a
standalone Kaggle submission.

Kculture change: only at the last executable step (718), choose the subset of
shed-adjacent actors whose full-inventory DROP maximizes approximate sellable
value under the 100-item shed capacity, then replace market activity with a
complete sale of projected sellable shed stock.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "artifacts/public_opponents/cok_v8_779caae.py"
SELLABLE = (
    "MELON",
    "STRAWBERRY",
    "MILK",
    "WOOL",
    "TOMATO",
    "EGG",
    "CARROT",
    "WHEAT",
    "FERTILIZER",
)
TERMINAL_STEP = 718


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4b_cok_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen R4A base: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BASE = _load_base()


def _mapping_get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default


def _inventory_value(inventory, prices):
    value = 0.0
    for item in SELLABLE:
        try:
            quantity = max(0, int(_mapping_get(inventory, item, 0) or 0))
            price = max(0.0, float(_mapping_get(prices, item, 0) or 0))
        except (TypeError, ValueError):
            continue
        value += quantity * price
    return value


def _inventory_weight(inventory):
    total = 0
    for quantity in dict(inventory or {}).values():
        try:
            total += max(0, int(quantity or 0))
        except (TypeError, ValueError):
            continue
    return total


def _choose_drop_subset(eligible, room, prices):
    """0/1 knapsack over actors; DROP is all-or-nothing per actor."""
    room = max(0, int(room))
    # dp[capacity] = (approx_value, tuple(actor_indexes))
    dp = [(0.0, tuple()) for _ in range(room + 1)]
    for actor_index, inventory in eligible:
        weight = _inventory_weight(inventory)
        value = _inventory_value(inventory, prices)
        if weight <= 0 or weight > room or value <= 0:
            continue
        previous = list(dp)
        for capacity in range(weight, room + 1):
            candidate_value = previous[capacity - weight][0] + value
            if candidate_value > dp[capacity][0]:
                dp[capacity] = (
                    candidate_value,
                    previous[capacity - weight][1] + (actor_index,),
                )
    best = max(dp, key=lambda row: (row[0], -len(row[1])))
    return set(best[1])


def _terminal_liquidate(obs, base_action):
    action = copy.deepcopy(base_action)
    seat = int(_mapping_get(obs, "player", 0) or 0)
    farms = list(_mapping_get(obs, "farms", []) or [])
    farm = farms[seat] if 0 <= seat < len(farms) else {}
    private = _mapping_get(obs, "private", {}) or {}
    shed = dict(_mapping_get(private, "shed", {}) or {})
    inventories = list(_mapping_get(private, "inventories", []) or [])
    positions = [
        _mapping_get(farm, "farmer", [0, 0]),
        *list(_mapping_get(farm, "hands", []) or []),
    ]
    tiles = list(_mapping_get(farm, "tiles", []) or [])
    board_size = len(tiles) or 10
    prices = _mapping_get(_mapping_get(obs, "market", {}) or {}, "prices", {}) or {}

    units = [
        list(action.get("farmer") or ["PASS"]),
        *[list(order or ["PASS"]) for order in (action.get("hands") or [])],
    ]
    while len(units) < len(positions):
        units.append(["PASS"])

    used = _inventory_weight(shed)
    room = max(0, 100 - used)
    eligible = []
    for actor_index, position in enumerate(positions):
        inventory = inventories[actor_index] if actor_index < len(inventories) else {}
        if (
            actor_index < len(units)
            and _BASE._v5_is_shed_access(position, board_size)
            and _inventory_weight(inventory) > 0
        ):
            eligible.append((actor_index, inventory))

    selected = _choose_drop_subset(eligible, room, prices)
    eligible_indexes = {actor_index for actor_index, _ in eligible}
    for actor_index in eligible_indexes:
        if actor_index in selected:
            units[actor_index] = ["DROP"]
        elif units[actor_index] and units[actor_index][0] == "DROP":
            # A low-value DROP can crowd higher-value stock out of a full shed.
            units[actor_index] = ["PASS"]

    action["farmer"] = units[0] if units else ["PASS"]
    action["hands"] = units[1:len(positions)]

    projected = _BASE._v5_projected_shed(obs, action)
    sale_orders = []
    # Highest current notional revenue first. With nine sellable types the
    # maxMarketOrdersPerTurn=10 cap cannot discard a product sale.
    ranked = []
    for item in SELLABLE:
        try:
            quantity = max(0, int(projected.get(item, 0) or 0))
            price = max(0.0, float(_mapping_get(prices, item, 0) or 0))
        except (TypeError, ValueError):
            continue
        if quantity > 0:
            ranked.append((price * quantity, item, quantity))
    ranked.sort(reverse=True)
    for _, item, quantity in ranked:
        sale_orders.append(["SELL", item, quantity])
    action["market"] = sale_orders[:10]
    return action


def agent(obs, config=None):
    action = _BASE.agent(obs, config)
    try:
        step = max(0, int(_mapping_get(obs, "step", 0) or 0))
    except (TypeError, ValueError):
        return action
    if step != TERMINAL_STEP:
        return action
    return _terminal_liquidate(obs, action)
