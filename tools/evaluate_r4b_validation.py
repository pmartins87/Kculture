"""Apply the predeclared KEXP-20260825-007 validation gate to three tournament reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))["overall"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--control", required=True, help="R4A vs Seyamalam tournament.json")
    p.add_argument("--candidate-seyamalam", required=True)
    p.add_argument("--candidate-r4a", required=True)
    p.add_argument("--output", default="artifacts/r4b_validation_gate.json")
    args = p.parse_args()

    control = load(args.control)
    cand_sey = load(args.candidate_seyamalam)
    cand_r4a = load(args.candidate_r4a)

    checks = {
        "zero_errors": (
            control["errors"] == 0 and cand_sey["errors"] == 0 and cand_r4a["errors"] == 0
        ),
        "direct_score_ge_0_50": cand_r4a["score_rate_tie_half"] >= 0.50,
        "direct_mean_delta_ge_0": cand_r4a["mean_money_delta"] >= 0,
        "seyamalam_wins_not_lower_than_control": cand_sey["wins"] >= control["wins"],
        "seyamalam_mean_not_lower_than_control": (
            cand_sey["mean_money_delta"] >= control["mean_money_delta"]
        ),
    }
    result = {
        "experiment": "KEXP-20260825-007-r4b-market-only-validation",
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "control_r4a_vs_seyamalam": control,
        "candidate_vs_seyamalam": cand_sey,
        "candidate_vs_r4a": cand_r4a,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["gate"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
