"""Summarize CR083 Phase-1 causal market-family ablations.

No threshold or promotion decision is emitted: this is architecture-forming evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    rows = []
    for p in sorted(a.results.rglob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if "metrics_a_vs_b" not in d:
            continue
        m = d["metrics_a_vs_b"]
        rows.append({
            "variant": d.get("a"),
            "opponent": d.get("b"),
            "master_seed": d.get("master_seed"),
            "seed_count": d.get("seed_count"),
            "games": m.get("games"),
            "wins": m.get("wins"),
            "losses": m.get("losses"),
            "ties": m.get("ties"),
            "score_rate": m.get("score_rate"),
            "mean_margin": m.get("mean_margin_secondary"),
            "median_margin": m.get("median_margin_secondary"),
            "min_margin": m.get("min_margin_secondary"),
            "max_margin": m.get("max_margin_secondary"),
            "non_done_games": m.get("non_done_games"),
            "errors": len(d.get("errors") or []),
        })

    expected = {
        "CR083_NO_SELL", "CR083_NO_BUY_SEED", "CR083_NO_BUY_PRODUCT",
        "CR083_NO_BUY_ANIMAL", "CR083_NO_HIRE", "CR083_NO_BUY_LAND",
    }
    present = {r["variant"] for r in rows}
    report = {
        "schema_version": "cr083-phase1-ablation-summary-v1",
        "architecture_research_only": True,
        "promotion_decision": None,
        "retune_on_master_9130830_permitted": False,
        "expected_variants": sorted(expected),
        "missing_variants": sorted(expected - present),
        "rows": sorted(rows, key=lambda r: r["variant"] or ""),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
