#!/usr/bin/env python3
"""Adaptive-expert gate for the frozen programme router.

Third-party public agents are downloaded transiently from Kaggle and used only as
opponents/benchmarks. Their source is never written back to this repository or uploaded
as a workflow artifact. The gate is fail-closed on source identity, runtime errors, or
incomplete episodes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import statistics
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import kagglehub
import numpy as np
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from solver.programme_router import ProgrammeRouter
from tools.build_public_programme_corpus_v1 import encode_tape, json_blobs, reconstruct_routes

EXPECTED_ENGINE = "1.32.7"
EXPERTS = [
    {
        "key": "modern_v47",
        "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
        "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
        "family": "modern41",
    },
    {
        "key": "legacy_v39",
        "handle": "ahmedberatozer/kaggriculture-v39-ready-before-the-rush",
        "expected_main_sha256": "708c7485fa964853b193f175dcd83020602c005e159ce82e38dc350b22e970c8",
        "family": "legacy13",
    },
]
SEEDS = list(range(61001, 61017))
PROMOTE_MIN_SCORE_DELTA = 0.0625
MAX_BLOCK_REGRESSION = 0.03125


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_extract(tf: tarfile.TarFile, dst: Path) -> None:
    base = dst.resolve()
    for member in tf.getmembers():
        target = (dst / member.name).resolve()
        if target != base and base not in target.parents:
            raise RuntimeError(f"unsafe archive member: {member.name}")
    tf.extractall(dst)


def find_public_package(handle: str, out: Path) -> tuple[Path, dict]:
    out.mkdir(parents=True, exist_ok=True)
    kagglehub.notebook_output_download(handle, output_dir=str(out), force_download=True)
    rows = []
    for p in sorted(out.rglob("*")):
        if not p.is_file() or not p.name.lower().endswith((".tar.gz", ".tgz", ".tar")):
            continue
        try:
            with tarfile.open(p, "r:*") as tf:
                names = sorted(m.name for m in tf.getmembers() if m.isfile())
        except Exception:
            continue
        if "main.py" in names:
            rows.append((p, names, sha256_bytes(p.read_bytes())))
    unique = {}
    for row in rows:
        unique.setdefault(row[2], row)
    if len(unique) != 1:
        raise RuntimeError(f"expected one unique root-main package for {handle}; got {[(x[0].name,x[2]) for x in rows]}")
    p, names, ah = next(iter(unique.values()))
    return p, {"archive_sha256": ah, "archive_bytes": p.stat().st_size, "members": names}


def unpack_package(archive: Path, dst: Path) -> Path:
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as tf:
        safe_extract(tf, dst)
    main = dst / "main.py"
    if not main.is_file():
        raise RuntimeError(f"root main.py absent after extract: {archive}")
    return main


def recover_modern_tapes(main_py: Path) -> np.ndarray:
    src = main_py.read_bytes()
    banks = []
    for _enc, _comp, obj, _objsha in json_blobs(src):
        if isinstance(obj, dict) and set(obj) >= {"actions", "routes", "shops"}:
            rr = reconstruct_routes(obj)
            if len(rr) == 41:
                banks.append(rr)
    if len(banks) != 1:
        raise RuntimeError(f"expected exactly one 41-route modern bank, found {len(banks)}")
    rr = banks[0]
    names = [name for name, _ in rr]
    expected = [f"route_{i}" for i in range(41)]
    if names != expected:
        raise RuntimeError(f"unexpected modern route order: {names[:5]} ... {names[-5:]}")
    return np.stack([encode_tape(tape) for _name, tape in rr]).astype(np.int16)


def purge_package_modules(root: Path) -> None:
    r = root.resolve()
    for name, mod in list(sys.modules.items()):
        fp = getattr(mod, "__file__", None)
        if not fp:
            continue
        try:
            p = Path(fp).resolve()
        except Exception:
            continue
        if p == r or r in p.parents:
            sys.modules.pop(name, None)


def load_public_agent(main_py: Path):
    root = main_py.parent.resolve()
    purge_package_modules(root)
    name = f"public_expert_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(name, main_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {main_py}")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(root))
    try:
        spec.loader.exec_module(mod)
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass
    agent = getattr(mod, "agent", None)
    if not callable(agent):
        raise RuntimeError(f"{main_py} exports no callable agent")
    return agent


def outcome(margin: float) -> float:
    return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5


def run_one(tapes: np.ndarray, model: dict, expert_main: Path, seed: int, seat: int, enabled: bool) -> dict:
    router = ProgrammeRouter(tapes, model, enabled=enabled)
    expert = load_public_agent(expert_main)

    def ours(obs, config=None):
        return router.act(obs, config or {})

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    t0 = time.perf_counter()
    if seat == 0:
        env.run([ours, expert])
    else:
        env.run([expert, ours])
    secs = time.perf_counter() - t0
    payload = env.toJSON()
    statuses = [str(x) for x in payload.get("statuses", [])]
    rewards = [float(x) for x in payload.get("rewards", [])]
    steps = len(payload.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"episode status failure seed={seed} seat={seat} enabled={enabled}: {statuses}")
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode result seed={seed} seat={seat}: steps={steps} rewards={rewards}")
    expected_calls = 1 if enabled else 0
    if router.calls != expected_calls:
        raise RuntimeError(f"router call count {router.calls} != {expected_calls}")
    mine, opp = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    return {
        "reward": mine,
        "opponent_reward": opp,
        "margin": mine - opp,
        "score": outcome(mine - opp),
        "seconds": secs,
    }


def summarize(rows: list[dict], key: str) -> dict:
    vals = [r[key]["margin"] for r in rows]
    scores = [r[key]["score"] for r in rows]
    return {
        "games": len(rows),
        "score_rate": float(np.mean(scores)) if rows else None,
        "mean_margin": statistics.mean(vals) if vals else None,
        "median_margin": statistics.median(vals) if vals else None,
        "wins": sum(v > 0 for v in vals),
        "losses": sum(v < 0 for v in vals),
        "ties": sum(v == 0 for v in vals),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/programme-adaptive-expert-gate/ADAPTIVE_EXPERT_GATE.json")
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(f"kaggle-environments version mismatch: {getattr(kaggle_environments,'__version__',None)}")

    model_receipt = json.loads((ROOT / "data/programme_teacher/2026-09-18/ROUTER_EPISODE_GATE.json").read_text())
    model = model_receipt["model"]
    if model["group"] != 0 or model["checkpoint"] != 144 or model["static_program"] != 15:
        raise RuntimeError(f"frozen router identity mismatch: {model}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    provenance = {}
    started = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="programme-adaptive-experts-") as td:
        tmp = Path(td)
        extracted = {}
        modern_tapes = None
        for spec in EXPERTS:
            dl = tmp / f"download_{spec['key']}"
            archive, receipt = find_public_package(spec["handle"], dl)
            pkg = tmp / f"pkg_{spec['key']}"
            main_py = unpack_package(archive, pkg)
            main_sha = sha256_bytes(main_py.read_bytes())
            if main_sha != spec["expected_main_sha256"]:
                raise RuntimeError(
                    f"{spec['key']} main.py identity mismatch: got {main_sha}, expected {spec['expected_main_sha256']}"
                )
            provenance[spec["key"]] = {
                "handle": spec["handle"],
                "family": spec["family"],
                "expected_main_sha256": spec["expected_main_sha256"],
                "observed_main_sha256": main_sha,
                **receipt,
            }
            extracted[spec["key"]] = main_py
            if spec["key"] == "modern_v47":
                modern_tapes = recover_modern_tapes(main_py)

        if modern_tapes is None or modern_tapes.shape[0] != 41:
            raise RuntimeError("modern tape bank not recovered")
        if max(model["members"] + [model["static_program"]]) >= len(modern_tapes):
            raise RuntimeError("router program id outside recovered modern bank")

        for spec in EXPERTS:
            key = spec["key"]
            expert_main = extracted[key]
            for seed in SEEDS:
                for seat in (0, 1):
                    pair = {}
                    for enabled, label in ((False, "static"), (True, "router")):
                        try:
                            pair[label] = run_one(modern_tapes, model, expert_main, seed, seat, enabled)
                        finally:
                            purge_package_modules(expert_main.parent)
                    rows.append({"expert": key, "seed": seed, "seat": seat, **pair})
                    print(
                        "ADAPTIVE_PAIR",
                        json.dumps({
                            "expert": key,
                            "seed": seed,
                            "seat": seat,
                            "static_margin": pair["static"]["margin"],
                            "router_margin": pair["router"]["margin"],
                        }, sort_keys=True),
                        flush=True,
                    )

    overall_static = summarize(rows, "static")
    overall_router = summarize(rows, "router")
    by_expert = {}
    for spec in EXPERTS:
        rr = [r for r in rows if r["expert"] == spec["key"]]
        s = summarize(rr, "static")
        q = summarize(rr, "router")
        by_expert[spec["key"]] = {
            "static": s,
            "router": q,
            "score_delta": q["score_rate"] - s["score_rate"],
            "mean_paired_margin_delta": statistics.mean(r["router"]["margin"] - r["static"]["margin"] for r in rr),
        }

    score_delta = overall_router["score_rate"] - overall_static["score_rate"]
    mean_paired_margin_delta = statistics.mean(r["router"]["margin"] - r["static"]["margin"] for r in rows)
    no_block_regression = all(v["score_delta"] >= -MAX_BLOCK_REGRESSION for v in by_expert.values())
    promote = (
        score_delta >= PROMOTE_MIN_SCORE_DELTA
        and mean_paired_margin_delta > 0
        and no_block_regression
    )
    decision = (
        "PROMOTE_STANDALONE_ROUTER_TO_HOSTED_CANDIDATE_GATE"
        if promote
        else "CLOSE_STANDALONE_ROUTER_OPEN_BOUNDED_TRANSACTION_MARKET_SEARCH"
    )

    result = {
        "schema": "kculture-programme-adaptive-expert-gate-v1",
        "pass_mechanical": True,
        "engine": EXPECTED_ENGINE,
        "router_model": model,
        "seeds": SEEDS,
        "experts": provenance,
        "episodes": len(rows) * 2,
        "paired_matchups": len(rows),
        "static": overall_static,
        "router": overall_router,
        "score_delta": score_delta,
        "mean_paired_margin_delta": mean_paired_margin_delta,
        "by_expert": by_expert,
        "gate": {
            "promote_min_score_delta": PROMOTE_MIN_SCORE_DELTA,
            "max_block_regression": MAX_BLOCK_REGRESSION,
            "requires_positive_mean_paired_margin_delta": True,
        },
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "rows": rows,
        "third_party_code_persisted": False,
        "automatic_kaggle_submission": False,
    }
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("ADAPTIVE_EXPERT_GATE_RESULT", json.dumps({
        "static_score_rate": overall_static["score_rate"],
        "router_score_rate": overall_router["score_rate"],
        "score_delta": score_delta,
        "mean_paired_margin_delta": mean_paired_margin_delta,
        "by_expert": {k:v["score_delta"] for k,v in by_expert.items()},
        "decision": decision,
        "seconds": result["seconds"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
