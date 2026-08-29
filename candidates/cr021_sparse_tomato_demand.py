"""CR-021A: preregistered one-slot TOMATO demand response over CR008.

See docs/CR021_PREREGISTRATION.md.  The candidate is intentionally tiny:
CR008 is delegated everywhere except a mechanics-visible JIT TOMATO purchase at
state 309, one possible WHEAT->TOMATO substitution at 310@(9,7), and one
full-yield WATER->HARVEST preservation on that same diverted tile.

No opponent/seed/episode identity is used.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/cr008_adaptive_frontrun.py"
BUY_STEP = 309
PLANT_STEP = 310
TARGET = (9, 7)
TOMATO_MIN_PRICE = 90.0
MAX_MARKET_ORDERS = 10
DEMAND_SHOPS = {"PIZZA_SHOP", "FARMERS_MARKET"}


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_cr021_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen CR008: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BASE = _load_base()
_STATE: dict[int, dict] = {}


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def _player(obs) -> int:
    try:
        return int(_get(obs, "player", 0) or 0)
    except Exception:
        return 0


def _step(obs) -> int:
    try:
        raw = _get(obs, "step", None)
        if raw is not None:
            return max(0, int(raw))
        day = max(0, int(_get(obs, "day", 0) or 0))
        hour = max(0, int(_get(obs, "hour", 0) or 0))
        return day * 24 + hour
    except Exception:
        return 0


def _farm(obs, pid):
    farms = _get(obs, "farms", []) or []
    return farms[pid] if 0 <= pid < len(farms) else {}


def _private_seeds(obs) -> dict:
    return _get(_get(obs, "private", {}) or {}, "seeds", {}) or {}


def _positions(obs, pid):
    farm = _farm(obs, pid)
    out = []
    raw = _get(farm, "farmer", None)
    out.append(tuple(raw) if isinstance(raw, (list, tuple)) and len(raw) >= 2 else (-1, -1))
    for pos in _get(farm, "hands", []) or []:
        out.append(tuple(pos) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else (-1, -1))
    return out


def _ops(action):
    return [action.get("farmer")] + list(action.get("hands") or [])


def _set_op(action, idx, op):
    if idx == 0:
        action["farmer"] = op
        return
    hands = list(action.get("hands") or [])
    j = idx - 1
    if 0 <= j < len(hands):
        hands[j] = op
        action["hands"] = hands


def _tile(obs, pid, pos):
    farm = _farm(obs, pid)
    tiles = _get(farm, "tiles", []) or []
    x, y = pos
    try:
        return tiles[y][x]
    except Exception:
        return None


def _tomato_plants(obs, pid) -> int:
    farm = _farm(obs, pid)
    n = 0
    for row in _get(farm, "tiles", []) or []:
        for tile in row or []:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "TOMATO":
                n += 1
    return n


def _price(obs, item):
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    try:
        return float(_get(prices, item, 0) or 0)
    except Exception:
        return 0.0


def _town_has_tomato_demand(obs) -> bool:
    town = _get(obs, "town", {}) or {}
    shops = {str(x).upper() for x in (_get(town, "unlocked_shops", []) or [])}
    return bool(shops & DEMAND_SHOPS)


def _count_market(action, kind, item) -> int:
    total = 0
    for order in list(action.get("market") or []):
        if not (isinstance(order, list) and len(order) >= 3 and order[:2] == [kind, item]):
            continue
        try:
            total += max(0, int(order[2] or 0))
        except Exception:
            pass
    return total


def _count_plants(action, item) -> int:
    return sum(
        1 for op in _ops(action)
        if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", item]
    )


def _project_position(pos, op):
    x, y = pos
    if not (isinstance(op, list) and op):
        return pos
    move = op[0]
    if move == "EAST": return (x + 1, y)
    if move == "WEST": return (x - 1, y)
    if move == "SOUTH": return (x, y + 1)
    if move == "NORTH": return (x, y - 1)
    return pos


def _base_places_unit_on_target(obs, action, pid) -> bool:
    if _tile(obs, pid, TARGET) is not None:
        return False
    pos = _positions(obs, pid)
    ops = _ops(action)
    return any(_project_position(p, ops[i] if i < len(ops) else None) == TARGET for i, p in enumerate(pos))


def _replace_target_wheat(obs, action, pid) -> bool:
    pos = _positions(obs, pid)
    ops = _ops(action)
    for i, p in enumerate(pos):
        op = ops[i] if i < len(ops) else None
        if p == TARGET and isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
            _set_op(action, i, ["PLANT", "TOMATO"])
            return True
    return False


def _preserve_full_tomato_harvest(obs, action, pid) -> bool:
    tile = _tile(obs, pid, TARGET)
    if not (
        isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
        and tile.get("crop") == "TOMATO"
        and int(tile.get("yield_units", 0) or 0) >= 4
    ):
        return False
    pos = _positions(obs, pid)
    ops = _ops(action)
    for i, p in enumerate(pos):
        op = ops[i] if i < len(ops) else None
        if p != TARGET or not (isinstance(op, list) and op):
            continue
        if op[0] == "HARVEST":
            return True
        if op[0] == "WATER":
            _set_op(action, i, ["HARVEST"])
            return True
    return False


def _fresh(step):
    return {
        "last_step": step,
        "pending": False,
        "expected_base_tomato_next": None,
        "diverted": False,
        "harvested": False,
        "trigger_count": 0,
        "plant_count": 0,
        "harvest_count": 0,
    }


def agent(obs, config=None):
    pid = _player(obs)
    step = _step(obs)
    st = _STATE.get(pid)
    if st is None or step == 0 or step <= int(st.get("last_step", -1)):
        st = _fresh(step)
        _STATE[pid] = st
    st["last_step"] = step

    base_action = _BASE.agent(obs, config)
    action = copy.deepcopy(base_action)

    if step == BUY_STEP:
        market = list(action.get("market") or [])
        trigger = (
            _town_has_tomato_demand(obs)
            and _price(obs, "TOMATO") >= TOMATO_MIN_PRICE
            and _tomato_plants(obs, pid) == 0
            and len(market) < MAX_MARKET_ORDERS
            and _base_places_unit_on_target(obs, base_action, pid)
        )
        if trigger:
            seeds = _private_seeds(obs)
            try:
                before = max(0, int(_get(seeds, "TOMATO", 0) or 0))
            except Exception:
                before = 0
            expected = max(0, before - _count_plants(base_action, "TOMATO")) + _count_market(base_action, "BUY_SEED", "TOMATO")
            market.append(["BUY_SEED", "TOMATO", 1])
            action["market"] = market
            st["pending"] = True
            st["expected_base_tomato_next"] = expected
            st["trigger_count"] += 1
        else:
            st["pending"] = False
            st["expected_base_tomato_next"] = None
        return action

    if step == PLANT_STEP and st.get("pending"):
        seeds = _private_seeds(obs)
        try:
            actual = max(0, int(_get(seeds, "TOMATO", 0) or 0))
            expected = max(0, int(st.get("expected_base_tomato_next", 0) or 0))
        except Exception:
            actual = expected = 0
        if actual > expected and _replace_target_wheat(obs, action, pid):
            st["diverted"] = True
            st["plant_count"] += 1
        st["pending"] = False
        st["expected_base_tomato_next"] = None
        return action

    if st.get("diverted") and not st.get("harvested") and step > PLANT_STEP:
        if _preserve_full_tomato_harvest(obs, action, pid):
            st["harvested"] = True
            st["harvest_count"] += 1

    return action
