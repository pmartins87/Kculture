from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import statistics
import tempfile
import traceback
from pathlib import Path

from kaggle_exact_runtime import (
    AgentProcess,
    agent_visible_observation,
    assert_reference_version,
    done_status,
    extract,
    make_reference_env,
    make_seeds,
    reference_config,
    reference_step,
)

CHECKPOINTS = (288, 432, 576, 696)


def get(o, k, default=None):
    try:
        return o.get(k, default)
    except AttributeError:
        try:
            return o[k]
        except Exception:
            return default


def crop_count(obs, seat: int, crop: str) -> int:
    farms = get(obs, "farms", []) or []
    if seat >= len(farms):
        return 0
    n = 0
    for row in get(farms[seat], "tiles", []) or []:
        if not isinstance(row, list):
            continue
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == crop:
                n += 1
    return n


def market_qty(action, op: str, product: str) -> int:
    total = 0
    for order in get(action, "market", []) or []:
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == op and order[1] == product:
            try:
                total += max(0, int(order[2]))
            except Exception:
                pass
    return total


def plant_count(action, crop: str) -> int:
    acts = [get(action, "farmer", None)] + list(get(action, "hands", []) or [])
    return sum(bool(a and len(a) >= 2 and a[0] == "PLANT" and a[1] == crop) for a in acts)


def reward_value(x):
    return None if x is None else float(x)


def play_episode(candidate_dir: Path, parent_dir: Path, seed: int, candidate_seat: int) -> dict:
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    candidate = AgentProcess(ctx, candidate_dir, f"cr075_c_{seed}_{candidate_seat}")
    parent = AgentProcess(ctx, parent_dir, f"cr075_p_{seed}_{candidate_seat}")
    rec = {
        "seed": int(seed),
        "candidate_seat": int(candidate_seat),
        "checkpoints": {},
        "candidate_buy_seed_melon_step264": 0,
        "candidate_buy_seed_carrot_step264": 0,
        "candidate_plant_melon_step275": 0,
        "candidate_plant_melon_step277": 0,
        "candidate_sell_melon_by_phase": {str(i): 0 for i in range(5)},
        "parent_sell_melon_by_phase": {str(i): 0 for i in range(5)},
        "max_agent_duration_s": 0.0,
    }
    try:
        steps = 0
        while not all(done_status(s.status) for s in env.state):
            obs0 = agent_visible_observation(env, 0)
            obs1 = agent_visible_observation(env, 1)
            obs_c = obs0 if candidate_seat == 0 else obs1
            obs_p = obs1 if candidate_seat == 0 else obs0
            step = int(get(obs_c, "step", steps) or steps)

            if step in CHECKPOINTS:
                rec["checkpoints"][str(step)] = {
                    "candidate_crop_melon": crop_count(obs_c, candidate_seat, "MELON"),
                    "parent_crop_melon": crop_count(obs_p, 1 - candidate_seat, "MELON"),
                    "candidate_crop_wheat": crop_count(obs_c, candidate_seat, "WHEAT"),
                    "parent_crop_wheat": crop_count(obs_p, 1 - candidate_seat, "WHEAT"),
                }

            if candidate_seat == 0:
                act_c, dc = candidate.call(obs0, config)
                act_p, dp = parent.call(obs1, config)
                actions = [act_c, act_p]
            else:
                act_p, dp = parent.call(obs0, config)
                act_c, dc = candidate.call(obs1, config)
                actions = [act_p, act_c]
            rec["max_agent_duration_s"] = max(rec["max_agent_duration_s"], dc, dp)

            if step == 264:
                rec["candidate_buy_seed_melon_step264"] = market_qty(act_c, "BUY_SEED", "MELON")
                rec["candidate_buy_seed_carrot_step264"] = market_qty(act_c, "BUY_SEED", "CARROT")
            elif step == 275:
                rec["candidate_plant_melon_step275"] = plant_count(act_c, "MELON")
            elif step == 277:
                rec["candidate_plant_melon_step277"] = plant_count(act_c, "MELON")

            phase = min(4, step // 144)
            rec["candidate_sell_melon_by_phase"][str(phase)] += market_qty(act_c, "SELL", "MELON")
            rec["parent_sell_melon_by_phase"][str(phase)] += market_qty(act_p, "SELL", "MELON")

            reference_step(env, actions, [dc, dp] if candidate_seat == 0 else [dp, dc])
            steps += 1
            if steps > 725:
                raise RuntimeError("episode exceeded expected length")

        rewards = [reward_value(env.state[p].reward) for p in (0, 1)]
        statuses = [str(env.state[p].status) for p in (0, 1)]
        rec["status_candidate"] = statuses[candidate_seat]
        rec["status_parent"] = statuses[1 - candidate_seat]
        rec["reward_candidate"] = rewards[candidate_seat]
        rec["reward_parent"] = rewards[1 - candidate_seat]
        if statuses[candidate_seat] == "DONE" and statuses[1 - candidate_seat] == "DONE" and None not in rewards:
            margin = rewards[candidate_seat] - rewards[1 - candidate_seat]
            rec["score_candidate"] = 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)
        elif statuses[candidate_seat] == "DONE" and statuses[1 - candidate_seat] != "DONE":
            rec["score_candidate"] = 1.0
        elif statuses[candidate_seat] != "DONE" and statuses[1 - candidate_seat] == "DONE":
            rec["score_candidate"] = 0.0
        else:
            rec["score_candidate"] = 0.5
        return rec
    finally:
        candidate.close()
        parent.close()


