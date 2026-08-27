"""KEXP-050: reallocate one existing state-614 WHEAT seed buy to CARROT.

Frozen R4B is delegated everywhere. At state 614 only, when the mechanics-
derived equal-route value signal

    3 * (CARROT_price - WHEAT_price) - 10 > 0

is positive and frozen R4B itself submits a BUY_SEED WHEAT order, replace one
unit of that WHEAT order with one CARROT in the same market slot. At state 615,
convert exactly one actual frozen-R4B PLANT WHEAT to CARROT only if observed
CARROT stock proves the substituted CARROT purchase arrived above frozen-base
expected stock.

This is a true seed-budget reallocation, not the +20 JIT extra purchase used by
KEXP-041. No identity or future information is used.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
BUY_STEP = 614
PLANT_STEP = 615
Q = 3.0


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4d_realloc614_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen R4B: {BASE_PATH}")
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


def _step(obs):
    try:
        return int(_get(obs, "step", 0) or 0)
    except Exception:
        return 0


def _player(obs):
    try:
        return int(_get(obs, "player", 0) or 0)
    except Exception:
        return 0


def _seeds(obs):
    return _get(_get(obs, "private", {}) or {}, "seeds", {}) or {}


def _price(obs, item):
    try:
        prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
        v = float(_get(prices, item, 0) or 0)
        return v if v > 0 else None
    except Exception:
        return None


def _unit_ops(action):
    yield action.get("farmer")
    for op in list(action.get("hands") or []):
        yield op


def _count_carrot_plants(action):
    return sum(
        isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "CARROT"]
        for op in _unit_ops(action)
    )


def _count_carrot_buys(action):
    total = 0
    for row in list(action.get("market") or []):
        if isinstance(row, list) and len(row) >= 3 and row[:2] == ["BUY_SEED", "CARROT"]:
            try:
                total += max(0, int(row[2] or 0))
            except Exception:
                pass
    return total


def _reallocate_one_wheat_buy(action):
    market = [list(row) if isinstance(row, list) else row for row in list(action.get("market") or [])]
    for i, row in enumerate(market):
        if not (isinstance(row, list) and len(row) >= 3 and row[:2] == ["BUY_SEED", "WHEAT"]):
            continue
        try:
            qty = max(0, int(row[2] or 0))
        except Exception:
            continue
        if qty != 1:
            # KEXP-050 is intentionally the clean one-for-one same-slot case.
            continue
        market[i] = ["BUY_SEED", "CARROT", 1]
        action["market"] = market
        return True
    return False


def _replace_one_wheat_plant(action):
    op = action.get("farmer")
    if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
        action["farmer"] = ["PLANT", "CARROT"]
        return True
    hands = list(action.get("hands") or [])
    for i, op in enumerate(hands):
        if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
            hands[i] = ["PLANT", "CARROT"]
            action["hands"] = hands
            return True
    return False


def agent(obs, config=None):
    base = _BASE.agent(obs, config)
    action = copy.deepcopy(base)
    step = _step(obs)
    pid = _player(obs)
    st = _STATE.get(pid)
    if st is None or step == 0 or step <= int(st.get("last_step", -1)):
        st = {"last_step": step, "pending": False, "expected_carrot": None}
        _STATE[pid] = st
    st["last_step"] = step

    if step == BUY_STEP:
        pw, pc = _price(obs, "WHEAT"), _price(obs, "CARROT")
        margin = None if pw is None or pc is None else Q * (pc - pw) - 10.0
        if margin is not None and margin > 0:
            try:
                carrot_before = max(0, int(_get(_seeds(obs), "CARROT", 0) or 0))
            except Exception:
                carrot_before = 0
            expected = max(0, carrot_before - _count_carrot_plants(base)) + _count_carrot_buys(base)
            if _reallocate_one_wheat_buy(action):
                st["pending"] = True
                st["expected_carrot"] = expected
                return action
        st["pending"] = False
        st["expected_carrot"] = None
        return action

    if step == PLANT_STEP and st.get("pending"):
        try:
            actual = max(0, int(_get(_seeds(obs), "CARROT", 0) or 0))
            expected = max(0, int(st.get("expected_carrot", 0) or 0))
        except Exception:
            actual = expected = 0
        if actual > expected:
            _replace_one_wheat_plant(action)
        st["pending"] = False
        st["expected_carrot"] = None
        return action

    if step > PLANT_STEP:
        st["pending"] = False
        st["expected_carrot"] = None
    return action
