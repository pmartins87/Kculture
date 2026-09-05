"""CR025: CR024 H11/M19 consensus + frozen CR008 high-confidence market overlay.

The consensus tape is supplied by the evaluator/builder. This module changes no
baseline action except appending the exact CR008 CARROT/STRAWBERRY SELL exploit
when the frozen public-state predictor crosses its frozen threshold.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CR008_PATH = ROOT / "candidates/cr008_adaptive_frontrun.py"


def _load_cr008():
    spec = importlib.util.spec_from_file_location("kculture_cr025_cr008_frozen", CR008_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(CR008_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CR008 = _load_cr008()


def make_agent(consensus_tape):
    """Return an independent stateful CR025 agent over one frozen consensus tape."""
    if len(consensus_tape) != 719:
        raise RuntimeError(f"consensus tape length {len(consensus_tape)} != 719")

    history = {0: {}, 1: {}}
    last_step = {0: -1, 1: -1}
    stats = {"triggered_orders": 0, "triggered_games": 0, "items": {"CARROT": 0, "STRAWBERRY": 0}}
    game_triggered = {0: False, 1: False}

    def remember(player, step, obs):
        history[player][step] = _CR008._snapshot(obs)
        cutoff = step - 30
        for k in list(history[player]):
            if k < cutoff:
                del history[player][k]

    def agent(obs, config=None):
        player = int(_CR008._get(obs, "player", 0) or 0)
        step = _CR008._clock_step(obs)
        if step == 0 or step < last_step[player]:
            history[player].clear()
            game_triggered[player] = False
        last_step[player] = step

        action = copy.deepcopy(consensus_tape[max(0, min(718, step))])
        prev = history[player].get(step - 24)
        if prev is not None:
            feat = _CR008._public_features(obs, prev, player)
            if feat:
                names = _CR008._MODELS["feature_names"]
                market = list(action.get("market") or [])
                already = {
                    o[1] for o in market
                    if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"
                }
                shed = _CR008._get(_CR008._get(obs, "private", {}) or {}, "shed", {}) or {}
                for target, item in _CR008.TARGET_TO_ITEM.items():
                    if len(market) >= 10:
                        break
                    if item in already:
                        continue
                    try:
                        qty = max(0, int(_CR008._get(shed, item, 0) or 0))
                    except Exception:
                        qty = 0
                    if qty <= 0:
                        continue
                    prob = _CR008._tree_prob(_CR008._MODELS["models"][target], feat, names)
                    threshold = float(_CR008._MODELS["thresholds"][target])
                    if prob >= threshold:
                        market.append(["SELL", item, qty])
                        already.add(item)
                        stats["triggered_orders"] += 1
                        stats["items"][item] += 1
                        if not game_triggered[player]:
                            game_triggered[player] = True
                            stats["triggered_games"] += 1
                action["market"] = market

        remember(player, step, obs)
        return action

    agent._cr025_stats = stats
    return agent
