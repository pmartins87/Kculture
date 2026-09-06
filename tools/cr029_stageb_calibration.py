"""CR029: fresh official-meta calibration of CR024, recent-top tape, and Indar V1.

The experiment is frozen before outcomes. It selects strong official episodes from
one date by manifest score only, requires exact deterministic reproduction of each
source episode, deduplicates winner tapes by content, then evaluates all candidates
on the same episode seeds/configurations in both seats. A disjoint synthetic seed
panel supplies direct pairwise checks. No runtime identity feature and no Kaggle
submission are used.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

from cr026_live_meta_cr024_benchmark import build_cr024

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr029_fresh_official_meta_calibration.json"
OUT = ROOT / "artifacts/cr029_stageb"
INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"


def get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def canonical(action: dict) -> bytes:
    return json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stream_hash(actions: list[dict], n: int) -> str:
    body = b"".join(canonical(a) + b"\0" for a in actions[:n])
    return hashlib.sha256(body).hexdigest()[:16]


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def actions_for(rep: dict, player: int) -> list[dict]:
    frames = rep.get("steps") or []
    return [
        copy.deepcopy((frames[t][player] or {}).get("action") or {})
        for t in range(1, len(frames))
    ]


def runtime_source(actions: list[dict], label: str) -> str:
    payload = json.dumps(actions, separators=(",", ":"), sort_keys=True)
    return f'''"""{label} deterministic action-tape entrypoint for CR029."""\nimport copy as _copy\nimport json as _json\n_T=_json.loads({payload!r})\ndef _clock(obs):\n    try:\n        raw=obs.get("step")\n        if raw is not None:return max(0,int(raw))\n    except Exception:pass\n    try:return max(0,int(obs.get("day") or 0))*24+max(0,int(obs.get("hour") or 0))\n    except Exception:return 0\ndef agent(obs,config=None):\n    return _copy.deepcopy(_T[max(0,min(len(_T)-1,_clock(obs)))]) if _T else {{}}\n'''


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(
        kagglehub.dataset_download(
            handle, path=filename, output_dir=str(out), force_download=True
        )
    )
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def final_rewards(rep: dict) -> list[float | None]:
    steps = rep.get("steps") or []
    if not steps:
        return [None, None]
    final = steps[-1]
    out = []
    for p in (0, 1):
        raw = final[p].get("reward") if p < len(final) else None
        try:
            x = float(raw)
            out.append(x if math.isfinite(x) else None)
        except Exception:
            out.append(None)
    return out


def final_statuses(rep: dict) -> list[str | None]:
    steps = rep.get("steps") or []
    if not steps:
        return [None, None]
    final = steps[-1]
    return [final[p].get("status") if p < len(final) else None for p in (0, 1)]


def winner_index(rewards: list[float | None]) -> int | None:
    if len(rewards) != 2 or any(x is None for x in rewards):
        return None
    if rewards[0] == rewards[1]:
        return None
    return 0 if float(rewards[0]) > float(rewards[1]) else 1


def score(delta: float) -> float:
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def play(own: Path, opp: Path, seed: int, seat: int, original_config=None) -> dict:
    cfg = copy.deepcopy(original_config) if isinstance(original_config, dict) else {}
    cfg["episodeSteps"] = 720
    cfg["seed"] = int(seed)
    agents = [str(own), str(opp)] if seat == 0 else [str(opp), str(own)]
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.run(agents)
    rep = env.toJSON()
    steps = rep.get("steps") or []
    statuses = final_statuses(rep)
    rewards = final_rewards(rep)
    if len(steps) != 720 or statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"short/non-DONE: steps={len(steps)} statuses={statuses}")
    if any(x is None for x in rewards):
        raise RuntimeError(f"missing reward: {rewards}")
    own_reward = float(rewards[seat])
    opp_reward = float(rewards[1 - seat])
    delta = own_reward - opp_reward
    return {
        "rewards": rewards,
        "delta": delta,
        "score": score(delta),
    }


def exact_source_reproduction(
    tape0: list[dict],
    tape1: list[dict],
    seed: int,
    original_config: dict,
    expected_rewards: list[float | None],
    folder: Path,
) -> bool:
    a = folder / "source_p0.py"
    b = folder / "source_p1.py"
    a.write_text(runtime_source(tape0, "CR029_SOURCE_P0"), encoding="utf-8")
    b.write_text(runtime_source(tape1, "CR029_SOURCE_P1"), encoding="utf-8")
    cfg = copy.deepcopy(original_config) if isinstance(original_config, dict) else {}
    cfg["episodeSteps"] = 720
    cfg["seed"] = int(seed)
    env = make("kaggriculture", configuration=cfg, debug=True)
    env.run([str(a), str(b)])
    rep = env.toJSON()
    got = final_rewards(rep)
    return (
        len(rep.get("steps") or []) == 720
        and final_statuses(rep) == ["DONE", "DONE"]
        and len(got) == len(expected_rewards) == 2
        and all(
            x is not None and y is not None and float(x) == float(y)
            for x, y in zip(got, expected_rewards)
        )
    )


def seed_values(obj) -> set[int]:
    out: set[int] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "seed" in str(k).lower():
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    try:
                        out.add(int(x))
                    except Exception:
                        pass
            out |= seed_values(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= seed_values(v)
    return out


def summarize(rows: list[dict]) -> dict:
    deltas = [float(r["delta"]) for r in rows]
    scores = [float(r["score"]) for r in rows]
    return {
        "games": len(rows),
        "wins": sum(x == 1.0 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "score_total": sum(scores),
        "score_rate": (sum(scores) / len(scores)) if scores else None,
        "mean_delta": statistics.mean(deltas) if deltas else None,
        "median_delta": statistics.median(deltas) if deltas else None,
    }


def paired_vs_control(candidate_rows: list[dict], control_rows: list[dict]) -> dict:
    key = lambda r: (str(r["episode_id"]), int(r["candidate_seat"]))
    c = {key(r): r for r in candidate_rows}
    b = {key(r): r for r in control_rows}
    common = sorted(set(c) & set(b))
    diffs = [float(c[k]["delta"]) - float(b[k]["delta"]) for k in common]
    return {
        "paired_rows": len(common),
        "score_gain": sum(float(c[k]["score"]) - float(b[k]["score"]) for k in common),
        "improvements": sum(float(c[k]["score"]) > float(b[k]["score"]) for k in common),
        "regressions": sum(float(c[k]["score"]) < float(b[k]["score"]) for k in common),
        "mean_delta_gain": statistics.mean(diffs) if diffs else None,
        "median_delta_gain": statistics.median(diffs) if diffs else None,
        "positive_margin_rows": sum(x > 0 for x in diffs),
        "negative_margin_rows": sum(x < 0 for x in diffs),
    }


def main() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    fresh_seeds = [int(x) for x in cfg["fresh_pairwise_seeds"]]
    forbidden: set[int] = set()
    for p in sorted((ROOT / "configs").glob("*.json")):
        if p.resolve() == CFG.resolve():
            continue
        try:
            forbidden |= seed_values(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    overlap = sorted(set(fresh_seeds) & forbidden)
    if overlap:
        raise RuntimeError(f"CR029 fresh seed firewall overlap: {overlap}")

    indar_receipt_path = OUT / "indar_receipt.json"
    indar_path = OUT / "indar_local.py"
    if not indar_receipt_path.is_file() or not indar_path.is_file():
        raise FileNotFoundError("workflow must prepare Indar package before CR029 calibration")
    indar_receipt = json.loads(indar_receipt_path.read_text(encoding="utf-8"))
    if indar_receipt.get("status") != "READY":
        raise RuntimeError(indar_receipt)
    if indar_receipt.get("archive_sha256") != cfg["indar"]["archive_sha256"]:
        raise RuntimeError("Indar archive provenance mismatch")
    if indar_receipt.get("original_main_sha256") != cfg["indar"]["main_sha256"]:
        raise RuntimeError("Indar main provenance mismatch")

    api = KaggleApi()
    api.authenticate()
    source_skips = []
    benchmark_errors = []
    source_receipts = []
    scenarios = []

    with tempfile.TemporaryDirectory(prefix="cr029-stageb-") as td:
        tmp = Path(td)

        cr024_actions, cr024_provenance = build_cr024(tmp / "cr024_source")
        cr024_path = tmp / "cr024.py"
        cr024_path.write_text(runtime_source(cr024_actions, "CR024_CONTROL"), encoding="utf-8")

        recent_meta = cfg["recent_top_source"]
        recent_dir = tmp / "recent_source"
        recent_dir.mkdir(parents=True, exist_ok=True)
        api.competition_episode_replay(int(recent_meta["episode_id"]), path=str(recent_dir), quiet=True)
        recent_replay_path = recent_dir / f"episode-{int(recent_meta['episode_id'])}-replay.json"
        recent_rep = json.loads(recent_replay_path.read_text(encoding="utf-8"))
        recent_actions = actions_for(recent_rep, int(recent_meta["source_seat"]))
        if len(recent_actions) != 719:
            raise RuntimeError(f"recent source tape length {len(recent_actions)}")
        stream_verification = {}
        for raw_n, expected in recent_meta["expected_stream_hashes"].items():
            n = int(raw_n)
            observed = stream_hash(recent_actions, n)
            stream_verification[str(n)] = {
                "expected": expected,
                "observed": observed,
                "exact": observed == expected,
            }
        if not all(x["exact"] for x in stream_verification.values()):
            raise RuntimeError(f"recent source stream mismatch: {stream_verification}")
        recent_path = tmp / "full_recent_top.py"
        recent_path.write_text(runtime_source(recent_actions, "CR028_FULL_RECENT_TOP"), encoding="utf-8")

        candidates = {
            "cr024": cr024_path,
            "full_recent_top": recent_path,
            "indar_v1": indar_path,
        }
        if set(candidates) != set(cfg["candidate_ids"]):
            raise RuntimeError("candidate config mismatch")

        index_rows = read_csv(download(INDEX_HANDLE, "manifest.csv", tmp / "index"))
        if not any(r.get("date") == cfg["source_date"] for r in index_rows):
            raise RuntimeError(f"official source date absent: {cfg['source_date']}")
        handle = f"kaggle/kaggriculture-episodes-{cfg['source_date']}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", tmp / "day")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[: int(cfg["manifest_scan_limit"])]

        seen_tapes: set[str] = set()
        for rank, mr in enumerate(manifest, start=1):
            if len(scenarios) >= int(cfg["target_unique_exact_scenarios"]):
                break
            eid = str(mr["episode_id"])
            try:
                rep = json.loads(
                    download(handle, f"{eid}.json", tmp / "episodes" / eid).read_text(encoding="utf-8")
                )
                if len(rep.get("steps") or []) < 720:
                    source_skips.append({"episode_id": eid, "rank": rank, "reason": "short_source"})
                    continue
                rewards = final_rewards(rep)
                wi = winner_index(rewards)
                if wi is None:
                    source_skips.append({"episode_id": eid, "rank": rank, "reason": "tie_or_missing_reward"})
                    continue
                info = rep.get("info") or {}
                seed = int(info.get("seed"))
                original_config = rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {}
                tapes = [actions_for(rep, 0), actions_for(rep, 1)]
                if any(len(t) != 719 for t in tapes):
                    source_skips.append({"episode_id": eid, "rank": rank, "reason": "bad_tape_length"})
                    continue
                winner_tape = tapes[wi]
                wsha = tape_sha(winner_tape)
                if wsha in seen_tapes:
                    source_skips.append({"episode_id": eid, "rank": rank, "reason": "duplicate_winner_tape", "winner_tape_sha256": wsha})
                    continue
                verify_dir = tmp / "verify" / eid
                verify_dir.mkdir(parents=True, exist_ok=True)
                exact = exact_source_reproduction(tapes[0], tapes[1], seed, original_config, rewards, verify_dir)
                names = info.get("TeamNames") or ["p0", "p1"]
                receipt = {
                    "rank": rank,
                    "episode_id": eid,
                    "avg_score": float(mr.get("avg_score") or 0),
                    "seed": seed,
                    "winner_seat": wi,
                    "winner_team": names[wi] if wi < len(names) else f"p{wi}",
                    "winner_tape_sha256": wsha,
                    "original_rewards": rewards,
                    "exact_terminal_reproduction": exact,
                }
                source_receipts.append(receipt)
                if not exact:
                    source_skips.append({"episode_id": eid, "rank": rank, "reason": "non_exact_terminal_reproduction"})
                    continue
                seen_tapes.add(wsha)
                scenarios.append({
                    **receipt,
                    "winner_tape": winner_tape,
                    "configuration": original_config,
                })
            except Exception as exc:
                source_skips.append({"episode_id": eid, "rank": rank, "reason": "source_exception", "error": repr(exc)[:500]})

        if len(scenarios) < int(cfg["min_unique_exact_scenarios"]):
            raise RuntimeError(
                f"insufficient exact unique official scenarios: {len(scenarios)} < {cfg['min_unique_exact_scenarios']}"
            )

        live_rows: list[dict] = []
        for sc in scenarios:
            opp_path = tmp / f"official_winner_{sc['episode_id']}.py"
            opp_path.write_text(runtime_source(sc["winner_tape"], f"OFFICIAL_WINNER_{sc['episode_id']}"), encoding="utf-8")
            for cid in cfg["candidate_ids"]:
                for seat in (0, 1):
                    try:
                        result = play(
                            candidates[cid],
                            opp_path,
                            int(sc["seed"]),
                            seat,
                            sc["configuration"],
                        )
                        live_rows.append({
                            "candidate_id": cid,
                            "episode_id": sc["episode_id"],
                            "source_rank": sc["rank"],
                            "source_avg_score": sc["avg_score"],
                            "source_winner_tape_sha256": sc["winner_tape_sha256"],
                            "candidate_seat": seat,
                            **result,
                        })
                    except Exception as exc:
                        benchmark_errors.append({
                            "phase": "official_meta",
                            "candidate_id": cid,
                            "episode_id": sc["episode_id"],
                            "candidate_seat": seat,
                            "error": repr(exc)[:500],
                        })

        pairwise_rows: list[dict] = []
        for left, right in cfg["pairwise_pairs"]:
            for seed in fresh_seeds:
                for left_seat in (0, 1):
                    try:
                        result = play(candidates[left], candidates[right], seed, left_seat, None)
                        pairwise_rows.append({
                            "left": left,
                            "right": right,
                            "seed": seed,
                            "left_seat": left_seat,
                            **result,
                        })
                    except Exception as exc:
                        benchmark_errors.append({
                            "phase": "fresh_pairwise",
                            "left": left,
                            "right": right,
                            "seed": seed,
                            "left_seat": left_seat,
                            "error": repr(exc)[:500],
                        })

    expected_live = len(scenarios) * 2 * len(cfg["candidate_ids"])
    expected_pairwise = len(cfg["pairwise_pairs"]) * len(fresh_seeds) * 2
    mechanical = (
        len(live_rows) == expected_live
        and len(pairwise_rows) == expected_pairwise
        and not benchmark_errors
    )

    live_metrics = {}
    live_by_candidate = {
        cid: [r for r in live_rows if r["candidate_id"] == cid]
        for cid in cfg["candidate_ids"]
    }
    control_rows = live_by_candidate["cr024"]
    for cid, rows in live_by_candidate.items():
        m = summarize(rows)
        m["paired_vs_cr024"] = (
            {
                "paired_rows": len(rows),
                "score_gain": 0.0,
                "improvements": 0,
                "regressions": 0,
                "mean_delta_gain": 0.0,
                "median_delta_gain": 0.0,
                "positive_margin_rows": 0,
                "negative_margin_rows": 0,
            }
            if cid == "cr024"
            else paired_vs_control(rows, control_rows)
        )
        live_metrics[cid] = m

    pairwise_metrics = {}
    pairwise_expected_each = len(fresh_seeds) * 2
    for left, right in cfg["pairwise_pairs"]:
        rows = [r for r in pairwise_rows if r["left"] == left and r["right"] == right]
        pairwise_metrics[f"{left}__vs__{right}"] = summarize(rows)

    finalist_checks = {}
    gate = cfg["gate"]
    for cid in ("full_recent_top", "indar_v1"):
        live = live_metrics[cid]["paired_vs_cr024"]
        pkey = f"{cid}__vs__cr024"
        pm = pairwise_metrics[pkey]
        finalist_checks[cid] = {
            "mechanical": mechanical,
            "live_meta_score_gain": mechanical and live["score_gain"] >= float(gate["live_meta_min_score_gain_vs_cr024"]),
            "live_meta_regressions": mechanical and live["regressions"] <= int(gate["live_meta_max_regressions_vs_cr024"]),
            "fresh_pairwise_vs_cr024": mechanical and pm["games"] == pairwise_expected_each and pm["score_total"] >= float(gate["fresh_pairwise_min_score_vs_cr024"]),
        }
        finalist_checks[cid]["passed"] = all(finalist_checks[cid].values())

    h2h = pairwise_metrics["indar_v1__vs__full_recent_top"]
    h2h_score = {
        "indar_v1": float(h2h["score_total"]),
        "full_recent_top": float(h2h["games"]) - float(h2h["score_total"]),
    }

    passing = [cid for cid in ("full_recent_top", "indar_v1") if finalist_checks[cid]["passed"]]

    def rank_key(cid: str):
        live = live_metrics[cid]
        paired = live["paired_vs_cr024"]
        direct = pairwise_metrics[f"{cid}__vs__cr024"]
        return (
            float(paired["score_gain"]),
            -int(paired["regressions"]),
            float(live["score_total"]),
            float(direct["score_total"]),
            float(h2h_score[cid]),
            float(paired["mean_delta_gain"]),
        )

    ranking = sorted(passing, key=rank_key, reverse=True)
    selected = ranking[0] if ranking else None
    decision = (
        f"SHORTLIST_{selected.upper()}_FOR_KAGGLE_PACKAGE_PREFLIGHT"
        if selected
        else "NO_STAGEB_PROMOTION__KEEP_CR024_AND_RESEARCH"
    )

    report = {
        "experiment": cfg["experiment"],
        "source_date": cfg["source_date"],
        "source_unique_exact_scenarios": len(scenarios),
        "source_receipts": source_receipts,
        "source_skips": source_skips,
        "recent_top_stream_verification": stream_verification,
        "recent_top_tape_sha256": tape_sha(recent_actions),
        "cr024_provenance": cr024_provenance,
        "indar_receipt": indar_receipt,
        "fresh_pairwise_seeds": fresh_seeds,
        "seed_firewall_forbidden_count": len(forbidden),
        "expected_live_rows": expected_live,
        "completed_live_rows": len(live_rows),
        "expected_pairwise_rows": expected_pairwise,
        "completed_pairwise_rows": len(pairwise_rows),
        "benchmark_errors": benchmark_errors,
        "mechanical_complete": mechanical,
        "live_metrics": live_metrics,
        "pairwise_metrics": pairwise_metrics,
        "finalist_checks": finalist_checks,
        "passing_finalists": passing,
        "ranking": ranking,
        "selected_for_next_stage": selected,
        "decision": decision,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
        "runtime_identity_features": False,
        "live_rows": live_rows,
        "pairwise_rows": pairwise_rows,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    compact = {
        k: v
        for k, v in report.items()
        if k not in ("live_rows", "pairwise_rows", "source_receipts", "source_skips", "indar_receipt")
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
