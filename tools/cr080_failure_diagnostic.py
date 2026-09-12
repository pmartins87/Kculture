"""CR080 post-failure telemetry on the already-used confirmation seeds.

This script is diagnostic only. It does not tune or select a CR080 variant.
It replays the frozen package with the exact pinned Kaggle runtime and measures
closed-loop drift from the source route that CR080 selected for each day.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import json
import math
import multiprocessing as mp
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from kaggle_exact_runtime import (
    AgentProcess,
    agent_visible_observation,
    done_status,
    extract,
    make_reference_env,
    make_seeds,
    reference_config,
    reference_step,
)


def _load_runtime_and_bank(agent_dir: Path):
    spec = importlib.util.spec_from_file_location("cr080_diag_runtime", agent_dir / "main.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import CR080 runtime")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with gzip.open(agent_dir / "routes.json.gz", "rt", encoding="utf-8") as f:
        bank = json.load(f)
    if not bank:
        raise RuntimeError("empty CR080 route bank")
    return mod, bank


def _components(current: dict, reference: dict) -> dict:
    farmer_dist = sum(abs(a - b) for a, b in zip(current["farmer"], reference["farmer"]))
    tile_mismatch = sum(a != b for a, b in zip(current["tiles"], reference["tiles"]))
    quadrant_diff = len(set(current["quadrants"]) ^ set(reference["quadrants"]))
    shop_l1 = sum(
        abs(current["shops"].get(k, 0) - reference["shops"].get(k, 0))
        for k in current["shops"].keys() | reference["shops"].keys()
    )
    economy_l1 = sum(abs(a - b) for a, b in zip(current["economy"], reference["economy"]))
    ref_money = math.expm1(reference["economy"][0]) if reference.get("economy") else None
    cur_money = math.expm1(current["economy"][0]) if current.get("economy") else None
    return {
        "farmer_dist": farmer_dist,
        "tile_mismatch": tile_mismatch,
        "quadrant_diff": quadrant_diff,
        "shop_l1": shop_l1,
        "economy_l1": economy_l1,
        "money_gap": None if ref_money is None or cur_money is None else cur_money - ref_money,
        "structural_cost": 10 * farmer_dist + tile_mismatch + 25 * quadrant_diff,
    }


def _worker_actions(action: dict) -> list[list]:
    return [list(action.get("farmer") or ["PASS"])] + [list(x) for x in (action.get("hands") or [])]


def _mean(xs):
    return statistics.mean(xs) if xs else 0.0


def _median(xs):
    return statistics.median(xs) if xs else 0.0


def play_episode(a_dir: Path, b_dir: Path, rt, bank: list[dict], seed: int, a_seat: int) -> dict:
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"cr080_diag_a_{seed}_{a_seat}")
    b = AgentProcess(ctx, b_dir, f"cr080_diag_b_{seed}_{a_seat}")

    selected = None
    selected_day = None
    selected_indices = []
    day_rows = []
    day_totals = defaultdict(Counter)
    totals = Counter()
    max_duration = 0.0

    try:
        steps = 0
        while not all(done_status(s.status) for s in env.state):
            obs0 = agent_visible_observation(env, 0)
            obs1 = agent_visible_observation(env, 1)
            obs_a = obs0 if a_seat == 0 else obs1
            step = int(rt.clock(obs_a))
            day = step // 24

            current_sig = rt.signature(obs_a)
            if selected is None or day != selected_day:
                if selected is not None and day < len(bank[selected]["signatures"]):
                    drift = _components(current_sig, bank[selected]["signatures"][day])
                    drift.update({"day": day, "kind": "prior_route_end_drift", "route": selected})
                    day_rows.append(drift)
                costs = [(*rt.route_cost(current_sig, row["signatures"][day]), i) for i, row in enumerate(bank)]
                best = min(costs)
                selected = int(best[-1])
                selected_indices.append(selected)
                selected_day = day
                match = _components(current_sig, bank[selected]["signatures"][day])
                match.update({"day": day, "kind": "selection_match", "route": selected})
                day_rows.append(match)

            ref = bank[selected]
            ref_action = ref["actions"][step]
            farm = obs_a["farms"][a_seat]
            positions = [list(farm["farmer"])] + [list(x) for x in (farm.get("hands") or [])]
            expected_positions = [list(x) for x in ref["positions"][step]]
            planned = _worker_actions(ref_action)

            cur_hands = max(0, len(positions) - 1)
            ref_hands = max(0, len(expected_positions) - 1)
            dc = day_totals[day]
            totals["worker_steps"] += len(positions)
            totals["hand_steps"] += cur_hands
            totals["expected_hand_steps"] += ref_hands
            dc["worker_steps"] += len(positions)
            dc["hand_steps"] += cur_hands
            dc["expected_hand_steps"] += ref_hands
            if cur_hands < ref_hands:
                totals["steps_with_hand_shortfall"] += 1
                totals["hand_shortfall_worker_steps"] += ref_hands - cur_hands
                dc["steps_with_hand_shortfall"] += 1
                dc["hand_shortfall_worker_steps"] += ref_hands - cur_hands
            elif cur_hands > ref_hands:
                totals["steps_with_hand_excess"] += 1
                totals["hand_excess_worker_steps"] += cur_hands - ref_hands
                dc["steps_with_hand_excess"] += 1
                dc["hand_excess_worker_steps"] += cur_hands - ref_hands

            mismatch_workers = 0
            replaced_productive = 0
            weed_candidates = 0
            for i, pos in enumerate(positions):
                target = expected_positions[i] if i < len(expected_positions) else pos
                source_act = planned[i] if i < len(planned) else ["PASS"]
                if pos != target:
                    mismatch_workers += 1
                    if source_act and source_act[0] not in {"PASS", "NORTH", "SOUTH", "EAST", "WEST"}:
                        replaced_productive += 1
                else:
                    x, y = pos
                    tile = farm["tiles"][y][x]
                    if (
                        source_act
                        and source_act[0] in {"PLANT", "WATER", "HARVEST"}
                        and isinstance(tile, dict)
                        and tile.get("kind") == "WEED"
                    ):
                        weed_candidates += 1
            totals["position_mismatch_worker_steps"] += mismatch_workers
            totals["productive_source_actions_at_mismatched_positions"] += replaced_productive
            totals["weed_repair_candidates"] += weed_candidates
            dc["position_mismatch_worker_steps"] += mismatch_workers
            dc["productive_source_actions_at_mismatched_positions"] += replaced_productive
            dc["weed_repair_candidates"] += weed_candidates
            if mismatch_workers:
                totals["steps_with_position_mismatch"] += 1
                dc["steps_with_position_mismatch"] += 1
            omitted = max(0, len(planned) - len(positions))
            extra = max(0, len(positions) - len(planned))
            totals["reference_hand_actions_omitted_by_missing_workers"] += omitted
            totals["extra_current_workers_without_reference_action"] += extra
            dc["reference_hand_actions_omitted_by_missing_workers"] += omitted
            dc["extra_current_workers_without_reference_action"] += extra

            market_ref = list(ref_action.get("market") or [])
            hires = sum(1 for o in market_ref if o and o[0] == "HIRE")
            totals["source_hire_orders"] += hires
            totals["source_market_orders"] += len(market_ref)
            dc["source_hire_orders"] += hires
            dc["source_market_orders"] += len(market_ref)

            if a_seat == 0:
                action_a, da = a.call(obs0, config)
                action_b, db = b.call(obs1, config)
                actions = [action_a, action_b]
            else:
                action_b, db = b.call(obs0, config)
                action_a, da = a.call(obs1, config)
                actions = [action_b, action_a]
            max_duration = max(max_duration, da, db)

            actual_workers = _worker_actions(action_a)
            mutations = sum(
                actual_workers[i] != planned[i]
                for i in range(min(len(actual_workers), len(planned)))
            )
            totals["actual_worker_action_mutations"] += mutations
            dc["actual_worker_action_mutations"] += mutations
            if list(action_a.get("market") or []) != market_ref[:10]:
                totals["market_action_mismatch_steps"] += 1
                dc["market_action_mismatch_steps"] += 1

            reference_step(env, actions, [da, db] if a_seat == 0 else [db, da])
            steps += 1
            if steps > 725:
                raise RuntimeError("episode exceeded expected length")

        rewards = [float(env.state[p].reward) for p in (0, 1)]
        statuses = [str(env.state[p].status) for p in (0, 1)]
        margin = rewards[a_seat] - rewards[1 - a_seat]
        score = 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)

        select_rows = [r for r in day_rows if r["kind"] == "selection_match"]
        drift_rows = [r for r in day_rows if r["kind"] == "prior_route_end_drift"]
        return {
            "seed": seed,
            "a_seat": a_seat,
            "score_a": score,
            "margin_a": margin,
            "reward_a": rewards[a_seat],
            "reward_b": rewards[1 - a_seat],
            "statuses": statuses,
            "steps": steps,
            "max_agent_duration_s": max_duration,
            "route_switches": sum(selected_indices[i] != selected_indices[i - 1] for i in range(1, len(selected_indices))),
            "unique_routes": len(set(selected_indices)),
            "selected_routes": selected_indices,
            "totals": dict(totals),
            "selection_mean": {
                k: _mean([float(r[k]) for r in select_rows if r.get(k) is not None])
                for k in ("farmer_dist", "tile_mismatch", "quadrant_diff", "shop_l1", "economy_l1", "money_gap", "structural_cost")
            },
            "drift_mean": {
                k: _mean([float(r[k]) for r in drift_rows if r.get(k) is not None])
                for k in ("farmer_dist", "tile_mismatch", "quadrant_diff", "shop_l1", "economy_l1", "money_gap", "structural_cost")
            },
            "day_rows": day_rows,
            "day_totals": {str(k): dict(v) for k, v in sorted(day_totals.items())},
        }
    finally:
        a.close()
        b.close()


def summarize(rows: list[dict]) -> dict:
    keys = [
        "steps_with_hand_shortfall",
        "hand_shortfall_worker_steps",
        "steps_with_hand_excess",
        "hand_excess_worker_steps",
        "steps_with_position_mismatch",
        "position_mismatch_worker_steps",
        "productive_source_actions_at_mismatched_positions",
        "weed_repair_candidates",
        "reference_hand_actions_omitted_by_missing_workers",
        "extra_current_workers_without_reference_action",
        "source_hire_orders",
        "actual_worker_action_mutations",
        "market_action_mismatch_steps",
    ]

    def group(sub):
        return {
            "games": len(sub),
            "score_rate": _mean([r["score_a"] for r in sub]),
            "mean_margin": _mean([r["margin_a"] for r in sub]),
            "median_margin": _median([r["margin_a"] for r in sub]),
            "mean_route_switches": _mean([r["route_switches"] for r in sub]),
            "mean_unique_routes": _mean([r["unique_routes"] for r in sub]),
            "mean_selection_tile_mismatch": _mean([r["selection_mean"]["tile_mismatch"] for r in sub]),
            "mean_selection_economy_l1": _mean([r["selection_mean"]["economy_l1"] for r in sub]),
            "mean_end_drift_tile_mismatch": _mean([r["drift_mean"]["tile_mismatch"] for r in sub]),
            "mean_end_drift_economy_l1": _mean([r["drift_mean"]["economy_l1"] for r in sub]),
            **{f"mean_{k}": _mean([float(r["totals"].get(k, 0)) for r in sub]) for k in keys},
        }

    wins = [r for r in rows if r["score_a"] == 1.0]
    losses = [r for r in rows if r["score_a"] == 0.0]
    ties = [r for r in rows if r["score_a"] == 0.5]

    by_day = {}
    for day in range(30):
        entry = {}
        for name, sub in (("wins", wins), ("losses", losses)):
            day_sel, day_drift = [], []
            for row in sub:
                for d in row["day_rows"]:
                    if d["day"] != day:
                        continue
                    (day_sel if d["kind"] == "selection_match" else day_drift).append(d)
            entry[name] = {
                "games": len(sub),
                "selection_tile_mismatch": _mean([x["tile_mismatch"] for x in day_sel]),
                "selection_economy_l1": _mean([x["economy_l1"] for x in day_sel]),
                "end_drift_tile_mismatch": _mean([x["tile_mismatch"] for x in day_drift]),
                "end_drift_economy_l1": _mean([x["economy_l1"] for x in day_drift]),
                "hand_shortfall_worker_steps": _mean([float(r.get("day_totals", {}).get(str(day), {}).get("hand_shortfall_worker_steps", 0)) for r in sub]),
                "position_mismatch_worker_steps": _mean([float(r.get("day_totals", {}).get(str(day), {}).get("position_mismatch_worker_steps", 0)) for r in sub]),
                "omitted_ref_hand_actions": _mean([float(r.get("day_totals", {}).get(str(day), {}).get("reference_hand_actions_omitted_by_missing_workers", 0)) for r in sub]),
                "worker_action_mutations": _mean([float(r.get("day_totals", {}).get(str(day), {}).get("actual_worker_action_mutations", 0)) for r in sub]),
            }
        by_day[str(day)] = entry

    return {
        "all": group(rows),
        "wins": group(wins),
        "losses": group(losses),
        "ties": group(ties),
        "by_day": by_day,
        "diagnostic_only": True,
        "retune_cr080_permitted": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cr080", type=Path, required=True)
    ap.add_argument("--opponent", type=Path, required=True)
    ap.add_argument("--opponent-id", required=True)
    ap.add_argument("--seed-count", type=int, default=32)
    ap.add_argument("--master-seed", type=int, default=9112081)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    with tempfile.TemporaryDirectory(prefix="cr080-failure-diag-") as td:
        root = Path(td)
        a_dir = extract(args.cr080, root, "cr080")
        b_dir = extract(args.opponent, root, "opponent")
        rt, bank = _load_runtime_and_bank(a_dir)
        for seed in make_seeds(args.seed_count, args.master_seed):
            for a_seat in (0, 1):
                rows.append(play_episode(a_dir, b_dir, rt, bank, seed, a_seat))
            print(json.dumps({"opponent": args.opponent_id, "seed": seed, "games": len(rows)}), flush=True)

    payload = {
        "schema_version": "cr080-post-failure-diagnostic-v1",
        "policy": "frozen CR080; confirmation seeds reused for diagnosis only",
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "opponent": args.opponent_id,
        "summary": summarize(rows),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"opponent": args.opponent_id, "summary": payload["summary"]}, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
