"""CR046A: independent live x-ray of the current Kaggriculture king.

Uses only the public leaderboard/list-episodes endpoints and public replay CDN,
mirroring destbreso's published X-ray methodology. Observational research only:
no runtime identity feature and no Kaggle submission.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import statistics
import time
from pathlib import Path

import requests

COMP_ID = 147734
LEADERBOARD_URL = "https://www.kaggle.com/api/i/competitions.LeaderboardService/GetLeaderboard"
LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
REPLAY_URL = "https://www.kaggleusercontent.com/episodes/{id}.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}
CHANNELS = ("farmer", "hands", "market")


def canon(a):
    return json.dumps(a or PASS, sort_keys=True, separators=(",", ":"))


def ch(a, name):
    a = a or PASS
    return json.dumps(a.get(name), sort_keys=True, separators=(",", ":"))


def classify(streams):
    if len(streams) < 2:
        return {"n": len(streams), "varying_fraction": None, "first_divergence": None, "channel_variation": {c: None for c in CHANNELS}}
    n = min(len(s) for s in streams)
    varying = 0
    first = None
    bych = {c: 0 for c in CHANNELS}
    for t in range(n):
        acts = [canon(s[t]) for s in streams]
        diff = len(set(acts)) > 1
        if diff:
            varying += 1
            if first is None:
                first = t
        for c in CHANNELS:
            if len({ch(s[t], c) for s in streams}) > 1:
                bych[c] += 1
    return {
        "n": len(streams),
        "turns_compared": n,
        "varying_fraction": varying / n if n else None,
        "first_divergence": first,
        "channel_variation": {c: bych[c] / n if n else None for c in CHANNELS},
    }


def sha_stream(stream):
    return hashlib.sha256("\n".join(canon(a) for a in stream).encode()).hexdigest()


def fetch_json(url, *, post=None, tries=4, timeout=120):
    last = None
    for i in range(tries):
        try:
            r = requests.post(url, json=post, timeout=timeout) if post is not None else requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            if i + 1 < tries:
                time.sleep(5 * (i + 1))
    raise last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-episodes", type=int, default=40)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    lb = fetch_json(LEADERBOARD_URL, post={"competitionId": COMP_ID})
    rows = lb.get("publicLeaderboard") or []
    if not rows:
        raise RuntimeError("empty public leaderboard")
    top = []
    for r in rows[:10]:
        top.append({k: r.get(k) for k in ("rank", "submissionId", "teamId", "teamName", "displayScore", "score") if k in r})
    king = int(rows[0]["submissionId"])

    eps = fetch_json(LIST_URL, post={"submissionId": king}).get("episodes") or []
    eps = [e for e in eps if e.get("state") == "COMPLETED" and e.get("endTime")]
    eps.sort(key=lambda e: e["endTime"], reverse=True)
    selected = eps[: args.max_episodes]
    if not selected:
        raise RuntimeError(f"no completed episodes for king {king}")

    data = []
    errors = []
    for e in selected:
        eid = int(e["id"])
        try:
            agents = {(a.get("index") or 0): a for a in e.get("agents", [])}
            me = next(i for i, a in agents.items() if int(a.get("submissionId") or -1) == king)
            rep = fetch_json(REPLAY_URL.format(id=eid), timeout=180)
            steps = rep.get("steps") or []
            if len(steps) < 719:
                raise RuntimeError(f"short replay {len(steps)}")
            stream = [((steps[t+1][me].get("action") if t+1 < len(steps) else None) or PASS) for t in range(719)]
            opp_stream = [((steps[t+1][1-me].get("action") if t+1 < len(steps) else None) or PASS) for t in range(719)]
            obs0 = steps[0][me].get("observation") or {}
            shops = []
            for frame in steps:
                o = frame[me].get("observation") or {}
                s = list(((o.get("town") or {}).get("unlocked_shops") or []))
                if len(s) >= 2:
                    shops = s[:2]
                    break
            a_me = agents[me]
            a_op = agents[1-me]
            margin = float(a_me.get("reward") or 0) - float(a_op.get("reward") or 0)
            data.append({
                "episode_id": eid,
                "end_time": e.get("endTime"),
                "seat": me,
                "seed": rep.get("seed") or obs0.get("seed"),
                "world": "__".join(map(str, shops)) if len(shops) == 2 else "?",
                "reward": float(a_me.get("reward") or 0),
                "opponent_reward": float(a_op.get("reward") or 0),
                "margin": margin,
                "updated_score": a_me.get("updatedScore"),
                "opponent_submission_id": a_op.get("submissionId"),
                "opponent_updated_score": a_op.get("updatedScore"),
                "stream_sha256": sha_stream(stream),
                "opp_stream_sha256": sha_stream(opp_stream),
                "stream": stream,
            })
        except Exception as ex:
            errors.append({"episode_id": eid, "error": repr(ex)[:1000]})

    streams = [r["stream"] for r in data]
    global_cls = classify(streams)
    by_world = collections.defaultdict(list)
    for r in data:
        by_world[r["world"]].append(r["stream"])
    world_cls = {w: classify(ss) for w, ss in sorted(by_world.items())}
    repeated_worlds = {w: v for w, v in world_cls.items() if v["n"] >= 2}
    within_vals = [v["varying_fraction"] for v in repeated_worlds.values() if v["varying_fraction"] is not None]
    firsts = [v["first_divergence"] for v in repeated_worlds.values() if v["first_divergence"] is not None]

    margins = [r["margin"] for r in data]
    scores = [float(r["updated_score"]) for r in data if r.get("updated_score") is not None]
    unique_shas = len({r["stream_sha256"] for r in data})
    compact_rows = [{k: v for k, v in r.items() if k != "stream"} for r in data]
    payload = {
        "experiment": "CR046A_LIVE_KING_XRAY_V1",
        "leaderboard_top10": top,
        "king_submission_id": king,
        "requested_episodes": args.max_episodes,
        "loaded_episodes": len(data),
        "errors": errors,
        "ledger": {
            "wins": sum(x > 0 for x in margins),
            "losses": sum(x < 0 for x in margins),
            "ties": sum(x == 0 for x in margins),
            "median_margin": statistics.median(margins) if margins else None,
            "mean_margin": statistics.mean(margins) if margins else None,
            "worst_margin": min(margins) if margins else None,
            "best_margin": max(margins) if margins else None,
            "latest_updated_score": scores[0] if scores else None,
        },
        "trajectory": {
            "unique_full_streams": unique_shas,
            "global": global_cls,
            "world_count": len(by_world),
            "repeated_world_count": len(repeated_worlds),
            "within_world_weighted_mean_variation": (
                sum(v["varying_fraction"] * v["n"] for v in repeated_worlds.values()) / sum(v["n"] for v in repeated_worlds.values())
                if repeated_worlds else None
            ),
            "within_world_median_variation": statistics.median(within_vals) if within_vals else None,
            "within_world_earliest_divergence": min(firsts) if firsts else None,
            "by_world": world_cls,
        },
        "episodes": compact_rows,
        "observational_only": True,
        "runtime_identity_features": False,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "episodes"}, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
