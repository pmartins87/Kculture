#!/usr/bin/env python3
"""Deterministically route a completed V23B result."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def improved_clusters(rows,mode,sha_to_cluster):
    return sorted({
      sha_to_cluster[str(r["main_sha256"])]
      for r in rows
      if str(r["mode"])==mode and float(r["score_delta"])>0 and str(r["main_sha256"]) in sha_to_cluster
    })

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--aggregate",required=True)
    ap.add_argument("--cluster-map",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    agg=json.loads(Path(args.aggregate).read_text())
    cmap=json.loads(Path(args.cluster_map).read_text())
    if not agg.get("mechanical_pass"): raise SystemExit("V23B aggregate mechanically invalid")
    rows=list(agg.get("rows") or []); sha_to_cluster=dict(cmap.get("sha_to_cluster") or {})
    decision=str(agg["decision"])
    market_clusters=improved_clusters(rows,"MARKET_ONLY",sha_to_cluster)
    physical_clusters=improved_clusters(rows,"PHYSICAL_ONLY",sha_to_cluster)
    route=None; selected=None; trace=[]
    if decision=="V23B_MARKET_DOMAIN_HEADROOM":
        route="OPEN_ONE_MARKET_MECHANISM_FAMILY"; selected="MARKET"
    elif decision=="V23B_PHYSICAL_DOMAIN_HEADROOM":
        route="OPEN_ONE_PHYSICAL_MECHANISM_FAMILY"; selected="PHYSICAL"
    elif decision=="V23B_BOTH_DOMAINS_HEADROOM":
        m=agg["by_mode"]["MARKET_ONLY"]; p=agg["by_mode"]["PHYSICAL_ONLY"]
        criteria=[
          ("improved_functional_clusters",len(market_clusters),len(physical_clusters)),
          ("improved_score_contexts",int(m["improved_score_contexts"]),int(p["improved_score_contexts"])),
          ("improved_seed_count",int(m["improved_seed_count"]),int(p["improved_seed_count"])),
          ("improved_sources",int(m["improved_sources"]),int(p["improved_sources"])),
          ("mean_score_delta",float(m["mean_score_delta"]),float(p["mean_score_delta"])),
          ("mean_margin_delta",float(m["mean_margin_delta"]),float(p["mean_margin_delta"])),
        ]
        for name,a,b in criteria:
            trace.append({"criterion":name,"market":a,"physical":b})
            if a>b: selected="MARKET"; break
            if b>a: selected="PHYSICAL"; break
        if selected is None:
            selected="MARKET"; trace.append({"criterion":"lexical_tiebreak","selected":"MARKET"})
        route="OPEN_ONE_MARKET_MECHANISM_FAMILY" if selected=="MARKET" else "OPEN_ONE_PHYSICAL_MECHANISM_FAMILY"
    elif decision=="V23B_CROSS_DOMAIN_INTERACTION_HEADROOM":
        route="ARCHITECTURAL_INTERACTION_RESET"
    elif decision=="V23B_NO_DOMAIN_WL_HEADROOM_RESET":
        route="BASELINE_ARCHITECTURE_AND_COMPETITION_STRATEGY_RESET"
    elif decision=="V23B_MECHANICS_INVALID":
        route="REPAIR_MECHANICS_ONLY"
    else:
        raise SystemExit(f"unknown decision {decision}")
    result={
      "schema":"kculture-all3-v23b-outcome-route-v1","source_decision":decision,"route":route,"selected_domain":selected,
      "market_improved_functional_clusters":market_clusters,"market_improved_functional_cluster_count":len(market_clusters),
      "physical_improved_functional_clusters":physical_clusters,"physical_improved_functional_cluster_count":len(physical_clusters),
      "selector_trace":trace,"manual_posthoc_selection_allowed":False,"automatic_kaggle_submission":False,
    }
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V23B_ROUTE_RESULT",json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
