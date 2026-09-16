#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from kaggle_exact_runtime import (
    agent_visible_observation,
    done_status,
    make_reference_env,
    reference_config,
    reference_step,
)
from solver.prize_solver_v0 import PLANS, _step
from solver.prize_solver_v1 import PrizeSolverV1
from solver.rollout_search import ForcedPlanSolverV1, clone_solver
from solver.value_features import encode_value_features


SEEDS = (92001, 92002, 92003)
BRANCH_DAYS = (4, 8, 12, 16, 20)
FORCE_DAYS = 3


def reward(env, seat):
    val = env.state[seat].reward
    return None if val is None else float(val)


def margin(env):
    a = reward(env, 0)
    b = reward(env, 1)
    if a is None or b is None:
        return None
    return a - b


def advance_one(env, cfg, a0, a1):
    o0 = agent_visible_observation(env, 0)
    o1 = agent_visible_observation(env, 1)
    x0 = a0.act(o0, cfg)
    x1 = a1.act(o1, cfg)
    reference_step(env, [x0, x1], [0.0, 0.0])


def run_to_step(env, cfg, a0, a1, target_step):
    while not all(done_status(s.status) for s in env.state):
        now = int(agent_visible_observation(env, 0).get("step", 0))
        if now >= target_step:
            break
        advance_one(env, cfg, a0, a1)


def run_to_end(env, cfg, a0, a1):
    guard = 0
    while not all(done_status(s.status) for s in env.state):
        advance_one(env, cfg, a0, a1)
        guard += 1
        if guard > 725:
            raise RuntimeError("rollout exceeded episode length")


def branch_label(env, cfg, base0, base1, plan, branch_step, force_steps):
    benv = copy.deepcopy(env)
    cand = ForcedPlanSolverV1.from_solver(base0, plan, branch_step + force_steps)
    opp = clone_solver(base1)
    run_to_end(benv, cfg, cand, opp)
    statuses = [str(s.status) for s in benv.state]
    return {
        "plan": plan.name,
        "margin": margin(benv),
        "reward0": reward(benv, 0),
        "reward1": reward(benv, 1),
        "statuses": statuses,
        "ok": statuses == ["DONE", "DONE"] and margin(benv) is not None,
    }


def main():
    rows = []
    failures = []
    for seed in SEEDS:
        env = make_reference_env(seed)
        cfg = reference_config(env)
        a0 = PrizeSolverV1()
        a1 = PrizeSolverV1()
        turns = max(1, int(cfg.get("turnsPerDay", 24)))
        force_steps = FORCE_DAYS * turns

        for day in BRANCH_DAYS:
            target = day * turns
            run_to_step(env, cfg, a0, a1, target)
            if all(done_status(s.status) for s in env.state):
                failures.append({"seed": seed, "day": day, "error": "baseline ended before branch"})
                break

            obs = agent_visible_observation(env, 0)
            branch_step = _step(obs, cfg)
            features = encode_value_features(obs, cfg)
            heuristic_plan = a0._select_plan(obs, cfg).name

            labels = []
            for plan in PLANS:
                result = branch_label(env, cfg, a0, a1, plan, branch_step, force_steps)
                labels.append(result)
                print(
                    "MACRO_BRANCH",
                    "seed", seed,
                    "day", day,
                    "plan", plan.name,
                    "margin", result["margin"],
                    "ok", result["ok"],
                    flush=True,
                )
                if not result["ok"]:
                    failures.append({"seed": seed, "day": day, "plan": plan.name, "result": result})

            valid = [x for x in labels if x["ok"]]
            if valid:
                best = max(valid, key=lambda x: (x["margin"], x["plan"]))
                h = next((x for x in valid if x["plan"] == heuristic_plan), None)
                heuristic_margin = None if h is None else h["margin"]
                regret = None if h is None else best["margin"] - h["margin"]
            else:
                best = {"plan": None, "margin": None}
                heuristic_margin = None
                regret = None

            rows.append({
                "seed": seed,
                "day": day,
                "step": branch_step,
                "force_days": FORCE_DAYS,
                "features": {k: float(v) for k, v in features.items()},
                "heuristic_plan": heuristic_plan,
                "heuristic_margin": heuristic_margin,
                "oracle_plan": best["plan"],
                "oracle_margin": best["margin"],
                "heuristic_regret": regret,
                "plan_returns": labels,
            })

            # Continue the single baseline trajectory to the next branch state.
            run_to_step(env, cfg, a0, a1, (day + 1) * turns)

    regrets = [r["heuristic_regret"] for r in rows if r["heuristic_regret"] is not None]
    exact_matches = sum(1 for r in rows if r["oracle_plan"] is not None and r["heuristic_plan"] == r["oracle_plan"])
    plan_counts = {}
    for r in rows:
        p = r["oracle_plan"]
        if p is not None:
            plan_counts[p] = plan_counts.get(p, 0) + 1

    result = {
        "schema": "prize-solver-macro-rollout-v0-v1",
        "engine": "kaggle-environments==1.32.7 exact runtime",
        "seeds": list(SEEDS),
        "branch_days": list(BRANCH_DAYS),
        "force_days": FORCE_DAYS,
        "branch_states": len(rows),
        "rollouts": sum(len(r["plan_returns"]) for r in rows),
        "failures": failures,
        "heuristic_oracle_exact_matches": exact_matches,
        "heuristic_oracle_match_rate": (exact_matches / len(rows)) if rows else 0.0,
        "mean_heuristic_regret": mean(regrets) if regrets else None,
        "max_heuristic_regret": max(regrets) if regrets else None,
        "oracle_plan_counts": plan_counts,
        "rows": rows,
    }
    out = ROOT / "PRIZE_SOLVER_MACRO_ROLLOUT_V0.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("MACRO_RESULT", json.dumps({
        "branch_states": result["branch_states"],
        "rollouts": result["rollouts"],
        "failures": len(failures),
        "match_rate": result["heuristic_oracle_match_rate"],
        "mean_regret": result["mean_heuristic_regret"],
        "max_regret": result["max_heuristic_regret"],
        "oracle_plan_counts": plan_counts,
    }, sort_keys=True), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
