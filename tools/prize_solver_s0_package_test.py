#!/usr/bin/env python3
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.kaggle_exact_runtime import (
    AgentProcess,
    PASS,
    agent_visible_observation,
    done_status,
    extract,
    make_reference_env,
    reference_config,
    reference_step,
)


def main():
    archive = ROOT / "R4D_PRIZE_SOLVER_S0_V4.tar.gz"
    if not archive.is_file():
        raise SystemExit(f"missing package: {archive}")

    seed = 92301
    env = make_reference_env(seed)
    cfg = reference_config(env)
    max_duration = 0.0
    calls = 0

    with tempfile.TemporaryDirectory(prefix="prize-solver-s0-") as td:
        package_dir = extract(archive, Path(td), "s0")
        ctx = mp.get_context("spawn")
        proc = AgentProcess(ctx, package_dir, "PRIZE_SOLVER_S0_V4")
        try:
            while not all(done_status(s.status) for s in env.state):
                obs = agent_visible_observation(env, 0)
                action, duration = proc.call(obs, cfg)
                max_duration = max(max_duration, float(duration))
                calls += 1
                reference_step(env, [action, PASS], [duration, 0.0])
        finally:
            proc.close()

    statuses = [str(s.status) for s in env.state]
    rewards = [s.reward for s in env.state]
    result = {
        "schema": "prize-solver-s0-v4-package-smoke-v1",
        "seed": seed,
        "calls": calls,
        "statuses": statuses,
        "rewards": rewards,
        "max_call_duration_s": max_duration,
        "pass": statuses == ["DONE", "DONE"] and calls >= 719 and rewards[0] is not None and float(rewards[0]) > 3000.0,
    }
    (ROOT / "PRIZE_SOLVER_S0_PACKAGE_SMOKE.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("S0_PACKAGE_SMOKE", json.dumps(result, sort_keys=True), flush=True)
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
