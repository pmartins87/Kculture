#!/usr/bin/env python3
"""Evaluate the frozen CR084 temporal high-strength replay proxy.

This is offline diagnostics only. Team name/rating/episode metadata are used solely to
select the pre-frozen public holdout. Agents receive only their legal replay
observation sequence. No replay identity, rating, episode id, hidden seed, future
state, or opponent-private state is passed into either agent.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import tarfile
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

START = datetime.fromisoformat("2026-09-13T08:00:31+00:00")
END = datetime.fromisoformat("2026-09-13T12:55:00+00:00")
MIN_SCORE = 2300.0
TARGET_TEAM = "Paulo Martins"
BASE_SHA = "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8"
CAND_SHA = "3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2"


def parse_time(s: str) -> datetime:
    # Kaggle CSV is UTC but omits explicit offset.
    return datetime.fromisoformat(s.strip()).replace(tzinfo=START.tzinfo)


def load_holdout_ids(path: Path) -> dict[str, str]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    out = {}
    for r in rows:
        typ = str(r.get("type", ""))
        state = str(r.get("state", ""))
        if "PUBLIC" not in typ or not state.endswith("COMPLETED"):
            continue
        ct = parse_time(str(r["createTime"]))
        if START <= ct <= END:
            out[str(r["id"])] = str(r["createTime"])
    return out


def load_scores(path: Path) -> dict[str, float]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    out = {}
    for r in rows:
        name = str(r.get("TeamName", ""))
        try:
            score = float(r.get("Score", ""))
        except Exception:
            continue
        out[name] = score
    return out


def extract_main(package: Path, root: Path, label: str) -> Path:
    d = root / label
    d.mkdir(parents=True, exist_ok=True)
    with tarfile.open(package, "r:gz") as tf:
        member = tf.getmember("main.py")
        f = tf.extractfile(member)
        if f is None:
            raise RuntimeError("main.py missing")
        (d / "main.py").write_bytes(f.read())
    return d / "main.py"


def load_module(main_py: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, main_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {main_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def physical(action: dict) -> list:
    return [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]


def tile_at(obs: dict, seat: int, x: int, y: int):
    farm = obs["farms"][seat]
    tiles = farm.get("tiles") or []
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def base_feeds_tile_later(replay: dict, seat: int, start_t: int, day: int, x: int, y: int) -> bool:
    # Actions generated from observation t are stored in replay step t+1. Inspect
    # baseline recorded physical actions from the event through the final observation
    # of that same day, including hour 23.
    steps = replay["steps"]
    for t in range(start_t, len(steps) - 1):
        obs = steps[t][seat].get("observation") or {}
        if int(obs.get("day", -1)) != day:
            if int(obs.get("day", -1)) > day:
                break
            continue
        rec = steps[t + 1][seat].get("action") or {}
        farm = obs["farms"][seat]
        positions = [farm.get("farmer"), *(farm.get("hands") or [])]
        acts = physical(rec)
        for i, pos in enumerate(positions):
            if i >= len(acts) or not pos:
                continue
            if int(pos[0]) == x and int(pos[1]) == y and acts[i] == ["FEED"]:
                return True
    return False


def next_day_tile(replay: dict, seat: int, day: int, x: int, y: int):
    for st in replay["steps"]:
        obs = st[seat].get("observation") or {}
        if int(obs.get("day", -1)) == day + 1 and int(obs.get("hour", -1)) == 0:
            return tile_at(obs, seat, x, y)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes-csv", type=Path, required=True)
    ap.add_argument("--leaderboard-csv", type=Path, required=True)
    ap.add_argument("--replay-root", type=Path, required=True)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    import hashlib
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(a.base) != BASE_SHA:
        raise RuntimeError("CR083 SHA mismatch")
    if sha(a.candidate) != CAND_SHA:
        raise RuntimeError("CR084 SHA mismatch")

    holdout = load_holdout_ids(a.episodes_csv)
    scores = load_scores(a.leaderboard_csv)
    replay_files = {p.stem.split("-")[1]: p for p in a.replay_root.rglob("episode-*-replay.json")}

    selected = []
    unmatched = []
    for eid, create_time in sorted(holdout.items(), key=lambda kv: int(kv[0])):
        p = replay_files.get(eid)
        if p is None:
            unmatched.append({"episode_id": eid, "reason": "replay_missing"})
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        names = list((d.get("info") or {}).get("TeamNames") or [])
        if TARGET_TEAM not in names or len(names) != 2:
            unmatched.append({"episode_id": eid, "reason": "target_team_not_resolved", "team_names": names})
            continue
        opp = names[1 - names.index(TARGET_TEAM)]
        if opp not in scores:
            unmatched.append({"episode_id": eid, "reason": "opponent_not_in_leaderboard", "opponent": opp})
            continue
        if scores[opp] >= MIN_SCORE:
            selected.append((eid, create_time, opp, scores[opp], p, d))

    report: dict[str, Any] = {
        "schema_version": "cr084-temporal-high-strength-proxy-v1",
        "window_start": START.isoformat(),
        "window_end": END.isoformat(),
        "high_strength_min_score": MIN_SCORE,
        "holdout_public_completed_episodes": len(holdout),
        "selected_high_strength_episodes": len(selected),
        "unmatched": unmatched,
        "episodes": [],
        "base_action_steps": 0,
        "base_action_mismatches": 0,
        "semantic_differences": 0,
        "semantic_violations": 0,
        "unique_first_rescue_opportunities": 0,
        "confirmed_preventable_escapes": 0,
        "episodes_with_confirmed_preventable_escape": 0,
        "high_strength_losses": 0,
        "losses_with_confirmed_preventable_escape": 0,
    }

    with tempfile.TemporaryDirectory(prefix="cr084-proxy-") as td:
        root = Path(td)
        bmain = extract_main(a.base, root, "base")
        cmain = extract_main(a.candidate, root, "cand")

        for idx, (eid, create_time, opp, opp_score, p, replay) in enumerate(selected):
            seat = list(replay["info"]["TeamNames"]).index(TARGET_TEAM)
            bmod = load_module(bmain, f"cr084_proxy_b_{idx}")
            cmod = load_module(cmain, f"cr084_proxy_c_{idx}")
            rewards = [float(x) for x in replay.get("rewards", [0, 0])]
            margin = rewards[seat] - rewards[1 - seat]
            result = "W" if margin > 0 else "L" if margin < 0 else "T"
            if result == "L":
                report["high_strength_losses"] += 1

            first_by_animal_day: dict[tuple[int, int, int], dict] = {}
            base_mismatch = 0
            semantic_viol = 0
            semantic_diff = 0

            steps = replay["steps"]
            for t in range(len(steps) - 1):
                obs = json.loads(json.dumps(steps[t][seat]["observation"]))
                rec = steps[t + 1][seat].get("action") or {}
                b = bmod.agent(json.loads(json.dumps(obs)))
                c = cmod.agent(json.loads(json.dumps(obs)))
                report["base_action_steps"] += 1
                if b != rec:
                    base_mismatch += 1
                    report["base_action_mismatches"] += 1

                if c == b:
                    continue
                semantic_diff += 1
                report["semantic_differences"] += 1
                valid = True
                if c.get("market") != b.get("market"):
                    valid = False
                ba = physical(b); ca = physical(c)
                farm = obs["farms"][seat]
                positions = [farm.get("farmer"), *(farm.get("hands") or [])]
                invs = list((obs.get("private") or {}).get("inventories") or [])
                seeds = dict((obs.get("private") or {}).get("seeds") or {})
                board = len(farm.get("tiles") or [])
                if len(ba) != len(ca) or len(ba) != len(positions):
                    valid = False
                for i in range(min(len(ba), len(ca), len(positions))):
                    if ba[i] == ca[i]:
                        continue
                    pos = positions[i]
                    if not pos:
                        valid = False; continue
                    x, y = int(pos[0]), int(pos[1])
                    tile = tile_at(obs, seat, x, y)
                    inv = invs[i] if i < len(invs) else {}
                    step = int(obs.get("step", int(obs.get("day", 0)) * 24 + int(obs.get("hour", 0))))
                    cond = (
                        576 <= step < 696
                        and ca[i] == ["FEED"]
                        and isinstance(tile, dict)
                        and tile.get("animal") is not None
                        and not bool(tile.get("fed_today"))
                        and int(tile.get("consecutive_unfed", 0)) >= 1
                        and int(inv.get("WHEAT", 0)) > 0
                    )
                    try:
                        cond = cond and bool(bmod._noop(ba[i], tile, inv, seeds, x, y, board))
                    except Exception:
                        cond = False
                    if not cond:
                        valid = False
                        continue
                    k = (int(obs.get("day", 0)), x, y)
                    if k not in first_by_animal_day:
                        first_by_animal_day[k] = {
                            "t": t, "step": step, "day": int(obs.get("day", 0)),
                            "hour": int(obs.get("hour", 0)), "x": x, "y": y,
                            "animal": str(tile.get("animal")), "unit": i,
                        }
                if not valid:
                    semantic_viol += 1
                    report["semantic_violations"] += 1

            confirmed = []
            for ev in first_by_animal_day.values():
                report["unique_first_rescue_opportunities"] += 1
                if base_feeds_tile_later(replay, seat, ev["t"], ev["day"], ev["x"], ev["y"]):
                    continue
                nxt = next_day_tile(replay, seat, ev["day"], ev["x"], ev["y"])
                same = isinstance(nxt, dict) and nxt.get("animal") == ev["animal"]
                if not same:
                    confirmed.append(ev)
                    report["confirmed_preventable_escapes"] += 1

            if confirmed:
                report["episodes_with_confirmed_preventable_escape"] += 1
                if result == "L":
                    report["losses_with_confirmed_preventable_escape"] += 1

            report["episodes"].append({
                "episode_id": eid,
                "create_time": create_time,
                "opponent_team": opp,
                "opponent_score": opp_score,
                "result": result,
                "money_margin": margin,
                "base_action_mismatches": base_mismatch,
                "semantic_differences": semantic_diff,
                "semantic_violations": semantic_viol,
                "unique_first_rescue_opportunities": len(first_by_animal_day),
                "confirmed_preventable_escapes": len(confirmed),
                "confirmed_events": confirmed,
            })

    n = report["selected_high_strength_episodes"]
    losses = report["high_strength_losses"]
    loss_align = 1.0 if losses == 0 else report["losses_with_confirmed_preventable_escape"] / losses
    checks = {
        "at_least_4_high_strength_episodes": n >= 4,
        "base_reproduction_100pct": report["base_action_mismatches"] == 0 and report["base_action_steps"] > 0,
        "semantic_fidelity_100pct": report["semantic_violations"] == 0,
        "at_least_2_episodes_with_confirmed_escape": report["episodes_with_confirmed_preventable_escape"] >= 2,
        "confirmed_escapes_mean_at_least_1_per_episode": n > 0 and report["confirmed_preventable_escapes"] >= n,
        "loss_alignment_at_least_50pct": loss_align >= 0.5,
        "no_unmatched_holdout_inputs": len(unmatched) == 0,
    }
    report["loss_alignment_rate"] = loss_align
    report["checks"] = checks
    report["pass"] = all(checks.values())
    if not checks["at_least_4_high_strength_episodes"] or not checks["base_reproduction_100pct"] or unmatched:
        report["decision"] = "CR084_PROXY_INCONCLUSIVE_NO_HOSTED_ACTION"
    else:
        report["decision"] = (
            "CR084_TEMPORAL_PROXY_PASS_AWAIT_LOCAL_PROMOTION_DECISION"
            if report["pass"] else "CLOSE_CR084_CRITICAL_FEED_RESCUE"
        )

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
