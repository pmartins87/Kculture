"""KEXP-041: one bounded state-adaptive CARROT substitution.

Frozen R4B is delegated everywhere. The only strategic mutation is:

* state 614: if the legal public value signal
      3 * (CARROT_price - WHEAT_price) - 20 > 0
  is positive, append exactly one BUY_SEED CARROT order when there is a free
  market slot;
* state 615: only if the extra seed is observed to have actually arrived,
  replace exactly one frozen-R4B PLANT WHEAT intent with PLANT CARROT.

Why 614->615: KEXP-040 found at least one R4B WHEAT plant at state 615 in all
36 development/exploratory episodes, and every sign-positive episode also had
this opportunity. KEXP-034 measured equal same-route yield q=3 for this block.
The extra-seed ledger is conservative: the wrapper records what CARROT stock
R4B itself should have on the next observation and only spends stock above that
baseline, preserving R4B-reserved CARROT seeds.

No seed/opponent/episode identity or future information is used.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
BUY_STEP = 614
PLANT_STEP = 615
MAX_MARKET_ORDERS = 10


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4d_jit_base", BASE_PATH)
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


def _player(obs) -> int:
    try:
        return int(_get(obs, "player", 0) or 0)
    except Exception:
        return 0


def _step(obs) -> int:
    try:
        return int(_get(obs, "step", 0) or 0)
    except Exception:
        return 0


def _private_seeds(obs) -> dict:
    private = _get(obs, "private", {}) or {}
    return _get(private, "seeds", {}) or {}


def _price(obs, item: str) -> float | None:
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    try:
        v = float(_get(prices, item, 0) or 0)
        return v if v > 0 else None
    except Exception:
        return None


def _unit_ops(action: dict):
    yield action.get("farmer")
    for op in list(action.get("hands") or []):
        yield op


def _count_carrot_plants(action: dict) -> int:
    n = 0
    for op in _unit_ops(action):
        if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "CARROT"]:
            n += 1
    return n


def _count_carrot_buys(action: dict) -> int:
    n = 0
    for order in list(action.get("market") or []):
        if not (isinstance(order, list) and len(order) >= 3 and order[:2] == ["BUY_SEED", "CARROT"]):
            continue
        try:
            n += max(0, int(order[2] or 0))
        except Exception:
            pass
    return n


def _replace_one_wheat_plant(action: dict) -> bool:
    op = action.get("farmer")
    if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
        action["farmer"] = ["PLANT", "CARROT"]
        return True
    hands = list(action.get("hands") or [])
    for i, hop in enumerate(hands):
        if isinstance(hop, list) and len(hop) >= 2 and hop[:2] == ["PLANT", "WHEAT"]:
            hands[i] = ["PLANT", "CARROT"]
            action["hands"] = hands
            return True
    return False


def _fresh_state(step: int) -> dict:
    return {
        "last_step": step,
        "pending": False,
        "expected_base_carrot_next": None,
    }


def agent(obs, config=None):
    base_action = _BASE.agent(obs, config)
    action = copy.deepcopy(base_action)
    step = _step(obs)
    pid = _player(obs)

    st = _STATE.get(pid)
    if st is None or step == 0 or step <= int(st.get("last_step", -1)):
        st = _fresh_state(step)
        _STATE[pid] = st
    st["last_step"] = step

    if step == BUY_STEP:
        pw = _price(obs, "WHEAT")
        pc = _price(obs, "CARROT")
        margin = None if pw is None or pc is None else 3.0 * (pc - pw) - 20.0
        market = list(action.get("market") or [])
        if margin is not None and margin > 0 and len(market) < MAX_MARKET_ORDERS:
            seeds = _private_seeds(obs)
            try:
                carrot_before = max(0, int(_get(seeds, "CARROT", 0) or 0))
            except Exception:
                carrot_before = 0
            base_plants = _count_carrot_plants(base_action)
            base_buys = _count_carrot_buys(base_action)
            # Conservative expected stock if R4B's own intended CARROT buy(s)
            # all succeed. If one fails, we may miss a substitution, never
            # steal a seed that the base route expected to retain.
            expected = max(0, carrot_before - base_plants) + base_buys
            market.append(["BUY_SEED", "CARROT", 1])
            action["market"] = market
            st["pending"] = True
            st["expected_base_carrot_next"] = expected
        else:
            st["pending"] = False
            st["expected_base_carrot_next"] = None
        return action

    if step == PLANT_STEP and st.get("pending"):
        seeds = _private_seeds(obs)
        try:
            actual = max(0, int(_get(seeds, "CARROT", 0) or 0))
            expected = max(0, int(st.get("expected_base_carrot_next", 0) or 0))
        except Exception:
            actual = expected = 0
        # Only stock above the conservative frozen-base expectation can be the
        # extra JIT seed. Spend at most one and only on an actual base WHEAT
        # plant intent.
        if actual > expected:
            _replace_one_wheat_plant(action)
        st["pending"] = False
        st["expected_base_carrot_next"] = None
        return action

    if step > PLANT_STEP:
        st["pending"] = False
        st["expected_base_carrot_next"] = None
    return action
