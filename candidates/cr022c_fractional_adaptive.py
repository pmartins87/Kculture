"""CR022C research factory: CR008 with adaptive-sale quantity as the only variable.

Not a hosted agent by itself. Stage-A/B evaluators call make_agent(numerator,
denominator). Forecast model, feature semantics, thresholds, target products,
timing and append placement are inherited exactly from frozen CR008. Only the
quantity of a newly appended adaptive SELL is replaced by ceil(stock*fraction).
"""
from __future__ import annotations

import importlib.util
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"


def _load_cr008():
    name = f"kculture_cr022c_cr008_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(name, CR008)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen CR008 {CR008}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_agent(numerator: int, denominator: int):
    numerator = int(numerator)
    denominator = int(denominator)
    if denominator <= 0 or numerator <= 0 or numerator > denominator:
        raise ValueError((numerator, denominator))

    m = _load_cr008()

    def append_fractional(obs, action, player, step):
        prev = m._HISTORY[player].get(step - 24)
        if prev is None:
            return action
        feat = m._public_features(obs, prev, player)
        if not feat:
            return action
        names = m._MODELS["feature_names"]
        market = list(action.get("market") or [])
        already = {
            o[1]
            for o in market
            if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"
        }
        shed = m._get(m._get(obs, "private", {}) or {}, "shed", {}) or {}
        for target, item in m.TARGET_TO_ITEM.items():
            if len(market) >= 10:
                break
            if item in already:
                continue
            try:
                stock = max(0, int(m._get(shed, item, 0) or 0))
            except Exception:
                stock = 0
            if stock <= 0:
                continue
            prob = m._tree_prob(m._MODELS["models"][target], feat, names)
            threshold = float(m._MODELS["thresholds"][target])
            if prob >= threshold:
                qty = max(1, (stock * numerator + denominator - 1) // denominator)
                market.append(["SELL", item, qty])
                already.add(item)
        action["market"] = market
        return action

    def agent(obs, config=None):
        player = int(m._get(obs, "player", 0) or 0)
        step = m._clock_step(obs)
        m._reset_if_needed(player, step)
        action = m._BASE.agent(obs, config)
        action = append_fractional(obs, action, player, step)
        m._remember(player, step, obs)
        return action

    return agent
