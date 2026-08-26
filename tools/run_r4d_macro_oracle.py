"""Development-only macro-policy oracle for Kculture R4D.

This is deliberately *not* an exact full-game solver. It exhaustively compares
three already-audited macro continuations (frozen R4B, default->10C4S,
default->6C8S) from the same development seed/seat/opponent setting, using the
exact Kaggriculture engine. Public state at the first three-shop boundary is
captured from the frozen R4B trajectory and paired with the ex-post best macro
continuation. The resulting oracle labels are for offline distillation only;
opponent identity, seed and future outcome are forbidden deployment features.

Validation and held-out partitions are refused.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kaggle_environments import make

from inspect_r4d_default_context import _snapshot
from run_episode import git_sha, package_version, resolve_agent

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = {
    "baseline": "file:candidates/r4b_ablation_market_only.py:agent",
    "default_to_10c4s": "file:candidates/r4d_default_to_10c4s.py:agent",
    "default_to_6c8s": "file:candidates/r4d_default_to_6c8s.py:agent",
}
OUTCOME_RANK = {"ERROR": -1, "LOSS": 0, "TIE": 1, "WIN": 2}


def _episode(spec: str, opponent: str, seed: int, seat: int, capture_public: bool = False) -> dict:
    specs = [spec, opponent] if seat == 0 else [opponent, spec]
    agents = [resolve_agent(s) for s in specs]  # fresh module state per episode
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run(agents)
    replay = env.toJSON()
    final = replay["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    rewards = [final[i].get("reward") for i in range(2)]
    c, o = seat, 1 - seat
    if statuses != ["DONE", "DONE"] or not all(isinstance(v, (int, float)) for v in rewards):
        result = {"outcome": "ERROR", "terminal_delta": None, "statuses": statuses, "rewards": rewards}
    else:
        delta = float(rewards[c]) - float(rewards[o])
        result = {
            "outcome": "WIN" if delta > 0 else ("LOSS" if delta < 0 else "TIE"),
            "terminal_delta": delta,
            "statuses": statuses,
            "rewards": rewards,
        }
    if capture_public:
        result["public_boundary"] = _snapshot(replay, c)
    return result


def _oracle_choice(results: dict[str, dict]) -> str:
    def key(name: str):
        r = results[name]
        delta = r["terminal_delta"] if isinstance(r["terminal_delta"], (int, float)) else float("-inf")
        # Competition objective first: W/T/L. Money margin is only a tie-breaker
        # inside the offline oracle because ladder rating itself is outcome based.
        return (OUTCOME_RANK[r["outcome"]], delta)
    return max(CANDIDATES, key=key)


def _aggregate(rows: list[dict]) -> dict:
    out = {}
    for name in CANDIDATES:
        rs = [r["results"][name] for r in rows]
        valid = [x for x in rs if x["outcome"] != "ERROR"]
        wins = sum(x["outcome"] == "WIN" for x in valid)
        ties = sum(x["outcome"] == "TIE" for x in valid)
        losses = sum(x["outcome"] == "LOSS" for x in valid)
        deltas = [x["terminal_delta"] for x in valid]
        out[name] = {
            "n": len(rs), "wins": wins, "ties": ties, "losses": losses,
            "errors": len(rs) - len(valid),
            "score_rate_tie_half": (wins + 0.5 * ties) / len(valid) if valid else None,
            "mean_terminal_delta": sum(deltas) / len(deltas) if deltas else None,
        }
    labels = {name: sum(r["oracle_choice"] == name for r in rows) for name in CANDIDATES}
    oracle_outcomes = [r["results"][r["oracle_choice"]] for r in rows]
    wins = sum(x["outcome"] == "WIN" for x in oracle_outcomes)
    ties = sum(x["outcome"] == "TIE" for x in oracle_outcomes)
    losses = sum(x["outcome"] == "LOSS" for x in oracle_outcomes)
    out["oracle_upper_bound"] = {
        "labels": labels,
        "wins": wins, "ties": ties, "losses": losses,
        "score_rate_tie_half": (wins + 0.5 * ties) / len(oracle_outcomes) if oracle_outcomes else None,
        "mean_terminal_delta": sum(x["terminal_delta"] for x in oracle_outcomes) / len(oracle_outcomes),
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--seed-config", default="configs/seed_partitions.json")
    ap.add_argument("--partition", default="development")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    partitions = json.loads((ROOT / args.seed_config).read_text(encoding="utf-8"))
    if args.partition != "development":
        raise SystemExit(f"Macro oracle is development-only; refusing {args.partition!r}")
    seeds = [int(s) for s in partitions["development"]]

    rows = []
    for seed in seeds:
        for seat in (0, 1):
            results = {}
            for name, spec in CANDIDATES.items():
                results[name] = _episode(spec, args.opponent, seed, seat, capture_public=(name == "baseline"))
            public = results["baseline"].pop("public_boundary")
            choice = _oracle_choice(results)
            rows.append({
                "seed": seed,
                "candidate_seat": seat,
                "public_boundary": public,
                "results": results,
                "oracle_choice": choice,
                "oracle_outcome": results[choice]["outcome"],
                "oracle_terminal_delta": results[choice]["terminal_delta"],
            })
            print(json.dumps({
                "seed": seed, "seat": seat,
                "static_route": public.get("static_v7_route"),
                "baseline": results["baseline"]["terminal_delta"],
                "d10": results["default_to_10c4s"]["terminal_delta"],
                "d6": results["default_to_6c8s"]["terminal_delta"],
                "oracle": choice,
            }, sort_keys=True))

    report = {
        "schema_version": "r4d-macro-oracle-v1",
        "experiment": "KEXP-20260826-017",
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "partition": "development",
        "opponent": args.opponent,
        "deployment_forbidden_features": ["seed", "opponent_identity", "future_outcome", "future_actions", "private_opponent_inventory"],
        "candidate_specs": CANDIDATES,
        "episodes": rows,
        "aggregate": _aggregate(rows),
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["aggregate"], indent=2, sort_keys=True))

    if any(report["aggregate"][name]["errors"] for name in CANDIDATES):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
