"""Inspect public state at the first fully observed three-shop boundary.

Development-only diagnostic for KEXP-20260826-016. It runs the frozen R4B
market-only candidate against one exact public opponent on the four development
seeds implicated by KEXP-014's weak late 8C/6S *observed farm state*, both
seats, then captures only information publicly observable to both players at
the first state where three shops are unlocked.

Important: KEXP-014 classified the physical farm at step 672, not COK's hidden
route label. Therefore this diagnostic records the static shop-prefix route
signal but does not assume every sampled row is the COK default route.
Seed IDs are only an analysis sampling device and are never policy features.
Validation/held-out partitions are refused.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from kaggle_environments import make

from run_episode import git_sha, package_version, resolve_agent

ROOT = Path(__file__).resolve().parents[1]
TARGET_SEEDS = (150614441, 1369296235, 393297156, 163219477)
MILK_SUPPORT = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}
LAYOUT_KEYS = ("cow", "sheep", "wheat", "melon", "strawberry", "empty_pasture")


def _farm_vector(farm: dict) -> dict:
    c = Counter()
    for row in farm.get("tiles", []) or []:
        if not isinstance(row, list):
            continue
        for tile in row:
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PASTURE":
                animal = tile.get("animal")
                if animal == "COW":
                    c["cow"] += 1
                elif animal == "SHEEP":
                    c["sheep"] += 1
                else:
                    c["empty_pasture"] += 1
            elif kind == "PLANT":
                crop = str(tile.get("crop") or "").lower()
                if crop:
                    c[crop] += 1
            elif kind == "WEED":
                c["weed"] += 1
            elif kind:
                c[str(kind).lower()] += 1
    return dict(sorted(c.items()))


def _signed_layout(ours: dict, opp: dict) -> dict:
    return {k: int(ours.get(k, 0)) - int(opp.get(k, 0)) for k in LAYOUT_KEYS}


def _layout_distance(ours: dict, opp: dict) -> int:
    return sum(abs(int(ours.get(k, 0)) - int(opp.get(k, 0))) for k in LAYOUT_KEYS)


def _actor_summary(farm: dict) -> dict:
    farmer = farm.get("farmer") if isinstance(farm, dict) else None
    hands = farm.get("hands", []) if isinstance(farm, dict) else []

    def pos(actor):
        if not isinstance(actor, dict):
            return None
        p = actor.get("position")
        return p if isinstance(p, (list, tuple)) else None

    return {
        "farmer_position": pos(farmer),
        "hand_count": len(hands or []),
        "hand_positions": [pos(h) for h in (hands or []) if isinstance(h, dict)],
    }


def _static_v7_route(first3: list[str]) -> str:
    if first3[:1] == ["YARN_STORE"]:
        return "6c12s_4q_first_yarn"
    if "YARN_STORE" in first3[:2]:
        return "6c12s_4q_second_yarn"
    if "YARN_STORE" in first3[:3]:
        return "6c8s_3q"
    if MILK_SUPPORT.intersection(first3[:3]):
        return "10c4s_3q"
    return "8c6s_3q"


def _first_three_boundary(replay: dict, candidate_seat: int) -> tuple[int, dict]:
    for step, frame in enumerate(replay.get("steps", [])):
        obs = frame[candidate_seat].get("observation", {})
        town = obs.get("town", {}) if isinstance(obs, dict) else {}
        shops = list(town.get("unlocked_shops", []) or []) if isinstance(town, dict) else []
        if len(shops) >= 3:
            return step, obs
    raise RuntimeError("Replay never exposed three unlocked shops")


def _snapshot(replay: dict, candidate_seat: int) -> dict:
    step, obs = _first_three_boundary(replay, candidate_seat)
    farms = obs.get("farms", []) or []
    if len(farms) != 2:
        raise RuntimeError(f"Expected two public farms, got {len(farms)}")
    ours = farms[candidate_seat]
    opp = farms[1 - candidate_seat]
    ov = _farm_vector(ours)
    pv = _farm_vector(opp)
    signed = _signed_layout(ov, pv)
    town = obs.get("town", {}) or {}
    market = obs.get("market", {}) or {}
    shops = list(town.get("unlocked_shops", []) or [])
    first3 = shops[:3]
    static_route = _static_v7_route(first3)
    prices = market.get("prices", {}) if isinstance(market, dict) else {}

    return {
        "boundary_step": step,
        "day": obs.get("day"),
        "hour": obs.get("hour"),
        "first_three_shops": first3,
        "static_v7_route": static_route,
        "static_default_8c6s": static_route == "8c6s_3q",
        "yarn_in_first_three": "YARN_STORE" in first3,
        "milk_support_in_first_three": bool(MILK_SUPPORT.intersection(first3)),
        "candidate_money": float(ours.get("money", 0) or 0),
        "opponent_money": float(opp.get("money", 0) or 0),
        "money_diff": float(ours.get("money", 0) or 0) - float(opp.get("money", 0) or 0),
        "candidate_layout": ov,
        "opponent_layout": pv,
        "signed_layout_diff": signed,
        "layout_l1_distance": _layout_distance(ov, pv),
        "candidate_actors": _actor_summary(ours),
        "opponent_actors": _actor_summary(opp),
        "hand_count_diff": len(ours.get("hands", []) or []) - len(opp.get("hands", []) or []),
        "market_prices": dict(sorted(prices.items())) if isinstance(prices, dict) else prices,
        "town": town,
    }


def _run(candidate_spec: str, opponent_spec: str, seed: int, candidate_seat: int) -> dict:
    specs = [candidate_spec, opponent_spec] if candidate_seat == 0 else [opponent_spec, candidate_spec]
    agents = [resolve_agent(spec) for spec in specs]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    env.run(agents)
    replay = env.toJSON()
    final = replay["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    rewards = [final[i].get("reward") for i in range(2)]
    if statuses != ["DONE", "DONE"] or not all(isinstance(v, (int, float)) for v in rewards):
        raise RuntimeError(f"Unclean terminal seed={seed} seat={candidate_seat}: {statuses} {rewards}")
    c = candidate_seat
    o = 1 - c
    terminal_delta = float(rewards[c]) - float(rewards[o])
    snap = _snapshot(replay, c)
    snap.update(
        {
            "seed": seed,
            "candidate_seat": c,
            "terminal_delta": terminal_delta,
            "outcome": "WIN" if terminal_delta > 0 else ("LOSS" if terminal_delta < 0 else "TIE"),
            "statuses": statuses,
            "rewards": rewards,
        }
    )
    return snap


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="file:candidates/r4b_ablation_market_only.py:agent")
    parser.add_argument("--opponent", required=True)
    parser.add_argument("--seed-config", default="configs/seed_partitions.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    partitions = json.loads((ROOT / args.seed_config).read_text(encoding="utf-8"))
    development = set(partitions["development"])
    validation = set(partitions["validation"])
    held_out = set(partitions["held_out"])
    target = set(TARGET_SEEDS)
    if not target <= development or target & validation or target & held_out:
        raise SystemExit("R4D context target seeds are not a strict development-only subset")

    rows = []
    for seed in TARGET_SEEDS:
        for seat in (0, 1):
            rows.append(_run(args.candidate, args.opponent, seed, seat))

    report = {
        "schema_version": "r4d-default-context-v2",
        "experiment": "KEXP-20260826-016",
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "candidate": args.candidate,
        "opponent": args.opponent,
        "development_only": True,
        "target_seeds": list(TARGET_SEEDS),
        "episodes": rows,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "episodes": len(rows),
        "wins": sum(r["outcome"] == "WIN" for r in rows),
        "losses": sum(r["outcome"] == "LOSS" for r in rows),
        "static_default_rows": sum(r["static_default_8c6s"] for r in rows),
        "mean_layout_l1": sum(r["layout_l1_distance"] for r in rows) / len(rows),
        "output": str(out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
