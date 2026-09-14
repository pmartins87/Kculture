"""CR088 Phase 0: deterministic population screen for current top replay tapes.

Public replay actions seed a diverse population.  Local H2H is used only for
mechanical/catastrophe screening because the exact hosted-byte league does not
reproduce hosted rating order.  This tool never submits to Kaggle.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import statistics
import tarfile
from pathlib import Path


PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_deterministic_tar(path: Path, members: list[tuple[str, bytes]]) -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name, data in sorted(members):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def runtime_source(tape: list[dict]) -> str:
    tape_json = canonical_bytes(tape).decode()
    return f'''"""CR088 Phase-0 replay-tape seed; public actions, no runtime identity."""
import copy as _copy
import json as _json

_TAPE = _json.loads({tape_json!r})

def _clock(obs):
    try:
        raw = obs.get("step")
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    try:
        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))
    except Exception:
        return 0

def agent(obs, config=None):
    step = max(0, min(718, _clock(obs)))
    return _copy.deepcopy(_TAPE[step])
'''


def load_meta(path: Path) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise RuntimeError("episodes metadata must be a list")
    return rows


def tape_filename(row: dict) -> str:
    return f"episode_{int(row['episode_id'])}_sid_{int(row['submission_id'])}.json"


def candidate_id(row: dict) -> str:
    return f"r{int(row['leaderboard_rank']):02d}_e{int(row['episode_id'])}_s{int(row['submission_id'])}"


def matrix_cmd(args) -> None:
    rows = load_meta(Path(args.metadata))
    tapes_dir = Path(args.tapes_dir)
    include = []
    for row in sorted(rows, key=lambda x: (int(x["leaderboard_rank"]), int(x["episode_id"]))):
        name = tape_filename(row)
        path = tapes_dir / name
        if not path.is_file():
            raise RuntimeError(f"missing tape {path}")
        tape = json.loads(path.read_text(encoding="utf-8"))
        observed = sha256(canonical_bytes(tape))
        if len(tape) != 719 or observed != row.get("tape_sha256"):
            raise RuntimeError(f"tape identity mismatch {name}: {len(tape)} {observed}")
        include.append({
            "candidate_id": candidate_id(row),
            "tape_file": name,
            "episode_id": int(row["episode_id"]),
            "submission_id": int(row["submission_id"]),
            "team_name": str(row["team_name"]),
            "source_rank": int(row["leaderboard_rank"]),
            "source_score": float(row["leaderboard_score"]),
            "tape_sha256": observed,
        })
    if len(include) != 30:
        raise RuntimeError(f"expected frozen 30-tape population, found {len(include)}")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"include": include}, separators=(",", ":"), sort_keys=True))
    print(json.dumps({"population": len(include), "unique_teams": len({x['team_name'] for x in include})}, sort_keys=True))


def build_cmd(args) -> None:
    rows = load_meta(Path(args.metadata))
    target = next(
        (r for r in rows if int(r["episode_id"]) == int(args.episode_id) and int(r["submission_id"]) == int(args.submission_id)),
        None,
    )
    if target is None:
        raise RuntimeError("candidate absent from frozen metadata")
    tape = json.loads(Path(args.tape).read_text(encoding="utf-8"))
    tape_sha = sha256(canonical_bytes(tape))
    if len(tape) != 719 or tape_sha != target.get("tape_sha256"):
        raise RuntimeError("frozen tape identity mismatch")
    source = runtime_source(tape).encode()
    provenance = (
        "CR088 Phase 0 public replay action-tape seed.\n"
        f"source episode={int(target['episode_id'])} submission={int(target['submission_id'])} "
        f"team={target['team_name']} rank={int(target['leaderboard_rank'])}\n"
        f"tape_sha256={tape_sha}\n"
        "Source identifiers are provenance only and are not runtime features.\n"
    ).encode()
    out = Path(args.output)
    write_deterministic_tar(out, [("main.py", source), ("CR088_PROVENANCE.txt", provenance)])
    first = out.read_bytes()
    rebuild = out.with_suffix(out.suffix + ".rebuild")
    write_deterministic_tar(rebuild, [("main.py", source), ("CR088_PROVENANCE.txt", provenance)])
    if first != rebuild.read_bytes():
        raise RuntimeError("non-deterministic package build")
    rebuild.unlink()
    manifest = {
        "schema": "cr088-top-tape-population-seed-v1",
        "candidate_id": candidate_id(target),
        "episode_id": int(target["episode_id"]),
        "submission_id_provenance_only": int(target["submission_id"]),
        "team_name_provenance_only": str(target["team_name"]),
        "source_rank_context_only": int(target["leaderboard_rank"]),
        "source_score_context_only": float(target["leaderboard_score"]),
        "tape_sha256": tape_sha,
        "archive_sha256": sha256(first),
        "action_count": 719,
        "runtime_identity_features": False,
        "runtime_network": False,
        "automatic_submission": False,
        "held_out_touched": False,
    }
    mp = Path(args.manifest)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(manifest, indent=2, sort_keys=True))


def collect_cmd(args) -> None:
    root = Path(args.result_dir)
    manifest = json.loads(Path(args.manifest).read_text())
    anchors = {}
    errors = 0
    non_done = 0
    seat_rates = []
    for path in sorted(root.glob("vs_*.json")):
        data = json.loads(path.read_text())
        metric = data["metrics_a_vs_b"]
        anchor = str(data["b"])
        score_rate = 0.0 if metric.get("score_rate") is None else float(metric["score_rate"])
        anchors[anchor] = {
            "games": int(metric["games"]),
            "wins": int(metric["wins"]),
            "losses": int(metric["losses"]),
            "ties": int(metric["ties"]),
            "score_rate": score_rate,
            "mean_margin": metric["mean_margin_secondary"],
        }
        errors += len(data.get("errors") or [])
        non_done += int(metric.get("non_done_games") or 0)
        seat_rates.extend(0.0 if v.get("score_rate") is None else float(v["score_rate"]) for v in data["metrics_by_a_seat"].values())
    expected = {"CR053_REAL", "CR052_REAL", "CR083", "CR086"}
    if set(anchors) != expected:
        raise RuntimeError(f"anchor set mismatch: {sorted(anchors)}")
    scores = [x["score_rate"] for x in anchors.values()]
    mean_score = statistics.mean(scores)
    worst_score = min(scores)
    seat_floor = min(seat_rates)
    robust_score = 0.50 * mean_score + 0.35 * worst_score + 0.15 * seat_floor
    out = {
        "schema": "cr088-top-tape-phase0-result-v1",
        **manifest,
        "anchors": anchors,
        "errors": errors,
        "non_done_games": non_done,
        "mean_anchor_score": mean_score,
        "worst_anchor_score": worst_score,
        "seat_floor_score": seat_floor,
        "robust_local_safety_score": robust_score,
        "mechanically_valid": errors == 0 and non_done == 0 and all(x["games"] == 6 for x in anchors.values()),
        "interpretation_limit": "local safety/diversity only; not a hosted-rating predictor",
    }
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))


def aggregate_cmd(args) -> None:
    rows = [json.loads(p.read_text()) for p in Path(args.input_dir).glob("**/candidate-summary.json")]
    if len(rows) != 30:
        raise RuntimeError(f"expected 30 candidate summaries, found {len(rows)}")
    valid = [r for r in rows if r["mechanically_valid"]]
    ranked = sorted(valid, key=lambda r: (r["robust_local_safety_score"], r["mean_anchor_score"], -r["source_rank_context_only"]), reverse=True)
    per_team = {}
    for row in ranked:
        team = row["team_name_provenance_only"]
        per_team.setdefault(team, row)
    hosted_prior = sorted(per_team.values(), key=lambda r: (r["source_rank_context_only"], -r["robust_local_safety_score"]))
    top_local = ranked[:10]
    out = {
        "schema": "cr088-top-tape-population-phase0-aggregate-v1",
        "population": len(rows),
        "mechanically_valid": len(valid),
        "mechanical_failures": len(rows) - len(valid),
        "anchors": ["CR053_REAL", "CR052_REAL", "CR083", "CR086"],
        "master_seed": 9220881,
        "seeds_per_anchor": 3,
        "hosted_order_reproduced_locally": False,
        "top_local_safety": [compact(r) for r in top_local],
        "best_valid_seed_per_source_team_in_hosted_rank_order": [compact(r) for r in hosted_prior],
        "decision": "PHASE0_COMPLETE_BUILD_DIVERSE_STATE_COHERENT_PHASE1",
        "automatic_submission": False,
        "held_out_touched": False,
        "warning": "Do not promote the highest local score directly; retain source-team/macro diversity and use Kaggle hosted probes for transfer.",
    }
    op = Path(args.output)
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))


def compact(r: dict) -> dict:
    return {
        "candidate_id": r["candidate_id"],
        "team": r["team_name_provenance_only"],
        "source_rank": r["source_rank_context_only"],
        "source_score": r["source_score_context_only"],
        "tape_sha256": r["tape_sha256"],
        "robust_local_safety_score": r["robust_local_safety_score"],
        "mean_anchor_score": r["mean_anchor_score"],
        "worst_anchor_score": r["worst_anchor_score"],
        "seat_floor_score": r["seat_floor_score"],
        "anchor_scores": {k: v["score_rate"] for k, v in sorted(r["anchors"].items())},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("matrix")
    m.add_argument("--metadata", required=True); m.add_argument("--tapes-dir", required=True); m.add_argument("--output", required=True)
    b = sub.add_parser("build")
    b.add_argument("--metadata", required=True); b.add_argument("--tape", required=True); b.add_argument("--episode-id", required=True, type=int); b.add_argument("--submission-id", required=True, type=int); b.add_argument("--output", required=True); b.add_argument("--manifest", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--result-dir", required=True); c.add_argument("--manifest", required=True); c.add_argument("--output", required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--input-dir", required=True); a.add_argument("--output", required=True)
    args = ap.parse_args()
    {"matrix": matrix_cmd, "build": build_cmd, "collect": collect_cmd, "aggregate": aggregate_cmd}[args.cmd](args)


if __name__ == "__main__":
    main()
