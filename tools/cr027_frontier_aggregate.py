"""Aggregate CR027 public frontier package screen shards without threshold rescue."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

CFG = Path(__file__).resolve().parents[1] / "configs/cr027_frontier_screen.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    reports = []
    for p in sorted(glob.glob(args.input_glob, recursive=True)):
        try:
            d = json.load(open(p, encoding="utf-8"))
            if d.get("experiment") == cfg["experiment"]:
                reports.append(d)
        except Exception:
            pass

    by_id = {r["candidate"]["id"]: r for r in reports}
    missing = [c["id"] for c in cfg["candidates"] if c["id"] not in by_id]

    def key(r):
        c = r.get("checks") or {}
        reactive = r.get("reactive") or {}
        return (
            1 if r.get("decision") == "SHORTLIST_FOR_HOSTED_CALIBRATION" else 0,
            1 if c.get("mechanical") else 0,
            float(reactive.get("score_gain") or -9999),
            -int(reactive.get("regressions") if reactive.get("regressions") is not None else 9999),
            float(r.get("direct_score") or -9999),
            float(reactive.get("mean_delta_gain") or -1e18),
        )

    ranking = []
    for r in sorted(reports, key=key, reverse=True):
        ranking.append({
            "id": r["candidate"]["id"],
            "handle": r["candidate"]["handle"],
            "reported_public_score_context": r["candidate"].get("reported_public_score_context"),
            "decision": r.get("decision"),
            "checks": r.get("checks"),
            "direct_score": r.get("direct_score"),
            "direct_mean_delta": r.get("direct_mean_delta"),
            "reactive": r.get("reactive"),
            "per_opponent": r.get("per_opponent"),
            "candidate_receipt": r.get("candidate_receipt"),
            "error_count": len(r.get("errors") or []),
        })

    shortlisted = [x for x in ranking if x["decision"] == "SHORTLIST_FOR_HOSTED_CALIBRATION"]
    payload = {
        "experiment": cfg["experiment"],
        "received": len(reports),
        "expected": len(cfg["candidates"]),
        "missing": missing,
        "ranking": ranking,
        "shortlisted": [x["id"] for x in shortlisted],
        "decision": "FRONTIER_SHORTLIST_AVAILABLE" if shortlisted else "NO_FRONTIER_PACKAGE_PASSED_FROZEN_SCREEN",
        "next": (
            "Run independent hosted calibration for the top shortlisted package before any ladder submission."
            if shortlisted else
            "Inspect failures and expand to another current public lineage; do not relax frozen thresholds."
        ),
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not reports:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
