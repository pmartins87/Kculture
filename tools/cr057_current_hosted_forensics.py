"""CR057: inspect current hosted CR052/CR053 reality and package parity.

Hosted evidence is now the calibration target.  We query each submitted agent's
latest completed public episodes, summarize W/L/opponents, and verify that:

* CR053's hosted action stream is exactly the frozen route-106309334 tape;
* CR052's hosted action stream is exactly what the pinned public V2 package
  returns on the SAME recorded observations.

This catches clock/package/runtime drift before we build any new proxy story.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
import sys
import time
from pathlib import Path

import requests

LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
REPLAY_URL = "https://www.kaggleusercontent.com/episodes/{id}.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}
SUBMISSIONS = {"cr052": 56073867, "cr053": 56073870}
CR053_SOURCE_SUBMISSION = 56064100
CR053_SOURCE_EPISODE = 106309334


def fetch_json(url: str, post=None, tries=6):
    last = None
    for i in range(tries):
        try:
            r = requests.post(url, json=post, timeout=180) if post is not None else requests.get(url, timeout=180)
            r.raise_for_status(); return r.json()
        except Exception as exc:
            last = exc
            if i + 1 < tries: time.sleep(3 * (i + 1))
    raise last


def canon(a) -> str:
    return json.dumps(a or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def locate_seat(meta: dict, submission_id: int) -> int:
    for a in meta.get("agents") or []:
        if int(a.get("submissionId") or -1) == int(submission_id):
            return int(a.get("index") or 0)
    raise RuntimeError(f"submission {submission_id} absent from episode {meta.get('id')}")


def action_tape(rep: dict, seat: int) -> list[dict]:
    steps = rep.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {len(steps)}")
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or PASS) for t in range(719)]


def load_agent(package_dir: Path):
    package_dir = package_dir.resolve()
    sys.path.insert(0, str(package_dir))
    p = package_dir / "main.py"
    spec = importlib.util.spec_from_file_location(f"cr057_agent_{time.time_ns()}", p)
    if spec is None or spec.loader is None: raise RuntimeError(p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    agent = getattr(mod, "agent", None)
    if not callable(agent): raise RuntimeError("CR052 package missing callable agent")
    return agent


def call(agent, obs):
    try: return agent(obs, None)
    except TypeError: return agent(obs)


def final_rewards(rep: dict) -> tuple[float, float]:
    steps = rep.get("steps") or []
    if not steps: return (float("nan"), float("nan"))
    vals = []
    for seat in (0, 1):
        v = (steps[-1][seat] or {}).get("reward")
        try: vals.append(float(v))
        except Exception: vals.append(float("nan"))
    return vals[0], vals[1]


def opponent_info(meta: dict, seat: int) -> dict:
    agents = list(meta.get("agents") or [])
    opp = next((a for a in agents if int(a.get("index") or 0) != seat), {})
    keep = {}
    for k, v in opp.items():
        if isinstance(v, (str, int, float, bool, type(None))): keep[k] = v
    return keep


def episode_names(rep: dict) -> list[str]:
    info = rep.get("info") or {}
    names = info.get("TeamNames") or info.get("teamNames") or []
    return [str(x) for x in names] if isinstance(names, list) else []


def source_cr053_tape() -> list[dict]:
    eps = fetch_json(LIST_URL, post={"submissionId": CR053_SOURCE_SUBMISSION}).get("episodes") or []
    meta = next((e for e in eps if int(e.get("id") or -1) == CR053_SOURCE_EPISODE), None)
    if meta is None: raise RuntimeError("CR053 source episode unavailable")
    seat = locate_seat(meta, CR053_SOURCE_SUBMISSION)
    rep = fetch_json(REPLAY_URL.format(id=CR053_SOURCE_EPISODE))
    return action_tape(rep, seat)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--cr052-package", required=True); ap.add_argument("--latest", type=int, default=16); ap.add_argument("--output", required=True); args = ap.parse_args()
    c52_agent = load_agent(Path(args.cr052_package))
    c53_tape = source_cr053_tape()
    report = {"schema_version":"cr057-current-hosted-forensics-v1", "submissions":{}, "latest_requested":args.latest}

    for label, sid in SUBMISSIONS.items():
        eps = fetch_json(LIST_URL, post={"submissionId": sid}).get("episodes") or []
        completed = [e for e in eps if e.get("state") == "COMPLETED" and e.get("endTime")]
        completed.sort(key=lambda e: e.get("endTime") or "", reverse=True)
        selected = completed[:args.latest]
        rows = []; mismatches = []
        for meta in selected:
            eid = int(meta["id"]); seat = locate_seat(meta, sid)
            rep = fetch_json(REPLAY_URL.format(id=eid)); steps = rep.get("steps") or []
            if len(steps) < 720: continue
            hosted = action_tape(rep, seat)
            if label == "cr053":
                for t, (a, b) in enumerate(zip(hosted, c53_tape)):
                    if canon(a) != canon(b):
                        if len(mismatches) < 20: mismatches.append({"episode_id":eid,"step":t,"hosted":a,"expected":b})
            else:
                # Replay semantics: obs at t -> action recorded at t+1.
                for t in range(719):
                    obs = (steps[t][seat] or {}).get("observation") or {}
                    expected = call(c52_agent, obs) or PASS
                    if canon(hosted[t]) != canon(expected):
                        if len(mismatches) < 20: mismatches.append({"episode_id":eid,"step":t,"hosted":hosted[t],"expected":expected})
            r0, r1 = final_rewards(rep); mine = (r0, r1)[seat]; opp = (r0, r1)[1-seat]
            margin = mine - opp if math.isfinite(mine) and math.isfinite(opp) else None
            rows.append({"episode_id":eid,"end_time":meta.get("endTime"),"seat":seat,"reward":mine,"opponent_reward":opp,"margin":margin,"names":episode_names(rep),"opponent_meta":opponent_info(meta,seat)})

        margins = [float(r["margin"]) for r in rows if r["margin"] is not None]
        w = sum(x > 0 for x in margins); l = sum(x < 0 for x in margins); t = len(margins)-w-l
        report["submissions"][label] = {
            "submission_id": sid,
            "completed_available": len(completed),
            "episodes_analyzed": len(rows),
            "wins": w, "losses": l, "ties": t,
            "score_rate": ((w + 0.5*t)/len(margins) if margins else None),
            "mean_margin": (statistics.mean(margins) if margins else None),
            "median_margin": (statistics.median(margins) if margins else None),
            "package_parity_pass": len(mismatches) == 0,
            "mismatch_examples": mismatches,
            "rows": rows,
        }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    compact = copy.deepcopy(report)
    for v in compact["submissions"].values(): v["rows"] = v["rows"][:5]
    print(json.dumps(compact, indent=2, sort_keys=True))
    if not all(x["package_parity_pass"] for x in report["submissions"].values()): raise SystemExit(4)


if __name__ == "__main__": main()
