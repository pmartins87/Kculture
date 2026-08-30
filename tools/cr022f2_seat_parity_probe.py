"""CR022F2: mechanical replay parity probe with explicit replay-seat normalization.

This probe reads no reward signal for tuning. It verifies whether the frozen hosted
CR008 action stream is reproduced when the replay seat is explicitly supplied as
`observation.player`, while preserving the stored observation's missing `step`
semantics used by the frozen CR007 encoder.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"


def as_dict(value):
    if isinstance(value, dict):
        return value
    fn = getattr(value, "to_dict", None)
    if callable(fn):
        return fn()
    raise TypeError(type(value))


def load_agent():
    spec = importlib.util.spec_from_file_location(f"cr022f2_{time.time_ns()}", CR008)
    if spec is None or spec.loader is None:
        raise RuntimeError(CR008)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def public_episodes(api, submission_id, limit):
    rows = []
    for item in api.competition_list_episodes(int(submission_id)) or []:
        d = as_dict(item)
        if d.get("state") != "COMPLETED" or d.get("type") != "EPISODE_TYPE_PUBLIC":
            continue
        agents = d.get("agents") or []
        seats = [i for i, a in enumerate(agents) if int(a.get("submissionId") or -1) == int(submission_id)]
        if seats:
            rows.append((d, seats[0]))
    rows.sort(key=lambda x: (str(x[0].get("endTime") or x[0].get("createTime") or ""), int(x[0].get("id") or 0)), reverse=True)
    return rows[:limit]


def download(api, episode_id, folder):
    api.competition_episode_replay(int(episode_id), path=str(folder), quiet=True)
    p = folder / f"episode-{int(episode_id)}-replay.json"
    if not p.exists():
        raise RuntimeError(f"missing replay {episode_id}")
    return p


def inspect_episode(path, seat, episode_id):
    rep = json.loads(path.read_text(encoding="utf-8"))
    steps = rep.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {episode_id}: {len(steps)}")
    agent = load_agent()
    mismatches = 0
    first = []
    for t in range(719):
        obs = copy.deepcopy(steps[t][seat].get("observation") or {})
        obs["player"] = int(seat)
        actual = steps[t + 1][seat].get("action") or {}
        predicted = agent(obs, None)
        if canon(predicted) != canon(actual):
            mismatches += 1
            if len(first) < 10:
                first.append(t)
    return {
        "episode_id": int(episode_id),
        "seat": int(seat),
        "compared": 719,
        "mismatches": mismatches,
        "first_mismatch_steps": first,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission-id", type=int, default=55866079)
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    api = KaggleApi()
    api.authenticate()
    rows = []
    errors = []
    with tempfile.TemporaryDirectory(prefix="kculture-cr022f2-") as td:
        root = Path(td)
        for ep, seat in public_episodes(api, args.submission_id, args.limit):
            eid = int(ep["id"])
            try:
                rows.append(inspect_episode(download(api, eid, root), seat, eid))
            except Exception as exc:
                errors.append({"episode_id": eid, "seat": seat, "error": repr(exc)})

    by_seat = {}
    for seat in (0, 1):
        xs = [r for r in rows if r["seat"] == seat]
        compared = sum(r["compared"] for r in xs)
        mismatches = sum(r["mismatches"] for r in xs)
        by_seat[str(seat)] = {
            "episodes": len(xs),
            "compared": compared,
            "mismatches": mismatches,
            "mismatch_rate": mismatches / compared if compared else None,
            "episodes_with_mismatch": sum(r["mismatches"] > 0 for r in xs),
        }

    payload = {
        "experiment": "CR022F2",
        "purpose": "mechanical seat-normalization parity only",
        "submission_id": args.submission_id,
        "requested_limit": args.limit,
        "episodes": len(rows),
        "errors": errors,
        "by_seat": by_seat,
        "rows": rows,
        "reward_used": False,
        "raw_replays_persisted": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("rows", "errors")}, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)
    if any(r["mismatches"] for r in rows):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
