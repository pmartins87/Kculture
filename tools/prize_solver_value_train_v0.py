#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kaggle_environments import make
from solver.prize_solver_v0 import PrizeSolver, ValueModel
from candidates.fp001_h10_cow_scale_module import make_agent as make_cow_agent
from candidates.fp001_e5_elite_mixed_animal import make_agent as make_e5_agent


FEATURES = (
    "money_diff",
    "own_land",
    "own_hands",
    "survival_risk",
    "shed_value",
    "field_value",
    "opp_field_value",
    "terminal_liquidity",
)


def plain(x):
    return json.loads(json.dumps(x))


def solver_fn():
    solver = PrizeSolver()
    def fn(obs, config=None):
        return solver.act(obs, config or {})
    return fn


def opponent_pool():
    return [
        ("pass", "pass"),
        ("random", "random"),
        ("starter", "starter"),
        ("cow6", make_cow_agent(6, harvest_threshold=6)),
        ("e5_mixed", make_e5_agent()),
    ]


def extract_rows(env, opponent_name, seed):
    payload = env.toJSON()
    rewards = list(payload.get("rewards") or [])
    if len(rewards) != 2 or any(x is None for x in rewards):
        return []
    final_margin = float(rewards[0]) - float(rewards[1])
    cfg = plain(env.configuration)
    rows = []
    vm = ValueModel()
    for i, pair in enumerate(payload.get("steps") or []):
        if i % 24 != 0 or not pair:
            continue
        state0 = pair[0]
        obs = state0.get("observation") if isinstance(state0, dict) else None
        if not isinstance(obs, dict):
            continue
        obs = plain(obs)
        obs.setdefault("player", 0)
        obs.setdefault("step", i)
        feats = vm.state_features(obs, cfg)
        rows.append({
            "seed": int(seed),
            "opponent": opponent_name,
            "step_index": i,
            "features": {k: float(feats[k]) for k in FEATURES},
            "target_margin": final_margin,
        })
    return rows


def run_game(seed, opponent_name, opponent):
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    env.run([solver_fn(), opponent])
    payload = env.toJSON()
    statuses = list(payload.get("statuses") or [])
    ok = statuses == ["DONE", "DONE"]
    return ok, extract_rows(env, opponent_name, seed)


def design(rows):
    X = np.asarray([[r["features"][k] for k in FEATURES] for r in rows], dtype=np.float64)
    y = np.asarray([r["target_margin"] for r in rows], dtype=np.float64)
    return X, y


def fit_ridge(train_rows, alpha=1e-3):
    X, y = design(train_rows)
    mu = X.mean(axis=0)
    sigma = X.std(axis=0)
    sigma[sigma < 1e-9] = 1.0
    Xn = (X - mu) / sigma
    ym = float(y.mean())
    yc = y - ym
    A = Xn.T @ Xn + float(alpha) * np.eye(Xn.shape[1])
    beta_n = np.linalg.solve(A, Xn.T @ yc)
    beta = beta_n / sigma
    intercept = ym - float(mu @ beta)
    return intercept, beta


def predict(rows, intercept, beta):
    X, y = design(rows)
    pred = float(intercept) + X @ beta
    return y, pred


def metrics(y, pred):
    y = np.asarray(y, dtype=np.float64)
    pred = np.asarray(pred, dtype=np.float64)
    mae = float(np.mean(np.abs(y - pred)))
    rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
    if len(y) > 1 and np.std(y) > 1e-9 and np.std(pred) > 1e-9:
        corr = float(np.corrcoef(y, pred)[0, 1])
    else:
        corr = 0.0
    sign_acc = float(np.mean((y >= 0) == (pred >= 0)))
    return {"mae": mae, "rmse": rmse, "corr": corr, "sign_acc": sign_acc}


def baseline_metrics(rows):
    y = np.asarray([r["target_margin"] for r in rows], dtype=np.float64)
    p = np.asarray([r["features"]["money_diff"] for r in rows], dtype=np.float64)
    # Calibrate a single affine money-diff baseline on the same rows for a fair yardstick.
    A = np.vstack([np.ones(len(p)), p]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    out = metrics(y, pred)
    out["intercept"] = float(coef[0])
    out["money_coef"] = float(coef[1])
    return out


def main():
    rows = []
    game_receipts = []
    seeds = tuple(range(91801, 91813))
    for opponent_name, opponent in opponent_pool():
        for seed in seeds:
            ok, game_rows = run_game(seed, opponent_name, opponent)
            game_receipts.append({"opponent": opponent_name, "seed": seed, "ok": ok, "samples": len(game_rows)})
            rows.extend(game_rows)
            print("VALUE_GAME", opponent_name, seed, "ok", ok, "samples", len(game_rows), flush=True)

    if not rows:
        raise SystemExit("no training rows extracted")
    train = [r for r in rows if r["seed"] % 3 != 0]
    test = [r for r in rows if r["seed"] % 3 == 0]
    intercept, beta = fit_ridge(train, alpha=10.0)
    ytr, ptr = predict(train, intercept, beta)
    yte, pte = predict(test, intercept, beta)

    train_m = metrics(ytr, ptr)
    test_m = metrics(yte, pte)
    baseline = baseline_metrics(test)
    weights = {k: float(v) for k, v in zip(FEATURES, beta)}

    # PS1 is intentionally strict: the learned representation must add information
    # beyond current bank balance on held-out seeds.
    beats_baseline = (
        test_m["mae"] < baseline["mae"]
        and test_m["sign_acc"] >= baseline["sign_acc"]
    )
    result = {
        "schema": "prize-solver-value-v0-v1",
        "engine": "kaggle-environments==1.32.7",
        "games": len(game_receipts),
        "samples": len(rows),
        "train_samples": len(train),
        "test_samples": len(test),
        "intercept": float(intercept),
        "weights": weights,
        "train_metrics": train_m,
        "test_metrics": test_m,
        "money_only_baseline": baseline,
        "beats_money_only_baseline": bool(beats_baseline),
        "games_receipt": game_receipts,
    }
    (ROOT / "PRIZE_SOLVER_VALUE_V0.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("VALUE_RESULT", json.dumps({
        "samples": result["samples"],
        "test": test_m,
        "baseline": baseline,
        "beats_baseline": beats_baseline,
    }, sort_keys=True), flush=True)

    # Training failure does not mean the solver architecture fails. The artifact is
    # still useful diagnostic evidence, so only mechanical game failures hard-fail.
    if any(not g["ok"] for g in game_receipts):
        raise SystemExit("one or more value-training games did not finish cleanly")


if __name__ == "__main__":
    main()
