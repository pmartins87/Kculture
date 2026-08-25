"""Multi-seed local tournament harness for Kculture.

Runs the candidate against a deterministic opponent pool, by default from both
player seats for every seed, and preserves raw episode outcomes plus aggregate
money/win diagnostics. Rating models can be layered on later; raw outcomes stay
primary.

Example:
    python tools/run_tournament.py \
        --candidate main:agent \
        --opponents pass starter \
        --seeds 1001 1002 1003 1004
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
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


def resolve_agent(spec: str):
    if spec in BUILT_INS:
        return spec
    if ":" not in spec:
        raise ValueError(f"Agent '{spec}' must be a built-in name or MODULE:FUNCTION")
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


def play(candidate_spec: str, opponent_spec: str, seed: int, candidate_seat: int):
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

    if statuses != ["DONE", "DONE"]:
        outcome = "ERROR"
    elif c_reward > o_reward:
        outcome = "WIN"
    elif c_reward < o_reward:
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
        "money_delta": c_reward - o_reward,
        "outcome": outcome,
        "wall_seconds": elapsed,
    }


def aggregate(episodes):
    valid = [e for e in episodes if e["outcome"] != "ERROR"]
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
    parser.add_argument("--candidate", default="main:agent")
    parser.add_argument("--opponents", nargs="+", default=["pass", "starter"])
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument(
        "--single-seat",
        action="store_true",
        help="Run candidate only as player 0 instead of both seats.",
    )
    parser.add_argument("--output-root", default="artifacts/tournaments")
    args = parser.parse_args()

    if "random" in args.opponents:
        print(
            "WARNING: Kaggle's built-in random agent constructs an unseeded RNG; "
            "do not use it for deterministic promotion gates.",
            file=sys.stderr,
        )

    seats = [0] if args.single_seat else [0, 1]
    episodes = []
    for opponent in args.opponents:
        for seed in args.seeds:
            for seat in seats:
                episodes.append(play(args.candidate, opponent, seed, seat))

    per_opponent = {
        opponent: aggregate([e for e in episodes if e["opponent"] == opponent])
        for opponent in args.opponents
    }

    signature = json.dumps(
        {
            "candidate": args.candidate,
            "opponents": args.opponents,
            "seeds": args.seeds,
            "seats": seats,
        },
        sort_keys=True,
    ).encode("utf-8")
    run_id = hashlib.sha256(signature).hexdigest()[:12]

    report = {
        "run_id": run_id,
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "candidate": args.candidate,
        "opponents": args.opponents,
        "seeds": args.seeds,
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
