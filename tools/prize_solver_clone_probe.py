#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from solver.prize_solver_v0 import PrizeSolver
from kaggle_exact_runtime import agent_visible_observation, make_reference_env, reference_config, reference_step, norm

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def state_snapshot(env):
    return norm([
        {
            "status": str(s.status),
            "reward": s.reward,
            "observation": s.observation,
        }
        for s in env.state
    ])


def main():
    seed = 91901
    env = make_reference_env(seed)
    cfg = reference_config(env)
    a = PrizeSolver()
    b = PrizeSolver()

    # Advance six days with two independent adaptive solvers.
    for _ in range(6 * 24):
        oa = agent_visible_observation(env, 0)
        ob = agent_visible_observation(env, 1)
        aa = a.act(oa, cfg)
        ab = b.act(ob, cfg)
        reference_step(env, [aa, ab], [0.0, 0.0])

    before = state_snapshot(env)
    result = {
        "schema": "prize-solver-clone-probe-v1",
        "seed": seed,
        "step_before": int(agent_visible_observation(env, 0).get("step", -1)),
        "deepcopy_ok": False,
        "same_before": False,
        "same_after_identical_step": False,
        "error": None,
    }
    try:
        clone = copy.deepcopy(env)
        result["deepcopy_ok"] = True
        result["same_before"] = state_snapshot(clone) == before

        # Identical actions from identical states must produce byte-equivalent state.
        reference_step(env, [PASS, PASS], [0.0, 0.0])
        reference_step(clone, [copy.deepcopy(PASS), copy.deepcopy(PASS)], [0.0, 0.0])
        result["same_after_identical_step"] = state_snapshot(clone) == state_snapshot(env)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    out = ROOT / "PRIZE_SOLVER_CLONE_PROBE.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("CLONE_PROBE", json.dumps(result, sort_keys=True), flush=True)
    if not (result["deepcopy_ok"] and result["same_before"] and result["same_after_identical_step"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
