"""Strict closed-loop parity gate for Kaggriculture.

Reference: kaggle-environments==1.32.7.
Accelerator: pinned kagsim engine 1.32.7.

For every turn we reconstruct the exact agent-visible Kaggle observation via the
framework's shared-state path, compare it with the adapted accelerator observation,
call the real submission packages through Kaggle's own Agent wrapper, and feed the
same actions into both engines.  The gate fails on the first state/RNG/reward
mismatch.  No fixed exogenous tape is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import tempfile
import traceback
from pathlib import Path

import kagsim

from kaggle_exact_runtime import (
    AgentProcess,
    MASTER_SEED,
    agent_visible_observation,
    assert_reference_version,
    done_status,
    extract,
    kagsim_agent_observation,
    make_reference_env,
    make_seeds,
    norm,
    reference_config,
    reference_step,
)

EXPECTED_KAGSIM_COMMIT = "da15925dcf2357d750cbae4bf35712011b4733c8"


def diff_path(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                return f"{path}.{key} missing in Kaggle"
            if key not in b:
                return f"{path}.{key} missing in kagsim"
            d = diff_path(a[key], b[key], f"{path}.{key}" if path else str(key))
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} length Kaggle={len(a)} kagsim={len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = diff_path(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    if a != b:
        return f"{path}: Kaggle={a!r} kagsim={b!r}"
    return None


def canonical_digest(obj) -> str:
    raw = json.dumps(norm(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def reward_value(x):
    return None if x is None else float(x)


def play_parity(a_dir: Path, b_dir: Path, seed: int, a_seat: int) -> dict:
    env = make_reference_env(seed)
    game = kagsim.Game(int(seed))
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"parity_a_{seed}_{a_seat}")
    b = AgentProcess(ctx, b_dir, f"parity_b_{seed}_{a_seat}")
    action_hash = hashlib.sha256()
    state_hash = hashlib.sha256()
    compared_turns = 0
    max_agent_duration = 0.0
    try:
        turn = 0
        while not all(done_status(s.status) for s in env.state):
            if game.done:
                raise AssertionError(f"kagsim terminated before Kaggle at turn {turn}")

            real_obs = [agent_visible_observation(env, p) for p in (0, 1)]
            sim_obs = [
                kagsim_agent_observation(
                    game,
                    p,
                    remaining_overage_time=float(real_obs[p].get("remainingOverageTime", 60.0)),
                )
                for p in (0, 1)
            ]
            for p in (0, 1):
                d = diff_path(real_obs[p], sim_obs[p])
                if d:
                    raise AssertionError(f"turn {turn} seat {p}: {d}")
                state_hash.update(
                    json.dumps(real_obs[p], sort_keys=True, separators=(",", ":")).encode("utf-8")
                )
            compared_turns += 1

            if a_seat == 0:
                x, dx = a.call(real_obs[0], config)
                y, dy = b.call(real_obs[1], config)
            else:
                x, dx = b.call(real_obs[0], config)
                y, dy = a.call(real_obs[1], config)
            max_agent_duration = max(max_agent_duration, dx, dy)

            # The accelerator does not model execution-time overage.  A parity PASS
            # is valid only when neither agent consumes overage in the audited path.
            act_timeout = float(env.configuration.actTimeout)
            if dx > act_timeout or dy > act_timeout:
                raise AssertionError(
                    f"turn {turn}: agent overage encountered dx={dx:.6f} dy={dy:.6f} "
                    f"actTimeout={act_timeout}; timing parity not provable with kagsim"
                )

            pair = [x, y]
            if any(isinstance(z, BaseException) for z in pair):
                raise AssertionError(f"turn {turn}: agent returned exception object {pair!r}")
            action_hash.update(
                json.dumps(norm(pair), sort_keys=True, separators=(",", ":")).encode("utf-8")
            )

            # Same adaptive actions, same turn, both engines.  No PASS substitution.
            reference_step(env, pair, [dx, dy])
            game.step(pair[0], pair[1])
            turn += 1
            if turn > 725:
                raise RuntimeError("episode exceeded expected maximum length")

        if not game.done:
            raise AssertionError("Kaggle terminated but kagsim did not")

        real_rewards = [reward_value(env.state[p].reward) for p in (0, 1)]
        sim_rewards = [reward_value(game.reward(p)) for p in (0, 1)]
        if real_rewards != sim_rewards:
            raise AssertionError(f"final rewards Kaggle={real_rewards} kagsim={sim_rewards}")

        statuses = [str(env.state[p].status) for p in (0, 1)]
        if any(s not in {"DONE"} for s in statuses):
            raise AssertionError(f"reference episode ended non-DONE: {statuses}")

        return {
            "seed": int(seed),
            "a_seat": int(a_seat),
            "turns": int(turn),
            "compared_turns": int(compared_turns),
            "real_rewards": real_rewards,
            "kagsim_rewards": sim_rewards,
            "statuses": statuses,
            "max_agent_duration_s": max_agent_duration,
            "action_digest": action_hash.hexdigest(),
            "state_digest": state_hash.hexdigest(),
            "status": "PASS",
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
    ap.add_argument("--seed-count", type=int, default=8)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    assert_reference_version()
    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7":
        raise RuntimeError(f"expected kagsim ENGINE_VERSION 1.32.7, got {getattr(kagsim, 'ENGINE_VERSION', None)!r}")

    rows = []
    errors = []
    seeds = make_seeds(args.seed_count, args.master_seed)
    with tempfile.TemporaryDirectory(prefix="kculture-parity-v2-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        for seed in seeds:
            for a_seat in (0, 1):
                try:
                    row = play_parity(a_dir, b_dir, seed, a_seat)
                    rows.append(row)
                    print(
                        json.dumps(
                            {
                                "seed": seed,
                                "a_seat": a_seat,
                                "status": "PASS",
                                "turns": row["turns"],
                                "max_agent_duration_s": row["max_agent_duration_s"],
                            }
                        ),
                        flush=True,
                    )
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
                            {"seed": seed, "a_seat": a_seat, "status": "FAIL", "error": repr(exc)}
                        ),
                        flush=True,
                    )
                    break
            if errors:
                break

    payload = {
        "schema_version": "kculture-kaggle-parity-v2",
        "reference_backend": "kaggle-environments==1.32.7",
        "reference_observation_path": "Environment.__get_shared_state(seat).observation",
        "reference_agent_wrapper": "kaggle_environments.agent.Agent",
        "accelerator_backend": "kagsim ENGINE_VERSION 1.32.7",
        "kagsim_source_commit": os.environ.get("KAGSIM_SOURCE_COMMIT", "unknown"),
        "expected_kagsim_source_commit": EXPECTED_KAGSIM_COMMIT,
        "simulation_mode": "closed_loop_adaptive_path_dependent_rng",
        "forced_environment_tape": False,
        "falsy_action_pass_substitution": False,
        "agent_rng_manipulation": False,
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "episodes_expected": args.seed_count * 2,
        "episodes_passed": len(rows),
        "rows": rows,
        "errors": errors,
        "verdict": "PASS" if not errors and len(rows) == args.seed_count * 2 else "FAIL",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    if payload["verdict"] != "PASS":
        raise SystemExit(4)


if __name__ == "__main__":
    main()
