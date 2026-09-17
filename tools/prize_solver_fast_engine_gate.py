#!/usr/bin/env python3
from __future__ import annotations

"""Gate the public bit-exact kagsim engine on the Ryzen workstation.

This is deliberately NOT a training job. It answers four questions before we spend
multi-day compute:
  1) are we running the pinned 1.32.7 kagsim build?
  2) does PrizeSolverV4 produce exactly the same final banks in kagsim L1 and the
     official kaggle-environments interpreter on fresh seeds?
  3) what is L0 fixed-stream throughput on this Ryzen as core count scales?
  4) what is L1 adaptive-agent throughput, i.e. the speed we actually get before L2?

The output is a machine-readable JSON receipt. A later continuous trainer may consume
its measured throughput, but this script does not alter any solver weights or policies.
"""

import argparse
import copy
import json
import os
import platform
import statistics
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PINNED_KAGSIM_COMMIT = "f0084b916343c37bbcbdc7de9d833dc96caff78f"
EXPECTED_ENGINE_VERSION = "1.32.7"

CFG = {
    "episodeSteps": 720,
    "turnsPerDay": 24,
    "boardSize": 10,
}


def _git_head(path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=path, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return str(x)


def _run_official(seed: int):
    from kaggle_environments import make
    from solver.prize_solver_v4 import PrizeSolverV4

    a0 = PrizeSolverV4()
    a1 = PrizeSolverV4()

    def f0(obs, config=None):
        return a0.act(obs, config or CFG)

    def f1(obs, config=None):
        return a1.act(obs, config or CFG)

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    t0 = time.perf_counter()
    env.run([f0, f1])
    secs = time.perf_counter() - t0
    payload = env.toJSON()
    rewards = tuple(float(v) for v in payload.get("rewards", []))
    statuses = tuple(str(v) for v in payload.get("statuses", []))
    steps = len(payload.get("steps") or [])
    return rewards, statuses, steps, secs


def _run_kagsim(seed: int, *, record_streams: bool = False):
    import kagsim
    from solver.prize_solver_v4 import PrizeSolverV4

    game = kagsim.Game(int(seed), 720)
    a0 = PrizeSolverV4()
    a1 = PrizeSolverV4()
    s0, s1 = [], []
    t0 = time.perf_counter()
    while not game.done:
        o0 = game.observe(0)
        o1 = game.observe(1)
        x0 = a0.act(o0, CFG)
        x1 = a1.act(o1, CFG)
        if record_streams:
            s0.append(copy.deepcopy(x0))
            s1.append(copy.deepcopy(x1))
        game.step(x0, x1)
    secs = time.perf_counter() - t0
    rewards = (float(game.reward(0)), float(game.reward(1)))
    telemetry = (_jsonable(game.telemetry(0)), _jsonable(game.telemetry(1)))
    return rewards, secs, s0, s1, telemetry


def _median_rate(samples):
    return statistics.median(samples) if samples else 0.0


def _thread_sweep(cpu_count: int):
    vals = [1, 2, 4, 8, 16, 24, 32]
    vals = [n for n in vals if n <= max(1, cpu_count)]
    if max(1, cpu_count) not in vals:
        vals.append(max(1, cpu_count))
    vals = sorted(set(vals))
    vals.append(0)  # kagsim auto/all cores
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/fast_engine_gate_v1")
    ap.add_argument("--parity-seeds", default="11,23,47")
    ap.add_argument("--l0-jobs", type=int, default=10000)
    ap.add_argument("--l0-reps", type=int, default=3)
    ap.add_argument("--l1-episodes", type=int, default=24)
    args = ap.parse_args()

    import kaggle_environments
    import kagsim

    engine_version = str(getattr(kagsim, "ENGINE_VERSION", "unknown"))
    kagsim_version = str(getattr(kagsim, "__version__", "unknown"))
    kaggle_env_version = str(getattr(kaggle_environments, "__version__", "unknown"))
    if engine_version != EXPECTED_ENGINE_VERSION:
        raise SystemExit(
            f"kagsim engine mismatch: got={engine_version} expected={EXPECTED_ENGINE_VERSION}"
        )
    if kaggle_env_version != EXPECTED_ENGINE_VERSION:
        raise SystemExit(
            f"kaggle-environments mismatch: got={kaggle_env_version} "
            f"expected={EXPECTED_ENGINE_VERSION}"
        )

    parity_seeds = [int(x) for x in args.parity_seeds.split(",") if x.strip()]
    parity_rows = []
    official_secs = []
    recorded_a = recorded_b = None
    recorded_telemetry = None

    print(
        "FAST_ENGINE_GATE_START",
        json.dumps({
            "kagsim_version": kagsim_version,
            "engine_version": engine_version,
            "kaggle_environments": kaggle_env_version,
            "cpu_count": os.cpu_count(),
            "parity_seeds": parity_seeds,
        }, sort_keys=True),
        flush=True,
    )

    for i, seed in enumerate(parity_seeds):
        off_rewards, statuses, steps, off_secs = _run_official(seed)
        fast_rewards, fast_secs, sa, sb, tel = _run_kagsim(
            seed, record_streams=(i == 0)
        )
        exact = off_rewards == fast_rewards
        row = {
            "seed": seed,
            "official_rewards": list(off_rewards),
            "kagsim_rewards": list(fast_rewards),
            "official_statuses": list(statuses),
            "official_steps": steps,
            "official_seconds": off_secs,
            "kagsim_l1_seconds": fast_secs,
            "exact_final_banks": exact,
        }
        parity_rows.append(row)
        official_secs.append(off_secs)
        print("PARITY", json.dumps(row, sort_keys=True), flush=True)
        if not exact:
            raise SystemExit(f"PARITY_FAIL seed={seed}: {off_rewards} != {fast_rewards}")
        if i == 0:
            recorded_a, recorded_b = sa, sb
            recorded_telemetry = tel

    # L0 raw-engine throughput. The recorded adaptive episode is now frozen into action
    # streams and replayed over a large seed panel. This measures the simulation core,
    # not the quality of those actions on the new seeds.
    stream_a = kagsim.Stream(recorded_a or [])
    stream_b = kagsim.Stream(recorded_b or [])
    jobs = [(stream_a, stream_b, i + 1000003) for i in range(args.l0_jobs)]
    cpu_count = int(os.cpu_count() or 1)
    l0 = []
    reference_results = None
    for threads in _thread_sweep(cpu_count):
        reps = []
        checksum = None
        for rep in range(args.l0_reps):
            t0 = time.perf_counter()
            out = kagsim.run_many(jobs, steps=720, threads=threads)
            secs = time.perf_counter() - t0
            eps = len(jobs) / max(secs, 1e-9)
            reps.append(eps)
            # A small deterministic checksum catches accidental result drift across
            # thread counts without serialising the full panel.
            checksum = [list(map(float, out[j])) for j in (0, len(out)//2, len(out)-1)]
            if reference_results is None:
                reference_results = checksum
            elif checksum != reference_results:
                raise SystemExit(
                    f"THREAD_PARITY_FAIL threads={threads} rep={rep}: "
                    f"{checksum} != {reference_results}"
                )
        row = {
            "threads": threads,
            "eps_samples": reps,
            "eps_median": _median_rate(reps),
            "checksum": checksum,
        }
        l0.append(row)
        print("L0", json.dumps(row, sort_keys=True), flush=True)

    # L1 adaptive-agent throughput. This is the relevant pre-L2 number: every step
    # crosses Python and runs PrizeSolverV4. It quantifies exactly how much performance
    # a VecGame/tensor interface must recover.
    l1_times = []
    l1_rewards = []
    for i in range(args.l1_episodes):
        seed = 2000003 + i
        r, secs, _, _, _ = _run_kagsim(seed, record_streams=False)
        l1_times.append(secs)
        l1_rewards.append(list(r))
    l1_total = sum(l1_times)
    l1_eps = len(l1_times) / max(l1_total, 1e-9)
    print(
        "L1",
        json.dumps({
            "episodes": len(l1_times),
            "seconds": l1_total,
            "eps": l1_eps,
            "median_episode_seconds": statistics.median(l1_times),
        }, sort_keys=True),
        flush=True,
    )

    official_total = sum(official_secs)
    official_eps = len(official_secs) / max(official_total, 1e-9)
    auto_row = next((x for x in l0 if x["threads"] == 0), None)
    best_row = max(l0, key=lambda x: x["eps_median"])

    result = {
        "schema": "prize-solver-fast-engine-gate-v1",
        "pass": True,
        "pinned_kagsim_commit": PINNED_KAGSIM_COMMIT,
        "kagsim_version": kagsim_version,
        "engine_version": engine_version,
        "kaggle_environments_version": kaggle_env_version,
        "kculture_git_head": _git_head(ROOT),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_count": cpu_count,
        "parity": parity_rows,
        "official_eps_on_parity_runs": official_eps,
        "l0": l0,
        "l0_best_eps": best_row["eps_median"],
        "l0_best_threads": best_row["threads"],
        "l0_auto_eps": None if auto_row is None else auto_row["eps_median"],
        "l1_adaptive": {
            "episodes": len(l1_times),
            "seconds": l1_total,
            "eps": l1_eps,
            "median_episode_seconds": statistics.median(l1_times),
            "sample_rewards": l1_rewards[:5],
        },
        "l1_speedup_vs_official": l1_eps / max(official_eps, 1e-9),
        "l0_to_l1_ratio": best_row["eps_median"] / max(l1_eps, 1e-9),
        "sample_telemetry_seed": parity_seeds[0] if parity_seeds else None,
        "sample_telemetry": recorded_telemetry,
    }

    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "FAST_ENGINE_GATE.json"
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("FAST_ENGINE_GATE_PASS", json.dumps({
        "out": str(out_path),
        "l0_best_eps": result["l0_best_eps"],
        "l0_best_threads": result["l0_best_threads"],
        "l1_eps": result["l1_adaptive"]["eps"],
        "official_eps": result["official_eps_on_parity_runs"],
        "l1_speedup_vs_official": result["l1_speedup_vs_official"],
        "l0_to_l1_ratio": result["l0_to_l1_ratio"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
