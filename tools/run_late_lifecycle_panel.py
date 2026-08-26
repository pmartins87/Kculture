"""Development-only late-horizon lifecycle diagnostic for Kaggriculture.

Runs an exact candidate/opponent pair on a named frozen seed partition in both
seats, fresh-loading file agents for every episode. The report is intentionally
state/engine based: it measures money trajectory, crop expiry, weeds, productive
acreage, labor and harvest/drop/SELL throughput near the terminal horizon.

This tool does not modify agent policy and must not be pointed at held-out seeds
for exploratory work.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path

from kaggle_environments import make

from run_episode import git_sha, package_version, resolve_agent

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = (
    "WHEAT",
    "CARROT",
    "TOMATO",
    "STRAWBERRY",
    "MELON",
    "EGG",
    "MILK",
    "WOOL",
    "FERTILIZER",
)
CHECKPOINTS = (600, 648, 672, 696, 708, 717, 718, 719)


def _private_totals(private: dict) -> tuple[int, int]:
    shed = private.get("shed", {}) if isinstance(private, dict) else {}
    shed_total = sum(int(shed.get(k, 0) or 0) for k in PRODUCTS)
    carried = 0
    for inv in (private.get("inventories", []) or []) if isinstance(private, dict) else []:
        if not isinstance(inv, dict):
            continue
        carried += sum(int(inv.get(k, 0) or 0) for k in PRODUCTS)
    return shed_total, carried


def _crop_state(farm: dict, step: int) -> dict:
    counts = Counter()
    expiry = Counter()
    yield_units = Counter()
    for row in farm.get("tiles", []) or []:
        if not isinstance(row, list):
            continue
        for tile in row:
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "WEED":
                counts["WEED"] += 1
            elif kind == "PLANT":
                crop = str(tile.get("crop"))
                counts[f"PLANT_{crop}"] += 1
                yield_units[crop] += int(tile.get("yield_units", 0) or 0)
                max_step = tile.get("max_lifespan_step")
                if isinstance(max_step, int):
                    if max_step == step:
                        expiry[f"EXPIRING_NOW_{crop}"] += 1
                    if step <= max_step <= 696:
                        expiry[f"EXPIRING_BY_696_{crop}"] += 1
            elif kind == "PASTURE":
                counts[f"PASTURE_{tile.get('animal')}"] += 1
            elif kind is not None:
                counts[str(kind)] += 1

    productive_crops = sum(v for k, v in counts.items() if k.startswith("PLANT_"))
    return {
        "counts": dict(sorted(counts.items())),
        "expiry": dict(sorted(expiry.items())),
        "yield_units": dict(sorted(yield_units.items())),
        "productive_crops": productive_crops,
        "weeds": counts.get("WEED", 0),
    }


def _checkpoint(replay: dict, player: int, step: int) -> dict:
    obs = replay["steps"][step][player]["observation"]
    farm = obs["farms"][player]
    shed_total, carried_total = _private_totals(obs.get("private", {}))
    crop = _crop_state(farm, step)
    return {
        "step": step,
        "day": obs.get("day"),
        "hour": obs.get("hour"),
        "money": float(farm.get("money", 0)),
        "hands": len(farm.get("hands", []) or []),
        "shed_total": shed_total,
        "carried_total": carried_total,
        "productive_crops": crop["productive_crops"],
        "weeds": crop["weeds"],
        "crop_counts": crop["counts"],
        "crop_expiry": crop["expiry"],
        "crop_yield_units": crop["yield_units"],
    }


def _window_actions(replay: dict, player: int, start: int, end: int) -> dict:
    farmer = Counter()
    hands = Counter()
    market = Counter()
    market_qty = Counter()

    for step in range(start, end + 1):
        action = replay["steps"][step][player].get("action")
        if not isinstance(action, dict):
            continue

        fa = action.get("farmer")
        if isinstance(fa, list) and fa:
            farmer[str(fa[0])] += 1

        for ha in action.get("hands", []) or []:
            if isinstance(ha, list) and ha:
                hands[str(ha[0])] += 1

        for ma in action.get("market", []) or []:
            if not isinstance(ma, list) or not ma:
                continue
            op = str(ma[0])
            market[op] += 1
            if op in {"SELL", "BUY"} and len(ma) >= 3:
                try:
                    market_qty[f"{op}_{ma[1]}"] += int(ma[2])
                except (TypeError, ValueError):
                    pass

    return {
        "farmer": dict(sorted(farmer.items())),
        "hands": dict(sorted(hands.items())),
        "market": dict(sorted(market.items())),
        "market_qty": dict(sorted(market_qty.items())),
        "pass_total": farmer.get("PASS", 0) + hands.get("PASS", 0),
        "harvest_total": farmer.get("HARVEST", 0) + hands.get("HARVEST", 0),
        "drop_total": farmer.get("DROP", 0) + hands.get("DROP", 0),
        "sell_qty_total": sum(v for k, v in market_qty.items() if k.startswith("SELL_")),
    }


def _safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if denom == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / denom


def _episode_features(row: dict) -> dict:
    c672 = row["candidate_checkpoints"]["672"]
    o672 = row["opponent_checkpoints"]["672"]
    c696 = row["candidate_checkpoints"]["696"]
    o696 = row["opponent_checkpoints"]["696"]
    c708 = row["candidate_checkpoints"]["708"]
    o708 = row["opponent_checkpoints"]["708"]
    cw = row["candidate_windows"]["696_718"]
    ow = row["opponent_windows"]["696_718"]

    def expiry(cp: dict, key: str) -> int:
        return int(cp.get("crop_expiry", {}).get(key, 0) or 0)

    c_straw_672 = expiry(c672, "EXPIRING_NOW_STRAWBERRY")
    o_straw_672 = expiry(o672, "EXPIRING_NOW_STRAWBERRY")
    c_straw_by696 = expiry(c672, "EXPIRING_BY_696_STRAWBERRY")
    o_straw_by696 = expiry(o672, "EXPIRING_BY_696_STRAWBERRY")

    return {
        "candidate_straw_expiring_672": c_straw_672,
        "opponent_straw_expiring_672": o_straw_672,
        "relative_straw_expiring_672": c_straw_672 - o_straw_672,
        "candidate_straw_expiring_by_696": c_straw_by696,
        "opponent_straw_expiring_by_696": o_straw_by696,
        "relative_straw_expiring_by_696": c_straw_by696 - o_straw_by696,
        "candidate_weeds_696": c696["weeds"],
        "opponent_weeds_696": o696["weeds"],
        "relative_weeds_696": c696["weeds"] - o696["weeds"],
        "candidate_productive_crops_696": c696["productive_crops"],
        "opponent_productive_crops_696": o696["productive_crops"],
        "relative_productive_crops_696": c696["productive_crops"] - o696["productive_crops"],
        "candidate_hands_708": c708["hands"],
        "opponent_hands_708": o708["hands"],
        "relative_hands_708": c708["hands"] - o708["hands"],
        "candidate_harvest_696_718": cw["harvest_total"],
        "opponent_harvest_696_718": ow["harvest_total"],
        "relative_harvest_696_718": cw["harvest_total"] - ow["harvest_total"],
        "candidate_drop_696_718": cw["drop_total"],
        "opponent_drop_696_718": ow["drop_total"],
        "relative_drop_696_718": cw["drop_total"] - ow["drop_total"],
        "candidate_sell_qty_696_718": cw["sell_qty_total"],
        "opponent_sell_qty_696_718": ow["sell_qty_total"],
        "relative_sell_qty_696_718": cw["sell_qty_total"] - ow["sell_qty_total"],
        "candidate_pass_696_718": cw["pass_total"],
        "opponent_pass_696_718": ow["pass_total"],
        "relative_pass_696_718": cw["pass_total"] - ow["pass_total"],
    }


def _group_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}
    feature_keys = sorted(rows[0]["features"].keys())
    return {
        "n": len(rows),
        "mean_delta_672": _safe_mean([r["delta_672"] for r in rows]),
        "mean_terminal_delta": _safe_mean([r["terminal_delta"] for r in rows]),
        "mean_late_swing_672_terminal": _safe_mean([r["late_swing_672_terminal"] for r in rows]),
        "mean_features": {
            k: _safe_mean([float(r["features"][k]) for r in rows]) for k in feature_keys
        },
    }


def _aggregate(rows: list[dict]) -> dict:
    wins = [r for r in rows if r["outcome"] == "WIN"]
    losses = [r for r in rows if r["outcome"] == "LOSS"]
    ties = [r for r in rows if r["outcome"] == "TIE"]
    errors = [r for r in rows if r["outcome"] == "ERROR"]

    correlations = {}
    valid = [r for r in rows if r["outcome"] != "ERROR"]
    if valid:
        for key in sorted(valid[0]["features"].keys()):
            correlations[key] = {
                "vs_late_swing": _pearson(
                    [float(r["features"][key]) for r in valid],
                    [float(r["late_swing_672_terminal"]) for r in valid],
                ),
                "vs_terminal_delta": _pearson(
                    [float(r["features"][key]) for r in valid],
                    [float(r["terminal_delta"]) for r in valid],
                ),
            }

    return {
        "n": len(rows),
        "win_count": len(wins),
        "loss_count": len(losses),
        "tie_count": len(ties),
        "error_count": len(errors),
        "score_rate_tie_half": (len(wins) + 0.5 * len(ties)) / len(valid) if valid else None,
        "all": _group_summary(valid),
        "win_group": _group_summary(wins),
        "loss_group": _group_summary(losses),
        "tie_group": _group_summary(ties),
        "feature_correlations": correlations,
    }


def _run_episode(candidate_spec: str, opponent_spec: str, seed: int, candidate_seat: int) -> dict:
    specs = [candidate_spec, opponent_spec] if candidate_seat == 0 else [opponent_spec, candidate_spec]
    # Resolve afresh per episode so module-global strategy state cannot leak.
    agents = [resolve_agent(spec) for spec in specs]

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    env.run(agents)
    replay = env.toJSON()

    c = candidate_seat
    o = 1 - c
    final = replay["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    rewards = [final[i].get("reward") for i in range(2)]

    if statuses != ["DONE", "DONE"] or not all(isinstance(v, (int, float)) for v in rewards):
        outcome = "ERROR"
        terminal_delta = None
    else:
        terminal_delta = float(rewards[c]) - float(rewards[o])
        outcome = "WIN" if terminal_delta > 0 else ("LOSS" if terminal_delta < 0 else "TIE")

    candidate_checkpoints = {str(s): _checkpoint(replay, c, s) for s in CHECKPOINTS}
    opponent_checkpoints = {str(s): _checkpoint(replay, o, s) for s in CHECKPOINTS}
    candidate_windows = {
        "672_695": _window_actions(replay, c, 672, 695),
        "696_718": _window_actions(replay, c, 696, 718),
    }
    opponent_windows = {
        "672_695": _window_actions(replay, o, 672, 695),
        "696_718": _window_actions(replay, o, 696, 718),
    }

    delta_672 = candidate_checkpoints["672"]["money"] - opponent_checkpoints["672"]["money"]
    row = {
        "seed": seed,
        "candidate_seat": candidate_seat,
        "statuses": statuses,
        "rewards": rewards,
        "outcome": outcome,
        "delta_672": delta_672,
        "terminal_delta": terminal_delta,
        "late_swing_672_terminal": terminal_delta - delta_672 if terminal_delta is not None else None,
        "candidate_checkpoints": candidate_checkpoints,
        "opponent_checkpoints": opponent_checkpoints,
        "candidate_windows": candidate_windows,
        "opponent_windows": opponent_windows,
    }
    row["features"] = _episode_features(row)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--opponent", required=True)
    parser.add_argument("--seed-config", default="configs/seed_partitions.json")
    parser.add_argument("--partition", default="development")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    seed_path = ROOT / args.seed_config
    partitions = json.loads(seed_path.read_text(encoding="utf-8"))
    seeds = partitions[args.partition]
    if args.partition != "development":
        raise SystemExit(
            f"Exploratory lifecycle panel is development-only; refusing partition={args.partition!r}"
        )

    rows = []
    for seed in seeds:
        for seat in (0, 1):
            row = _run_episode(args.candidate, args.opponent, int(seed), seat)
            rows.append(row)
            print(
                json.dumps(
                    {
                        "seed": seed,
                        "candidate_seat": seat,
                        "outcome": row["outcome"],
                        "delta_672": row["delta_672"],
                        "terminal_delta": row["terminal_delta"],
                        "late_swing": row["late_swing_672_terminal"],
                        "features": row["features"],
                    },
                    sort_keys=True,
                )
            )

    report = {
        "schema_version": 1,
        "environment": "kaggriculture",
        "kaggle_environments_version": package_version(),
        "git_sha": git_sha(),
        "candidate": args.candidate,
        "opponent": args.opponent,
        "seed_config": args.seed_config,
        "partition": args.partition,
        "seeds": seeds,
        "candidate_seats": [0, 1],
        "checkpoints": list(CHECKPOINTS),
        "episodes": rows,
        "aggregate": _aggregate(rows),
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["aggregate"], indent=2, sort_keys=True))

    if report["aggregate"]["error_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
