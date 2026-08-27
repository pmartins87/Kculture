"""Run one frozen CR-002 league pair on common fresh seeds and both seats."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from tools.run_tournament import aggregate, play  # noqa: E402


def load_config(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def agent_specs(cfg: dict) -> dict[str, str]:
    specs = {
        item["id"]: f"file:artifacts/cr002/agents/{item['id']}/main.py:agent"
        for item in cfg["public_agents"]
    }
    specs.update({item["id"]: item["spec"] for item in cfg["local_agents"]})
    return specs


def fresh_seeds(cfg: dict) -> list[int]:
    partitions = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))
    forbidden = {int(seed) for values in partitions.values() for seed in values}
    rng = random.Random(int(cfg["fresh_seed_master"]))
    seeds = []
    while len(seeds) < int(cfg["seeds_per_pair"]):
        s = rng.randrange(1, 2**31 - 1)
        if s not in forbidden and s not in seeds:
            seeds.append(s)
    return seeds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--config", default="configs/competitive_reset_league_v1.json")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    specs = agent_specs(cfg)
    if args.a == args.b:
        raise SystemExit("Pair must contain distinct agents")
    if args.a not in specs or args.b not in specs:
        raise SystemExit(f"Unknown pair {args.a}, {args.b}")

    seeds = fresh_seeds(cfg)
    episodes = []
    runner_errors = []
    for seed in seeds:
        for seat_a in (0, 1):
            try:
                row = play(specs[args.a], specs[args.b], seed, seat_a)
                row["agent_a"] = args.a
                row["agent_b"] = args.b
                episodes.append(row)
            except Exception as exc:
                runner_errors.append({
                    "seed": seed,
                    "seat_a": seat_a,
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                })

    valid_rows = list(episodes)
    overall = aggregate(valid_rows)
    # Runner exceptions did not reach aggregate(), so count them explicitly.
    overall["errors"] += len(runner_errors)
    overall["episodes"] += len(runner_errors)

    signature = hashlib.sha256(json.dumps({
        "league_id": cfg["league_id"],
        "a": args.a,
        "b": args.b,
        "seeds": seeds,
        "both_seats": True,
    }, sort_keys=True).encode()).hexdigest()[:16]

    report = {
        "experiment": "CR-002",
        "league_id": cfg["league_id"],
        "pair_id": f"{args.a}__vs__{args.b}",
        "run_signature": signature,
        "agent_a": args.a,
        "agent_b": args.b,
        "spec_a": specs[args.a],
        "spec_b": specs[args.b],
        "seeds": seeds,
        "both_seats": True,
        "episodes": episodes,
        "runner_errors": runner_errors,
        "overall_from_a_perspective": overall,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "pair": report["pair_id"],
        "seeds": seeds,
        "overall": overall,
        "runner_error_count": len(runner_errors),
    }, indent=2, sort_keys=True))

    if overall["errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
