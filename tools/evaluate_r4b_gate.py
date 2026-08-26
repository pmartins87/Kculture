"""Evaluate the predeclared R4B development gates from tournament artifacts.

This script does not run any games and never opens validation/held-out seeds. It
only consumes existing `tournament.json` reports produced by run_tournament.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

R4A = "file:artifacts/public_opponents/cok_v8_779caae.py:agent"
R4B = "file:candidates/r4b_terminal_liquidation.py:agent"
SEY = "file:artifacts/public_opponents/seyamalam_v21_8b8c421.py:agent"


def load_reports(root: Path):
    reports = []
    for path in sorted(root.rglob("tournament.json")):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        report["_path"] = path.as_posix()
        reports.append(report)
    return reports


def matching(reports, candidate: str, opponent: str):
    rows = [
        r for r in reports
        if r.get("candidate") == candidate
        and r.get("opponents") == [opponent]
        and r.get("seed_partition") == "development"
        and len(r.get("seeds") or []) == 8
        and r.get("candidate_seats") == [0, 1]
    ]
    if len(rows) != 1:
        raise RuntimeError(
            f"Expected exactly one report for candidate={candidate!r}, "
            f"opponent={opponent!r}; found {len(rows)}"
        )
    return rows[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="artifacts/tournaments")
    parser.add_argument("--output", default="artifacts/r4b_gate.json")
    args = parser.parse_args()

    reports = load_reports(Path(args.root))
    control = matching(reports, R4A, SEY)
    test = matching(reports, R4B, SEY)
    direct = matching(reports, R4B, R4A)

    c = control["overall"]
    t = test["overall"]
    d = direct["overall"]

    checks = {
        "zero_runtime_errors": all(x["overall"]["errors"] == 0 for x in (control, test, direct)),
        "r4b_mean_delta_vs_sey_ge_r4a_control": t["mean_money_delta"] >= c["mean_money_delta"],
        "r4b_direct_score_rate_ge_half": d["score_rate_tie_half"] >= 0.50,
        "r4b_direct_mean_delta_ge_zero": d["mean_money_delta"] >= 0,
    }
    payload = {
        "result": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "control_r4a_vs_seyamalam": {
            "path": control["_path"],
            "overall": c,
        },
        "r4b_vs_seyamalam": {
            "path": test["_path"],
            "overall": t,
            "mean_delta_change_vs_control": t["mean_money_delta"] - c["mean_money_delta"],
        },
        "r4b_vs_r4a": {
            "path": direct["_path"],
            "overall": d,
        },
        "development_only": True,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(0 if payload["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
