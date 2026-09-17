#!/usr/bin/env python3
from __future__ import annotations

"""First real search teacher for the full-solver campaign.

This is deliberately NOT PPO and NOT the old five-plan classifier.  A candidate is a
32-dimensional strategic controller.  The controller itself executes adaptively inside
C++ against current state, while CEM searches the factorised strategy surface over an
opponent population and many exact worlds.

The output is a bootstrap teacher/checkpoint and a data source for the later learned
policy/value.  Hosted Kaggle strength is NOT inferred from this local objective.
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

import kagteacher  # noqa: E402

PARAM_NAMES = [
    "cow_max", "sheep_max", "goose_max",
    "wheat_tiles", "carrot_tiles", "tomato_tiles", "strawberry_tiles", "melon_tiles",
    "hands", "lands", "cash_reserve", "wheat_per_animal",
    "feed_priority", "care_priority", "harvest_trigger", "fertilizer_priority",
    "sell_common",
    "sell_wheat", "sell_carrot", "sell_tomato", "sell_strawberry", "sell_melon",
    "sell_egg", "sell_milk", "sell_wool", "sell_fertilizer",
    "opponent_pressure_sensitivity", "growth_speed", "terminal_day",
    "land_density_trigger", "hire_aggression", "diversification_response",
]
assert len(PARAM_NAMES) == int(kagteacher.PARAM_WIDTH) == 32


def vec(**kw):
    # Broad prior, not a plan. Every coordinate remains independently searchable.
    x = np.array([
        .42, .25, .12, .55, .08, .12, .12, .40,
        .50, .33, .18, .36, .70, .65, .38, .55,
        .42,
        .42, .42, .42, .42, .42, .42, .42, .42, .42,
        .35, .62, .48, .58, .50, .35,
    ], dtype=np.float64)
    for k, v in kw.items():
        x[PARAM_NAMES.index(k)] = float(v)
    return np.clip(x, 0.0, 1.0)


def initial_population_bank():
    # Diverse adaptive opponents.  These are not ranked or claimed strong; their job is
    # to stop the bootstrap search from overfitting to a single mirror policy.
    return np.stack([
        vec(),
        vec(cow_max=.72, sheep_max=.10, goose_max=.05, melon_tiles=.28,
            wheat_tiles=.72, care_priority=.82, wheat_per_animal=.58),
        vec(cow_max=.18, sheep_max=.68, goose_max=.08, melon_tiles=.25,
            wheat_tiles=.66, care_priority=.78),
        vec(cow_max=.12, sheep_max=.12, goose_max=.65, wheat_tiles=.52,
            carrot_tiles=.22, melon_tiles=.32),
        vec(cow_max=.22, sheep_max=.14, goose_max=.05, melon_tiles=.76,
            strawberry_tiles=.40, tomato_tiles=.30, hands=.62, lands=.65),
        vec(cow_max=.28, sheep_max=.20, goose_max=.12, cash_reserve=.62,
            lands=.05, hands=.25, hire_aggression=.22, sell_common=.25),
        vec(cow_max=.52, sheep_max=.35, goose_max=.12, growth_speed=.92,
            cash_reserve=.06, hands=.72, hire_aggression=.82, lands=.72),
        vec(cow_max=.30, sheep_max=.22, goose_max=.18, opponent_pressure_sensitivity=.88,
            diversification_response=.92, sell_common=.58),
    ])


def arrays(result):
    keys = [
        "mean_margin", "win_rate", "tie_rate", "mean_own_bank", "mean_opp_bank",
        "worst_margin", "silent_loss_coins", "dead_actions", "hand_pass_turns",
        "animals_escaped", "plants_dry",
    ]
    return {k: np.asarray(result[k], dtype=np.float64) for k in keys}


def objective(metrics):
    m = metrics
    # Win rate dominates; margin and robustness break ties. Telemetry penalties are
    # intentionally small: they help reject self-demolishing optima without turning
    # the search into a hand-coded efficiency contest.
    return (
        2.00 * (m["win_rate"] - 0.5)
        + 0.55 * np.tanh(m["mean_margin"] / 10000.0)
        + 0.12 * np.tanh(m["worst_margin"] / 25000.0)
        - 0.04 * np.tanh(m["silent_loss_coins"] / 3000.0)
        - 0.015 * np.tanh(m["dead_actions"] / 80.0)
    )


def summarize_one(params, metrics, idx=0):
    return {
        "params": {name: float(params[idx, j]) for j, name in enumerate(PARAM_NAMES)},
        **{k: float(v[idx]) for k, v in metrics.items()},
        "objective": float(objective(metrics)[idx]),
    }


def eval_batch(candidates, league, seeds, threads=0):
    t0 = time.perf_counter()
    raw = kagteacher.evaluate(
        np.ascontiguousarray(candidates, dtype=np.float64),
        np.ascontiguousarray(league, dtype=np.float64),
        [int(x) for x in seeds],
        int(threads),
    )
    wall = time.perf_counter() - t0
    m = arrays(raw)
    return m, {
        "native_seconds": float(raw["seconds"]),
        "wall_seconds": wall,
        "episodes_per_second": float(raw["episodes_per_second"]),
        "games_per_candidate": int(raw["games_per_candidate"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generations", type=int, default=4)
    ap.add_argument("--population", type=int, default=96)
    ap.add_argument("--train-seeds", type=int, default=4)
    ap.add_argument("--holdout-seeds", type=int, default=12)
    ap.add_argument("--elite-frac", type=float, default=0.16)
    ap.add_argument("--seed", type=int, default=20260917)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--out", default="runs/native_teacher_bootstrap_v0/TEACHER_BOOTSTRAP.json")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    league = initial_population_bank()
    center = vec()
    baseline = center.copy()
    sigma = np.full(32, 0.22, dtype=np.float64)
    sigma[[8, 9, 10, 28, 29]] = 0.15

    train_seeds = np.arange(11001, 11001 + args.train_seeds, dtype=np.uint64)
    holdout = np.arange(19001, 19001 + args.holdout_seeds, dtype=np.uint64)
    history = []
    all_params = []
    all_scores = []
    total_episodes = 0
    start = time.perf_counter()

    print("TEACHER_CEM_START", json.dumps({
        "schema": str(kagteacher.SCHEMA), "engine": str(kagteacher.ENGINE_VERSION),
        "param_width": 32, "population": args.population, "generations": args.generations,
        "league": len(league), "train_seeds": args.train_seeds,
    }, sort_keys=True), flush=True)

    best = center.copy()
    best_score = -1e30
    for gen in range(args.generations):
        pop = rng.normal(center, sigma, size=(args.population, 32))
        pop = np.clip(pop, 0.0, 1.0)
        pop[0] = center
        pop[1] = best
        # Inject fresh global diversity every generation.
        n_random = max(2, args.population // 12)
        pop[-n_random:] = rng.uniform(0.0, 1.0, size=(n_random, 32))

        met, perf = eval_batch(pop, league, train_seeds, args.threads)
        score = objective(met)
        order = np.argsort(score)[::-1]
        elite_n = max(4, int(math.ceil(args.population * args.elite_frac)))
        elite = pop[order[:elite_n]]
        elite_score = score[order[:elite_n]]

        # Rank-weighted CEM update; do not collapse sigma below meaningful exploration.
        w = np.linspace(1.0, 0.2, elite_n)
        w /= w.sum()
        new_center = np.sum(elite * w[:, None], axis=0)
        var = np.sum(((elite - new_center) ** 2) * w[:, None], axis=0)
        center = np.clip(0.72 * center + 0.28 * new_center, 0.0, 1.0)
        sigma = np.clip(0.76 * sigma + 0.24 * np.sqrt(var + 1e-5), 0.045, 0.35)

        idx = int(order[0])
        if score[idx] > best_score:
            best_score = float(score[idx])
            best = pop[idx].copy()

        games = args.population * len(league) * args.train_seeds * 2
        total_episodes += games
        row = {
            "generation": gen,
            "best_objective": float(score[idx]),
            "median_objective": float(np.median(score)),
            "best_win_rate": float(met["win_rate"][idx]),
            "best_mean_margin": float(met["mean_margin"][idx]),
            "best_mean_bank": float(met["mean_own_bank"][idx]),
            "best_silent_loss": float(met["silent_loss_coins"][idx]),
            "best_dead_actions": float(met["dead_actions"][idx]),
            "sigma_mean": float(np.mean(sigma)),
            **perf,
        }
        history.append(row)
        all_params.append(pop)
        all_scores.append(score)
        print("TEACHER_GEN", json.dumps(row, sort_keys=True), flush=True)

        # Archive one materially different strong elite into the opponent population.
        # Keep the bank bounded so later generations remain cheap and nonstationarity is controlled.
        cand = pop[idx]
        if np.min(np.linalg.norm(league - cand[None, :], axis=1)) > 0.35:
            league = np.concatenate([league, cand[None, :]], axis=0)
            if len(league) > 12:
                league = np.concatenate([league[:8], league[-4:]], axis=0)

    # Fixed holdout comparison: same worlds and same opponent bank for baseline and champion.
    compare = np.stack([baseline, best])
    hold_met, hold_perf = eval_batch(compare, league, holdout, args.threads)
    hold_score = objective(hold_met)
    baseline_summary = summarize_one(compare, hold_met, 0)
    champion_summary = summarize_one(compare, hold_met, 1)
    objective_delta = float(hold_score[1] - hold_score[0])

    elapsed = time.perf_counter() - start
    result = {
        "schema": "full-solver-native-teacher-bootstrap-v0",
        "engine_version": str(kagteacher.ENGINE_VERSION),
        "parameter_names": PARAM_NAMES,
        "generations": args.generations,
        "population": args.population,
        "league_size_final": int(len(league)),
        "train_seeds": train_seeds.tolist(),
        "holdout_seeds": holdout.tolist(),
        "history": history,
        "baseline_holdout": baseline_summary,
        "champion_holdout": champion_summary,
        "holdout_objective_delta": objective_delta,
        "holdout_perf": hold_perf,
        "total_search_episodes": int(total_episodes + 2 * len(league) * len(holdout) * 2),
        "elapsed_seconds": elapsed,
        "champion_vector": best.tolist(),
        "league_vectors": league.tolist(),
        # Gate means infrastructure/search loop is functional and found a non-worse candidate.
        # It is NOT a claim about Kaggle rating.
        "pass": bool(np.isfinite(hold_score).all() and champion_summary["mean_own_bank"] > 0 and objective_delta >= -0.02),
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    np.savez_compressed(
        out.with_name("TEACHER_SEARCH_DATA.npz"),
        params=np.concatenate(all_params, axis=0),
        objective=np.concatenate(all_scores, axis=0),
        champion=best,
        league=league,
    )

    print("TEACHER_HOLDOUT", json.dumps({
        "baseline_objective": baseline_summary["objective"],
        "champion_objective": champion_summary["objective"],
        "delta": objective_delta,
        "baseline_win_rate": baseline_summary["win_rate"],
        "champion_win_rate": champion_summary["win_rate"],
        "champion_mean_margin": champion_summary["mean_margin"],
        "champion_mean_bank": champion_summary["mean_own_bank"],
        "eps": hold_perf["episodes_per_second"],
    }, sort_keys=True), flush=True)
    print("TEACHER_BOOTSTRAP_RESULT", json.dumps({
        "pass": result["pass"], "episodes": result["total_search_episodes"],
        "seconds": elapsed, "out": str(out),
    }, sort_keys=True), flush=True)
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
