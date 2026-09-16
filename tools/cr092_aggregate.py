#!/usr/bin/env python3
"""Aggregate CR092 broad O1 edges and freeze counterfactual router labels."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median

EXACT = {"CR053_REAL", "CR052_REAL", "CR083", "CR086"}
MACROS = {
    "r01_e108766633_s56156662",
    "r02_e108761464_s56114097",
    "r03_e108766659_s56209748",
    "r06_e108754069_s56205640",
    "r07_e108766657_s56132899",
    "r09_e108766659_s56097405",
    "r10_e108754200_s56210228",
}
EXPECTED_OPPONENTS = EXACT | MACROS


def load_edges(root: Path):
    payloads = []
    # actions/download-artifact with merge-multiple may retain a nested
    # `artifacts/` directory from each uploaded edge. Search recursively so the
    # aggregation semantics are invariant to that transport-only layout.
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") == "cr092-broad-option-edge-v1":
            payloads.append((path, data))
    by = {data["opponent"]: (path, data) for path, data in payloads}
    missing = sorted(EXPECTED_OPPONENTS - set(by))
    extra = sorted(set(by) - EXPECTED_OPPONENTS)
    if missing or extra:
        raise SystemExit(f"CR092 edge set mismatch missing={missing} extra={extra}")
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--labels", required=True)
    args = ap.parse_args()

    by = load_edges(Path(args.input_dir))
    edges = {}
    mechanics_failures = []
    total_episode_failures = 0
    total_violations = 0
    total_reorders = 0
    all_rows = []

    for opponent in sorted(by):
        path, data = by[opponent]
        m = data["mechanics"]
        if not m.get("mechanics_pass"):
            mechanics_failures.append(opponent)
        total_episode_failures += int(m.get("failures", 0))
        total_violations += int(m.get("violations", 0))
        total_reorders += int(m.get("o1_reorders", 0))
        all_rows.extend(data.get("rows", []))
        edges[opponent] = {
            "CR053_BASE": data["summaries"]["CR053_BASE"],
            "CR053_O1": data["summaries"]["CR053_O1"],
            "delta": data["edge_score_delta_o1_minus_base"],
            "mechanics": m,
            "artifact_source_file": path.name,
        }

    mechanics_pass = (
        not mechanics_failures
        and total_episode_failures == 0
        and total_violations == 0
        and len(all_rows) == 264
    )
    option_active = total_reorders > 0

    paired = {}
    for row in all_rows:
        key = (row["opponent"], int(row["seed"]), int(row["seat"]))
        paired.setdefault(key, {})[row["treatment"]] = row

    labels = []
    rejected_branch_mismatch = []
    incomplete_pairs = []
    no_reorder_pairs = 0

    for key in sorted(paired):
        treatments = paired[key]
        base = treatments.get("CR053_BASE")
        o1 = treatments.get("CR053_O1")
        opponent, seed, seat = key
        if base is None or o1 is None:
            incomplete_pairs.append({"opponent": opponent, "seed": seed, "seat": seat})
            continue
        if not base.get("done") or not o1.get("done"):
            continue
        first_step = o1.get("first_reorder_step")
        if first_step is None:
            no_reorder_pairs += 1
            continue

        o1_hash = o1.get("first_reorder_observation_hash")
        base_hash = (base.get("observation_hashes") or {}).get(str(first_step))
        branch_match = bool(o1_hash and base_hash and o1_hash == base_hash)
        record = {
            "opponent_stratum_metadata_only": opponent,
            "seed_metadata_only": seed,
            "seat_metadata_only": seat,
            "first_reorder_step": int(first_step),
            "branch_state_hash": o1_hash,
            "base_same_step_hash": base_hash,
            "branch_state_match": branch_match,
            "wl_base": float(base["outcome"]),
            "wl_o1": float(o1["outcome"]),
            "wl_delta": float(o1["outcome"] - base["outcome"]),
            "margin_base_diagnostic": float(base["margin"]),
            "margin_o1_diagnostic": float(o1["margin"]),
            "margin_delta_diagnostic": float(o1["margin"] - base["margin"]),
            "legal_branch_observation": o1.get("first_reorder_observation"),
            "legal_cr086_derived_state": o1.get("first_reorder_latent_state"),
        }
        if branch_match:
            labels.append(record)
        else:
            rejected_branch_mismatch.append(record)

    positive = [r for r in labels if r["wl_delta"] > 0]
    negative = [r for r in labels if r["wl_delta"] < 0]
    zero = [r for r in labels if r["wl_delta"] == 0]
    positive_strata = sorted({r["opponent_stratum_metadata_only"] for r in positive})
    negative_strata = sorted({r["opponent_stratum_metadata_only"] for r in negative})

    deltas = {opp: float(edges[opp]["delta"]) for opp in sorted(edges)}
    numeric = list(deltas.values())
    macro_deltas = [deltas[opp] for opp in sorted(MACROS)]
    mean_delta = mean(numeric)
    median_delta = median(numeric)
    macro_mean_delta = mean(macro_deltas)
    nonnegative_edges = sum(x >= 0 for x in numeric)
    positive_edges = sum(x > 0 for x in numeric)
    regressed_edges = sum(x < 0 for x in numeric)
    max_improvement = max(numeric)
    worst_regression = min(numeric)

    catastrophe_edges = []
    for opponent in sorted(edges):
        base_score = edges[opponent]["CR053_BASE"]["score"]
        o1_score = edges[opponent]["CR053_O1"]["score"]
        if base_score is not None and o1_score is not None and base_score >= 0.25 and o1_score == 0.0:
            catastrophe_edges.append(opponent)

    broad_survival = (
        mechanics_pass
        and option_active
        and len(numeric) == 11
        and mean_delta >= 0.02
        and nonnegative_edges >= 8
        and worst_regression >= -0.125
        and macro_mean_delta >= 0.0
        and not catastrophe_edges
    )

    routing_signal = (
        mechanics_pass
        and option_active
        and len(positive) >= 8
        and len(negative) >= 8
        and len(positive_strata) >= 2
        and len(negative_strata) >= 2
    )

    if not mechanics_pass:
        decision = "CR092_MECHANICS_FAIL_NO_STRATEGIC_VERDICT"
    elif not option_active:
        decision = "CR092_OPTION_DORMANT_NO_STRATEGIC_VERDICT"
    elif broad_survival and routing_signal:
        decision = "CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER"
    elif broad_survival:
        decision = "CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION"
    elif routing_signal and max_improvement >= 0.125 and worst_regression <= -0.125:
        decision = "CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY"
    else:
        decision = "CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1"

    labels_payload = {
        "schema": "cr092-counterfactual-router-labels-v1",
        "feature_legality": "public/shared state + controlled player's own private state + mechanics-derived CR086 state only",
        "runtime_opponent_identity_feature": False,
        "runtime_hidden_seed_feature": False,
        "label": "wl_delta_o1_minus_base",
        "labels": labels,
        "rejected_branch_state_mismatches": rejected_branch_mismatch,
        "no_reorder_pairs": no_reorder_pairs,
        "incomplete_pairs": incomplete_pairs,
        "held_out_touched": False,
    }

    result = {
        "schema": "cr092-broad-option-router-label-gate-v1",
        "engine": "kaggle-environments==1.32.7",
        "seeds": [91401, 91402, 91403, 91404, 91405, 91406],
        "opponents": sorted(EXPECTED_OPPONENTS),
        "episodes_total": len(all_rows),
        "mechanics": {
            "mechanics_pass": mechanics_pass,
            "failed_edges": mechanics_failures,
            "episode_failures": total_episode_failures,
            "violations": total_violations,
            "o1_reorders": total_reorders,
            "option_active": option_active,
        },
        "edges": edges,
        "edge_score_deltas_o1_minus_base": deltas,
        "gate": {
            "mean_edge_score_delta": mean_delta,
            "median_edge_score_delta": median_delta,
            "macro_mean_edge_score_delta": macro_mean_delta,
            "positive_edges": positive_edges,
            "nonnegative_edges": nonnegative_edges,
            "regressed_edges": regressed_edges,
            "max_improvement": max_improvement,
            "worst_regression": worst_regression,
            "catastrophe_edges": catastrophe_edges,
            "broad_survival": broad_survival,
        },
        "router_labels": {
            "admissible": len(labels),
            "positive": len(positive),
            "zero": len(zero),
            "negative": len(negative),
            "positive_strata": positive_strata,
            "negative_strata": negative_strata,
            "rejected_branch_state_mismatches": len(rejected_branch_mismatch),
            "no_reorder_pairs": no_reorder_pairs,
            "incomplete_pairs": len(incomplete_pairs),
            "routing_signal": routing_signal,
        },
        "decision": decision,
        "held_out_touched": False,
        "automatic_submission": False,
    }

    labels_path = Path(args.labels)
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.write_text(json.dumps(labels_payload, indent=2, sort_keys=True), encoding="utf-8")

    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("CR092_RESULT", json.dumps(result, sort_keys=True), flush=True)
    print("CR092_DECISION", decision, flush=True)
    print("CR092_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
