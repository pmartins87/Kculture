#!/usr/bin/env python3
"""Read-only forensic summary for hosted Kaggriculture episode replays.

The Kaggle replay schema records team names in ``info.TeamNames`` and final money in
``rewards``.  This analyzer uses only those offline replay fields; it never contacts
Kaggle, never mutates submissions, and none of the identity fields it reads are
intended for runtime policy use.
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def infer_seat_and_names(data: dict, target_team_name: str):
    info = data.get("info") if isinstance(data.get("info"), dict) else {}
    names = info.get("TeamNames")
    if not isinstance(names, list) or len(names) < 2:
        agents = info.get("Agents")
        if isinstance(agents, list):
            names = [a.get("Name") if isinstance(a, dict) else str(a) for a in agents]
    if not isinstance(names, list) or len(names) < 2:
        return None, None, None
    normalized = [str(x) for x in names[:2]]
    hits = [i for i, name in enumerate(normalized) if name == target_team_name]
    if len(hits) != 1:
        return None, normalized, None
    seat = hits[0]
    return seat, normalized, normalized[1 - seat]


def final_rewards(data: dict):
    vals = data.get("rewards")
    if isinstance(vals, list) and len(vals) >= 2:
        try:
            return [float(vals[0]), float(vals[1])]
        except (TypeError, ValueError):
            pass
    # Defensive fallback only; current official replay schema uses top-level rewards.
    steps = data.get("steps")
    if isinstance(steps, list) and steps:
        final = steps[-1]
        if isinstance(final, list) and len(final) >= 2:
            out = []
            for a in final[:2]:
                out.append(a.get("reward") if isinstance(a, dict) else None)
            if all(v is not None for v in out):
                try:
                    return [float(out[0]), float(out[1])]
                except (TypeError, ValueError):
                    pass
    return None


def episode_id(path: Path, data: dict):
    info = data.get("info") if isinstance(data.get("info"), dict) else {}
    if info.get("EpisodeId") is not None:
        return str(info["EpisodeId"])
    digits = "".join(c for c in path.stem if c.isdigit())
    return digits or path.stem


def grouped_stats(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r["opponent_team"]].append(r)
    out = []
    for opponent, games in groups.items():
        margins = [g["margin"] for g in games]
        out.append(
            {
                "opponent_team": opponent,
                "games": len(games),
                "wins": sum(g["result"] == "W" for g in games),
                "losses": sum(g["result"] == "L" for g in games),
                "ties": sum(g["result"] == "T" for g in games),
                "mean_margin": statistics.fmean(margins),
                "median_margin": statistics.median(margins),
            }
        )
    return sorted(out, key=lambda x: (-x["games"], x["mean_margin"], x["opponent_team"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay-root", required=True)
    ap.add_argument("--target-team-name", required=True)
    ap.add_argument("--target-submission", default=None)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    root = Path(args.replay_root)
    files = sorted(root.rglob("*.json"))
    rows = []
    unresolved = []
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            unresolved.append({"file": str(p), "error": repr(e)})
            continue

        rewards = final_rewards(data)
        seat, team_names, opponent = infer_seat_and_names(data, args.target_team_name)
        eid = episode_id(p, data)
        rec = {
            "episode_id": eid,
            "file": str(p),
            "seat": seat,
            "team_names": team_names,
            "opponent_team": opponent,
            "rewards": rewards,
        }
        if rewards is None or seat not in (0, 1):
            unresolved.append(rec)
            continue

        margin = rewards[seat] - rewards[1 - seat]
        rec.update(
            {
                "target_reward": rewards[seat],
                "opponent_reward": rewards[1 - seat],
                "margin": margin,
                "result": "W" if margin > 0 else "L" if margin < 0 else "T",
            }
        )
        rows.append(rec)

    margins = [r["margin"] for r in rows]
    summary = {
        "schema_version": "cr083-hosted-forensics-v2-teamname",
        "target_submission": args.target_submission,
        "target_team_name": args.target_team_name,
        "identity_use": "offline forensic only; prohibited as runtime policy feature",
        "replay_json_files": len(files),
        "resolved_games": len(rows),
        "unresolved_games": len(unresolved),
        "wins": sum(r["result"] == "W" for r in rows),
        "losses": sum(r["result"] == "L" for r in rows),
        "ties": sum(r["result"] == "T" for r in rows),
        "score_rate": (sum(r["result"] == "W" for r in rows) + 0.5 * sum(r["result"] == "T" for r in rows)) / len(rows) if rows else None,
        "mean_margin": statistics.fmean(margins) if margins else None,
        "median_margin": statistics.median(margins) if margins else None,
        "min_margin": min(margins) if margins else None,
        "max_margin": max(margins) if margins else None,
        "opponents_unique": len({r["opponent_team"] for r in rows}),
        "by_opponent": grouped_stats(rows),
        "worst": sorted(rows, key=lambda r: r["margin"])[:10],
        "best": sorted(rows, key=lambda r: r["margin"], reverse=True)[:10],
        "games": rows,
        "unresolved": unresolved,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
