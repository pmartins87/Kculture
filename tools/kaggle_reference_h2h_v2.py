"""Seat-balanced Kaggriculture H2H using the pinned Kaggle runtime itself.

No accelerator is involved.  Submission packages execute in isolated spawned
processes through kaggle_environments.agent.Agent and receive observations via the
same shared-state reconstruction path used by the official Environment runner.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import random
import statistics
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
    reference_config,
    reference_step,
)

BOOTSTRAP_DRAWS = 20000


def reward_value(x):
    return None if x is None else float(x)


def play_episode(a_dir: Path, b_dir: Path, seed: int, a_seat: int) -> dict:
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"ref_a_{seed}_{a_seat}")
    b = AgentProcess(ctx, b_dir, f"ref_b_{seed}_{a_seat}")
    max_duration = 0.0
    try:
        steps = 0
        while not all(done_status(s.status) for s in env.state):
            obs0 = agent_visible_observation(env, 0)
            obs1 = agent_visible_observation(env, 1)
            if a_seat == 0:
                x, dx = a.call(obs0, config)
                y, dy = b.call(obs1, config)
            else:
                x, dx = b.call(obs0, config)
                y, dy = a.call(obs1, config)
            max_duration = max(max_duration, dx, dy)
            reference_step(env, [x, y], [dx, dy])
            steps += 1
            if steps > 725:
                raise RuntimeError("Kaggle environment exceeded expected episode length")

        rewards = [reward_value(env.state[p].reward) for p in (0, 1)]
        statuses = [str(env.state[p].status) for p in (0, 1)]

        # Current promoted candidates are expected to finish DONE.  If a future
        # agent errors/timeouts, retain hosted semantics by treating a sole failure
        # as a loss instead of silently replacing its action with PASS.
        a_status = statuses[a_seat]
        b_status = statuses[1 - a_seat]
        if a_status == "DONE" and b_status != "DONE":
            score_a = 1.0
            margin_a = None
        elif a_status != "DONE" and b_status == "DONE":
            score_a = 0.0
            margin_a = None
        elif a_status != "DONE" or b_status != "DONE":
            score_a = 0.5
            margin_a = None
        else:
            if rewards[0] is None or rewards[1] is None:
                raise RuntimeError(f"DONE episode has null reward: {rewards}")
            margin_a = (rewards[0] - rewards[1]) if a_seat == 0 else (rewards[1] - rewards[0])
            score_a = 1.0 if margin_a > 0 else (0.0 if margin_a < 0 else 0.5)

        return {
            "seed": int(seed),
            "a_seat": int(a_seat),
            "reward_seat0": rewards[0],
            "reward_seat1": rewards[1],
            "status_seat0": statuses[0],
            "status_seat1": statuses[1],
            "margin_a": margin_a,
            "score_a": score_a,
            "steps": int(steps),
            "max_agent_duration_s": max_duration,
        }
    finally:
        a.close()
        b.close()


def basic_summary(rows: list[dict]) -> dict:
    scores = [float(r["score_a"]) for r in rows]
    margins = [float(r["margin_a"]) for r in rows if r["margin_a"] is not None]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_rate": statistics.mean(scores) if scores else None,
        "mean_margin_secondary": statistics.mean(margins) if margins else None,
        "median_margin_secondary": statistics.median(margins) if margins else None,
        "min_margin_secondary": min(margins) if margins else None,
        "max_margin_secondary": max(margins) if margins else None,
        "non_done_games": sum(
            r["status_seat0"] != "DONE" or r["status_seat1"] != "DONE" for r in rows
        ),
        "max_agent_duration_s": max((r["max_agent_duration_s"] for r in rows), default=0.0),
    }


def paired_seed_scores(rows: list[dict]) -> list[float]:
    by_seed: dict[int, list[float]] = {}
    for row in rows:
        by_seed.setdefault(int(row["seed"]), []).append(float(row["score_a"]))
    bad = sorted(s for s, vals in by_seed.items() if len(vals) != 2)
    if bad:
        raise RuntimeError(f"seat pairing incomplete for seeds: {bad[:20]}")
    return [statistics.mean(by_seed[s]) for s in sorted(by_seed)]


def paired_bootstrap(rows: list[dict], draws: int = BOOTSTRAP_DRAWS) -> dict:
    pair_scores = paired_seed_scores(rows)
    estimate = statistics.mean(pair_scores)
    if len(pair_scores) == 1:
        return {"paired_seeds": 1, "estimate": estimate, "ci95": [estimate, estimate], "pair_scores": pair_scores}
    rng = random.Random(MASTER_SEED ^ 0x9E3779B9)
    n = len(pair_scores)
    boots = [
        statistics.mean(pair_scores[rng.randrange(n)] for _ in range(n))
        for _ in range(draws)
    ]
    boots.sort()
    lo = boots[int(0.025 * (draws - 1))]
    hi = boots[int(0.975 * (draws - 1))]
    return {
        "paired_seeds": n,
        "estimate": estimate,
        "bootstrap_draws": draws,
        "ci95": [lo, hi],
        "pair_scores": pair_scores,
        "decisive_vs_0_5": bool(hi < 0.5 or lo > 0.5),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--a-id", required=True)
    ap.add_argument("--b-id", required=True)
    ap.add_argument("--seed-count", type=int, default=32)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    assert_reference_version()
    rows: list[dict] = []
    errors: list[dict] = []
    seeds = make_seeds(args.seed_count, args.master_seed)

    with tempfile.TemporaryDirectory(prefix="kculture-reference-v2-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        for seed in seeds:
            for a_seat in (0, 1):
                try:
                    rows.append(play_episode(a_dir, b_dir, seed, a_seat))
                except Exception as exc:
                    errors.append(
                        {
                            "seed": seed,
                            "a_seat": a_seat,
                            "error": repr(exc),
                            "traceback": traceback.format_exc()[-10000:],
                        }
                    )
            print(
                json.dumps(
                    {
                        "pair": f"{args.a_id}-{args.b_id}",
                        "completed_games": len(rows),
                        "errors": len(errors),
                        "last_seed": seed,
                    }
                ),
                flush=True,
            )
            if errors:
                break

    metrics = basic_summary(rows)
    by_seat = {
        str(seat): basic_summary([r for r in rows if r["a_seat"] == seat])
        for seat in (0, 1)
    }
    uncertainty = paired_bootstrap(rows) if not errors and len(rows) == args.seed_count * 2 else None
    payload = {
        "schema_version": "kculture-kaggle-reference-h2h-v2",
        "reference_backend": "kaggle-environments==1.32.7",
        "reference_observation_path": "Environment.__get_shared_state(seat).observation",
        "reference_agent_wrapper": "kaggle_environments.agent.Agent",
        "simulation_mode": "official_reference_engine_path_dependent_rng",
        "forced_environment_tape": False,
        "falsy_action_pass_substitution": False,
        "agent_rng_manipulation": False,
        "agent_process_isolation": "fresh_spawned_process_per_package_per_episode",
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "seat_balanced": True,
        "primary_metric": "seat_balanced_win_loss_score_rate",
        "money_margin_role": "diagnostic_only",
        "metrics_a_vs_b": metrics,
        "metrics_by_a_seat": by_seat,
        "paired_seed_uncertainty": uncertainty,
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
