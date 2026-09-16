#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kaggle_environments import make
from solver.prize_solver_v4 import PrizeSolverV4


def wrap(solver):
    def fn(obs, config=None):
        action = solver.act(obs, config or {})
        assert isinstance(action, dict)
        assert isinstance(action.get("farmer"), list)
        assert isinstance(action.get("hands"), list)
        assert isinstance(action.get("market"), list)
        assert len(action["market"]) <= 10
        return action
    return fn


def one(seed, opponent):
    a = PrizeSolverV4()
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    if opponent == "self":
        b = PrizeSolverV4()
        agents = [wrap(a), wrap(b)]
    else:
        agents = [wrap(a), opponent]
    env.run(agents)
    payload = env.toJSON()
    statuses = list(payload.get("statuses") or [])
    rewards = list(payload.get("rewards") or [])
    steps = len(payload.get("steps") or [])
    ok = statuses == ["DONE", "DONE"] and len(rewards) == 2 and all(x is not None for x in rewards)
    return {
        "seed": seed,
        "opponent": opponent,
        "ok": ok,
        "statuses": statuses,
        "rewards": rewards,
        "steps": steps,
    }


def main():
    rows = []
    for opponent in ("pass", "random", "starter", "self"):
        for seed in (91701, 91702, 91703):
            row = one(seed, opponent)
            rows.append(row)
            print("PRIZE_SOLVER_SMOKE", json.dumps(row, sort_keys=True), flush=True)

    failures = [r for r in rows if not r["ok"]]
    pass_rows = [r for r in rows if r["opponent"] == "pass" and r["ok"]]
    positive_pass = sum(1 for r in pass_rows if float(r["rewards"][0]) > 3000.0)
    nonzero_rewards = sum(1 for r in rows if r["ok"] and float(r["rewards"][0]) > 0.0)
    economic_bootstrap_pass = positive_pass >= 1 and nonzero_rewards >= 6

    result = {
        "schema": "prize-solver-v4-smoke-v1",
        "games": len(rows),
        "failures": len(failures),
        "all_done": not failures,
        "positive_pass_games": positive_pass,
        "nonzero_reward_games": nonzero_rewards,
        "economic_bootstrap_pass": economic_bootstrap_pass,
        "rows": rows,
    }
    out = ROOT / "PRIZE_SOLVER_V0_SMOKE.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("PRIZE_SOLVER_RESULT", json.dumps({
        "games": result["games"],
        "failures": result["failures"],
        "all_done": result["all_done"],
        "positive_pass_games": positive_pass,
        "nonzero_reward_games": nonzero_rewards,
        "economic_bootstrap_pass": economic_bootstrap_pass,
    }, sort_keys=True))
    if failures or not economic_bootstrap_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
