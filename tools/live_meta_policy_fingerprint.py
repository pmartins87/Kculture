"""Determinism/repeatability fingerprint for official top Kaggriculture Episodes.

Observational research only. Team names are grouping labels, never deployable
features. Raw episode JSONs live only in a temporary directory.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import itertools
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"
WINDOWS = (
    (0, 215),
    (216, 599),
    (600, 671),
    (672, 695),
    (696, 718),
)


def download_file(handle: str, filename: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = kagglehub.dataset_download(
        handle, path=filename, output_dir=str(out_dir), force_download=True
    )
    path = Path(result)
    if not path.is_file():
        raise FileNotFoundError(f"download failed: {handle}:{filename}: {path}")
    return path


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def canon_action(value) -> str:
    if not isinstance(value, dict):
        value = {}
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def first_three_shops(steps: list, player: int) -> tuple[str, ...]:
    for frame in steps:
        obs = frame[player].get("observation", {}) or {}
        shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
        if len(shops) >= 3:
            return tuple(str(x) for x in shops[:3])
    return tuple()


def trajectory(rep: dict, player: int, episode_id: str, avg_score: float) -> dict:
    steps = rep.get("steps") or []
    names = (rep.get("info") or {}).get("TeamNames") or ["p0", "p1"]
    actions = []
    for idx in range(min(719, len(steps))):
        actions.append(canon_action(steps[idx][player].get("action")))
    if len(actions) < 719:
        actions.extend([canon_action({})] * (719 - len(actions)))
    rewards = []
    for p in (0, 1):
        try:
            rewards.append(float(steps[-1][p].get("reward")))
        except (TypeError, ValueError):
            rewards.append(float("nan"))
    reward = rewards[player]
    finite = [x for x in rewards if x == x]
    winner = bool(finite and reward == max(finite))
    payload = "\n".join(actions).encode("utf-8")
    return {
        "episode_id": episode_id,
        "avg_score": avg_score,
        "player": player,
        "team": names[player] if player < len(names) else f"p{player}",
        "reward": None if reward != reward else reward,
        "winner": winner,
        "shops3": first_three_shops(steps, player),
        "actions": actions,
        "trajectory_sha256": hashlib.sha256(payload).hexdigest(),
    }


def pair_agreement(a: list[str], b: list[str], start: int, end: int) -> float:
    end = min(end, len(a) - 1, len(b) - 1)
    if end < start:
        return float("nan")
    n = end - start + 1
    return sum(a[i] == b[i] for i in range(start, end + 1)) / n


def summarize_group(rows: list[dict]) -> dict:
    pairs = list(itertools.combinations(rows, 2))
    pair_stats = {}
    modal_stats = {}
    for start, end in WINDOWS:
        key = f"{start}_{end}"
        vals = [pair_agreement(a["actions"], b["actions"], start, end) for a, b in pairs]
        vals = [x for x in vals if x == x]
        pair_stats[key] = {
            "mean": statistics.mean(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "pairs": len(vals),
        }
        per_step = []
        for step in range(start, end + 1):
            counts = collections.Counter(r["actions"][step] for r in rows)
            per_step.append(max(counts.values()) / len(rows))
        modal_stats[key] = statistics.mean(per_step) if per_step else None

    hashes = collections.Counter(r["trajectory_sha256"] for r in rows)
    return {
        "n": len(rows),
        "wins": sum(bool(r["winner"]) for r in rows),
        "unique_full_trajectory_hashes": len(hashes),
        "full_trajectory_hash_counts": dict(hashes.most_common()),
        "pairwise_exact_action_agreement": pair_stats,
        "mean_per_step_modal_agreement": modal_stats,
    }


def summarize_team(rows: list[dict]) -> dict:
    out = summarize_group(rows)
    prefix = collections.defaultdict(list)
    for row in rows:
        prefix[tuple(row["shops3"])].append(row)
    out["shop_prefix_groups"] = {}
    for key, members in sorted(prefix.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        label = "|".join(key) if key else "<missing>"
        item = summarize_group(members)
        item["shops3"] = list(key)
        out["shop_prefix_groups"][label] = item
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if not 1 <= args.top <= 20:
        raise SystemExit("--top must be 1..20")

    with tempfile.TemporaryDirectory(prefix="kculture-fingerprint-") as tmp:
        root = Path(tmp)
        index = sorted(
            read_csv(download_file(INDEX_HANDLE, "manifest.csv", root / "index")),
            key=lambda r: r["date"],
        )
        if not index:
            raise RuntimeError("empty official episodes index")
        date = args.date or index[-1]["date"]
        idx_row = next((r for r in index if r["date"] == date), None)
        if idx_row is None:
            raise RuntimeError(f"date absent from official index: {date}")

        day_handle = f"kaggle/kaggriculture-episodes-{date}"
        day_dir = root / "day"
        manifest = sorted(
            read_csv(download_file(day_handle, "manifest.csv", day_dir)),
            key=lambda r: -float(r["avg_score"]),
        )
        selected = manifest[: args.top]
        rows = []
        for item in selected:
            eid = str(item["episode_id"])
            ep_path = download_file(day_handle, f"{eid}.json", day_dir / eid)
            with ep_path.open("r", encoding="utf-8") as fh:
                rep = json.load(fh)
            for player in (0, 1):
                rows.append(trajectory(rep, player, eid, float(item["avg_score"])))

    teams = collections.defaultdict(list)
    for row in rows:
        teams[row["team"]].append(row)

    report = {
        "schema_version": "live-policy-fingerprint-v1",
        "source": {
            "index_handle": INDEX_HANDLE,
            "day_handle": day_handle,
            "date": date,
            "index_row": idx_row,
            "selection": "highest avg_score in official day manifest",
            "top_n": len(selected),
            "score_range": [
                float(selected[0]["avg_score"]) if selected else None,
                float(selected[-1]["avg_score"]) if selected else None,
            ],
        },
        "teams": {team: summarize_team(members) for team, members in sorted(teams.items())},
        "trajectory_receipts": [
            {
                "episode_id": r["episode_id"],
                "player": r["player"],
                "team": r["team"],
                "winner": r["winner"],
                "shops3": list(r["shops3"]),
                "trajectory_sha256": r["trajectory_sha256"],
            }
            for r in rows
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    compact = {
        "date": date,
        "top_n": len(selected),
        "teams": {
            team: {
                "n": stats["n"],
                "wins": stats["wins"],
                "unique_full_trajectory_hashes": stats["unique_full_trajectory_hashes"],
                "pairwise_core_216_599": stats["pairwise_exact_action_agreement"]["216_599"],
                "modal_core_216_599": stats["mean_per_step_modal_agreement"]["216_599"],
                "largest_prefix_n": max(
                    (g["n"] for g in stats["shop_prefix_groups"].values()), default=0
                ),
            }
            for team, stats in report["teams"].items()
        },
        "output": str(out),
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
