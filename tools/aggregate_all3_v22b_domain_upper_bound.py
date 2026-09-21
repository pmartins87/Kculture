#!/usr/bin/env python3
"""Aggregate dormant V22B fresh-frontier domain upper-bound shards."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

MODES = ("BASE", "MARKET_ONLY", "PHYSICAL_ONLY", "FULL_SHADOW")


def summarize(rows):
    if not rows:
        return {}
    improved = [r for r in rows if float(r["score_delta"]) > 0]
    regressed = [r for r in rows if float(r["score_delta"]) < 0]
    return {
        "contexts": len(rows),
        "improved_score_contexts": len(improved),
        "regressed_score_contexts": len(regressed),
        "improved_source_shas": sorted({r["main_sha256"] for r in improved}),
        "improved_sources": len({r["main_sha256"] for r in improved}),
        "improved_seeds": sorted({int(r["seed"]) for r in improved}),
        "improved_seed_count": len({int(r["seed"]) for r in improved}),
        "mean_score_delta": statistics.fmean(float(r["score_delta"]) for r in rows),
        "mean_margin_delta": statistics.fmean(float(r["margin_delta"]) for r in rows),
    }


def domain_pass(s):
    if not s:
        return False
    return (
        s["improved_score_contexts"] >= 4
        and s["improved_sources"] >= 2
        and s["improved_seed_count"] >= 2
        and s["mean_score_delta"] > 0
        and s["regressed_score_contexts"] <= s["improved_score_contexts"] / 2
    )


def full_pass(s):
    if not s:
        return False
    return (
        s["improved_score_contexts"] >= 4
        and s["improved_sources"] >= 2
        and s["improved_seed_count"] >= 2
        and s["mean_score_delta"] > 0
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--hard-config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.hard_config).read_text())
    contexts = list(cfg.get("hard_contexts") or [])
    nctx = len(contexts)

    docs = [json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures = [f for d in docs for f in d.get("failures", [])]
    rows = [r for d in docs for r in d.get("rows", [])]

    expected_keys = {
        (str(c["context_id"]), mode)
        for c in contexts
        for mode in MODES
    }
    actual_keys = {
        (str(r["context_id"]), str(r["mode"]))
        for r in rows
    }

    mechanical_pass = (
        len(docs) == 4
        and all(bool(d.get("mechanical_pass")) for d in docs)
        and not failures
        and len(rows) == nctx * len(MODES)
        and actual_keys == expected_keys
    )

    by_mode = {
        mode: summarize([r for r in rows if r["mode"] == mode])
        for mode in MODES
    }

    market = domain_pass(by_mode["MARKET_ONLY"])
    physical = domain_pass(by_mode["PHYSICAL_ONLY"])
    full = full_pass(by_mode["FULL_SHADOW"])

    if not mechanical_pass:
        decision = "V22B_MECHANICS_INVALID"
    elif market and not physical:
        decision = "V22B_MARKET_DOMAIN_HEADROOM"
    elif physical and not market:
        decision = "V22B_PHYSICAL_DOMAIN_HEADROOM"
    elif market and physical:
        decision = "V22B_BOTH_DOMAINS_HEADROOM"
    elif full:
        decision = "V22B_CROSS_DOMAIN_INTERACTION_HEADROOM"
    else:
        decision = "V22B_NO_DOMAIN_WL_HEADROOM_RESET"

    result = {
        "schema": "kculture-all3-v22b-domain-upper-bound-v1",
        "mechanical_pass": mechanical_pass,
        "decision": decision,
        "hard_contexts": nctx,
        "by_mode": by_mode,
        "market_pass": market,
        "physical_pass": physical,
        "full_shadow_ceiling_pass": full,
        "rows": rows,
        "failures": failures,
        "automatic_kaggle_submission": False,
        "opponent_identity_runtime_feature_allowed": False,
    }

    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(
        "V22B_RESULT",
        json.dumps(
            {
                "decision": decision,
                "mechanical_pass": mechanical_pass,
                "hard_contexts": nctx,
                "by_mode": by_mode,
                "market_pass": market,
                "physical_pass": physical,
                "full_shadow_ceiling_pass": full,
                "failures": len(failures),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not mechanical_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
