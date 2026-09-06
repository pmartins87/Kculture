"""CR030: screen lineage-diverse complete current-meta policies vs full_recent_top.

Candidate selection is frozen by config before outcomes. Complete 719-action
policies only; no splicing, blending, identity-aware runtime logic, or sealed
final stress data.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import tempfile
from pathlib import Path

import kagglehub
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "configs/cr030_diverse_complete_screen.json"
DATA_ROOT = ROOT / "artifacts/cr030_diverse/data"
OUT = ROOT / "artifacts/cr030_diverse/report.json"


def dl(dataset: str, name: str, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(dataset, path=name, output_dir=str(root), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def norm_id(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def canonical(action: dict) -> bytes:
    return json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stream_hash(actions: list[dict], n: int) -> str:
    return hashlib.sha256(b"".join(canonical(a) + b"\0" for a in actions[:n])).hexdigest()[:16]


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def collect_ints(obj) -> set[int]:
    out: set[int] = set()
    if isinstance(obj, bool):
        return out
    if isinstance(obj, int):
        out.add(obj)
    elif isinstance(obj, float) and obj.is_integer():
        out.add(int(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            out |= collect_ints(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= collect_ints(v)
    return out


def seed_firewall(seeds: list[int]) -> dict:
    forbidden: set[int] = set()
    files = []
    for p in sorted((ROOT / "configs").glob("*.json")):
        if p.resolve() == CFG_PATH.resolve():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        vals = collect_ints(data)
        forbidden |= vals
        files.append({"path": str(p.relative_to(ROOT)), "ints": len(vals)})
    overlap = sorted(set(seeds) & forbidden)
    if overlap:
        raise RuntimeError(f"CR030 seed firewall violation: {overlap}")
    return {"forbidden_int_count": len(forbidden), "scanned_configs": len(files), "overlap": overlap}


def actions_for(replay: dict, seat: int) -> list[dict]:
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay: {len(steps)}")
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or {}) for t in range(719)]


def tape_agent(tape: list[dict]):
    def agent(obs, config=None):
        try:
            raw = obs.get("step")
            step = int(raw) if raw is not None else int(obs.get("day") or 0) * 24 + int(obs.get("hour") or 0)
        except Exception:
            step = 0
        return copy.deepcopy(tape[max(0, min(718, step))])
    return agent


def play(candidate: list[dict], champion: list[dict], seed: int, candidate_seat: int) -> dict:
    ca = tape_agent(candidate)
    ch = tape_agent(champion)
    agents = [ca, ch] if candidate_seat == 0 else [ch, ca]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
    env.run(agents)
    final = env.toJSON()["steps"][-1]
    statuses = [final[i].get("status") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses {statuses}")
    own = float(final[candidate_seat].get("reward"))
    opp = float(final[1 - candidate_seat].get("reward"))
    delta = own - opp
    score = 1.0 if delta > 0 else 0.5 if delta == 0 else 0.0
    return {"seed": int(seed), "candidate_seat": candidate_seat, "self_reward": own, "champion_reward": opp, "delta": delta, "score": score}


def main() -> None:
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    seeds = [int(x) for x in cfg["fresh_development_seeds"]]
    firewall = seed_firewall(seeds)
    dataset = cfg["dataset"]

    ep = pd.read_csv(dl(dataset, "episodes.csv", DATA_ROOT))
    sh = pd.read_csv(dl(dataset, "stream_hashes.csv", DATA_ROOT))
    ft = pd.read_csv(dl(dataset, "episode_features.csv", DATA_ROOT))

    seats = pd.concat([
        ep[["episode_id", f"sub_{s}", f"team_{s}", f"rating_{s}", "end_time"]]
          .rename(columns={f"sub_{s}": "submission_id", f"team_{s}": "team", f"rating_{s}": "rating"})
          .assign(seat=s)
        for s in (0, 1)
    ], ignore_index=True)
    eng = ft[["episode_id", "seat", "engine_version"]].copy()
    for d in (seats, sh, eng):
        d["episode_id"] = norm_id(d["episode_id"])
        d["seat"] = pd.to_numeric(d["seat"], errors="coerce").astype("Int64")
    seats["submission_id"] = norm_id(seats["submission_id"])
    seats["rating"] = pd.to_numeric(seats["rating"], errors="coerce")
    seats["end_time"] = pd.to_datetime(seats["end_time"], errors="coerce", utc=True)
    eng["engine_version"] = eng["engine_version"].astype(str)

    x = seats.merge(eng, on=["episode_id", "seat"], how="inner").merge(sh, on=["episode_id", "seat"], how="left")
    x = x[(x["engine_version"] == str(cfg["engine_version"])) & x["rating"].notna() & x["end_time"].notna()].copy()
    if x.empty:
        raise RuntimeError("no current-engine rated rows")
    max_time = x["end_time"].max()
    cutoff = max_time - pd.Timedelta(days=int(cfg["recent_days_from_dataset_max"]))
    x = x[x["end_time"] >= cutoff].copy()
    x = x[x["stream_h200"].notna() & x["stream_h719"].notna()].copy()
    champ_h200 = str(cfg["champion"]["stream_h200"])
    champ_h719 = str(cfg["champion"]["stream_h719"])
    x = x[(x["stream_h200"].astype(str) != champ_h200) & (x["stream_h719"].astype(str) != champ_h719)]
    x = x.sort_values(["rating", "end_time"], ascending=[False, False])

    # Build a larger frozen-ranked pool, then validate exact source tapes in that
    # order until max_candidates mechanically valid lineage-diverse policies exist.
    pool = []
    seen_sub: set[str] = set()
    seen_team: set[str] = set()
    seen_h200: set[str] = set()
    seen_h719: set[str] = set()
    for _, r in x.iterrows():
        sub = str(r["submission_id"]); team = str(r["team"])
        h200 = str(r["stream_h200"]); h719 = str(r["stream_h719"])
        if sub in seen_sub or team in seen_team or h200 in seen_h200 or h719 in seen_h719:
            continue
        if not sub or sub == "nan" or not team or team == "nan":
            continue
        pool.append({
            "episode_id": int(str(r["episode_id"])), "seat": int(r["seat"]),
            "submission_id": sub, "team": team, "rating": float(r["rating"]),
            "end_time": r["end_time"].isoformat(), "stream_h200": h200, "stream_h719": h719,
        })
        seen_sub.add(sub); seen_team.add(team); seen_h200.add(h200); seen_h719.add(h719)
        if len(pool) >= 30:
            break

    api = KaggleApi(); api.authenticate()
    source_errors = []
    selected = []
    tapes: dict[str, list[dict]] = {}
    champion = cfg["champion"]

    with tempfile.TemporaryDirectory(prefix="cr030-diverse-") as td_raw:
        td = Path(td_raw)
        champ_episode = int(champion["episode_id"])
        api.competition_episode_replay(champ_episode, path=str(td), quiet=True)
        champ_replay = json.loads((td / f"episode-{champ_episode}-replay.json").read_text(encoding="utf-8"))
        champion_tape = actions_for(champ_replay, int(champion["source_seat"]))
        if tape_sha(champion_tape) != champion["tape_sha256"]:
            raise RuntimeError("champion source tape SHA mismatch")
        if stream_hash(champion_tape, 200) != champ_h200 or stream_hash(champion_tape, 719) != champ_h719:
            raise RuntimeError("champion stream identity mismatch")

        for meta in pool:
            if len(selected) >= int(cfg["max_candidates"]):
                break
            try:
                eid = int(meta["episode_id"])
                api.competition_episode_replay(eid, path=str(td), quiet=True)
                p = td / f"episode-{eid}-replay.json"
                replay = json.loads(p.read_text(encoding="utf-8"))
                tape = actions_for(replay, int(meta["seat"]))
                observed_h200 = stream_hash(tape, 200)
                observed_h719 = stream_hash(tape, 719)
                if observed_h200 != meta["stream_h200"] or observed_h719 != meta["stream_h719"]:
                    raise RuntimeError(f"stream mismatch h200={observed_h200} h719={observed_h719}")
                cid = f"c{len(selected)+1:02d}_e{eid}_s{meta['seat']}"
                enriched = dict(meta)
                enriched.update({"candidate_id": cid, "tape_sha256": tape_sha(tape), "action_count": len(tape)})
                selected.append(enriched)
                tapes[cid] = tape
            except Exception as exc:
                source_errors.append({"meta": meta, "error": repr(exc)})

        if len(selected) < min(4, int(cfg["max_candidates"])):
            raise RuntimeError(f"too few valid CR030 candidates: {len(selected)}")

        rows = []
        play_errors = []
        metrics = {}
        for meta in selected:
            cid = meta["candidate_id"]
            cr = []
            for seed in seeds:
                for seat in (0, 1):
                    try:
                        row = play(tapes[cid], champion_tape, seed, seat)
                        row["candidate_id"] = cid
                        cr.append(row); rows.append(row)
                    except Exception as exc:
                        play_errors.append({"candidate_id": cid, "seed": seed, "seat": seat, "error": repr(exc)})
            score = sum(r["score"] for r in cr)
            deltas = [r["delta"] for r in cr]
            metrics[cid] = {
                "games": len(cr), "score_total": score,
                "wins": sum(1 for r in cr if r["score"] == 1.0),
                "ties": sum(1 for r in cr if r["score"] == 0.5),
                "losses": sum(1 for r in cr if r["score"] == 0.0),
                "mean_delta": sum(deltas) / len(deltas) if deltas else math.nan,
                "source_rating": meta["rating"], "source_end_time": meta["end_time"],
                "stream_h200": meta["stream_h200"], "stream_h719": meta["stream_h719"],
            }

    expected_per = len(seeds) * 2
    valid_ids = [m["candidate_id"] for m in selected if metrics[m["candidate_id"]]["games"] == expected_per]
    ranking = sorted(valid_ids, key=lambda cid: (
        metrics[cid]["score_total"], metrics[cid]["mean_delta"], metrics[cid]["source_rating"], metrics[cid]["source_end_time"]
    ), reverse=True)
    shortlist = ranking[:3]
    strong = [cid for cid in ranking if metrics[cid]["score_total"] >= 5.0]
    mechanical = not play_errors and all(metrics[cid]["games"] == expected_per for cid in valid_ids) and len(valid_ids) >= 4

    report = {
        "experiment": cfg["experiment"],
        "engine_version": cfg["engine_version"],
        "dataset_max_end_time": max_time.isoformat(), "recent_cutoff": cutoff.isoformat(),
        "seed_firewall": firewall, "fresh_development_seeds": seeds,
        "champion": champion, "candidate_pool_preview": pool[:12],
        "selected_candidates": selected, "source_error_count": len(source_errors), "source_errors": source_errors,
        "row_count": len(rows), "expected_rows": len(selected) * expected_per,
        "play_error_count": len(play_errors), "play_errors": play_errors,
        "metrics": metrics, "ranking": ranking, "shortlist_top3": shortlist, "strong_challengers": strong,
        "mechanical_complete": mechanical, "held_out_touched": False, "runtime_identity_features": False,
        "automatic_kaggle_submission": False,
        "decision": "SHORTLIST_FOR_CR030_STAGE_B" if mechanical and shortlist else "CR030_MECHANICAL_FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "decision": report["decision"], "selected_candidates": selected,
        "metrics": metrics, "ranking": ranking, "shortlist_top3": shortlist,
        "strong_challengers": strong, "play_errors": play_errors,
        "source_errors": source_errors,
    }, indent=2, sort_keys=True))
    if not mechanical:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
