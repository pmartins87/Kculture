"""Deterministic single-episode runner and replay logger for Kculture.

Examples:
    python tools/run_episode.py --agent0 file:main.py:agent --agent1 starter --seed 123
    python tools/run_episode.py --agent0 file:main.py:agent --agent1 file:artifacts/public_opponents/cok_v8_779caae.py:agent --seed 123

Built-in Kaggle agents may be named directly: pass, random, starter.
File agents use file:PATH.py:FUNCTION and are loaded into fresh module state.
Python module callables may also use MODULE:FUNCTION syntax.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
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
    parser.add_argument("--agent0", default="file:main.py:agent")
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

    if statuses == ["DONE", "DONE"] and all(isinstance(v, (int, float)) for v in rewards):
        if rewards[0] > rewards[1]:
            winner = 0
        elif rewards[1] > rewards[0]:
            winner = 1
        else:
            winner = "tie"
        delta = rewards[0] - rewards[1]
    else:
        winner = "error"
        delta = None

    safe_a0 = args.agent0.replace(":", "-").replace("/", "-")
    safe_a1 = args.agent1.replace(":", "-").replace("/", "-")
    episode_id = f"seed-{args.seed}__{safe_a0}_vs_{safe_a1}"
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
        "money_delta_p0_minus_p1": delta,
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
