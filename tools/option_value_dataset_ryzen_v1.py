#!/usr/bin/env python3
"""Ryzen-scale resumable option-value dataset generator for V47 option library V0.

Each process owns complete seeds and writes one shard per seed. The model-facing feature
contract is imported from the already-passed V0 pilot; opponent/seed/seat remain metadata
only. This tool never submits to Kaggle.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.option_value_dataset_v0_pilot import (
    BASE,
    EXPECTED_ENGINE,
    MODEL_FEATURE_NAMES,
    OPPONENTS,
    acquire,
    purge,
    run_episode,
)

DEFAULT_OPPONENTS = tuple(x["key"] for x in OPPONENTS)


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _stable_json_hash(obj) -> str:
    import hashlib
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _write_json_atomic(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _make_seeds(count: int, master_seed: int) -> list[int]:
    rng = random.Random(int(master_seed))
    out = set()
    while len(out) < int(count):
        x = rng.randint(1, 2_147_483_646)
        # Keep away from explicitly frozen pilot/runtime ranges.
        if 64000 <= x <= 69999:
            continue
        out.add(x)
    return sorted(out)


def _source_manifest(run_dir: Path, selected_opponents: tuple[str, ...]) -> dict:
    sources = run_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    provenance = {}

    base_main, rec = acquire(BASE, sources / "base")
    provenance["base"] = rec
    paths = {"base": str(base_main.resolve())}

    specs = {x["key"]: x for x in OPPONENTS}
    for key in selected_opponents:
        spec = specs[key]
        if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
            paths[key] = str(base_main.resolve())
            provenance[key] = {
                **rec,
                "key": key,
                "role": "opponent",
                "reused_exact_base_bytes": True,
            }
        else:
            p, orec = acquire(spec, sources / f"opp_{key}")
            paths[key] = str(p.resolve())
            provenance[key] = orec

    return {"paths": paths, "provenance": provenance}


def _run_seed(job: dict) -> dict:
    seed = int(job["seed"])
    base_main = Path(job["paths"]["base"])
    selected_opponents = tuple(job["opponents"])
    seats = tuple(int(x) for x in job["seats"])
    paths = {k: Path(v) for k, v in job["paths"].items()}
    rows = []
    matchups = []
    failures = []

    for opp_key in selected_opponents:
        opp_main = paths[opp_key]
        all_paths = [base_main, opp_main]
        for seat in seats:
            key = {"opponent": opp_key, "seed": seed, "seat": seat}
            try:
                purge(all_paths)
                d = run_episode(
                    base_main, opp_main, seed=seed, seat=seat, mode="discovery"
                )
                if d.get("entrypoint") != "_y_agent_shopherd":
                    raise RuntimeError(
                        f"discovery entrypoint mismatch: {d.get('entrypoint')}"
                    )

                purge(all_paths)
                b = run_episode(
                    base_main, opp_main, seed=seed, seat=seat, mode="base"
                )
                if d["rewards"] != b["rewards"]:
                    raise RuntimeError(
                        f"discovery/base replay mismatch {d['rewards']} != {b['rewards']}"
                    )

                matchup = {
                    **key,
                    "base_rewards": b["rewards"],
                    "base_score": b["score"],
                    "base_margin": b["margin"],
                    "options_found": sorted(d["events"].keys()),
                    "replay_parity": True,
                }

                for option_id, event in sorted(d["events"].items()):
                    purge(all_paths)
                    tr = run_episode(
                        base_main,
                        opp_main,
                        seed=seed,
                        seat=seat,
                        mode="treatment",
                        event=event,
                    )
                    feats = event["features"]
                    if tuple(feats.keys()) != MODEL_FEATURE_NAMES:
                        raise RuntimeError("feature contract changed inside worker")
                    rows.append({
                        "state_hash": event["state_hash"],
                        "option_id": option_id,
                        "features": feats,
                        "base_action_key": event["base_action_key"],
                        "step": int(event["step"]),
                        "base_score": float(b["score"]),
                        "option_score": float(tr["score"]),
                        "score_delta": float(tr["score"] - b["score"]),
                        "base_margin": float(b["margin"]),
                        "option_margin": float(tr["margin"]),
                        "margin_delta": float(tr["margin"] - b["margin"]),
                        "metadata": {
                            "opponent": opp_key,
                            "seed": seed,
                            "seat": seat,
                        },
                    })

                matchups.append(matchup)
            except Exception as exc:
                failures.append({**key, "error": f"{type(exc).__name__}: {exc}"})
            finally:
                purge(all_paths)

    return {
        "seed": seed,
        "rows": rows,
        "matchups": matchups,
        "failures": failures,
    }


def _aggregate(out_dir: Path, manifest: dict) -> dict:
    rows = []
    matchups = []
    failures = []
    completed_seeds = 0

    for path in sorted((out_dir / "shards").glob("seed_*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        completed_seeds += 1
        rows.extend(d.get("rows", []))
        matchups.extend(d.get("matchups", []))
        failures.extend(d.get("failures", []))

    by_option = {}
    for option_id in ("O-RW1", "O-TW1"):
        rr = [r for r in rows if r.get("option_id") == option_id]
        by_option[option_id] = {
            "rows": len(rr),
            "positive_score_delta": sum(float(r["score_delta"]) > 0 for r in rr),
            "negative_score_delta": sum(float(r["score_delta"]) < 0 for r in rr),
            "neutral_score_delta": sum(float(r["score_delta"]) == 0 for r in rr),
            "mean_score_delta": (
                mean(float(r["score_delta"]) for r in rr) if rr else None
            ),
            "mean_margin_delta": (
                mean(float(r["margin_delta"]) for r in rr) if rr else None
            ),
            "unique_state_hashes": len({r["state_hash"] for r in rr}),
        }

    by_opponent = {}
    for key in manifest["opponents"]:
        rr = [r for r in rows if r["metadata"]["opponent"] == key]
        by_opponent[key] = {
            "rows": len(rr),
            "mean_score_delta": (
                mean(float(r["score_delta"]) for r in rr) if rr else None
            ),
            "positive_score_delta": sum(float(r["score_delta"]) > 0 for r in rr),
            "negative_score_delta": sum(float(r["score_delta"]) < 0 for r in rr),
        }

    summary = {
        "schema": "kculture-option-value-dataset-ryzen-v1-summary",
        "manifest": manifest,
        "completed_seeds": completed_seeds,
        "matchups": len(matchups),
        "rows": len(rows),
        "unique_state_hashes": len({r["state_hash"] for r in rows}),
        "rows_by_option": by_option,
        "rows_by_opponent": by_opponent,
        "failures": failures,
        "mechanical_pass": not failures,
    }
    _write_json_atomic(out_dir / "SUMMARY.json", summary)

    # Compact training JSONL: metadata remains present for split/audit, never a feature.
    jsonl_tmp = out_dir / "TRAINING_ROWS.jsonl.tmp"
    with jsonl_tmp.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    jsonl_tmp.replace(out_dir / "TRAINING_ROWS.jsonl")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/option_value_v1_250")
    ap.add_argument("--seed-count", type=int, default=250)
    ap.add_argument("--master-seed", type=int, default=26091802)
    ap.add_argument(
        "--opponents",
        default=",".join(DEFAULT_OPPONENTS),
        help="comma-separated keys from the frozen public opponent league",
    )
    ap.add_argument("--seats", default="0,1")
    ap.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 8) - 2),
    )
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"engine mismatch: {getattr(kaggle_environments,'__version__',None)}"
        )

    selected_opponents = tuple(
        x.strip() for x in args.opponents.split(",") if x.strip()
    )
    unknown = sorted(set(selected_opponents) - set(DEFAULT_OPPONENTS))
    if unknown:
        raise SystemExit(f"unknown opponents: {unknown}")
    seats = tuple(int(x.strip()) for x in args.seats.split(",") if x.strip())
    if not seats or any(x not in (0, 1) for x in seats):
        raise SystemExit(f"invalid seats: {seats}")

    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    shards = out_dir / "shards"
    shards.mkdir(parents=True, exist_ok=True)

    sources = _source_manifest(out_dir, selected_opponents)
    seeds = _make_seeds(args.seed_count, args.master_seed)
    manifest = {
        "schema": "kculture-option-value-dataset-ryzen-v1-manifest",
        "source_commit": _git_head(),
        "engine": EXPECTED_ENGINE,
        "seed_count": int(args.seed_count),
        "master_seed": int(args.master_seed),
        "opponents": list(selected_opponents),
        "seats": list(seats),
        "options": ["O-RW1", "O-TW1"],
        "model_feature_names": list(MODEL_FEATURE_NAMES),
        "hosted_entrypoint": "_y_agent_shopherd",
        "provenance": sources["provenance"],
    }
    manifest["config_sha256"] = _stable_json_hash(manifest)

    manifest_path = out_dir / "MANIFEST.json"
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old.get("config_sha256") != manifest["config_sha256"]:
            raise SystemExit(
                f"refusing to mix incompatible configs in {out_dir}; choose another --out"
            )
    else:
        _write_json_atomic(manifest_path, manifest)

    pending = [s for s in seeds if not (shards / f"seed_{s}.json").exists()]
    done_before = len(seeds) - len(pending)
    print(
        "OPTION_VALUE_RYZEN_START",
        json.dumps({
            "seed_count": len(seeds),
            "resume_done": done_before,
            "pending": len(pending),
            "workers": int(args.workers),
            "opponents": selected_opponents,
            "seats": seats,
            "max_rows": len(seeds) * len(selected_opponents) * len(seats) * 2,
            "out": str(out_dir),
        }, sort_keys=True),
        flush=True,
    )

    start = time.time()
    if pending:
        common = {
            "paths": sources["paths"],
            "opponents": selected_opponents,
            "seats": seats,
        }
        with ProcessPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
            futs = {
                ex.submit(_run_seed, {"seed": s, **common}): s
                for s in pending
            }
            completed = done_before
            for fut in as_completed(futs):
                seed = futs[fut]
                try:
                    result = fut.result()
                except Exception as exc:
                    result = {
                        "seed": seed,
                        "rows": [],
                        "matchups": [],
                        "failures": [{"seed": seed, "exception": repr(exc)}],
                    }
                _write_json_atomic(shards / f"seed_{seed}.json", result)
                completed += 1
                if completed % 5 == 0 or completed == len(seeds):
                    elapsed = max(1.0, time.time() - start)
                    rate = max(0.0, (completed - done_before) / elapsed)
                    rows_so_far = sum(
                        len(json.loads(p.read_text(encoding="utf-8")).get("rows", []))
                        for p in shards.glob("seed_*.json")
                    )
                    print(
                        "OPTION_VALUE_RYZEN_PROGRESS",
                        json.dumps({
                            "seeds": f"{completed}/{len(seeds)}",
                            "new_seed_rate_per_s": rate,
                            "rows_so_far": rows_so_far,
                        }, sort_keys=True),
                        flush=True,
                    )

    summary = _aggregate(out_dir, manifest)
    print(
        "OPTION_VALUE_RYZEN_DONE",
        json.dumps({
            "completed_seeds": summary["completed_seeds"],
            "rows": summary["rows"],
            "unique_state_hashes": summary["unique_state_hashes"],
            "failures": len(summary["failures"]),
            "rows_by_option": summary["rows_by_option"],
            "out": str(out_dir),
        }, sort_keys=True),
        flush=True,
    )
    if summary["failures"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
