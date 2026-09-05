"""CR026 Phase 0: benchmark frozen CR024 consensus against current live-meta winner tapes.

This is development diagnostics, not a deployable identity-aware strategy. It uses
only public official episode action streams and never exposes team/episode identity
to the agent. The purpose is to replace the now-saturated legacy opponent panel
with current strong opponents before designing CR026.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
BUILDER = ROOT / "tools/build_cr024_consensus_submission.py"
INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def actions_for(rep: dict, player: int) -> list[dict]:
    frames = rep.get("steps") or []
    out = []
    for frame_index in range(1, len(frames)):
        frame = frames[frame_index]
        action = frame[player].get("action") if player < len(frame) else None
        out.append(copy.deepcopy(action) if isinstance(action, dict) else {})
    return out


def tape_agent(actions: list[dict]):
    def agent(obs, config=None):
        try:
            raw = get(obs, "step", None)
            if raw is not None:
                step = int(raw)
            else:
                step = int(get(obs, "day", 0) or 0) * 24 + int(get(obs, "hour", 0) or 0)
        except Exception:
            step = 0
        if 0 <= step < len(actions):
            return copy.deepcopy(actions[step])
        return {}
    return agent


def final_rewards(rep: dict) -> list[float | None]:
    if not rep.get("steps"):
        return [None, None]
    final = rep["steps"][-1]
    out = []
    for p in (0, 1):
        r = final[p].get("reward") if p < len(final) else None
        try:
            x = float(r)
            out.append(x if math.isfinite(x) else None)
        except Exception:
            out.append(None)
    return out


def final_statuses(rep: dict) -> list[str | None]:
    if not rep.get("steps"):
        return [None, None]
    final = rep["steps"][-1]
    return [final[p].get("status") if p < len(final) else None for p in (0, 1)]


def run_pair(seed: int, agents: list, original_config: dict | None) -> dict:
    cfg = copy.deepcopy(original_config) if isinstance(original_config, dict) else {}
    cfg["episodeSteps"] = 720
    cfg["seed"] = int(seed)
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.run(agents)
    rep = env.toJSON()
    return {
        "rewards": final_rewards(rep),
        "statuses": final_statuses(rep),
        "steps": len(rep.get("steps") or []),
    }


def exact_rewards(a, b) -> bool:
    return len(a) == len(b) == 2 and all(x is not None and y is not None and float(x) == float(y) for x, y in zip(a, b))


def winner_index(rewards) -> int | None:
    if len(rewards) != 2 or any(x is None for x in rewards) or rewards[0] == rewards[1]:
        return None
    return 0 if rewards[0] > rewards[1] else 1


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def tape_sha(actions: list[dict]) -> str:
    b = json.dumps(actions, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def build_cr024(folder: Path):
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    builder = load_module(BUILDER, "cr026_cr024_builder")
    api = KaggleApi(); api.authenticate()
    t11, p11 = builder.download_tape(api, cfg["routes"]["top11_openloop"], folder)
    t19, p19 = builder.download_tape(api, cfg["routes"]["top19_openloop"], folder)
    consensus = builder.build_consensus(t11, t19)
    return consensus, {"top11": p11, "top19": p19, "tape_sha256": tape_sha(consensus)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-04")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if not 1 <= args.top <= 20:
        raise SystemExit("--top must be 1..20")

    rows = []
    source = []
    errors = []

    with tempfile.TemporaryDirectory(prefix="cr026-live-meta-") as td:
        tmp = Path(td)
        consensus, provenance = build_cr024(tmp / "cr024")
        cr024 = tape_agent(consensus)

        index_rows = sorted(read_csv(download(INDEX_HANDLE, "manifest.csv", tmp / "index")), key=lambda r: r["date"])
        idx = next((r for r in index_rows if r["date"] == args.date), None)
        if idx is None:
            raise RuntimeError(f"official date absent: {args.date}")
        handle = f"kaggle/kaggriculture-episodes-{args.date}"
        manifest = sorted(read_csv(download(handle, "manifest.csv", tmp / "day")), key=lambda r: -float(r["avg_score"]))[:args.top]

        scenarios = []
        for rank, mr in enumerate(manifest, start=1):
            eid = str(mr["episode_id"])
            try:
                rep = json.loads(download(handle, f"{eid}.json", tmp / "episodes" / eid).read_text(encoding="utf-8"))
                info = rep.get("info") or {}
                seed = int(info.get("seed"))
                names = info.get("TeamNames") or ["p0", "p1"]
                original = final_rewards(rep)
                wi = winner_index(original)
                tapes = [actions_for(rep, 0), actions_for(rep, 1)]
                original_config = rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {}
                replay = run_pair(seed, [tape_agent(tapes[0]), tape_agent(tapes[1])], original_config)
                exact = replay["steps"] == 720 and exact_rewards(original, replay["rewards"]) and all(s == "DONE" for s in replay["statuses"])
                receipt = {
                    "rank": rank,
                    "episode_id": eid,
                    "avg_score": float(mr["avg_score"]),
                    "seed": seed,
                    "team_names": names,
                    "original_rewards": original,
                    "winner_seat": wi,
                    "winner_team": None if wi is None else (names[wi] if wi < len(names) else f"p{wi}"),
                    "winner_tape_sha256": None if wi is None else tape_sha(tapes[wi]),
                    "exact_terminal_reproduction": exact,
                }
                source.append(receipt)
                if exact and wi is not None:
                    scenarios.append({
                        **receipt,
                        "winner_tape": tapes[wi],
                        "configuration": original_config,
                    })
            except Exception as exc:
                errors.append({"phase": "source", "episode_id": eid, "error": repr(exc)})

        for sc in scenarios:
            opp = tape_agent(sc["winner_tape"])
            for candidate_seat in (0, 1):
                try:
                    agents = [cr024, opp] if candidate_seat == 0 else [opp, cr024]
                    result = run_pair(sc["seed"], agents, sc["configuration"])
                    statuses = result["statuses"]
                    if result["steps"] != 720 or statuses != ["DONE", "DONE"]:
                        raise RuntimeError(f"non-DONE/short result steps={result['steps']} statuses={statuses}")
                    own = result["rewards"][candidate_seat]
                    other = result["rewards"][1 - candidate_seat]
                    if own is None or other is None:
                        raise RuntimeError("missing rewards")
                    delta = float(own) - float(other)
                    rows.append({
                        "episode_id": sc["episode_id"],
                        "rank": sc["rank"],
                        "avg_score": sc["avg_score"],
                        "source_winner_team": sc["winner_team"],
                        "source_winner_tape_sha256": sc["winner_tape_sha256"],
                        "seed": sc["seed"],
                        "candidate_seat": candidate_seat,
                        "self_reward": own,
                        "opponent_reward": other,
                        "delta": delta,
                        "score": score(delta),
                    })
                except Exception as exc:
                    errors.append({"phase": "benchmark", "episode_id": sc["episode_id"], "candidate_seat": candidate_seat, "error": repr(exc)})

    wins = sum(r["score"] == 1.0 for r in rows)
    losses = sum(r["score"] == 0.0 for r in rows)
    ties = sum(r["score"] == 0.5 for r in rows)
    score_total = sum(r["score"] for r in rows)
    deltas = [float(r["delta"]) for r in rows]
    team_breakdown = {}
    for r in rows:
        t = r["source_winner_team"]
        x = team_breakdown.setdefault(t, {"games": 0, "wins": 0, "losses": 0, "ties": 0, "score": 0.0, "deltas": []})
        x["games"] += 1; x["score"] += r["score"]; x["deltas"].append(r["delta"])
        if r["score"] == 1.0: x["wins"] += 1
        elif r["score"] == 0.0: x["losses"] += 1
        else: x["ties"] += 1
    for x in team_breakdown.values():
        x["score_rate"] = x["score"] / x["games"] if x["games"] else None
        x["mean_delta"] = statistics.mean(x.pop("deltas")) if x["games"] else None

    expected = len(scenarios) * 2
    mechanical = len(rows) == expected and not errors
    score_rate = score_total / len(rows) if rows else None
    gap_found = mechanical and (losses > 0 or (score_rate is not None and score_rate < 0.90))
    decision = (
        "CR026_CURRENT_META_GAP_FOUND__SCREEN_RECENT_WINNER_TAPES"
        if gap_found else
        "CR024_CURRENT_META_STRONG__SEARCH_FINE_GRAIN_IMPROVEMENTS"
        if mechanical else
        "CR026_BENCHMARK_MECHANICAL_FAIL"
    )
    report = {
        "experiment": "CR026_LIVE_META_CR024_BENCHMARK",
        "source_date": args.date,
        "top_requested": args.top,
        "source_exact_scenarios": len(scenarios),
        "expected_benchmark_rows": expected,
        "completed_benchmark_rows": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "cr024_provenance": provenance,
        "metrics": {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "score_total": score_total,
            "score_rate": score_rate,
            "mean_delta": statistics.mean(deltas) if deltas else None,
            "median_delta": statistics.median(deltas) if deltas else None,
            "min_delta": min(deltas) if deltas else None,
            "max_delta": max(deltas) if deltas else None,
        },
        "team_breakdown": team_breakdown,
        "source": source,
        "rows": rows,
        "held_out_touched": False,
        "decision": decision,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "decision": decision,
        "source_exact_scenarios": len(scenarios),
        "completed_rows": len(rows),
        "errors": len(errors),
        "metrics": report["metrics"],
        "team_breakdown": team_breakdown,
    }, indent=2, sort_keys=True))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
