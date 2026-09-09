"""Hosted-faithful action trace for structural CR071 research.

Runs two frozen submission packages through kaggle-environments==1.32.7 using
the exact runtime primitives already parity-gated in this branch and records the
action emitted by each agent at every step.  This is explanatory infrastructure:
promotion still uses seat-balanced W/L in kaggle_reference_h2h_v2.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import tempfile
import traceback
from pathlib import Path

from kaggle_exact_runtime import (
    AgentProcess,
    MASTER_SEED,
    agent_visible_observation,
    assert_reference_version,
    done_status,
    extract,
    make_reference_env,
    make_seeds,
    norm,
    reference_config,
    reference_step,
)


def reward_value(x):
    return None if x is None else float(x)


def play_episode(a_dir: Path, b_dir: Path, seed: int, a_seat: int) -> dict:
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"trace_a_{seed}_{a_seat}")
    b = AgentProcess(ctx, b_dir, f"trace_b_{seed}_{a_seat}")
    trace = []
    max_duration = 0.0
    try:
        steps = 0
        while not all(done_status(s.status) for s in env.state):
            obs0 = agent_visible_observation(env, 0)
            obs1 = agent_visible_observation(env, 1)
            current_step = int(obs0.get("step", steps) or steps)
            if a_seat == 0:
                x, dx = a.call(obs0, config)
                y, dy = b.call(obs1, config)
                action_a, action_b = x, y
            else:
                x, dx = b.call(obs0, config)
                y, dy = a.call(obs1, config)
                action_a, action_b = y, x
            max_duration = max(max_duration, dx, dy)
            trace.append({
                "step": current_step,
                "action_a": norm(action_a),
                "action_b": norm(action_b),
            })
            reference_step(env, [x, y], [dx, dy])
            steps += 1
            if steps > 725:
                raise RuntimeError("Kaggle environment exceeded expected episode length")

        rewards = [reward_value(env.state[p].reward) for p in (0, 1)]
        statuses = [str(env.state[p].status) for p in (0, 1)]
        a_status = statuses[a_seat]
        b_status = statuses[1 - a_seat]
        if a_status == "DONE" and b_status != "DONE":
            score_a, margin_a = 1.0, None
        elif a_status != "DONE" and b_status == "DONE":
            score_a, margin_a = 0.0, None
        elif a_status != "DONE" or b_status != "DONE":
            score_a, margin_a = 0.5, None
        else:
            if rewards[0] is None or rewards[1] is None:
                raise RuntimeError(f"DONE episode has null reward: {rewards}")
            margin_a = (rewards[0] - rewards[1]) if a_seat == 0 else (rewards[1] - rewards[0])
            score_a = 1.0 if margin_a > 0 else (0.0 if margin_a < 0 else 0.5)

        return {
            "seed": int(seed),
            "a_seat": int(a_seat),
            "score_a": score_a,
            "margin_a_secondary": margin_a,
            "reward_seat0": rewards[0],
            "reward_seat1": rewards[1],
            "status_seat0": statuses[0],
            "status_seat1": statuses[1],
            "steps": steps,
            "max_agent_duration_s": max_duration,
            "trace": trace,
        }
    finally:
        a.close()
        b.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--a-id", required=True)
    ap.add_argument("--b-id", required=True)
    ap.add_argument("--seed-count", type=int, default=16)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    assert_reference_version()
    rows = []
    errors = []
    seeds = make_seeds(args.seed_count, args.master_seed)
    with tempfile.TemporaryDirectory(prefix="kculture-reference-action-trace-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        for seed in seeds:
            for a_seat in (0, 1):
                try:
                    rows.append(play_episode(a_dir, b_dir, seed, a_seat))
                except Exception as exc:
                    errors.append({
                        "seed": int(seed),
                        "a_seat": int(a_seat),
                        "error": repr(exc),
                        "traceback": traceback.format_exc()[-10000:],
                    })
            print(json.dumps({
                "pair": f"{args.a_id}-{args.b_id}",
                "completed_games": len(rows),
                "errors": len(errors),
                "last_seed": int(seed),
            }), flush=True)
            if errors:
                break

    payload = {
        "schema_version": "kculture-kaggle-reference-action-trace-v1",
        "reference_backend": "kaggle-environments==1.32.7",
        "purpose": "structural_component_research_only",
        "promotion_metric": "seat-balanced W/L remains primary; trace is explanatory",
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "errors": errors,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
