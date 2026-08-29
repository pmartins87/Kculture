"""CR-020 legacy causal sanity on the 16 frozen pre-CR020 diagnostic pairs.

This does not use CR-020 preregistered seeds.  It checks the mechanism that
motivated the candidate before any fresh CR-020 outcomes are exposed:
- the four historical CR-011 W->L catastrophes must be recovered to the frozen
  R4B winner outcome;
- the single historical L->W favorable conversion must remain favorable.

No thresholds or candidate parameters are tuned here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cr015_preregistered_evaluation as E

CFG = ROOT / "configs/cr014b_affected_pairs_v1.json"
R4B = ROOT / "candidates/r4b_ablation_market_only.py"
CR015 = ROOT / "candidates/cr015_liquidation_phase_early_order.py"
CR020 = ROOT / "candidates/cr020_monotone_append_latch.py"


def result(path: Path, opponent: Path, seed: int, seat: int):
    own, opp, delta = E.play(path, opponent, seed, seat)
    return {"self": own, "opp": opp, "delta": delta, "score": E.score(delta)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    opp_dir = Path(args.opponent_dir)
    if not opp_dir.is_absolute():
        opp_dir = ROOT / opp_dir
    cfg = json.loads(CFG.read_text(encoding="utf-8"))

    rows = []
    errors = []
    for p in cfg["pairs"]:
        seed = int(p["seed"])
        seat = int(p["seat"])
        opponent = opp_dir / f"{p['opponent']}.py"
        try:
            row = {
                "opponent": p["opponent"],
                "seed": seed,
                "seat": seat,
                "historical_cr011_score_gain": float(p["score_gain"]),
                "r4b": result(R4B, opponent, seed, seat),
                "cr015": result(CR015, opponent, seed, seat),
                "cr020": result(CR020, opponent, seed, seat),
            }
            row["cr020_vs_r4b_score_gain"] = row["cr020"]["score"] - row["r4b"]["score"]
            row["cr020_vs_r4b_relative_gain"] = row["cr020"]["delta"] - row["r4b"]["delta"]
            row["cr020_vs_cr015_relative_gain"] = row["cr020"]["delta"] - row["cr015"]["delta"]
            rows.append(row)
        except Exception as exc:
            errors.append({
                "opponent": p["opponent"], "seed": seed, "seat": seat,
                "error": repr(exc),
            })

    catastrophic = [r for r in rows if r["historical_cr011_score_gain"] < 0]
    favorable = [r for r in rows if r["historical_cr011_score_gain"] > 0]
    recovered = sum(r["cr020"]["score"] >= r["r4b"]["score"] for r in catastrophic)
    preserved = sum(r["cr020"]["score"] > r["r4b"]["score"] for r in favorable)

    passed = (
        not errors
        and len(rows) == len(cfg["pairs"])
        and len(catastrophic) == 4
        and recovered == 4
        and len(favorable) == 1
        and preserved == 1
    )
    payload = {
        "experiment": "CR-020-legacy-causal-sanity",
        "data_policy": "only frozen pre-CR020 CR-014B diagnostic pairs",
        "candidate": str(CR020.relative_to(ROOT)),
        "status": "PASS" if passed else "FAIL",
        "rows_completed": len(rows),
        "error_count": len(errors),
        "historical_catastrophic_cases": len(catastrophic),
        "catastrophic_outcomes_recovered": recovered,
        "historical_favorable_cases": len(favorable),
        "favorable_outcomes_preserved": preserved,
        "rows": rows,
        "errors": errors,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k not in ("rows", "errors")}, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
