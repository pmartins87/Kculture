#!/usr/bin/env python3
from __future__ import annotations

"""Train Prize Solver PS3 value/Q model from exact PS2 counterfactual rollouts.

The model predicts *macro advantage* rather than raw final score:
    A(s, p) = return(s, p) - mean_p return(s, p)
This removes much of the seed/state difficulty signal and focuses learning capacity on
which macro plan is better in the current visible state.

Training is offline only and uses numpy. The exported JSON can be evaluated by a tiny
pure-Python inference helper in the hosted agent; no ML framework is required at
runtime.
"""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _stable_seed_bucket(seed: int, mod: int = 5) -> int:
    raw = hashlib.sha256(str(int(seed)).encode("utf-8")).digest()
    return int.from_bytes(raw[:8], "big") % mod


def _load_rows(run_dir: Path):
    manifest = json.loads((run_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    plan_names = list(manifest.get("plans", []))
    if not plan_names:
        raise SystemExit("manifest has no plans")

    states = []
    feature_names = None
    for path in sorted((run_dir / "shards").glob("seed_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("failures"):
            raise SystemExit(f"failures present in {path}: {data['failures'][:2]}")
        for row in data.get("rows", []):
            feats = row.get("features", {})
            if feature_names is None:
                feature_names = sorted(feats)
            elif sorted(feats) != feature_names:
                raise SystemExit(f"feature schema mismatch in {path}")
            returns = {
                x["plan"]: float(x["margin"])
                for x in row.get("plan_returns", [])
                if x.get("ok") and x.get("margin") is not None
            }
            if set(returns) != set(plan_names):
                raise SystemExit(
                    f"plan-return mismatch seed={row.get('seed')} day={row.get('day')}: "
                    f"got={sorted(returns)} expected={sorted(plan_names)}"
                )
            states.append({
                "seed": int(row["seed"]),
                "day": int(row["day"]),
                "features": feats,
                "returns": returns,
                "oracle_plan": row.get("oracle_plan"),
                "heuristic_plan": row.get("heuristic_plan"),
            })
    if not states:
        raise SystemExit("no training states found")
    return manifest, feature_names or [], plan_names, states


def _matrix(states, feature_names, plan_names):
    xs, ys, groups, labels = [], [], [], []
    for gi, state in enumerate(states):
        vals = np.asarray([state["returns"][p] for p in plan_names], dtype=np.float64)
        center = float(vals.mean())
        base = [float(state["features"][k]) for k in feature_names]
        for pi, plan in enumerate(plan_names):
            onehot = [0.0] * len(plan_names)
            onehot[pi] = 1.0
            xs.append(base + onehot)
            ys.append(float(state["returns"][plan]) - center)
            groups.append(gi)
            labels.append(plan)
    return (
        np.asarray(xs, dtype=np.float64),
        np.asarray(ys, dtype=np.float64).reshape(-1, 1),
        np.asarray(groups, dtype=np.int64),
        labels,
    )


def _relu(x):
    return np.maximum(x, 0.0)


def _forward(x, params):
    z1 = x @ params["W1"] + params["b1"]
    h1 = _relu(z1)
    z2 = h1 @ params["W2"] + params["b2"]
    h2 = _relu(z2)
    y = h2 @ params["W3"] + params["b3"]
    return y, (x, z1, h1, z2, h2)


def _mse(x, y, params):
    pred, _ = _forward(x, params)
    return float(np.mean((pred - y) ** 2))


def _train_mlp(x_train, y_train, x_val, y_val, seed, hidden1, hidden2, epochs, batch, lr, l2, patience):
    rng = np.random.default_rng(seed)
    d = x_train.shape[1]
    params = {
        "W1": rng.normal(0.0, math.sqrt(2.0 / max(1, d)), size=(d, hidden1)),
        "b1": np.zeros((1, hidden1)),
        "W2": rng.normal(0.0, math.sqrt(2.0 / max(1, hidden1)), size=(hidden1, hidden2)),
        "b2": np.zeros((1, hidden2)),
        "W3": rng.normal(0.0, math.sqrt(2.0 / max(1, hidden2)), size=(hidden2, 1)),
        "b3": np.zeros((1, 1)),
    }
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(vv) for k, vv in params.items()}
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    t = 0
    best = None
    best_val = float("inf")
    bad = 0

    for epoch in range(1, epochs + 1):
        order = rng.permutation(len(x_train))
        for start in range(0, len(order), batch):
            idx = order[start:start + batch]
            xb, yb = x_train[idx], y_train[idx]
            pred, cache = _forward(xb, params)
            x, z1, h1, z2, h2 = cache
            n = max(1, len(xb))
            dy = 2.0 * (pred - yb) / n

            grads = {}
            grads["W3"] = h2.T @ dy + l2 * params["W3"]
            grads["b3"] = dy.sum(axis=0, keepdims=True)
            dh2 = dy @ params["W3"].T
            dz2 = dh2 * (z2 > 0.0)
            grads["W2"] = h1.T @ dz2 + l2 * params["W2"]
            grads["b2"] = dz2.sum(axis=0, keepdims=True)
            dh1 = dz2 @ params["W2"].T
            dz1 = dh1 * (z1 > 0.0)
            grads["W1"] = x.T @ dz1 + l2 * params["W1"]
            grads["b1"] = dz1.sum(axis=0, keepdims=True)

            t += 1
            for k in params:
                m[k] = beta1 * m[k] + (1.0 - beta1) * grads[k]
                v[k] = beta2 * v[k] + (1.0 - beta2) * (grads[k] ** 2)
                mh = m[k] / (1.0 - beta1 ** t)
                vh = v[k] / (1.0 - beta2 ** t)
                params[k] -= lr * mh / (np.sqrt(vh) + eps)

        val = _mse(x_val, y_val, params)
        train = _mse(x_train, y_train, params)
        if epoch == 1 or epoch % 10 == 0:
            print(f"PS3_EPOCH epoch={epoch} train_mse={train:.6f} val_mse={val:.6f}", flush=True)
        if val + 1e-10 < best_val:
            best_val = val
            best = {k: vv.copy() for k, vv in params.items()}
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                print(f"PS3_EARLY_STOP epoch={epoch} best_val={best_val:.6f}", flush=True)
                break
    return best or params, best_val


def _evaluate_policy(states, feature_names, plan_names, x_mean, x_std, y_scale, params):
    regrets = []
    exact = 0
    heuristic_regrets = []
    for state in states:
        preds = {}
        base = [float(state["features"][k]) for k in feature_names]
        for pi, plan in enumerate(plan_names):
            onehot = [0.0] * len(plan_names)
            onehot[pi] = 1.0
            x = np.asarray([base + onehot], dtype=np.float64)
            x = (x - x_mean) / x_std
            pred, _ = _forward(x, params)
            preds[plan] = float(pred[0, 0]) * y_scale
        chosen = max(plan_names, key=lambda p: (preds[p], p))
        oracle = max(plan_names, key=lambda p: (state["returns"][p], p))
        best_return = float(state["returns"][oracle])
        regrets.append(best_return - float(state["returns"][chosen]))
        exact += int(chosen == oracle)
        hp = state.get("heuristic_plan")
        if hp in state["returns"]:
            heuristic_regrets.append(best_return - float(state["returns"][hp]))
    regrets_np = np.asarray(regrets, dtype=np.float64)
    hreg_np = np.asarray(heuristic_regrets, dtype=np.float64) if heuristic_regrets else np.asarray([], dtype=np.float64)
    return {
        "states": len(states),
        "policy_oracle_match_rate": exact / max(1, len(states)),
        "policy_mean_regret": float(regrets_np.mean()) if len(regrets_np) else None,
        "policy_median_regret": float(np.median(regrets_np)) if len(regrets_np) else None,
        "policy_p90_regret": float(np.quantile(regrets_np, 0.90)) if len(regrets_np) else None,
        "heuristic_mean_regret": float(hreg_np.mean()) if len(hreg_np) else None,
        "heuristic_median_regret": float(np.median(hreg_np)) if len(hreg_np) else None,
    }


def _tolist(params):
    return {k: v.tolist() for k, v in params.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default="runs/ps2_v4_2k_v2")
    ap.add_argument("--out", default="models/prize_solver_value_v1.json")
    ap.add_argument("--seed", type=int, default=26091701)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--hidden1", type=int, default=64)
    ap.add_argument("--hidden2", type=int, default=32)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=0.0015)
    ap.add_argument("--l2", type=float, default=1e-5)
    ap.add_argument("--patience", type=int, default=35)
    args = ap.parse_args()

    run_dir = (ROOT / args.run_dir).resolve()
    manifest, feature_names, plan_names, states = _load_rows(run_dir)
    train_states = [s for s in states if _stable_seed_bucket(s["seed"]) != 0]
    val_states = [s for s in states if _stable_seed_bucket(s["seed"]) == 0]
    if not train_states or not val_states:
        raise SystemExit(f"bad split train={len(train_states)} val={len(val_states)}")

    x_train, y_train, _, _ = _matrix(train_states, feature_names, plan_names)
    x_val, y_val, _, _ = _matrix(val_states, feature_names, plan_names)

    x_mean = x_train.mean(axis=0, keepdims=True)
    x_std = x_train.std(axis=0, keepdims=True)
    x_std[x_std < 1e-8] = 1.0
    y_scale = float(max(1.0, y_train.std()))
    xt = (x_train - x_mean) / x_std
    xv = (x_val - x_mean) / x_std
    yt = y_train / y_scale
    yv = y_val / y_scale

    print(
        f"PS3_START states={len(states)} train_states={len(train_states)} val_states={len(val_states)} "
        f"samples={len(x_train)+len(x_val)} features={len(feature_names)} plans={len(plan_names)} y_scale={y_scale:.3f}",
        flush=True,
    )
    params, best_val = _train_mlp(
        xt, yt, xv, yv,
        seed=args.seed,
        hidden1=args.hidden1,
        hidden2=args.hidden2,
        epochs=args.epochs,
        batch=args.batch,
        lr=args.lr,
        l2=args.l2,
        patience=args.patience,
    )
    train_metrics = _evaluate_policy(train_states, feature_names, plan_names, x_mean, x_std, y_scale, params)
    val_metrics = _evaluate_policy(val_states, feature_names, plan_names, x_mean, x_std, y_scale, params)

    model = {
        "schema": "prize-solver-value-v1",
        "objective": "macro_advantage",
        "source_run": str(run_dir),
        "source_manifest": manifest,
        "feature_names": feature_names,
        "plan_names": plan_names,
        "input_mean": x_mean.reshape(-1).tolist(),
        "input_std": x_std.reshape(-1).tolist(),
        "target_scale": y_scale,
        "architecture": {"hidden1": args.hidden1, "hidden2": args.hidden2, "activation": "relu"},
        "weights": _tolist(params),
        "best_val_normalized_mse": best_val,
        "train_metrics": train_metrics,
        "validation_metrics": val_metrics,
    }
    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
    print("PS3_DONE", json.dumps({
        "out": str(out),
        "train": train_metrics,
        "validation": val_metrics,
        "best_val_normalized_mse": best_val,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
