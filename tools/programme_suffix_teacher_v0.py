#!/usr/bin/env python3
from __future__ import annotations

"""State-conditioned exact suffix-search gate over the public programme corpus.

The search never uses hidden seed/opponent identity as model input. Offline exact
counterfactuals may use simulator seeds to generate targets, but the router is fitted
only to current legal/public state + own private inventory features emitted by kagprog.

Candidate continuations are restricted to tapes with an EXACT executed prefix at each
checkpoint. This makes switching mechanically conservative: every candidate reaches the
same current state before its suffix is compared.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native" / "programme"))
import kagprog  # noqa: E402


def utility(margin):
    margin = np.asarray(margin, dtype=np.float64)
    win = (margin > 0).astype(np.float64) + 0.5 * (margin == 0)
    # Win dominates. Margin remains informative when every continuation loses.
    return win + 0.30 * np.tanh(margin / 40000.0)


def leaf_action(U, idx):
    if len(idx) == 0:
        return 0, -1e300
    sums = U[idx].sum(axis=0)
    action = int(np.argmax(sums))
    return action, float(sums[action])


def fit_tree(X, U, idx, depth, max_depth, min_leaf):
    action, base = leaf_action(U, idx)
    node = {"action": action, "n": int(len(idx))}
    if depth >= max_depth or len(idx) < 2 * min_leaf:
        return node

    best_gain = 1e-9
    best = None
    for feature in range(X.shape[1]):
        values = X[idx, feature]
        lo = float(np.min(values))
        hi = float(np.max(values))
        if not np.isfinite(lo + hi) or hi <= lo:
            continue
        thresholds = np.unique(np.quantile(values, [0.25, 0.50, 0.75]))
        for threshold in thresholds:
            mask = values <= threshold
            nl = int(mask.sum())
            nr = len(idx) - nl
            if nl < min_leaf or nr < min_leaf:
                continue
            left_idx = idx[mask]
            right_idx = idx[~mask]
            _, left_value = leaf_action(U, left_idx)
            _, right_value = leaf_action(U, right_idx)
            gain = left_value + right_value - base
            if gain > best_gain:
                best_gain = gain
                best = (feature, float(threshold), left_idx, right_idx)

    if best is None:
        return node

    feature, threshold, left_idx, right_idx = best
    node.update({
        "feature": int(feature),
        "threshold": threshold,
        "gain_per_sample": float(best_gain / len(idx)),
        "left": fit_tree(X, U, left_idx, depth + 1, max_depth, min_leaf),
        "right": fit_tree(X, U, right_idx, depth + 1, max_depth, min_leaf),
    })
    return node


def predict(tree, X):
    out = np.empty(len(X), dtype=np.int32)
    for i, row in enumerate(X):
        node = tree
        while "feature" in node:
            node = node["left"] if row[node["feature"]] <= node["threshold"] else node["right"]
        out[i] = int(node["action"])
    return out


def eval_choice(margins, U, choice):
    ix = np.arange(len(choice))
    selected_margin = margins[ix, choice]
    selected_u = U[ix, choice]
    return {
        "utility": float(np.mean(selected_u)),
        "win_rate": float(np.mean(selected_margin > 0) + 0.5 * np.mean(selected_margin == 0)),
        "mean_margin": float(np.mean(selected_margin)),
        "median_margin": float(np.median(selected_margin)),
        "p10_margin": float(np.quantile(selected_margin, 0.10)),
    }


def prefix_groups(tapes, checkpoint, min_group):
    groups = {}
    for i, tape in enumerate(tapes):
        digest = hashlib.sha256(np.ascontiguousarray(tape[:checkpoint]).tobytes()).hexdigest()
        groups.setdefault(digest, []).append(i)
    return [members for members in groups.values() if len(members) >= min_group]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="runs/public_programme_corpus_v1/PROGRAMME_CORPUS.npz")
    ap.add_argument("--manifest", default="runs/public_programme_corpus_v1/PROGRAMME_CORPUS.json")
    ap.add_argument("--checkpoints", default="144,168,192,216,240")
    ap.add_argument("--train-seeds", type=int, default=6)
    ap.add_argument("--holdout-seeds", type=int, default=6)
    ap.add_argument("--min-group", type=int, default=2)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--out", default="runs/programme_suffix_teacher_v0/PROGRAMME_SUFFIX_TEACHER.json")
    args = ap.parse_args()

    if args.train_seeds < 1 or args.holdout_seeds < 1:
        raise ValueError("train and holdout seeds must both be positive")
    corpus = np.load(ROOT / args.corpus)
    tapes = np.asarray(corpus["tapes"], dtype=np.int32)
    manifest = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))

    if tapes.ndim != 3 or tapes.shape[1:] != (719, int(kagprog.ACTION_WIDTH)):
        raise RuntimeError(f"bad programme corpus shape: {tapes.shape}")

    checkpoints = [int(x) for x in args.checkpoints.split(",") if x]
    seeds = np.arange(
        51001,
        51001 + args.train_seeds + args.holdout_seeds,
        dtype=np.uint64,
    )
    S = len(seeds)
    M = len(tapes)

    print("PROGRAMME_TEACHER_START", json.dumps({
        "engine": str(kagprog.ENGINE_VERSION),
        "schema": str(kagprog.SCHEMA),
        "programmes": M,
        "checkpoints": checkpoints,
        "train_seeds": args.train_seeds,
        "holdout_seeds": args.holdout_seeds,
        "feature_width": int(kagprog.FEATURE_WIDTH),
    }, sort_keys=True), flush=True)

    start = time.perf_counter()
    raw = kagprog.evaluate_matrix(
        tapes, tapes, [int(x) for x in seeds], args.threads
    )
    matrix = np.asarray(raw["margin"], dtype=np.float64)

    print("PROGRAMME_MATRIX", json.dumps({
        "episodes": int(M * M * S * 2),
        "eps": float(raw["episodes_per_second"]),
        "seconds": float(raw["seconds"]),
    }, sort_keys=True), flush=True)

    # Ordering used by kagprog.prefix_features: opponent, seed, seat.
    opponent_index = np.repeat(np.arange(M), S * 2)
    seed_index = np.tile(np.repeat(np.arange(S), 2), M)
    seat_index = np.tile(np.array([0, 1]), M * S)
    train_mask = seed_index < args.train_seeds
    holdout_mask = ~train_mask

    group_rows = []
    counterfactual_targets = {}
    ds_features = []
    ds_checkpoint = []
    ds_group = []
    ds_oracle = []
    ds_tree = []
    ds_static = []
    ds_oracle_margin = []
    ds_tree_margin = []
    ds_static_margin = []
    ds_holdout = []
    ds_opponent = []
    ds_seed = []
    ds_seat = []

    group_id = 0
    for checkpoint in checkpoints:
        groups = prefix_groups(tapes, checkpoint, args.min_group)
        for members_list in groups:
            members = np.asarray(members_list, dtype=np.int32)
            representative = int(members[0])

            # Exact prefix equality means this one state trace is valid for every
            # candidate continuation in the group.
            X = np.asarray(
                kagprog.prefix_features(
                    tapes[representative],
                    tapes,
                    [int(x) for x in seeds],
                    checkpoint,
                    args.threads,
                ),
                dtype=np.float32,
            )

            # [candidate, opponent, seed, seat] -> [scenario, candidate]
            R = np.transpose(matrix[members], (1, 2, 3, 0)).reshape(
                M * S * 2, len(members)
            )
            U = utility(R)
            if not np.isfinite(X).all() or not np.isfinite(R).all():
                raise RuntimeError("non-finite features or counterfactual returns")
            counterfactual_targets[f"group_{group_id}_programs"] = members
            counterfactual_targets[f"group_{group_id}_margins"] = R.astype(np.float32)

            train_idx = np.flatnonzero(train_mask)
            test_idx = np.flatnonzero(holdout_mask)

            static_local = int(np.argmax(U[train_idx].mean(axis=0)))
            static_choice = np.full(len(test_idx), static_local, dtype=np.int32)

            min_leaf = max(12, min(48, len(train_idx) // 20))
            tree = fit_tree(
                X, U, train_idx, 0, args.max_depth, min_leaf
            )
            tree_choice = predict(tree, X[test_idx])
            oracle_choice = np.argmax(U[test_idx], axis=1).astype(np.int32)

            static_stats = eval_choice(
                R[test_idx], U[test_idx], static_choice
            )
            tree_stats = eval_choice(
                R[test_idx], U[test_idx], tree_choice
            )
            oracle_stats = eval_choice(
                R[test_idx], U[test_idx], oracle_choice
            )

            row = {
                "group_id": group_id,
                "checkpoint": checkpoint,
                "members": [int(x) for x in members],
                "size": int(len(members)),
                "representative": representative,
                "static_program": int(members[static_local]),
                "static": static_stats,
                "tree": tree_stats,
                "oracle": oracle_stats,
                "tree_delta_utility": tree_stats["utility"] - static_stats["utility"],
                "oracle_headroom_utility": oracle_stats["utility"] - static_stats["utility"],
                "tree_model": tree,
            }
            group_rows.append(row)

            print("PROGRAMME_GROUP", json.dumps({
                k: v for k, v in row.items()
                if k not in {"members", "tree_model"}
            }, sort_keys=True), flush=True)

            # Save counterfactual teacher targets. scenario_seed is provenance only;
            # it is never present in X and therefore cannot leak to the runtime model.
            all_oracle = np.argmax(U, axis=1).astype(np.int32)
            all_tree = predict(tree, X)
            all_static = np.full(len(X), static_local, dtype=np.int32)
            ix = np.arange(len(X))

            ds_features.append(X)
            ds_checkpoint.append(np.full(len(X), checkpoint, dtype=np.int16))
            ds_group.append(np.full(len(X), group_id, dtype=np.int16))
            ds_oracle.append(members[all_oracle])
            ds_tree.append(members[all_tree])
            ds_static.append(members[all_static])
            ds_oracle_margin.append(R[ix, all_oracle].astype(np.float32))
            ds_tree_margin.append(R[ix, all_tree].astype(np.float32))
            ds_static_margin.append(R[ix, all_static].astype(np.float32))
            ds_holdout.append(holdout_mask.astype(np.uint8))
            ds_opponent.append(opponent_index.astype(np.int16))
            ds_seed.append(seeds[seed_index])
            ds_seat.append(seat_index.astype(np.uint8))
            group_id += 1

    if not group_rows:
        raise RuntimeError("no prefix-compatible programme groups found")

    # Equal weighting by decision group prevents the largest bank from completely
    # erasing smaller but distinct programme families.
    static_utility = float(np.mean([r["static"]["utility"] for r in group_rows]))
    tree_utility = float(np.mean([r["tree"]["utility"] for r in group_rows]))
    oracle_utility = float(np.mean([r["oracle"]["utility"] for r in group_rows]))
    static_wr = float(np.mean([r["static"]["win_rate"] for r in group_rows]))
    tree_wr = float(np.mean([r["tree"]["win_rate"] for r in group_rows]))
    oracle_wr = float(np.mean([r["oracle"]["win_rate"] for r in group_rows]))

    aggregate = {
        "static_utility": static_utility,
        "tree_utility": tree_utility,
        "oracle_utility": oracle_utility,
        "tree_delta_vs_static": tree_utility - static_utility,
        "oracle_headroom_vs_static": oracle_utility - static_utility,
        "static_win_rate": static_wr,
        "tree_win_rate": tree_wr,
        "oracle_win_rate": oracle_wr,
    }

    result = {
        "schema": "kculture-programme-suffix-teacher-v0",
        "gate_scope": "infrastructure_only_not_strategic_promotion",
        "generalization_scope": "new_seeds_same_static_opponent_bank",
        "corpus_sha256": hashlib.sha256((ROOT / args.corpus).read_bytes()).hexdigest(),
        "feature_runtime_parity": "pending",
        "engine_version": str(kagprog.ENGINE_VERSION),
        "programmes": M,
        "source_notebooks": manifest["notebooks"],
        "unique_sources": manifest["unique_sources"],
        "checkpoints": checkpoints,
        "groups": len(group_rows),
        "matrix_eps": float(raw["episodes_per_second"]),
        "group_results": group_rows,
        "aggregate": aggregate,
        "elapsed_seconds": time.perf_counter() - start,
        # Infrastructure/search gate only. Hosted strength is still unknown.
        "pass": bool(
            np.isfinite([static_utility, tree_utility, oracle_utility]).all()
            and oracle_utility >= static_utility - 1e-9
        ),
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    np.savez_compressed(
        out.with_name("PROGRAMME_TEACHER_DATA.npz"),
        **counterfactual_targets,
        features=np.concatenate(ds_features),
        checkpoint=np.concatenate(ds_checkpoint),
        group=np.concatenate(ds_group),
        oracle_program=np.concatenate(ds_oracle),
        tree_program=np.concatenate(ds_tree),
        static_program=np.concatenate(ds_static),
        oracle_margin=np.concatenate(ds_oracle_margin),
        tree_margin=np.concatenate(ds_tree_margin),
        static_margin=np.concatenate(ds_static_margin),
        holdout=np.concatenate(ds_holdout),
        opponent_program=np.concatenate(ds_opponent),
        scenario_seed=np.concatenate(ds_seed),
        seat=np.concatenate(ds_seat),
    )

    print("PROGRAMME_TEACHER_RESULT", json.dumps({
        "pass": result["pass"],
        "groups": result["groups"],
        **aggregate,
        "states": int(sum(len(x) for x in ds_features)),
        "seconds": result["elapsed_seconds"],
        "out": str(out),
    }, sort_keys=True), flush=True)

    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
