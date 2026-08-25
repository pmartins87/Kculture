"""Find the earliest closed-loop action divergence between two agents.

Each policy is run independently against the same passive opponent with the same
seed and seat. Only the first differing action is treated as a shared-state
comparison: before that point the controlled player's action history is the
same, so the observations should also match. Later actions are intentionally
not compared as if they came from a common trajectory.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_episode import resolve_agent  # noqa: E402


def _episode(agent_spec: str, seed: int, seat: int):
    agent = resolve_agent(agent_spec)
    agents = [agent, "pass"] if seat == 0 else ["pass", agent]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    env.run(agents)
    return env.toJSON()


def _normalize_observation(observation):
    """Drop runtime-budget noise before state equality checks."""
    if not isinstance(observation, dict):
        return observation
    return {
        key: value
        for key, value in observation.items()
        if key not in {"remainingOverageTime"}
    }


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _public_context(player_step: dict):
    obs = player_step.get("observation") or {}
    town = obs.get("town") or {}
    farms = obs.get("farms") or []
    market = obs.get("market") or {}
    return {
        "day": obs.get("day"),
        "hour": obs.get("hour"),
        "shops": list(town.get("unlocked_shops") or []),
        "farm_money": [f.get("money") if isinstance(f, dict) else None for f in farms],
        "market_prices": dict(market.get("prices") or {}),
    }


def compare(agent_a: str, agent_b: str, seed: int, seat: int):
    a = _episode(agent_a, seed, seat)
    b = _episode(agent_b, seed, seat)
    a_steps = a.get("steps", [])
    b_steps = b.get("steps", [])
    limit = min(len(a_steps), len(b_steps))

    first = None
    observations_equal_before_divergence = True
    for index in range(limit):
        pa = a_steps[index][seat]
        pb = b_steps[index][seat]
        oa = _normalize_observation(pa.get("observation"))
        ob = _normalize_observation(pb.get("observation"))

        if _canonical(pa.get("action")) != _canonical(pb.get("action")):
            first = {
                "state_index": index,
                "agent_a_action": pa.get("action"),
                "agent_b_action": pb.get("action"),
                "observation_equal_at_divergence": _canonical(oa) == _canonical(ob),
                "public_context": _public_context(pa),
            }
            break

        if _canonical(oa) != _canonical(ob):
            observations_equal_before_divergence = False

    final_a = a_steps[-1][seat] if a_steps else {}
    final_b = b_steps[-1][seat] if b_steps else {}
    return {
        "seed": seed,
        "seat": seat,
        "first_divergence": first,
        "observations_equal_before_first_action_divergence": observations_equal_before_divergence,
        "agent_a_terminal": {
            "status": final_a.get("status"),
            "reward": final_a.get("reward"),
        },
        "agent_b_terminal": {
            "status": final_b.get("status"),
            "reward": final_b.get("reward"),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-a", required=True)
    parser.add_argument("--agent-b", required=True)
    parser.add_argument("--seed-partition", default="development")
    parser.add_argument("--limit-seeds", type=int, default=4)
    parser.add_argument("--output", default="artifacts/prefix_comparison.json")
    args = parser.parse_args()

    partitions = json.loads(
        (ROOT / "configs" / "seed_partitions.json").read_text(encoding="utf-8")
    )
    seeds = list(partitions[args.seed_partition])[: args.limit_seeds]
    rows = [
        compare(args.agent_a, args.agent_b, seed, seat)
        for seed in seeds
        for seat in (0, 1)
    ]

    divergence_indices = [
        row["first_divergence"]["state_index"]
        for row in rows
        if row["first_divergence"] is not None
    ]
    result = {
        "agent_a": args.agent_a,
        "agent_b": args.agent_b,
        "seed_partition": args.seed_partition,
        "seeds": seeds,
        "rows": rows,
        "summary": {
            "comparisons": len(rows),
            "identical_full_trajectory_actions": sum(
                row["first_divergence"] is None for row in rows
            ),
            "min_first_divergence_state_index": min(divergence_indices)
            if divergence_indices
            else None,
            "max_first_divergence_state_index": max(divergence_indices)
            if divergence_indices
            else None,
            "all_pre_divergence_observations_equal": all(
                row["observations_equal_before_first_action_divergence"]
                for row in rows
            ),
            "all_divergence_states_equal": all(
                row["first_divergence"] is None
                or row["first_divergence"]["observation_equal_at_divergence"]
                for row in rows
            ),
        },
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
