#!/usr/bin/env python3
"""FP001 FP1 causal runtime test in kaggle-environments==1.32.7.

The candidate performs no physical farming.  The only treatment is a WHEAT
BUY_PRODUCT on a known town pulse and a SELL on the next turn.  This makes the
bank delta attributable to H1 rather than route, production, or replay imitation.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "candidates" / "fp001_h1_town_wheat_carry.py"
DEFAULT_SEEDS = list(range(61001, 61017))
NULL_SEEDS = list(range(62001, 62005))
STARTING_MONEY = 3000.0


def load_candidate():
    spec = importlib.util.spec_from_file_location("fp001_h1_candidate", CANDIDATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CANDIDATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pass_agent(obs, config=None):
    player = int(getattr(obs, "player", 0) if not isinstance(obs, dict) else obs.get("player", 0))
    farms = getattr(obs, "farms", []) if not isinstance(obs, dict) else obs.get("farms", [])
    hands_n = 0
    try:
        farm = farms[player]
        hands = farm.get("hands", []) if isinstance(farm, dict) else getattr(farm, "hands", [])
        hands_n = len(hands or [])
    except Exception:
        hands_n = 0
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hands_n)], "market": []}


def instrument(agent_fn):
    stats = {"buy_orders": 0, "sell_orders": 0, "buy_qty": 0, "sell_qty": 0}

    def wrapped(obs, config=None):
        action = agent_fn(obs, config)
        for order in list(action.get("market") or []):
            if not (isinstance(order, list) and len(order) >= 3):
                continue
            op, item = order[0], order[1]
            try:
                qty = int(order[2])
            except (TypeError, ValueError):
                qty = 0
            if item == "WHEAT" and op == "BUY_PRODUCT":
                stats["buy_orders"] += 1
                stats["buy_qty"] += qty
            elif item == "WHEAT" and op == "SELL":
                stats["sell_orders"] += 1
                stats["sell_qty"] += qty
        return action

    return wrapped, stats


def run_episode(candidate, seed: int, seat: int, flat_price: bool = False):
    config = {
        "episodeSteps": 720,
        "startingMoney": int(STARTING_MONEY),
        "seed": seed,
    }
    if flat_price:
        config["marketParams"] = {"WHEAT": {"below_target": 0.0, "above_target": 0.0}}

    wrapped, stats = instrument(candidate.agent)
    agents = [wrapped, pass_agent] if seat == 0 else [pass_agent, wrapped]
    env = make("kaggriculture", configuration=config, debug=True)
    env.run(agents)
    j = env.toJSON()
    statuses = list(j["statuses"])
    rewards = list(j["rewards"])
    assert statuses == ["DONE", "DONE"], (seed, seat, flat_price, statuses)
    return float(rewards[seat]), float(rewards[1 - seat]), stats


def run_control(seed: int):
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "startingMoney": int(STARTING_MONEY), "seed": seed},
        debug=True,
    )
    env.run([pass_agent, pass_agent])
    j = env.toJSON()
    assert list(j["statuses"]) == ["DONE", "DONE"]
    rewards = [float(x) for x in j["rewards"]]
    assert rewards == [STARTING_MONEY, STARTING_MONEY], (seed, rewards)
    return rewards


def summarize(values):
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
    }


def main() -> None:
    candidate = load_candidate()

    # Exact PASS baseline for the same fresh seeds.
    for seed in DEFAULT_SEEDS:
        run_control(seed)

    default_by_seat = {0: [], 1: []}
    default_stats = {0: {"buy_orders": 0, "sell_orders": 0, "buy_qty": 0, "sell_qty": 0},
                     1: {"buy_orders": 0, "sell_orders": 0, "buy_qty": 0, "sell_qty": 0}}

    for seed in DEFAULT_SEEDS:
        for seat in (0, 1):
            own, opp, stats = run_episode(candidate, seed, seat, flat_price=False)
            delta = own - STARTING_MONEY
            default_by_seat[seat].append(delta)
            assert opp == STARTING_MONEY, (seed, seat, opp)
            for k, v in stats.items():
                default_stats[seat][k] += v

    all_default = default_by_seat[0] + default_by_seat[1]
    assert min(all_default) > 0, summarize(all_default)
    for seat in (0, 1):
        assert default_stats[seat]["buy_orders"] > 0
        assert default_stats[seat]["sell_orders"] > 0
        assert default_stats[seat]["buy_qty"] == default_stats[seat]["sell_qty"], default_stats[seat]

    # Causal null: the agent still performs the carry, but WHEAT price is flat.
    # Town inventory depletion therefore cannot create price appreciation.
    null_deltas = []
    null_triggers = {"buy_orders": 0, "sell_orders": 0, "buy_qty": 0, "sell_qty": 0}
    for seed in NULL_SEEDS:
        for seat in (0, 1):
            own, opp, stats = run_episode(candidate, seed, seat, flat_price=True)
            null_deltas.append(own - STARTING_MONEY)
            assert opp == STARTING_MONEY, (seed, seat, opp)
            for k, v in stats.items():
                null_triggers[k] += v

    assert null_triggers["buy_orders"] > 0 and null_triggers["sell_orders"] > 0, null_triggers
    assert all(delta == 0 for delta in null_deltas), null_deltas

    print("FP1_CAUSAL_RUNTIME_PASS")
    print("default_seat0", summarize(default_by_seat[0]))
    print("default_seat1", summarize(default_by_seat[1]))
    print("default_all", summarize(all_default))
    print("default_triggers_seat0", default_stats[0])
    print("default_triggers_seat1", default_stats[1])
    print("flat_price_null", summarize(null_deltas), null_triggers)


if __name__ == "__main__":
    main()
