#!/usr/bin/env python3
"""Materialize the frozen V22B hard-context config from a binding V22A result.

This is a mechanical transformer only:
- requires V22A_FRESH_FRONTIER_HARD_POPULATION_READY;
- requires exact frozen V22A seeds/seats;
- uses all and only rows with score < 1.0;
- deterministic ordering/context IDs;
- no outcome-driven subset selection beyond the pre-registered non-win definition.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_SEEDS = [79101, 79102, 79103, 79104, 79105, 79106]
EXPECTED_SEATS = [0, 1]
EXPECTED_DECISION = "V22A_FRESH_FRONTIER_HARD_POPULATION_READY"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v22a", required=True)
    ap.add_argument("--workflow-id", type=int, required=True)
    ap.add_argument("--artifact-id", type=int, required=True)
    ap.add_argument("--artifact-digest", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = json.loads(Path(args.v22a).read_text())

    errors = []
    if not bool(src.get("mechanical_pass")):
        errors.append("V22A mechanical_pass is false")
    if src.get("decision") != EXPECTED_DECISION:
        errors.append(f"V22A decision is {src.get('decision')!r}, expected {EXPECTED_DECISION!r}")
    if list(src.get("discovery_seeds") or []) != EXPECTED_SEEDS:
        errors.append("V22A discovery seeds do not match frozen 79101..79106")
    if list(src.get("seats") or []) != EXPECTED_SEATS:
        errors.append("V22A seats do not match frozen [0,1]")
    if src.get("top30_acquisition_failures"):
        errors.append("V22A contains acquisition failures")
    if src.get("smoke_failures"):
        errors.append("V22A contains smoke failures")
    if src.get("episode_failures"):
        errors.append("V22A contains episode failures")

    rows = list(src.get("rows") or [])
    if len(rows) != int(src.get("completed_games", -1)):
        errors.append("V22A row count != completed_games")

    hard = [r for r in rows if float(r["score"]) < 1.0]
    hard_shas = sorted({str(r["main_sha256"]) for r in hard})
    hard_seeds = sorted({int(r["seed"]) for r in hard})

    if len(hard) < 12:
        errors.append(f"hard contexts {len(hard)} < 12")
    if len(hard_shas) < 4:
        errors.append(f"hard source SHAs {len(hard_shas)} < 4")
    if len(hard_seeds) < 3:
        errors.append(f"hard seeds {len(hard_seeds)} < 3")

    selected_reps = {
        str(r["main_sha256"]): r
        for r in list(src.get("selected_representatives") or [])
    }

    hard_sorted = sorted(
        hard,
        key=lambda r: (
            int(r["rank"]),
            str(r["main_sha256"]),
            int(r["seed"]),
            int(r["seat"]),
        ),
    )

    contexts = []
    seen = set()
    for i, r in enumerate(hard_sorted):
        key = (str(r["main_sha256"]), int(r["seed"]), int(r["seat"]))
        if key in seen:
            errors.append(f"duplicate hard context key {key}")
            continue
        seen.add(key)

        sha = str(r["main_sha256"])
        rep = selected_reps.get(sha)
        if rep is None:
            errors.append(f"hard row SHA not in selected representatives: {sha}")
            continue
        if str(rep.get("representative_ref")) != str(r["ref"]):
            errors.append(
                f"hard row ref mismatch for {sha}: {r['ref']} != {rep.get('representative_ref')}"
            )
            continue

        contexts.append(
            {
                "context_id": f"v22a_hard_{i:03d}",
                "rank": int(r["rank"]),
                "ref": str(r["ref"]),
                "main_sha256": sha,
                "seed": int(r["seed"]),
                "seat": int(r["seat"]),
                "base_score": float(r["score"]),
                "base_margin": float(r["margin"]),
                "base_result": str(r["result"]),
            }
        )

    if errors:
        result = {
            "schema": "kculture-all3-v22b-hard-config-materialization-v1",
            "mechanical_pass": False,
            "errors": errors,
            "automatic_kaggle_submission": False,
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print("V22B_HARD_CONFIG_RESULT", json.dumps(result, sort_keys=True))
        raise SystemExit(2)

    result = {
        "schema": "kculture-all3-v22b-hard-context-config-v1",
        "source_v22a_workflow": int(args.workflow_id),
        "source_v22a_artifact_id": int(args.artifact_id),
        "source_v22a_artifact_digest": str(args.artifact_digest),
        "source_v22a_decision": src["decision"],
        "source_v22a_expected_games": int(src["expected_games"]),
        "source_v22a_completed_games": int(src["completed_games"]),
        "source_v22a_selected_representatives": [
            {
                "rank": int(r["representative_rank"]),
                "ref": str(r["representative_ref"]),
                "main_sha256": str(r["main_sha256"]),
            }
            for r in list(src.get("selected_representatives") or [])
        ],
        "frozen_discovery_seeds": EXPECTED_SEEDS,
        "frozen_seats": EXPECTED_SEATS,
        "hard_context_count": len(contexts),
        "hard_source_shas": hard_shas,
        "hard_seeds": hard_seeds,
        "hard_contexts": contexts,
        "selection_rule": "all and only binding V22A rows with score < 1.0",
        "manual_context_selection_allowed": False,
        "automatic_kaggle_submission": False,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        "V22B_HARD_CONFIG_RESULT",
        json.dumps(
            {
                "mechanical_pass": True,
                "hard_contexts": len(contexts),
                "hard_sources": len(hard_shas),
                "hard_seeds": len(hard_seeds),
                "source_v22a_workflow": int(args.workflow_id),
            },
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
