"""Prize-first Kaggriculture live-meta radar from official daily top Episodes datasets.

Downloads only the official index manifest, the latest day's manifest and a
small number of top-Elo episode JSONs through kagglehub. Produces a compact
report and does not persist the large episode files as GitHub artifacts.

This is observational research only. It never touches Kculture validation or
held-out seed partitions and never uses opponent identity as a deployable
policy feature.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
MOVE_OPS = {"NORTH", "SOUTH", "EAST", "WEST"}
CHECKPOINTS = (600, 648, 672, 696, 708, 717, 719)


def download_file(handle: str, filename: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = kagglehub.dataset_download(
        handle,
        path=filename,
        output_dir=str(out_dir),
        force_download=True,
    )
    path = Path(result)
    if not path.is_file():
        raise FileNotFoundError(f"kagglehub did not return file {handle}:{filename}: {path}")
    return path


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def farm_comp(farm: dict) -> dict:
    c = collections.Counter()
    for row in farm.get("tiles", []) or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            animal = tile.get("animal")
            if animal:
                c[str(animal)] += 1
            elif tile.get("kind") == "PLANT":
                c[str(tile.get("crop", "?"))] += 1
            elif tile.get("kind") == "WEED":
                c["WEED"] += 1
            elif tile.get("kind"):
                c[str(tile.get("kind"))] += 1
    return dict(sorted(c.items()))


def first_three_shops(steps: list, player: int) -> list[str]:
    for frame in steps:
        obs = frame[player].get("observation", {}) or {}
        shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
        if len(shops) >= 3:
            return shops[:3]
    return []


def checkpoint(steps: list, player: int, idx: int) -> dict | None:
    if idx >= len(steps):
        return None
    obs = steps[idx][player].get("observation", {}) or {}
    farms = obs.get("farms") or []
    if player >= len(farms):
        return None
    farm = farms[player]
    return {
        "step": idx,
        "money": float(farm.get("money", 0) or 0),
        "hands": len(farm.get("hands", []) or []),
        "quads": len(farm.get("unlocked_quadrants", []) or []),
        "comp": farm_comp(farm),
    }


def profile_player(rep: dict, player: int) -> dict:
    steps = rep["steps"]
    names = (rep.get("info") or {}).get("TeamNames") or ["p0", "p1"]
    acts = collections.Counter()
    market_ops = collections.Counter()
    market_qty = collections.Counter()
    seeds = collections.Counter()

    for frame in steps:
        action = frame[player].get("action")
        if not isinstance(action, dict):
            continue
        unit_actions = [action.get("farmer")] + list(action.get("hands") or [])
        for op in unit_actions:
            if isinstance(op, list) and op:
                acts[str(op[0])] += 1
        for order in action.get("market", []) or []:
            if not isinstance(order, list) or not order:
                continue
            op = str(order[0])
            market_ops[op] += 1
            if op == "BUY_SEED" and len(order) >= 3:
                try:
                    seeds[str(order[1])] += int(order[2])
                except (TypeError, ValueError):
                    pass
            if op in {"SELL", "BUY", "BUY_SEED"} and len(order) >= 3:
                try:
                    market_qty[f"{op}_{order[1]}"] += int(order[2])
                except (TypeError, ValueError):
                    pass

    final = steps[-1][player]
    obs = steps[-1][0].get("observation", {}) or {}
    farms = obs.get("farms") or [{}, {}]
    farm = farms[player] if player < len(farms) else {}
    total = sum(acts.values()) or 1
    movement = sum(acts[d] for d in MOVE_OPS)
    passes = acts["PASS"]
    productive = total - movement - passes
    reward = final.get("reward")

    return {
        "player": player,
        "team_name": names[player] if player < len(names) else f"p{player}",
        "reward": reward,
        "status": final.get("status"),
        "first_three_shops": first_three_shops(steps, player),
        "final_quads": len(farm.get("unlocked_quadrants", []) or []),
        "final_hands": len(farm.get("hands", []) or []),
        "final_comp": farm_comp(farm),
        "action_total": total,
        "movement_pct": 100.0 * movement / total,
        "pass_pct": 100.0 * passes / total,
        "productive_pct": 100.0 * productive / total,
        "action_counts": dict(sorted(acts.items())),
        "market_order_counts": dict(sorted(market_ops.items())),
        "market_quantities": dict(sorted(market_qty.items())),
        "seeds_bought": dict(sorted(seeds.items())),
        "checkpoints": {
            str(s): checkpoint(steps, player, s) for s in CHECKPOINTS if s < len(steps)
        },
    }


def summarize(players: list[dict]) -> dict:
    if not players:
        return {}
    winners = []
    for i in range(0, len(players), 2):
        pair = players[i:i+2]
        numeric = [p for p in pair if isinstance(p.get("reward"), (int, float))]
        if len(numeric) == 2:
            best = max(float(p["reward"]) for p in numeric)
            winners.extend(p for p in numeric if float(p["reward"]) == best)

    def mean(key: str, rows: list[dict]) -> float | None:
        vals = [float(r[key]) for r in rows if isinstance(r.get(key), (int, float))]
        return statistics.mean(vals) if vals else None

    farms = collections.Counter()
    for p in winners:
        c = p["final_comp"]
        farms[
            f"{c.get('COW',0)}C/{c.get('SHEEP',0)}S/{c.get('GOOSE',0)}G | "
            f"W{c.get('WHEAT',0)} S{c.get('STRAWBERRY',0)} "
            f"T{c.get('TOMATO',0)} C{c.get('CARROT',0)} | {p['final_quads']}Q"
        ] += 1

    seed_totals = collections.Counter()
    sell_totals = collections.Counter()
    action_totals = collections.Counter()
    for p in winners:
        seed_totals.update(p["seeds_bought"])
        action_totals.update(p["action_counts"])
        for k, v in p["market_quantities"].items():
            if k.startswith("SELL_"):
                sell_totals[k[5:]] += v

    n = len(winners) or 1
    return {
        "player_games": len(players),
        "winner_profiles": len(winners),
        "winner_mean_reward": mean("reward", winners),
        "winner_mean_movement_pct": mean("movement_pct", winners),
        "winner_mean_pass_pct": mean("pass_pct", winners),
        "winner_mean_productive_pct": mean("productive_pct", winners),
        "winner_modal_final_farms": farms.most_common(10),
        "winner_mean_seeds_bought": {k: v / n for k, v in sorted(seed_totals.items())},
        "winner_mean_sell_qty": {k: v / n for k, v in sorted(sell_totals.items())},
        "winner_mean_action_counts": {k: v / n for k, v in sorted(action_totals.items())},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD; default latest official index row")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if args.top < 1 or args.top > 20:
        raise SystemExit("--top must be 1..20")

    with tempfile.TemporaryDirectory(prefix="kculture-meta-") as tmp:
        root = Path(tmp)
        index_path = download_file(INDEX_HANDLE, "manifest.csv", root / "index")
        index = read_csv(index_path)
        if not index:
            raise RuntimeError("official episodes index is empty")
        index = sorted(index, key=lambda r: r["date"])
        date = args.date or index[-1]["date"]
        idx_row = next((r for r in index if r["date"] == date), None)
        if idx_row is None:
            raise RuntimeError(f"date {date} absent from official index")

        day_handle = f"kaggle/kaggriculture-episodes-{date}"
        day_dir = root / "day"
        manifest_path = download_file(day_handle, "manifest.csv", day_dir)
        manifest = read_csv(manifest_path)
        manifest = sorted(manifest, key=lambda r: -float(r["avg_score"]))
        selected = manifest[: args.top]

        episodes = []
        players = []
        for row in selected:
            episode_id = str(row["episode_id"])
            episode_path = download_file(day_handle, f"{episode_id}.json", day_dir / episode_id)
            with episode_path.open("r", encoding="utf-8") as fh:
                rep = json.load(fh)
            pair = [profile_player(rep, 0), profile_player(rep, 1)]
            players.extend(pair)
            episodes.append({
                "episode_id": episode_id,
                "avg_score": float(row["avg_score"]),
                "size_bytes": int(row.get("size_bytes") or episode_path.stat().st_size),
                "players": pair,
            })

    report = {
        "schema_version": "live-meta-radar-v1",
        "source": {
            "index_handle": INDEX_HANDLE,
            "day_handle": day_handle,
            "date": date,
            "index_row": idx_row,
        },
        "selection": {
            "criterion": "highest avg_score in official day manifest",
            "top_n": len(selected),
        },
        "episodes": episodes,
        "aggregate": summarize(players),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "date": date,
        "episode_count": idx_row.get("episode_count"),
        "top_avg_score": idx_row.get("top_avg_score"),
        "median_avg_score": idx_row.get("median_avg_score"),
        "selected_avg_scores": [float(r["avg_score"]) for r in selected],
        "aggregate": report["aggregate"],
        "output": str(out),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
