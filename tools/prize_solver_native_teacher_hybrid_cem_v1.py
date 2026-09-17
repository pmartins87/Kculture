#!/usr/bin/env python3
from __future__ import annotations

"""Hybrid CEM: synthetic adaptive league + seven frozen top replay tapes.

This is a short competitive bridge, not the final solver.  It asks whether the native
parametric controller discovered by the bootstrap survives contact with historically
strong public behaviours, and it refines the seed controller without letting either the
mirror-controller family or the replay tapes dominate the objective.

The resulting vector is intended as a warm-start teacher for state-conditioned search.
No hosted-rating claim is made from this local gate.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "native" / "teacher"
sys.path.insert(0, str(NATIVE))
sys.path.insert(0, str(ROOT / "tools"))

import kagteacher  # noqa: E402
import prize_solver_native_teacher_cem_v0 as base  # noqa: E402
from frozen_tape_utils import find_default_pack, load_frozen_top_tapes  # noqa: E402


def metrics(raw):
    return base.arrays(raw)


def tape_objective(m):
    return base.objective(m)


def hybrid_objective(param_m, tape_m, tape_raw):
    p = base.objective(param_m)
    t = tape_objective(tape_m)
    per = np.asarray(tape_raw["per_tape_win_rate"], dtype=np.float64)
    robust = np.min(per, axis=1)
    # Balanced: general adaptive population + historical top-behaviour anchors.
    # Worst-tape bonus discourages a brittle exploit that cycles across one replay family.
    return 0.50 * p + 0.50 * t + 0.18 * (robust - 0.5)


def evaluate(pop, league, tapes, seeds, threads):
    t0 = time.perf_counter()
    rp = kagteacher.evaluate(
        np.ascontiguousarray(pop, dtype=np.float64),
        np.ascontiguousarray(league, dtype=np.float64),
        [int(x) for x in seeds],
        int(threads),
    )
    rt = kagteacher.evaluate_tapes(
        np.ascontiguousarray(pop, dtype=np.float64),
        np.ascontiguousarray(tapes, dtype=np.int32),
        [int(x) for x in seeds],
        int(threads),
    )
    pm, tm = metrics(rp), metrics(rt)
    score = hybrid_objective(pm, tm, rt)
    return pm, tm, rt, score, {
        "wall_seconds": time.perf_counter() - t0,
        "param_eps": float(rp["episodes_per_second"]),
        "tape_eps": float(rt["episodes_per_second"]),
        "param_games_per_candidate": int(rp["games_per_candidate"]),
        "tape_games_per_candidate": int(rt["games_per_candidate"]),
    }


def row_summary(pop, pm, tm, traw, score, idx, names):
    per_wr = np.asarray(traw["per_tape_win_rate"])[idx]
    per_margin = np.asarray(traw["per_tape_mean_margin"])[idx]
    return {
        "hybrid_objective": float(score[idx]),
        "param_win_rate": float(pm["win_rate"][idx]),
        "param_mean_margin": float(pm["mean_margin"][idx]),
        "tape_win_rate": float(tm["win_rate"][idx]),
        "tape_mean_margin": float(tm["mean_margin"][idx]),
        "tape_worst_margin": float(tm["worst_margin"][idx]),
        "worst_tape_win_rate": float(np.min(per_wr)),
        "mean_bank": float(0.5 * (pm["mean_own_bank"][idx] + tm["mean_own_bank"][idx])),
        "dead_actions": float(0.5 * (pm["dead_actions"][idx] + tm["dead_actions"][idx])),
        "per_tape": {
            name: {
                "win_rate": float(per_wr[j]),
                "mean_margin": float(per_margin[j]),
            }
            for j, name in enumerate(names)
        },
        "params": {
            name: float(pop[idx, j])
            for j, name in enumerate(base.PARAM_NAMES)
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", default="runs/native_teacher_bootstrap_v0/TEACHER_BOOTSTRAP.json")
    ap.add_argument("--search-data", default="runs/native_teacher_bootstrap_v0/TEACHER_SEARCH_DATA.npz")
    ap.add_argument("--frozen-pack", default=None)
    ap.add_argument("--generations", type=int, default=8)
    ap.add_argument("--population", type=int, default=256)
    ap.add_argument("--train-seeds", type=int, default=8)
    ap.add_argument("--holdout-seeds", type=int, default=32)
    ap.add_argument("--elite-frac", type=float, default=0.12)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026091702)
    ap.add_argument("--out", default="runs/native_teacher_hybrid_v1/HYBRID_TEACHER.json")
    args = ap.parse_args()

    if str(kagteacher.SCHEMA) != "kculture-native-teacher-v1":
        raise RuntimeError(f"expected kagteacher v1, got {kagteacher.SCHEMA}")

    boot_path = ROOT / args.bootstrap
    boot = json.loads(boot_path.read_text(encoding="utf-8"))
    champion = np.asarray(boot["champion_vector"], dtype=np.float64)
    baseline = np.asarray(
        [boot["baseline_holdout"]["params"][n] for n in base.PARAM_NAMES],
        dtype=np.float64,
    )
    league = np.asarray(boot["league_vectors"], dtype=np.float64)

    pack = Path(args.frozen_pack) if args.frozen_pack else find_default_pack(ROOT)
    frozen_names, tapes = load_frozen_top_tapes(pack)
    if int(kagteacher.TAPE_ACTION_WIDTH) != tapes.shape[2]:
        raise RuntimeError((kagteacher.TAPE_ACTION_WIDTH, tapes.shape))

    rng = np.random.default_rng(args.seed)
    center = champion.copy()
    best = champion.copy()
    sigma = np.full(32, 0.18, dtype=np.float64)
    sigma[[8, 9, 10, 28, 29]] = 0.12

    # Reuse the best bootstrap candidates instead of discarding already paid-for search.
    warm = []
    search_path = ROOT / args.search_data
    if search_path.is_file():
        old = np.load(search_path)
        op = np.asarray(old["params"], dtype=np.float64)
        oscore = np.asarray(old["objective"], dtype=np.float64)
        for idx in np.argsort(oscore)[::-1][:12]:
            warm.append(op[int(idx)].copy())

    train_seeds = np.arange(31001, 31001 + args.train_seeds, dtype=np.uint64)
    holdout_seeds = np.arange(41001, 41001 + args.holdout_seeds, dtype=np.uint64)

    print("HYBRID_TEACHER_START", json.dumps({
        "schema": str(kagteacher.SCHEMA),
        "engine": str(kagteacher.ENGINE_VERSION),
        "population": args.population,
        "generations": args.generations,
        "param_league": int(len(league)),
        "frozen_tapes": frozen_names,
        "train_seeds": args.train_seeds,
        "holdout_seeds": args.holdout_seeds,
    }, sort_keys=True), flush=True)

    # Starting score is measured on the exact training families for fair comparison.
    spm, stm, strw, ss, _ = evaluate(
        np.stack([champion]), league, tapes, train_seeds, args.threads
    )
    best_score = float(ss[0])

    history = []
    all_params, all_score = [], []
    total_games = 0
    t_start = time.perf_counter()

    for gen in range(args.generations):
        pop = rng.normal(center, sigma, size=(args.population, 32))
        pop = np.clip(pop, 0.0, 1.0)
        pop[0] = center
        pop[1] = best
        for j, w in enumerate(warm[: min(len(warm), max(0, args.population // 16))], start=2):
            if j >= args.population:
                break
            pop[j] = w

        # Keep broad exploration alive.  Half global, half larger mutations around champion.
        n_explore = max(8, args.population // 10)
        half = n_explore // 2
        pop[-n_explore:-half] = rng.uniform(0.0, 1.0, size=(n_explore - half, 32))
        pop[-half:] = np.clip(
            champion[None, :] + rng.normal(0.0, 0.30, size=(half, 32)), 0.0, 1.0
        )

        pm, tm, traw, score, perf = evaluate(pop, league, tapes, train_seeds, args.threads)
        order = np.argsort(score)[::-1]
        elite_n = max(8, int(math.ceil(args.population * args.elite_frac)))
        elite = pop[order[:elite_n]]
        weights = np.linspace(1.0, 0.15, elite_n)
        weights /= weights.sum()
        new_center = np.sum(elite * weights[:, None], axis=0)
        var = np.sum(((elite - new_center) ** 2) * weights[:, None], axis=0)
        center = np.clip(0.70 * center + 0.30 * new_center, 0.0, 1.0)
        sigma = np.clip(0.75 * sigma + 0.25 * np.sqrt(var + 1e-5), 0.035, 0.32)

        idx = int(order[0])
        if float(score[idx]) > best_score:
            best_score = float(score[idx])
            best = pop[idx].copy()

        row = {
            "generation": gen,
            **{k: v for k, v in row_summary(pop, pm, tm, traw, score, idx, frozen_names).items()
               if k != "params" and k != "per_tape"},
            "median_hybrid_objective": float(np.median(score)),
            "p90_hybrid_objective": float(np.quantile(score, 0.90)),
            "sigma_mean": float(np.mean(sigma)),
            **perf,
        }
        history.append(row)
        all_params.append(pop.copy())
        all_score.append(score.copy())
        total_games += args.population * (
            int(perf["param_games_per_candidate"]) + int(perf["tape_games_per_candidate"])
        )
        print("HYBRID_GEN", json.dumps(row, sort_keys=True), flush=True)

        # Add only materially different elite strategies; fixed synthetic core remains.
        for cand_idx in order[:4]:
            cand = pop[int(cand_idx)]
            if np.min(np.linalg.norm(league - cand[None, :], axis=1)) > 0.32:
                league = np.concatenate([league, cand[None, :]], axis=0)
                if len(league) > 16:
                    league = np.concatenate([league[:8], league[-8:]], axis=0)

    compare = np.stack([baseline, champion, best])
    hpm, htm, htraw, hscore, hperf = evaluate(
        compare, league, tapes, holdout_seeds, args.threads
    )
    labels = ["baseline", "bootstrap_champion", "hybrid_champion"]
    holdout = {
        labels[i]: row_summary(compare, hpm, htm, htraw, hscore, i, frozen_names)
        for i in range(3)
    }

    delta_boot = float(hscore[2] - hscore[1])
    elapsed = time.perf_counter() - t_start
    result = {
        "schema": "full-solver-native-teacher-hybrid-v1",
        "engine_version": str(kagteacher.ENGINE_VERSION),
        "frozen_pack": str(pack),
        "frozen_names": frozen_names,
        "generations": args.generations,
        "population": args.population,
        "train_seeds": train_seeds.tolist(),
        "holdout_seeds": holdout_seeds.tolist(),
        "history": history,
        "holdout": holdout,
        "holdout_delta_vs_bootstrap": delta_boot,
        "hybrid_champion_vector": best.tolist(),
        "league_vectors": league.tolist(),
        "total_search_games": int(total_games),
        "elapsed_seconds": elapsed,
        "holdout_perf": hperf,
        # Functional gate only. Hosted strength still requires hosted evaluation.
        "pass": bool(
            np.isfinite(hscore).all()
            and holdout["hybrid_champion"]["mean_bank"] > 0
            and hscore[2] >= hscore[1] - 0.03
        ),
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    np.savez_compressed(
        out.with_name("HYBRID_SEARCH_DATA.npz"),
        params=np.concatenate(all_params, axis=0),
        objective=np.concatenate(all_score, axis=0),
        champion=best,
        league=league,
        tapes=tapes,
    )

    print("HYBRID_HOLDOUT", json.dumps({
        "baseline": {
            "score": holdout["baseline"]["hybrid_objective"],
            "param_wr": holdout["baseline"]["param_win_rate"],
            "tape_wr": holdout["baseline"]["tape_win_rate"],
        },
        "bootstrap": {
            "score": holdout["bootstrap_champion"]["hybrid_objective"],
            "param_wr": holdout["bootstrap_champion"]["param_win_rate"],
            "tape_wr": holdout["bootstrap_champion"]["tape_win_rate"],
            "worst_tape_wr": holdout["bootstrap_champion"]["worst_tape_win_rate"],
        },
        "hybrid": {
            "score": holdout["hybrid_champion"]["hybrid_objective"],
            "param_wr": holdout["hybrid_champion"]["param_win_rate"],
            "tape_wr": holdout["hybrid_champion"]["tape_win_rate"],
            "worst_tape_wr": holdout["hybrid_champion"]["worst_tape_win_rate"],
        },
        "delta_vs_bootstrap": delta_boot,
    }, sort_keys=True), flush=True)
    print("HYBRID_TEACHER_RESULT", json.dumps({
        "pass": result["pass"],
        "games": result["total_search_games"],
        "seconds": elapsed,
        "out": str(out),
    }, sort_keys=True), flush=True)
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
