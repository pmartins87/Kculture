"""R4B ablation: terminal market liquidation only, no unit-action changes.

Research-only wrapper over the frozen COK V8 R4A source. It delegates every
physical farmer/hand action to R4A unchanged. On executable step 718 it removes
terminal non-SELL market orders, expands each existing product SELL to all
projected shed stock for that product, and appends SELLs for projected products
that R4A omitted.

Why this is a useful ablation:
- official terminal reward is farm money only;
- official SELL commits one unit at a time for a positive price floored at $1;
- market processing occurs after unit actions;
- therefore this isolates sale-completeness from R4B's more speculative choice
  to replace a physical action with DROP.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "artifacts/public_opponents/cok_v8_779caae.py"
TERMINAL_STEP = 718
SELLABLE = (
    "WHEAT",
    "CARROT",
    "TOMATO",
    "STRAWBERRY",
    "MELON",
    "EGG",
    "MILK",
    "WOOL",
    "FERTILIZER",
)


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4b_market_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen R4A base: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BASE = _load_base()


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default


def _terminal_market_only(obs, base_action):
    action = copy.deepcopy(base_action)
    projected = _BASE._v5_projected_shed(obs, action)
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}

    # Keep the first-occurrence order of R4A's existing SELL products. This
    # preserves the route's economically intentional ordering while expanding
    # quantity to the full same-turn projected stock. Terminal BUY/HIRE/LAND
    # orders cannot create post-terminal production and are omitted here.
    existing_order = []
    seen = set()
    for order in list(action.get("market") or []):
        if not (isinstance(order, list) and len(order) >= 2 and order[0] == "SELL"):
            continue
        item = order[1]
        if item in SELLABLE and item not in seen:
            seen.add(item)
            existing_order.append(item)

    market = []
    for item in existing_order:
        try:
            quantity = max(0, int(projected.get(item, 0) or 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity:
            market.append(["SELL", item, quantity])

    # Omitted products go after R4A's retained sale order. Rank only this suffix
    # so the ablation does not gratuitously reorder the base's existing sells.
    omitted = []
    for item in SELLABLE:
        if item in seen:
            continue
        try:
            quantity = max(0, int(projected.get(item, 0) or 0))
            price = max(0.0, float(_get(prices, item, 0) or 0))
        except (TypeError, ValueError):
            continue
        if quantity:
            omitted.append((price * quantity, item, quantity))
    omitted.sort(reverse=True)
    market.extend(["SELL", item, quantity] for _, item, quantity in omitted)

    # There are only nine sellable product types, below the official/default
    # maxMarketOrdersPerTurn=10. Keep the cap explicit for malformed configs.
    action["market"] = market[:10]
    return action


def agent(obs, config=None):
    action = _BASE.agent(obs, config)
    try:
        step = max(0, int(_get(obs, "step", 0) or 0))
    except (TypeError, ValueError):
        return action
    if step != TERMINAL_STEP:
        return action
    return _terminal_market_only(obs, action)
