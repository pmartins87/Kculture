"""Deterministic single-episode runner and replay logger for Kculture.

Example:
    python tools/run_episode.py --agent0 main:agent --agent1 starter --seed 123

Built-in Kaggle agents may be named directly: pass, random, starter.
Python callables use MODULE:FUNCTION syntax.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
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


def action_counts(replay: dict, player: int) -> dict:
    farmer = Counter()
    hands = Counter()
    market = Counter()

    for step in replay.get("steps", []):
        if player >= len(step):
            continue
        action = step[player].get("action")
        if not isinstance(action, dict):
            continue

        farmer_action = action.get("farmer")
        if isinstance(farmer_action, list) and farmer_action:
            farmer[str(farmer_action[0])] += 1

        for hand_action in action.get("hands", []) or []:
            if isinstance(hand_action, list) and hand_action:
                hands[str(hand_action[0])] += 1

        for market_action in action.get("market", []) or []:
            if isinstance(market_action, list) and market_action:
                market[str(market_action[0])] += 1

    return {
        "farmer": dict(sorted(farmer.items())),
        "hands": dict(sorted(hands.items())),
        "market": dict(sorted(market.items())),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent0", default="main:agent")
    parser.add_argument("--agent1", default="starter")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--episode-steps", type=int, default=720)
    parser.add_argument("--output-root", default="artifacts/episodes")
    args = parser.parse_args()

    a0 = resolve_agent(args.agent0)
    a1 = resolve_agent(args.agent1)

    started = time.perf_counter()
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": args.episode_steps, "seed": args.seed},
        debug=True,
    )
    env.run([a0, a1])
    elapsed = time.perf_counter() - started

    replay = env.toJSON()
    final = replay["steps"][-1]
    rewards = [final[i].get("reward") for i in range(2)]
    statuses = [final[i].get("status") for i in range(2)]

    if rewards[0] > rewards[1]:
        winner = 0
    elif rewards[1] > rewards[0]:
        winner = 1
    else:
        winner = "tie"

    episode_id = (
        f"seed-{args.seed}__{args.agent0.replace(':', '-')}_vs_"
        f"{args.agent1.replace(':', '-')}"
    ).replace("/", "-")
    out_dir = ROOT / args.output_root / episode_id
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "seed": args.seed,
        "episode_steps": args.episode_steps,
        "agents": [args.agent0, args.agent1],
        "statuses": statuses,
        "rewards": rewards,
        "money_delta_p0_minus_p1": rewards[0] - rewards[1],
        "winner": winner,
        "wall_seconds": elapsed,
        "action_counts": [action_counts(replay, 0), action_counts(replay, 1)],
    }

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "replay.json").write_text(
        json.dumps(replay, separators=(",", ":")), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, sort_keys=True))

    if statuses != ["DONE", "DONE"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
