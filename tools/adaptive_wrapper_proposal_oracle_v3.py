#!/usr/bin/env python3
"""Diverse adaptive-wrapper proposal oracle V3.

V47 remains the executed organism. A larger panel of strong public agents runs in
shadow mode on the exact same live observation. A proposal is admissible only when
farmer + hands exactly equal V47 and only market differs. The official exact engine
then evaluates each unique one-turn proposal, after which V47 resumes.

Purpose: discover W/L headroom outside the V47-family stratum before inventing more
handwritten options or fitting a larger selector.

Offline only. Third-party source is transient and never persisted by this script.
"""
from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from tools.adaptive_wrapper_proposal_oracle_v2 import (
    EXPECTED_ENGINE,
    BASE,
    acquire,
    run_discovery,
    run_base,
    run_branch,
    select_events,
    summarize,
    purge_all,
)
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS

PROPOSERS = [
    {
        "key": "ready_stock",
        "handle": "alperen5252525/kaggriculture-ready-stock-earlier-sales",
        "expected_main_sha256": "45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017",
    },
    {
        "key": "market_smart",
        "handle": "tetsutani/market-smart-farming-kaggriculture",
        "expected_main_sha256": "f6a756cfb900b9d5f499905d596b63f1fde2445342ac4b1ae04e353739bd62d2",
    },
    {
        "key": "v46_microstructure",
        "handle": "ahmedberatozer/kaggriculture-v46-first-turn-microstructure-and-s",
        "expected_main_sha256": "735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6",
    },
    {
        "key": "v48_queue",
        "handle": "ahmedberatozer/kaggriculture-v48-clear-the-queue",
        "expected_main_sha256": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    },
    {
        "key": "shop_aware",
        "handle": "tetsutani/shop-aware-farming-kaggriculture",
        "expected_main_sha256": "411875c97d6a178ec4df59b696b13708ba2fac754cae924851395a0578ca983d",
    },
    {
        "key": "router_2715",
        "handle": "nusrati/2715-6",
        "expected_main_sha256": "66585d1a5dbfe11c946a3c400278592f860342bc4a8f5e5f87f2a9293348984b",
    },
    {
        "key": "conditional_memory",
        "handle": "ravi123a321at/177-180-fresh-top-30-v21-1-conditional-memory",
        "expected_main_sha256": "d9dc24ce5429ec628ead0621a160bee90725350683d7dfcc4686fcaf511f3aab",
    },
    {
        "key": "tactical_memory",
        "handle": "web3cainiao/kaggriculture-v21-tactical-memory",
        "expected_main_sha256": "630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054",
    },
    {
        "key": "best_market",
        "handle": "reyhanksatria/best-market-agent-high-strategy",
        "expected_main_sha256": "d39dba50793d9777c990347443bf0c481c78adaea86055f6f6b0600dcfcd9f2e",
    },
]
SEEDS = [72001, 72002]
MODERN41_KEYS = {"v47_mirror", "ready_stock", "v48"}
MIN_BRANCH_STATES = 20


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/adaptive-wrapper-proposal-v3/ADAPTIVE_WRAPPER_PROPOSAL_V3.json",
    )
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit(
            f"kaggle-environments mismatch: {getattr(kaggle_environments,'__version__',None)}"
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    failures: list[dict] = []
    rows: list[dict] = []
    matchup_receipts: list[dict] = []
    provenance: dict[str, Any] = {}
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="adaptive-wrapper-proposal-v3-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")

            paths_by_sha = {BASE["expected_main_sha256"]: base_main}
            proposer_paths: dict[str, Path] = {}
            for spec in PROPOSERS:
                sha = spec["expected_main_sha256"]
                if sha in paths_by_sha:
                    p = paths_by_sha[sha]
                    proposer_paths[spec["key"]] = p
                    provenance[spec["key"]] = {
                        "key": spec["key"],
                        "handle": spec["handle"],
                        "expected_main_sha256": sha,
                        "observed_main_sha256": sha,
                        "reused_exact_bytes": True,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"proposal_{spec['key']}")
                    proposer_paths[spec["key"]] = p
                    paths_by_sha[sha] = p
                    provenance[spec["key"]] = rec

            opponent_paths: dict[str, Path] = {}
            for spec in V2_OPPONENTS:
                sha = spec["expected_main_sha256"]
                if sha in paths_by_sha:
                    p = paths_by_sha[sha]
                    opponent_paths[spec["key"]] = p
                    provenance[f"opp_{spec['key']}"] = {
                        "key": spec["key"],
                        "handle": spec["handle"],
                        "expected_main_sha256": sha,
                        "observed_main_sha256": sha,
                        "family": spec.get("family"),
                        "reused_exact_bytes": True,
                    }
                else:
                    p, rec = acquire(spec, tmp / f"opp_{spec['key']}")
                    opponent_paths[spec["key"]] = p
                    paths_by_sha[sha] = p
                    provenance[f"opp_{spec['key']}"] = {
                        **rec,
                        "family": spec.get("family"),
                    }

            all_paths = list({str(p.resolve()): p for p in [
                base_main, *proposer_paths.values(), *opponent_paths.values()
            ]}.values())

            for opp_spec in V2_OPPONENTS:
                opp_key = opp_spec["key"]
                opp_main = opponent_paths[opp_key]
                for seed in SEEDS:
                    for seat in (0, 1):
                        key = {"opponent": opp_key, "seed": seed, "seat": seat}
                        try:
                            purge_all(all_paths)
                            discovery = run_discovery(
                                base_main, proposer_paths, opp_main, seed=seed, seat=seat
                            )
                            purge_all(all_paths)
                            parity = run_base(
                                base_main, opp_main, seed=seed, seat=seat
                            )
                            if discovery["rewards"] != parity["rewards"]:
                                raise RuntimeError(
                                    f"shadow discovery changed rewards: "
                                    f"{discovery['rewards']} != {parity['rewards']}"
                                )

                            events = select_events(discovery["trace"])
                            matchup_receipts.append({
                                **key,
                                "replay_parity": True,
                                "base_rewards": discovery["rewards"],
                                "base_margin": discovery["margin"],
                                "disagreement_states": sum(
                                    1 for x in discovery["trace"] if x["proposals"]
                                ),
                                "selected_steps": [int(x["step"]) for x in events],
                                "selected_proposal_counts": [
                                    len(x["proposals"]) for x in events
                                ],
                            })

                            for event in events:
                                candidates = [{
                                    "label": "BASE",
                                    "sources": ["v47"],
                                    "action_key": event["base_action_key"],
                                    "reward": discovery["reward"],
                                    "opponent_reward": discovery["opponent_reward"],
                                    "margin": discovery["margin"],
                                    "score": discovery["score"],
                                }]
                                for proposal in event["proposals"]:
                                    purge_all(all_paths)
                                    res = run_branch(
                                        base_main, proposer_paths, opp_main,
                                        seed=seed, seat=seat,
                                        event=event, proposal=proposal,
                                    )
                                    candidates.append({
                                        "label": sorted(proposal["sources"])[0],
                                        "sources": sorted(proposal["sources"]),
                                        "action_key": proposal["action_key"],
                                        "reward": res["reward"],
                                        "opponent_reward": res["opponent_reward"],
                                        "margin": res["margin"],
                                        "score": res["score"],
                                    })

                                oracle = max(
                                    candidates,
                                    key=lambda x: (
                                        float(x["score"]),
                                        float(x["margin"]),
                                        ",".join(x["sources"]),
                                    ),
                                )
                                row = {
                                    **key,
                                    "family": opp_spec.get("family"),
                                    "step": int(event["step"]),
                                    "proposal_count": len(candidates),
                                    "base": candidates[0],
                                    "oracle": oracle,
                                    "candidates": candidates,
                                }
                                rows.append(row)
                                print("WRAPPER_PROPOSAL_V3_BRANCH", json.dumps({
                                    **key,
                                    "step": event["step"],
                                    "proposals": len(candidates),
                                    "base_score": candidates[0]["score"],
                                    "oracle_sources": oracle["sources"],
                                    "oracle_score": oracle["score"],
                                    "margin_delta": oracle["margin"] - candidates[0]["margin"],
                                }, sort_keys=True), flush=True)
                        except Exception as exc:
                            failures.append({
                                **key,
                                "error": f"{type(exc).__name__}: {exc}",
                            })
                        finally:
                            purge_all(all_paths)
    except Exception as exc:
        failures.append({
            "phase": "acquisition_or_setup",
            "error": f"{type(exc).__name__}: {exc}",
        })

    overall = summarize(rows)
    by_opponent = {
        spec["key"]: summarize([r for r in rows if r["opponent"] == spec["key"]])
        for spec in V2_OPPONENTS
    }
    outside_rows = [r for r in rows if r["opponent"] not in MODERN41_KEYS]
    outside = summarize(outside_rows)
    outside_positive_opponents = [
        k for k, v in by_opponent.items()
        if k not in MODERN41_KEYS and v and float(v.get("score_delta", 0.0)) > 0.0
    ]

    oracle_sources = Counter()
    outside_oracle_sources = Counter()
    for row in rows:
        if row["oracle"]["label"] != "BASE":
            for src in row["oracle"]["sources"]:
                oracle_sources[src] += 1
                if row["opponent"] not in MODERN41_KEYS:
                    outside_oracle_sources[src] += 1

    mechanical_pass = (
        not failures
        and len(rows) >= MIN_BRANCH_STATES
        and all(x.get("replay_parity") for x in matchup_receipts)
    )
    outside_flips = int(outside.get("nonwin_to_win_flips", 0) or 0)
    if mechanical_pass and outside_flips >= 2 and len(outside_positive_opponents) >= 2:
        decision = "WRAPPER_PROPOSAL_DIVERSE_WL_HEADROOM_PASS"
    elif mechanical_pass and (
        outside_flips >= 1 or len(outside_positive_opponents) >= 1
    ):
        decision = "WRAPPER_PROPOSAL_OUTSIDE_WL_HEADROOM_WEAK"
    elif mechanical_pass and int(overall.get("nonwin_to_win_flips", 0) or 0) >= 2:
        decision = "WRAPPER_PROPOSAL_NARROW_HEADROOM_ONLY"
    elif mechanical_pass and float(outside.get("mean_oracle_margin_delta", 0.0) or 0.0) > 0.0:
        decision = "WRAPPER_PROPOSAL_OUTSIDE_MARGIN_ONLY"
    elif mechanical_pass:
        decision = "WRAPPER_PROPOSAL_NO_HEADROOM"
    else:
        decision = "WRAPPER_PROPOSAL_MECHANICS_INVALID"

    result = {
        "schema": "kculture-adaptive-wrapper-proposal-oracle-v3",
        "engine": EXPECTED_ENGINE,
        "base": BASE,
        "proposers": PROPOSERS,
        "opponents": V2_OPPONENTS,
        "seeds": SEEDS,
        "modern41_opponent_keys": sorted(MODERN41_KEYS),
        "provenance": provenance,
        "matchups": matchup_receipts,
        "branch_states": len(rows),
        "candidate_rollouts": sum(max(0, r["proposal_count"] - 1) for r in rows),
        "summary": overall,
        "outside_modern41_summary": outside,
        "outside_positive_opponents": outside_positive_opponents,
        "by_opponent": by_opponent,
        "oracle_source_counts": dict(oracle_sources),
        "outside_oracle_source_counts": dict(outside_oracle_sources),
        "failures": failures,
        "mechanical_pass": mechanical_pass,
        "decision": decision,
        "seconds": time.perf_counter() - started,
        "rows": rows,
        "offline_oracle_only": True,
        "automatic_kaggle_submission": False,
        "third_party_code_persisted": False,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("WRAPPER_PROPOSAL_V3_RESULT", json.dumps({
        "decision": decision,
        "branch_states": len(rows),
        "candidate_rollouts": result["candidate_rollouts"],
        "mechanical_pass": mechanical_pass,
        "summary": overall,
        "outside_modern41_summary": outside,
        "outside_positive_opponents": outside_positive_opponents,
        "oracle_source_counts": dict(oracle_sources),
        "outside_oracle_source_counts": dict(outside_oracle_sources),
        "failures": len(failures),
        "seconds": result["seconds"],
    }, sort_keys=True), flush=True)

    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
