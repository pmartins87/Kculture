"""Validate pinned local Kaggriculture against actual hosted Kaggle replays.

This is the highest-trust local parity gate.  It does not execute our agents and
it does not use kagsim.  Instead it takes the action pair recorded by real hosted
Kaggle episodes, feeds those actions into kaggle-environments==1.32.7 with the
hosted RNG seed, and checks the resulting raw environment state after every turn.

The sole intentionally ignored observation field is remainingOverageTime: it is
wall-clock execution accounting and the replay does not contain per-turn agent
runtime logs needed to reconstruct it.  Game state, RNG-dependent shop/weed
events, rewards, statuses, and every other observation field must match exactly.
"""
from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from kaggle_exact_runtime import EXPECTED_KAGGLE_VERSION, assert_reference_version, norm

IGNORED_OBSERVATION_KEYS = {"remainingOverageTime"}


def clean_observation(obs):
    out = norm(obs)
    for key in IGNORED_OBSERVATION_KEYS:
        out.pop(key, None)
    return out


def diff_path(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            child = f"{path}.{key}" if path else str(key)
            if key not in a:
                return f"{child} missing locally"
            if key not in b:
                return f"{child} missing in hosted replay"
            d = diff_path(a[key], b[key], child)
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} length local={len(a)} hosted={len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = diff_path(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    # Treat numerically identical int/float representations as equal, exactly as
    # JSON/Kaggle semantics do for values such as 3000 vs 3000.0.
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if float(a) == float(b):
            return None
    if a != b:
        return f"{path}: local={a!r} hosted={b!r}"
    return None


def compare_state(env, hosted_step, replay_name: str, turn: int):
    if len(env.state) != len(hosted_step):
        raise AssertionError(
            f"{replay_name} turn {turn}: player count local={len(env.state)} hosted={len(hosted_step)}"
        )
    for p, (local_state, hosted_state) in enumerate(zip(env.state, hosted_step)):
        local_obs = clean_observation(local_state.observation)
        hosted_obs = clean_observation(hosted_state.get("observation", {}))
        d = diff_path(local_obs, hosted_obs, f"seat{p}.observation")
        if d:
            raise AssertionError(f"{replay_name} turn {turn}: {d}")

        local_status = str(local_state.status)
        hosted_status = str(hosted_state.get("status"))
        if local_status != hosted_status:
            raise AssertionError(
                f"{replay_name} turn {turn} seat {p}: status local={local_status} hosted={hosted_status}"
            )

        local_reward = local_state.reward
        hosted_reward = hosted_state.get("reward")
        if local_reward is None or hosted_reward is None:
            if local_reward is not None or hosted_reward is not None:
                raise AssertionError(
                    f"{replay_name} turn {turn} seat {p}: reward local={local_reward!r} hosted={hosted_reward!r}"
                )
        elif float(local_reward) != float(hosted_reward):
            raise AssertionError(
                f"{replay_name} turn {turn} seat {p}: reward local={local_reward!r} hosted={hosted_reward!r}"
            )


def build_replay_env(replay: dict):
    from kaggle_environments import make

    config = dict(replay.get("configuration") or {})
    hosted_seed = (replay.get("info") or {}).get("seed")
    if hosted_seed is None:
        raise AssertionError("hosted replay does not expose info.seed")
    # Hosted replay configuration may serialize seed as null; info.seed is the
    # actual RNG seed chosen for the episode and is what reproduces the trajectory.
    config["seed"] = int(hosted_seed)
    env = make("kaggriculture", configuration=config, debug=False)
    env.reset(2)
    return env, int(hosted_seed)


def validate_replay(path: Path) -> dict:
    replay = json.loads(path.read_text(encoding="utf-8"))
    if replay.get("name") != "kaggriculture":
        raise AssertionError(f"{path}: not a kaggriculture replay")
    if str(replay.get("module_version")) != EXPECTED_KAGGLE_VERSION:
        raise AssertionError(
            f"{path}: hosted module_version={replay.get('module_version')!r}, "
            f"expected {EXPECTED_KAGGLE_VERSION}"
        )
    steps = replay.get("steps") or []
    if not steps:
        raise AssertionError(f"{path}: replay has no steps")

    env, seed = build_replay_env(replay)
    compare_state(env, steps[0], path.name, 0)

    # In Kaggle replay JSON, steps[t].action is the action that produced state t.
    # Step 0 contains the reset/default action.  Therefore replay 1..N-1.
    for turn in range(1, len(steps)):
        actions = [steps[turn][p].get("action") for p in range(len(steps[turn]))]
        env.step(actions)
        compare_state(env, steps[turn], path.name, turn)

    local_rewards = [s.reward for s in env.state]
    hosted_rewards = replay.get("rewards")
    if hosted_rewards is not None:
        if len(local_rewards) != len(hosted_rewards) or any(
            (x is None) != (y is None) or (x is not None and float(x) != float(y))
            for x, y in zip(local_rewards, hosted_rewards)
        ):
            raise AssertionError(
                f"{path.name}: final rewards local={local_rewards!r} hosted={hosted_rewards!r}"
            )
    local_statuses = [str(s.status) for s in env.state]
    hosted_statuses = [str(x) for x in (replay.get("statuses") or [])]
    if hosted_statuses and local_statuses != hosted_statuses:
        raise AssertionError(
            f"{path.name}: final statuses local={local_statuses!r} hosted={hosted_statuses!r}"
        )

    return {
        "replay": str(path),
        "episode_id": (replay.get("info") or {}).get("EpisodeId"),
        "seed": seed,
        "turns": len(steps),
        "final_rewards": [None if x is None else float(x) for x in local_rewards],
        "final_statuses": local_statuses,
        "status": "PASS",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Directory containing hosted replay JSON files")
    ap.add_argument("--output", required=True)
    ap.add_argument("--limit", type=int, default=0, help="0 = validate every replay")
    args = ap.parse_args()

    assert_reference_version()
    root = Path(args.root)
    files = sorted(root.rglob("*-replay.json"))
    if args.limit > 0:
        files = files[: args.limit]
    if not files:
        raise SystemExit(f"no hosted replay JSON files found under {root}")

    rows = []
    errors = []
    for path in files:
        try:
            row = validate_replay(path)
            rows.append(row)
            print(
                json.dumps(
                    {
                        "replay": path.name,
                        "episode_id": row["episode_id"],
                        "seed": row["seed"],
                        "turns": row["turns"],
                        "status": "PASS",
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            errors.append(
                {
                    "replay": str(path),
                    "error": repr(exc),
                    "traceback": traceback.format_exc()[-10000:],
                }
            )
            print(
                json.dumps({"replay": path.name, "status": "FAIL", "error": repr(exc)}),
                flush=True,
            )
            # First divergence is enough to invalidate the local-reference claim.
            break

    payload = {
        "schema_version": "kculture-hosted-golden-replay-parity-v1",
        "reference_backend": f"kaggle-environments=={EXPECTED_KAGGLE_VERSION}",
        "hosted_truth": True,
        "comparison": "raw_environment_state_transition_by_transition",
        "ignored_observation_keys": sorted(IGNORED_OBSERVATION_KEYS),
        "ignored_reason": "remainingOverageTime depends on hosted wall-clock agent durations absent from replay",
        "replays_discovered": len(files),
        "replays_passed": len(rows),
        "rows": rows,
        "errors": errors,
        "verdict": "PASS" if not errors and len(rows) == len(files) else "FAIL",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    if payload["verdict"] != "PASS":
        raise SystemExit(5)


if __name__ == "__main__":
    main()
