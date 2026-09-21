#!/usr/bin/env python3
"""Deterministically route a completed binding V22B aggregate.

Implements the pre-registered outcome router. It does not change V22B's
decision; for BOTH only, it applies the frozen tie-break criteria using the
V22A BASE functional-cluster map.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MARKET = "MARKET_ONLY"
PHYSICAL = "PHYSICAL_ONLY"

def improved_clusters(rows, mode, sha_to_cluster):
    return sorted({
        sha_to_cluster[str(r["main_sha256"])]
        for r in rows
        if str(r["mode"]) == mode
        and float(r["score_delta"]) > 0
        and str(r["main_sha256"]) in sha_to_cluster
    })

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--aggregate", required=True)
    ap.add_argument("--cluster-map", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    agg=json.loads(Path(args.aggregate).read_text())
    cmap=json.loads(Path(args.cluster_map).read_text())
    if not agg.get("mechanical_pass"):
        raise SystemExit("V22B aggregate is not mechanically valid")
    sha_to_cluster=dict(cmap.get("sha_to_cluster") or {})
    rows=list(agg.get("rows") or [])
    decision=str(agg.get("decision"))

    market_clusters=improved_clusters(rows, MARKET, sha_to_cluster)
    physical_clusters=improved_clusters(rows, PHYSICAL, sha_to_cluster)

    route=None
    selected_domain=None
    selector_trace=[]

    if decision=="V22B_MARKET_DOMAIN_HEADROOM":
        route="OPEN_ONE_MARKET_MECHANISM_FAMILY"
        selected_domain="MARKET"
    elif decision=="V22B_PHYSICAL_DOMAIN_HEADROOM":
        route="OPEN_ONE_PHYSICAL_MECHANISM_FAMILY"
        selected_domain="PHYSICAL"
    elif decision=="V22B_BOTH_DOMAINS_HEADROOM":
        bm=agg["by_mode"][MARKET]
        bp=agg["by_mode"][PHYSICAL]
        criteria=[
            ("improved_functional_clusters", len(market_clusters), len(physical_clusters)),
            ("improved_score_contexts", int(bm["improved_score_contexts"]), int(bp["improved_score_contexts"])),
            ("improved_seed_count", int(bm["improved_seed_count"]), int(bp["improved_seed_count"])),
            ("improved_sources", int(bm["improved_sources"]), int(bp["improved_sources"])),
            ("mean_score_delta", float(bm["mean_score_delta"]), float(bp["mean_score_delta"])),
            ("mean_margin_delta", float(bm["mean_margin_delta"]), float(bp["mean_margin_delta"])),
        ]
        for name,m,p in criteria:
            selector_trace.append({"criterion":name,"market":m,"physical":p})
            if m>p:
                selected_domain="MARKET"; break
            if p>m:
                selected_domain="PHYSICAL"; break
        if selected_domain is None:
            selected_domain="MARKET"
            selector_trace.append({"criterion":"lexical_tiebreak","selected":"MARKET"})
        route=(
            "OPEN_ONE_MARKET_MECHANISM_FAMILY"
            if selected_domain=="MARKET"
            else "OPEN_ONE_PHYSICAL_MECHANISM_FAMILY"
        )
    elif decision=="V22B_CROSS_DOMAIN_INTERACTION_HEADROOM":
        route="ARCHITECTURAL_INTERACTION_RESET"
    elif decision=="V22B_NO_DOMAIN_WL_HEADROOM_RESET":
        route="BASELINE_ARCHITECTURE_AND_COMPETITION_STRATEGY_RESET"
    elif decision=="V22B_MECHANICS_INVALID":
        route="REPAIR_MECHANICS_ONLY"
    else:
        raise SystemExit(f"unknown V22B decision {decision!r}")

    result={
        "schema":"kculture-all3-v22b-outcome-route-v1",
        "source_decision":decision,
        "route":route,
        "selected_domain":selected_domain,
        "market_improved_functional_clusters":market_clusters,
        "market_improved_functional_cluster_count":len(market_clusters),
        "physical_improved_functional_clusters":physical_clusters,
        "physical_improved_functional_cluster_count":len(physical_clusters),
        "selector_trace":selector_trace,
        "manual_posthoc_selection_allowed":False,
        "automatic_kaggle_submission":False,
    }
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V22B_ROUTE_RESULT",json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
