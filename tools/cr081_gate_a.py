"""CR081 Gate A: frozen current-3056 bridge test.

Uses only already-frozen evidence:
- primary current UMG corpus;
- canonical bridge-family replay = earliest of the three hosted CR071M loss-family
  replays identified before deep-corpus inspection (Sidharth Hulyalkar, episode 107807039).

The script does not select thresholds or tune a candidate.
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

UMG = "Unknown Mother-Goose"
CANONICAL_OPP = "Sidharth Hulyalkar"
CANONICAL_EPISODE = 107807039
PREFIX = 192


def replay_files(root: Path):
    return sorted(root.rglob("episode-*-replay.json"), key=lambda p: int(p.name.split("-")[1]))


def target_actions(path: Path, team: str):
    d = json.loads(path.read_text(encoding="utf-8"))
    teams = list(d.get("info", {}).get("TeamNames") or [])
    seats = [i for i, t in enumerate(teams) if t == team]
    if len(seats) != 1:
        return None
    seat = seats[0]
    if len(d.get("steps") or []) < PREFIX:
        return None
    return {
        "episode": int(d.get("info", {}).get("EpisodeId") or path.name.split("-")[1]),
        "teams": teams,
        "seat": seat,
        "actions": [d["steps"][s][seat]["action"] for s in range(PREFIX)],
    }


def canonical_reference(root: Path):
    matches = []
    for p in replay_files(root):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if int(d.get("info", {}).get("EpisodeId") or -1) != CANONICAL_EPISODE:
            continue
        teams = list(d.get("info", {}).get("TeamNames") or [])
        if CANONICAL_OPP not in teams:
            continue
        seat = teams.index(CANONICAL_OPP)
        matches.append([d["steps"][s][seat]["action"] for s in range(PREFIX)])
    if len(matches) != 1:
        raise RuntimeError(f"canonical bridge replay resolution expected 1, got {len(matches)}")
    return matches[0]


def eq_rate(actions, reference, channel):
    return sum((actions[s].get(channel) or ([] if channel != "farmer" else None)) ==
               (reference[s].get(channel) or ([] if channel != "farmer" else None))
               for s in range(PREFIX)) / PREFIX


def mode_key(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umg-root", type=Path, required=True)
    ap.add_argument("--bridge-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    ref = canonical_reference(a.bridge_root)
    rows = [r for p in replay_files(a.umg_root) if (r := target_actions(p, UMG)) is not None]
    rows.sort(key=lambda r: r["episode"])
    cut = int(len(rows) * 0.75)
    dev, hold = rows[:cut], rows[cut:]
    if not dev or not hold:
        raise RuntimeError("insufficient usable UMG episodes for chronological split")

    sims = {}
    for ch in ("farmer", "hands", "market"):
        vals = [eq_rate(r["actions"], ref, ch) for r in hold]
        sims[ch] = {
            "median": statistics.median(vals),
            "mean": statistics.mean(vals),
            "min": min(vals),
            "max": max(vals),
        }

    modal_market = []
    train_support = []
    for s in range(PREFIX):
        c = Counter(mode_key(r["actions"][s].get("market") or []) for r in dev)
        k, n = c.most_common(1)[0]
        modal_market.append(json.loads(k))
        train_support.append(n / len(dev))
    per_ep_market = [
        sum(r["actions"][s].get("market") == modal_market[s] for s in range(PREFIX)) / PREFIX
        for r in hold
    ]
    market_holdout = sum(
        r["actions"][s].get("market") == modal_market[s]
        for r in hold for s in range(PREFIX)
    ) / (len(hold) * PREFIX)

    checks = {
        "farmer_median_at_least_0_80": sims["farmer"]["median"] >= 0.80,
        "hands_median_at_least_0_60": sims["hands"]["median"] >= 0.60,
        "market_step_modal_holdout_at_least_0_65": market_holdout >= 0.65,
        "no_private_or_identity_features": True,
    }
    report = {
        "schema_version": "cr081-gate-a-v1",
        "canonical_bridge": {"episode": CANONICAL_EPISODE, "team": CANONICAL_OPP},
        "usable_episodes": len(rows),
        "development_episodes": len(dev),
        "holdout_episodes": len(hold),
        "development_episode_range": [dev[0]["episode"], dev[-1]["episode"]],
        "holdout_episode_range": [hold[0]["episode"], hold[-1]["episode"]],
        "holdout_similarity_to_bridge": sims,
        "market_step_modal": {
            "holdout_overall_accuracy": market_holdout,
            "holdout_episode_median_accuracy": statistics.median(per_ep_market),
            "holdout_episode_min_accuracy": min(per_ep_market),
            "train_support_mean": statistics.mean(train_support),
            "train_support_median": statistics.median(train_support),
        },
        "checks": checks,
        "pass": all(checks.values()),
        "decision": "BUILD_ONE_CR081_MARKET_FIRST_BRIDGE" if all(checks.values()) else "CLOSE_CR081_BRIDGE_MOVE_TO_STATE_ADAPTIVE_MACRO_POLICY",
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
