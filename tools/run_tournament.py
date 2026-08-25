"""Multi-seed local tournament harness for Kculture.

Key invariants:
- deterministic environment seeds;
- candidate evaluated from both seats by default;
- file-based agents are freshly loaded for every episode to prevent global
  state leakage across matches;
- raw outcomes/money deltas remain primary evidence;
- development, validation, and held-out seed partitions are explicit.

Examples:
    python tools/run_tournament.py --candidate file:main.py:agent --opponents pass starter --seeds 1001 1002
    python tools/run_tournament.py --candidate file:main.py:agent --opponent-pool configs/opponent_pool.json --seed-partition development
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import statistics
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BUILT_INS = {"pass", "random", "starter"}


def _load_file_agent(spec: str):
    body = spec[len("file:") :]
    if ":" not in body:
        raise ValueError(f"File agent '{spec}' must use file:PATH.py:FUNCTION")
    path_text, function_name = body.rsplit(":", 1)
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    unique = hashlib.sha256(f"{path}:{time.time_ns()}".encode()).hexdigest()[:16]
    module_spec = importlib.util.spec_from_file_location(f"kculture_episode_{unique}", path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    fn = getattr(module, function_name)
    if not callable(fn):
        raise TypeError(f"{spec} is not callable")
    return fn


def resolve_agent(spec: str):
    if spec in BUILT_INS:
        return spec
    if spec.startswith("file:"):
        return _load_file_agent(spec)
    if ":" not in spec:
        raise ValueError(
            f"Agent '{spec}' must be a built-in, file:PATH.py:FUNCTION, or MODULE:FUNCTION"
        )
    module_name, function_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    fn = getattr(module, function_name)
    if not callable(fn):
        raise TypeError(f"{spec} is not callable")
    return fn


def git_sha() -> str:
    if os.getenv("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def package_version() -> str:
    try:
        return version("kaggle-environments")
    except PackageNotFoundError:
        return "unknown"


def _load_seed_partition(config_path: str, partition: str):
    path = Path(config_path)
    if not path.is_absolute():
        path = ROOT / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    if partition not in payload:
        raise KeyError(f"Unknown seed partition: {partition}")
    return list(map(int, payload[partition]))


def _load_opponent_pool(config_path: str):
    path = Path(config_path)
    if not path.is_absolute():
        path = ROOT / path
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("pool_id", path.stem), [item["spec"] for item in payload["opponents"]]


def play(candidate_spec: str, opponent_spec: str, seed: int, candidate_seat: int):
    # Resolve inside each episode. file: specs therefore receive fresh module state.
    candidate = resolve_agent(candidate_spec)
    opponent = resolve_agent(opponent_spec)
    agents = [candidate, opponent] if candidate_seat == 0 else [opponent, candidate]

    started = time.perf_counter()
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    env.run(agents)
    elapsed = time.perf_counter() - started

    replay = env.toJSON()
    final = replay["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    rewards = [final[i].get("reward") for i in range(2)]

    c = candidate_seat
    o = 1 - c
    c_reward = rewards[c]
    o_reward = rewards[o]
    numeric = isinstance(c_reward, (int, float)) and isinstance(o_reward, (int, float))

    if statuses != ["DONE", "DONE"] or not numeric:
        outcome = "ERROR"
        delta = None
    else:
        delta = c_reward - o_reward
        if delta > 0:
            outcome = "WIN"
        elif delta < 0:
            outcome = "LOSS"
        else:
            outcome = "TIE"

    return {
        "seed": seed,
        "opponent": opponent_spec,
        "candidate_seat": candidate_seat,
        "statuses": statuses,
        "candidate_reward": c_reward,
        "opponent_reward": o_reward,
        "money_delta": delta,
        "outcome": outcome,
        "wall_seconds": elapsed,
    }


def aggregate(episodes):
    valid = [e for e in episodes if e["outcome"] != "ERROR" and e["money_delta"] is not None]
    deltas = [e["money_delta"] for e in valid]
    wins = sum(e["outcome"] == "WIN" for e in valid)
    losses = sum(e["outcome"] == "LOSS" for e in valid)
    ties = sum(e["outcome"] == "TIE" for e in valid)
    errors = len(episodes) - len(valid)
    n = len(valid)

    return {
        "episodes": len(episodes),
        "valid_episodes": n,
        "errors": errors,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate_excluding_ties": (wins / (wins + losses)) if (wins + losses) else None,
        "score_rate_tie_half": ((wins + 0.5 * ties) / n) if n else None,
        "mean_money_delta": statistics.mean(deltas) if deltas else None,
        "median_money_delta": statistics.median(deltas) if deltas else None,
        "pstdev_money_delta": statistics.pstdev(deltas) if len(deltas) > 1 else (0.0 if deltas else None),
        "min_money_delta": min(deltas) if deltas else None,
        "max_money_delta": max(deltas) if deltas else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="file:main.py:agent")

    opponent_group = parser.add_mutually_exclusive_group()
    opponent_group.add_argument("--opponents", nargs="+")
    opponent_group.add_argument("--opponent-pool")

    seed_group = parser.add_mutually_exclusive_group(required=True)
    seed_group.add_argument("--seeds", nargs="+", type=int)
    seed_group.add_argument(
        "--seed-partition", choices=["development", "validation", "held_out"]
    )
    parser.add_argument("--seed-config", default="configs/seed_partitions.json")
    parser.add_argument("--limit-seeds", type=int)
    parser.add_argument(
        "--single-seat",
        action="store_true",
        help="Run candidate only as player 0 instead of both seats.",
    )
    parser.add_argument("--output-root", default="artifacts/tournaments")
    args = parser.parse_args()

    pool_id = None
    if args.opponent_pool:
        pool_id, opponents = _load_opponent_pool(args.opponent_pool)
    else:
        opponents = args.opponents or ["pass", "starter"]

    if args.seed_partition:
        seeds = _load_seed_partition(args.seed_config, args.seed_partition)
    else:
        seeds = args.seeds
    if args.limit_seeds is not None:
        if args.limit_seeds < 1:
            raise ValueError("--limit-seeds must be >= 1")
        seeds = seeds[: args.limit_seeds]

    if "random" in opponents:
        print(
            "WARNING: Kaggle's built-in random agent constructs an unseeded RNG; "
            "do not use it for deterministic promotion gates.",
            file=sys.stderr,
        )

    seats = [0] if args.single_seat else [0, 1]
    episodes = []
    for opponent in opponents:
        for seed in seeds:
            for seat in seats:
                episodes.append(play(args.candidate, opponent, seed, seat))

    per_opponent = {
        opponent: aggregate([e for e in episodes if e["opponent"] == opponent])
        for opponent in opponents
    }

    signature_payload = {
        "candidate": args.candidate,
        "opponents": opponents,
        "opponent_pool": pool_id,
        "seed_partition": args.seed_partition,
        "seeds": seeds,
        "seats": seats,
    }
    signature = json.dumps(signature_payload, sort_keys=True).encode("utf-8")
    run_id = hashlib.sha256(signature).hexdigest()[:12]

    report = {
        "run_id": run_id,
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "candidate": args.candidate,
        "opponents": opponents,
        "opponent_pool": pool_id,
        "seed_partition": args.seed_partition,
        "seeds": seeds,
        "candidate_seats": seats,
        "episodes": episodes,
        "per_opponent": per_opponent,
        "overall": aggregate(episodes),
    }

    out_dir = ROOT / args.output_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tournament.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if report["overall"]["errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