def med(values):
    return statistics.median(values) if values else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--parent", required=True)
    ap.add_argument("--seed-count", type=int, default=12)
    ap.add_argument("--master-seed", type=int, default=9092032)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    assert_reference_version()
    rows = []
    errors = []
    seeds = make_seeds(args.seed_count, args.master_seed)
    with tempfile.TemporaryDirectory(prefix="cr075-audit-") as td:
        root = Path(td)
        cdir = extract(Path(args.candidate), root, "candidate")
        pdir = extract(Path(args.parent), root, "parent")
        for seed in seeds:
            for seat in (0, 1):
                try:
                    rows.append(play_episode(cdir, pdir, seed, seat))
                except Exception as exc:
                    errors.append({"seed": seed, "candidate_seat": seat, "error": repr(exc), "traceback": traceback.format_exc()[-8000:]})
            print(json.dumps({"seed": seed, "games": len(rows), "errors": len(errors)}), flush=True)
            if errors:
                break

    games = len(rows)
    cp = {}
    for checkpoint in CHECKPOINTS:
        key = str(checkpoint)
        cvals = [r["checkpoints"][key]["candidate_crop_melon"] for r in rows if key in r["checkpoints"]]
        pvals = [r["checkpoints"][key]["parent_crop_melon"] for r in rows if key in r["checkpoints"]]
        cp[key] = {
            "candidate_median_crop_melon": med(cvals),
            "parent_median_crop_melon": med(pvals),
            "median_delta_crop_melon": (med(cvals) - med(pvals)) if cvals and pvals else None,
            "candidate_nonzero_games": sum(v > 0 for v in cvals),
            "parent_nonzero_games": sum(v > 0 for v in pvals),
        }

    phase = {}
    for i in range(5):
        cvals = [r["candidate_sell_melon_by_phase"][str(i)] for r in rows]
        pvals = [r["parent_sell_melon_by_phase"][str(i)] for r in rows]
        phase[str(i)] = {
            "candidate_median_sell_qty": med(cvals),
            "parent_median_sell_qty": med(pvals),
            "candidate_nonzero_games": sum(v > 0 for v in cvals),
            "parent_nonzero_games": sum(v > 0 for v in pvals),
        }

    intervention = {
        "step264_buy_melon3_games": sum(r["candidate_buy_seed_melon_step264"] == 3 for r in rows),
        "step264_buy_carrot0_games": sum(r["candidate_buy_seed_carrot_step264"] == 0 for r in rows),
        "step275_plant_melon1_games": sum(r["candidate_plant_melon_step275"] >= 1 for r in rows),
        "step277_plant_melon2_games": sum(r["candidate_plant_melon_step277"] >= 2 for r in rows),
    }
    non_done = sum(r.get("status_candidate") != "DONE" or r.get("status_parent") != "DONE" for r in rows)
    score_rate = statistics.mean(r["score_candidate"] for r in rows) if rows else None

    # Frozen gate: local W/L is only a catastrophic-safety floor, never a hosted-strength proxy.
    causal_signal = (
        cp.get("288", {}).get("median_delta_crop_melon") is not None
        and cp["288"]["median_delta_crop_melon"] >= 1
    )
    mechanics = (
        not errors
        and games == args.seed_count * 2
        and non_done == 0
        and intervention["step264_buy_melon3_games"] == games
        and intervention["step264_buy_carrot0_games"] == games
        and intervention["step275_plant_melon1_games"] >= int(0.75 * games)
        and intervention["step277_plant_melon2_games"] >= int(0.75 * games)
    )
    safety_floor = score_rate is not None and score_rate >= 0.25
    gate = "MECHANICAL_CAUSAL_PASS" if mechanics and causal_signal and safety_floor else "REJECT_OR_REPAIR"

    payload = {
        "schema_version": "kculture-cr075-melon-persistence-audit-v1",
        "reference_backend": "kaggle-environments==1.32.7",
        "master_seed": args.master_seed,
        "paired_seeds": args.seed_count,
        "games": games,
        "errors": errors,
        "non_done_games": non_done,
        "intervention_execution": intervention,
        "checkpoint_melon": cp,
        "sell_melon_by_phase": phase,
        "candidate_local_score_rate_diagnostic_only": score_rate,
        "local_score_role": "catastrophic mechanical safety floor only; not hosted-strength promotion evidence",
        "gate": gate,
        "next_action": "REVIEW_ONE_HOSTED_SLOT" if gate == "MECHANICAL_CAUSAL_PASS" else "DO_NOT_SUBMIT",
        "automatic_kaggle_submission": False,
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
