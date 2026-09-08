"""Exact-reference matchup forensics for candidate selector research.

Runs two submission packages through kaggle-environments==1.32.7 using the same
hosted-faithful process isolation as kaggle_reference_h2h_v2, but additionally
captures only agent-visible checkpoints.  This is intended to explain *where*
a strategy wins (shop prefixes, market state, public farm development, etc.),
not to replace seat-balanced W/L as the promotion metric.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
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

DEFAULT_CHECKPOINTS = (72, 144, 216, 288, 360, 432, 504, 576, 648, 696, 719)


def _n(value) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def _tile_summary(farm: dict) -> dict:
    counts: dict[str, int] = {}
    planted = 0
    animals = 0
    weeds = 0
    unlocked = 0
    for row in farm.get("tiles", []) or []:
        for tile in row or []:
            if tile == "LOCKED":
                continue
            unlocked += 1
            if not isinstance(tile, dict):
                continue
            kind = str(tile.get("kind") or "UNKNOWN")
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "PLANT":
                planted += 1
            if tile.get("animal") is not None:
                animals += 1
            if kind == "WEED":
                weeds += 1
    return {
        "unlocked_tiles": unlocked,
        "planted_tiles": planted,
        "animal_tiles": animals,
        "weed_tiles": weeds,
        "kind_counts": counts,
    }


def visible_snapshot(obs: dict) -> dict:
    player = int(obs.get("player", 0) or 0)
    farms = list(obs.get("farms", []) or [])
    own = farms[player] if player < len(farms) else {}
    opp = farms[1 - player] if len(farms) > 1 else {}
    market = obs.get("market", {}) or {}
    private = obs.get("private", {}) or {}
    town = obs.get("town", {}) or {}
    return {
        "step": int(obs.get("step", 0) or 0),
        "day": int(obs.get("day", 0) or 0),
        "hour": int(obs.get("hour", 0) or 0),
        "shops": list(town.get("unlocked_shops", []) or []),
        "market_prices": dict(market.get("prices", {}) or {}),
        "market_inventory": dict(market.get("inventory", {}) or {}),
        "own_money": _n(own.get("money", 0)),
        "opp_money": _n(opp.get("money", 0)),
        "own_hands": len(own.get("hands", []) or []),
        "opp_hands": len(opp.get("hands", []) or []),
        "own_quadrants": len(own.get("unlocked_quadrants", []) or []),
        "opp_quadrants": len(opp.get("unlocked_quadrants", []) or []),
        "own_tiles": _tile_summary(own),
        "opp_tiles": _tile_summary(opp),
        "own_shed": dict(private.get("shed", {}) or {}),
        "own_seeds": dict(private.get("seeds", {}) or {}),
    }


def reward_value(x):
    return None if x is None else float(x)


def play_episode(a_dir: Path, b_dir: Path, seed: int, a_seat: int, checkpoints: set[int]) -> dict:
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"forensic_a_{seed}_{a_seat}")
    b = AgentProcess(ctx, b_dir, f"forensic_b_{seed}_{a_seat}")
    captures: dict[str, dict] = {}
    max_duration = 0.0
    try:
        steps = 0
        while not all(done_status(s.status) for s in env.state):
            obs0 = agent_visible_observation(env, 0)
            obs1 = agent_visible_observation(env, 1)
            current_step = int(obs0.get("step", steps) or steps)
            if current_step in checkpoints:
                # Capture the observation visible to A, whichever physical seat A occupies.
                captures[str(current_step)] = visible_snapshot(obs0 if a_seat == 0 else obs1)
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
        a_status = statuses[a_seat]
        b_status = statuses[1 - a_seat]
        if a_status == "DONE" and b_status != "DONE":
            score_a, margin_a = 1.0, None
        elif a_status != "DONE" and b_status == "DONE":
            score_a, margin_a = 0.0, None
        elif a_status != "DONE" or b_status != "DONE":
            score_a, margin_a = 0.5, None
        else:
            if rewards[0] is None or rewards[1] is None:
                raise RuntimeError(f"DONE episode has null reward: {rewards}")
            margin_a = (rewards[0] - rewards[1]) if a_seat == 0 else (rewards[1] - rewards[0])
            score_a = 1.0 if margin_a > 0 else (0.0 if margin_a < 0 else 0.5)

        return {
            "seed": int(seed),
            "a_seat": int(a_seat),
            "score_a": score_a,
            "margin_a_secondary": margin_a,
            "reward_seat0": rewards[0],
            "reward_seat1": rewards[1],
            "status_seat0": statuses[0],
            "status_seat1": statuses[1],
            "steps": steps,
            "max_agent_duration_s": max_duration,
            "checkpoints": captures,
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
    ap.add_argument("--seed-count", type=int, default=16)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--checkpoints", default=",".join(str(x) for x in DEFAULT_CHECKPOINTS))
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    assert_reference_version()
    checkpoints = {int(x.strip()) for x in args.checkpoints.split(",") if x.strip()}
    rows: list[dict] = []
    errors: list[dict] = []
    seeds = make_seeds(args.seed_count, args.master_seed)

    with tempfile.TemporaryDirectory(prefix="kculture-reference-forensics-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        for seed in seeds:
            for a_seat in (0, 1):
                try:
                    rows.append(play_episode(a_dir, b_dir, seed, a_seat, checkpoints))
                except Exception as exc:
                    errors.append({
                        "seed": int(seed),
                        "a_seat": int(a_seat),
                        "error": repr(exc),
                        "traceback": traceback.format_exc()[-10000:],
                    })
            print(json.dumps({
                "pair": f"{args.a_id}-{args.b_id}",
                "completed_games": len(rows),
                "errors": len(errors),
                "last_seed": int(seed),
            }), flush=True)
            if errors:
                break

    payload = {
        "schema_version": "kculture-kaggle-reference-matchup-forensics-v1",
        "reference_backend": "kaggle-environments==1.32.7",
        "purpose": "selector_and_component_research_only",
        "promotion_metric": "use kaggle_reference_h2h_v2 seat-balanced W/L; forensic features are explanatory",
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "checkpoints": sorted(checkpoints),
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
