#!/usr/bin/env python3
"""Aggregate frozen CR089 heterogeneous population H2H edges."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--opponents", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    candidates = [x for x in args.candidates.split(",") if x]
    opponents = [x for x in args.opponents.split(",") if x]
    rows = []
    for path in Path(args.input_dir).glob("**/result.json"):
        payload = json.loads(path.read_text())
        metric = payload["metrics_a_vs_b"]
        rows.append({
            "candidate": payload["a"],
            "opponent": payload["b"],
            "games": metric["games"],
            "wins": metric["wins"],
            "losses": metric["losses"],
            "ties": metric["ties"],
            "score_rate": metric["score_rate"],
            "mean_margin": metric["mean_margin_secondary"],
            "non_done": metric["non_done_games"],
            "errors": len(payload.get("errors") or []),
            "seat_floor": min(
                0.0 if x.get("score_rate") is None else float(x["score_rate"])
                for x in payload["metrics_by_a_seat"].values()
            ),
        })

    expected = {(a, b) for a in candidates for b in opponents}
    observed = {(r["candidate"], r["opponent"]) for r in rows}
    if observed != expected:
        raise RuntimeError({"missing": sorted(expected - observed), "extra": sorted(observed - expected)})

    summaries = []
    for candidate in candidates:
        edges = sorted((r for r in rows if r["candidate"] == candidate), key=lambda x: opponents.index(x["opponent"]))
        scores = [float(r["score_rate"]) for r in edges]
        valid = all(r["games"] == 12 and r["errors"] == 0 and r["non_done"] == 0 for r in edges)
        summary = {
            "candidate": candidate,
            "mechanically_valid": valid,
            "mean_edge_score": statistics.mean(scores),
            "median_edge_score": statistics.median(scores),
            "worst_edge_score": min(scores),
            "seat_floor": min(r["seat_floor"] for r in edges),
            "edges_at_least_0_25": sum(x >= 0.25 for x in scores),
            "edges_at_least_0_50": sum(x >= 0.50 for x in scores),
            "zero_score_edges": sum(x == 0.0 for x in scores),
            "eligible_population_survivor": bool(
                valid
                and statistics.mean(scores) >= 0.45
                and sum(x >= 0.25 for x in scores) >= len(opponents) - 3
                and sum(x == 0.0 for x in scores) <= 3
                and min(r["seat_floor"] for r in edges) >= 1.0 / 6.0
            ),
            "edges": edges,
        }
        summaries.append(summary)

    comparison = None
    by_name = {x["candidate"]: x for x in summaries}
    if {"C5_BASE", "C5_M6S1"}.issubset(by_name):
        base_edges = {x["opponent"]: x for x in by_name["C5_BASE"]["edges"]}
        crop_edges = {x["opponent"]: x for x in by_name["C5_M6S1"]["edges"]}
        deltas = [crop_edges[o]["score_rate"] - base_edges[o]["score_rate"] for o in opponents]
        comparison = {
            "treatment": "C5_M6S1",
            "control": "C5_BASE",
            "mean_edge_score_delta": statistics.mean(deltas),
            "median_edge_score_delta": statistics.median(deltas),
            "improved_edges": sum(x > 0 for x in deltas),
            "tied_edges": sum(x == 0 for x in deltas),
            "regressed_edges": sum(x < 0 for x in deltas),
            "severe_regressions": sum(x <= -0.25 for x in deltas),
            "new_zero_score_edges": sum(crop_edges[o]["score_rate"] == 0.0 and base_edges[o]["score_rate"] > 0.0 for o in opponents),
            "by_opponent": {o: deltas[i] for i, o in enumerate(opponents)},
        }
        transfer_pass = bool(
            by_name["C5_M6S1"]["eligible_population_survivor"]
            and comparison["mean_edge_score_delta"] >= 0.05
            and comparison["median_edge_score_delta"] >= 0.0
            and comparison["regressed_edges"] <= 3
            and comparison["severe_regressions"] <= 2
            and comparison["new_zero_score_edges"] == 0
        )
        comparison["population_transfer_pass"] = transfer_pass
        if transfer_pass:
            decision = "ADVANCE_C5_M6S1_TO_MARKET_FACTORIAL"
        elif by_name["C5_M6S1"]["eligible_population_survivor"]:
            decision = "M6S1_ABSOLUTE_SAFE_BUT_NO_CAUSAL_POPULATION_GAIN"
        else:
            decision = "M6S1_FAILS_POPULATION_COMPATIBILITY"
    else:
        eligible = [x for x in summaries if x["eligible_population_survivor"]]
        eligible.sort(key=lambda x: (x["mean_edge_score"], x["median_edge_score"], x["worst_edge_score"]), reverse=True)
        decision = "PHYSICAL_ARCHITECTURE_FAIL_POPULATION_COMPATIBILITY" if not eligible else f"ADVANCE_{eligible[0]['candidate']}_TO_MARKET_FACTORIAL"

    out = {
        "schema": "cr089-heterogeneous-population-gate-v1",
        "master_seed": 9270915,
        "seeds_per_edge": 6,
        "candidates": candidates,
        "opponents": opponents,
        "summaries": summaries,
        "treatment_vs_control": comparison,
        "decision": decision,
        "interpretation_limit": "Mechanics/catastrophe/coverage gate; local ordering is not a hosted population rating predictor.",
        "automatic_submission": False,
        "held_out_touched": False,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
