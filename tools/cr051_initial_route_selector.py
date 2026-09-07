"""CR051: initial-state selector over 40 coherent live-king routes.

CR049 and CR050 falsified action-level imitation.  Here we preserve complete
recorded trajectories and ask a different question: is the correct *route* for a
season inferable before the first action?

For train/tune/validation random seeds (both seats), all 40 frozen live-king
tapes are evaluated against the exact CR029 tape with bit-exact kagsim L0.  A
KNN regressor sees only the initial observation's exogenous market vector plus
shop/weather categories and predicts each route's margin.  It falls back to
CR029 (margin 0, a tie against itself) unless predicted advantage exceeds a
threshold. Hyperparameters are chosen on tune only and evaluated once on the
untouched validation panel.
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import statistics
import time
from pathlib import Path

import numpy as np
import kagsim

import cr049_live_king_knn_clone as c49

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr051_initial_route_selector.json"


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    lo, hi = int(spec["range_min"]), int(spec["range_max"])
    out = set()
    while len(out) < int(spec["count"]):
        out.add(r.randint(lo, hi))
    return sorted(out)


def frozen_routes(cfg: dict) -> list[dict]:
    sid = int(cfg["source_submission_id"])
    eps = c49.fetch_json(c49.LIST_URL, post={"submissionId": sid}).get("episodes") or []
    eps = [e for e in eps if e.get("state") == "COMPLETED" and e.get("endTime")]
    eps.sort(key=lambda e: e["endTime"], reverse=True)
    eps = eps[:40]
    if len(eps) != 40:
        raise RuntimeError(f"expected 40 frozen source episodes, got {len(eps)}")
    routes = []
    for i, meta in enumerate(eps):
        loaded = c49.episode_pairs(meta, sid)
        tape = [copy.deepcopy(p[2]) for p in loaded["pairs"]]
        if len(tape) != 719:
            raise RuntimeError(f"short tape episode {loaded['episode_id']}")
        routes.append({
            "route_index": i,
            "episode_id": int(loaded["episode_id"]),
            "seat": int(loaded["seat"]),
            "end_time": loaded["end_time"],
            "tape": tape,
        })
        if (i + 1) % 8 == 0:
            print(json.dumps({"routes_harvested": i + 1}))
    return routes


def initial_feature(seed: int, seat: int) -> tuple[np.ndarray, tuple[str, ...]]:
    g = kagsim.Game(int(seed))
    obs = g.observe(int(seat))
    vec, cats = c49.signature(obs)
    # Only exogenous information available before action 0: market prices,
    # market inventory/demand plus categorical shops/weather. Farm/private state
    # is essentially the common starting template and would add noise.
    return vec[223:250].astype(np.float32), tuple(cats)


def build_samples(seeds: list[int]) -> tuple[np.ndarray, list[tuple[str, ...]], list[tuple[int, int]]]:
    xs = []; cats = []; keys = []
    for seed in seeds:
        for seat in (0, 1):
            v, c = initial_feature(seed, seat)
            xs.append(v); cats.append(c); keys.append((int(seed), int(seat)))
    return np.stack(xs, axis=0), cats, keys


def evaluate_all_routes(routes: list[dict], base: list[dict], keys: list[tuple[int, int]]) -> np.ndarray:
    streams = [kagsim.Stream(r["tape"]) for r in routes]
    base_stream = kagsim.Stream(base)
    jobs = []
    meta = []
    for sample_i, (seed, seat) in enumerate(keys):
        for route_i, s in enumerate(streams):
            if seat == 0:
                jobs.append((s, base_stream, int(seed)))
            else:
                jobs.append((base_stream, s, int(seed)))
            meta.append((sample_i, route_i, seat))
    t0 = time.time()
    results = kagsim.run_many(jobs)
    margins = np.zeros((len(keys), len(routes)), dtype=np.float32)
    for result, (sample_i, route_i, seat) in zip(results, meta):
        a, b = float(result[0]), float(result[1])
        margins[sample_i, route_i] = (a - b) if seat == 0 else (b - a)
    print(json.dumps({"route_games": len(jobs), "elapsed_s": time.time() - t0}))
    return margins


def standardize(train_x: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = train_x.mean(axis=0)
    sd = train_x.std(axis=0)
    sd = np.where(sd < 1e-6, 1.0, sd)
    return (train_x - mu) / sd, (x - mu) / sd, sd


def predict_knn(train_x: np.ndarray, train_cats: list[tuple[str, ...]], train_y: np.ndarray,
                query_x: np.ndarray, query_cats: list[tuple[str, ...]], k: int,
                cat_penalty: float, batch: int = 128) -> np.ndarray:
    tx, qx, _ = standardize(train_x, query_x)
    out = np.empty((len(query_x), train_y.shape[1]), dtype=np.float32)
    for start in range(0, len(query_x), batch):
        q = qx[start:start + batch]
        # [B, N]
        d = np.sum((q[:, None, :] - tx[None, :, :]) ** 2, axis=2)
        if cat_penalty:
            for qi in range(q.shape[0]):
                qc = query_cats[start + qi]
                d[qi] += float(cat_penalty) * np.asarray(
                    [sum(a != b for a, b in zip(qc, tc)) for tc in train_cats],
                    dtype=np.float32,
                )
        kk = min(int(k), train_y.shape[0])
        nn = np.argpartition(d, kk - 1, axis=1)[:, :kk]
        for qi in range(q.shape[0]):
            out[start + qi] = train_y[nn[qi]].mean(axis=0)
    return out


def selector_metrics(pred: np.ndarray, actual: np.ndarray, threshold: float) -> dict:
    rows = []
    chosen = []
    for i in range(len(actual)):
        j = int(np.argmax(pred[i]))
        advantage = float(pred[i, j])
        if advantage > float(threshold):
            margin = float(actual[i, j]); route = j
        else:
            margin = 0.0; route = -1
        rows.append(margin); chosen.append(route)
    wins = sum(x > 0 for x in rows); losses = sum(x < 0 for x in rows); ties = len(rows) - wins - losses
    return {
        "samples": len(rows),
        "wins": wins, "losses": losses, "ties": ties,
        "score_rate": (wins + 0.5 * ties) / len(rows),
        "mean_margin": statistics.mean(rows),
        "median_margin": statistics.median(rows),
        "fallback_rate": sum(j < 0 for j in chosen) / len(chosen),
        "route_histogram": {str(j): chosen.count(j) for j in sorted(set(chosen))},
    }


def oracle_metrics(actual: np.ndarray) -> dict:
    ms = np.maximum(actual.max(axis=1), 0.0)
    wins = int(np.sum(ms > 0)); ties = int(np.sum(ms == 0)); losses = int(np.sum(ms < 0))
    return {
        "samples": len(ms), "wins": wins, "losses": losses, "ties": ties,
        "score_rate": float((wins + 0.5 * ties) / len(ms)),
        "mean_margin": float(np.mean(ms)),
        "median_margin": float(np.median(ms)),
    }


def best_static_index(train_y: np.ndarray) -> int:
    # Choose a route by training mean margin only; no validation peeking.
    return int(np.argmax(train_y.mean(axis=0)))


def static_metrics(actual: np.ndarray, j: int) -> dict:
    ms = actual[:, int(j)]
    wins = int(np.sum(ms > 0)); losses = int(np.sum(ms < 0)); ties = len(ms) - wins - losses
    return {
        "route_index": int(j), "samples": len(ms), "wins": wins, "losses": losses, "ties": ties,
        "score_rate": float((wins + 0.5 * ties) / len(ms)),
        "mean_margin": float(np.mean(ms)), "median_margin": float(np.median(ms)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7":
        raise RuntimeError("wrong kagsim engine")
    idle = kagsim.Stream([])
    if tuple(kagsim.run_episode(idle, idle, seed=11)) != (3000.0, 3000.0):
        raise RuntimeError("kagsim self-check failed")

    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base = bundle["recent_top"]["tape"]
    if len(base) != 719:
        raise RuntimeError(f"CR029 tape len={len(base)}")
    routes = frozen_routes(cfg)

    train_seeds = make_seeds(cfg["train_seed_generator"])
    tune_seeds = make_seeds(cfg["tune_seed_generator"])
    val_seeds = make_seeds(cfg["validation_seed_generator"])
    if set(train_seeds) & set(tune_seeds) or set(train_seeds) & set(val_seeds) or set(tune_seeds) & set(val_seeds):
        raise RuntimeError("seed panel overlap")

    train_x, train_c, train_keys = build_samples(train_seeds)
    tune_x, tune_c, tune_keys = build_samples(tune_seeds)
    val_x, val_c, val_keys = build_samples(val_seeds)
    train_y = evaluate_all_routes(routes, base, train_keys)
    tune_y = evaluate_all_routes(routes, base, tune_keys)
    val_y = evaluate_all_routes(routes, base, val_keys)

    grid_results = []
    best = None
    for k in cfg["selector_grid"]["k"]:
        for cp in cfg["selector_grid"]["categorical_penalty"]:
            pred = predict_knn(train_x, train_c, train_y, tune_x, tune_c, int(k), float(cp))
            for thr in cfg["selector_grid"]["fallback_margin_threshold"]:
                m = selector_metrics(pred, tune_y, float(thr))
                row = {"k": int(k), "categorical_penalty": float(cp),
                       "fallback_margin_threshold": float(thr), "metrics": m}
                grid_results.append(row)
                key = (m["score_rate"], m["mean_margin"], -m["fallback_rate"])
                if best is None or key > best[0]:
                    best = (key, row)
    chosen = best[1]

    # Refit references using train+tune after hyperparameters are frozen.
    ref_x = np.concatenate([train_x, tune_x], axis=0)
    ref_c = train_c + tune_c
    ref_y = np.concatenate([train_y, tune_y], axis=0)
    pred_val = predict_knn(ref_x, ref_c, ref_y, val_x, val_c,
                           int(chosen["k"]), float(chosen["categorical_penalty"]))
    val_selector = selector_metrics(pred_val, val_y, float(chosen["fallback_margin_threshold"]))

    bs = best_static_index(train_y)
    static_val = static_metrics(val_y, bs)
    oracle_val = oracle_metrics(val_y)
    gate = cfg["promotion_gate"]
    checks = {
        "validation_score_rate": val_selector["score_rate"] >= float(gate["min_validation_score_rate_vs_cr029"]),
        "validation_mean_margin": val_selector["mean_margin"] >= float(gate["min_validation_mean_margin"]),
        "gain_over_best_static": val_selector["score_rate"] - static_val["score_rate"] >= float(gate["min_gain_over_best_static_score_rate"]),
    }
    passed = all(checks.values())

    payload = {
        "experiment": cfg["experiment"],
        "engine": "1.32.7",
        "source_submission_id": int(cfg["source_submission_id"]),
        "route_episode_ids": [r["episode_id"] for r in routes],
        "route_count": len(routes),
        "train_seed_generator": cfg["train_seed_generator"],
        "tune_seed_generator": cfg["tune_seed_generator"],
        "validation_seed_generator": cfg["validation_seed_generator"],
        "tune_grid": grid_results,
        "chosen_selector": chosen,
        "validation_selector": val_selector,
        "validation_best_static": static_val,
        "validation_oracle": oracle_val,
        "checks": checks,
        "decision": "SHORTLIST_CR051_FOR_PACKAGE_PREFLIGHT" if passed else "CR051_INITIAL_ROUTE_SELECTOR_NOT_PROMOTED",
        "kaggle_hidden_test_touched": false,
        "automatic_kaggle_submission": false,
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
