#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from kaggle_exact_runtime import agent_visible_observation, done_status, make_reference_env, reference_config, reference_step
from solver.prize_solver_v3 import PrizeSolverV3

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def summarize(obs, solver, last_action=None):
    p = int(obs.get("player", 0))
    farm = obs["farms"][p]
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    animals = Counter()
    structures = Counter()
    crops = Counter()
    weeds = 0
    empty = 0
    held_yield = Counter()
    for row in farm.get("tiles", []):
        for tile in row:
            if tile is None:
                empty += 1
            elif tile == "LOCKED":
                continue
            elif isinstance(tile, dict):
                kind = tile.get("kind")
                if kind == "PLANT":
                    crop = tile.get("crop")
                    crops[crop] += 1
                    held_yield[crop] += int(tile.get("yield_units", 0))
                elif kind == "WEED":
                    weeds += 1
                elif kind in ("COOP", "PASTURE"):
                    structures[kind] += 1
                    animal = tile.get("animal")
                    if animal:
                        animals[animal] += 1
                        product = {"COW":"MILK","SHEEP":"WOOL","GOOSE":"EGG"}.get(animal)
                        if product:
                            held_yield[product] += int(tile.get("yield_units", 0))
    return {
        "step": int(obs.get("step", -1)),
        "day": int(obs.get("day", -1)),
        "hour": int(obs.get("hour", -1)),
        "money": float(farm.get("money", 0)),
        "unlocked": list(farm.get("unlocked_quadrants", [])),
        "hires_today": int(farm.get("hires_today", 0)),
        "hands": len(farm.get("hands", [])),
        "animals_board": dict(animals),
        "structures": dict(structures),
        "crops_board": dict(crops),
        "held_yield": dict(held_yield),
        "shed": {k:int(v) for k,v in shed.items() if int(v)},
        "seeds": {k:int(v) for k,v in (private.get("seeds") or {}).items() if int(v)},
        "weeds": weeds,
        "empty_unlocked": empty,
        "plan": None if solver.current_plan is None else solver.current_plan.name,
        "last_action": last_action,
    }


def main():
    seed = 92101
    env = make_reference_env(seed)
    cfg = reference_config(env)
    solver = PrizeSolverV3()
    trace = []
    op_counts = Counter()
    market_counts = Counter()
    last_action = None

    while not all(done_status(s.status) for s in env.state):
        obs = agent_visible_observation(env, 0)
        step = int(obs.get("step", 0))
        if step % 24 == 0:
            trace.append(summarize(obs, solver, last_action))
        action = solver.act(obs, cfg)
        last_action = action
        for act in [action.get("farmer") or []] + list(action.get("hands") or []):
            if act:
                op_counts[str(act[0])] += 1
        for order in action.get("market") or []:
            if order:
                market_counts[str(order[0])] += 1
        reference_step(env, [action, PASS], [0.0, 0.0])

    final_obs = agent_visible_observation(env, 0)
    trace.append(summarize(final_obs, solver, last_action))
    result = {
        "schema": "prize-solver-v3-day-trace-v1",
        "seed": seed,
        "final_rewards": [env.state[0].reward, env.state[1].reward],
        "unit_op_counts": dict(op_counts),
        "market_order_counts": dict(market_counts),
        "trace": trace,
    }
    (ROOT / "PRIZE_SOLVER_V1_DAY_TRACE.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("TRACE_RESULT", json.dumps({
        "final_rewards": result["final_rewards"],
        "unit_op_counts": result["unit_op_counts"],
        "market_order_counts": result["market_order_counts"],
        "days": len(trace),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
