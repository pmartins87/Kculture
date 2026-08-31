"""Aggregate the preregistered CR024A guarded-top19 Stage-B evaluation."""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import defaultdict
from pathlib import Path

EXPECTED_ROWS = 168
MIN_RAW_HARMFUL = 2
MIN_GUARD_RECALL = 0.50
MAX_GUARD_FPR = 0.15
MIN_HYBRID_NET = 4
MAX_HYBRID_RAW_HARM_FRAC = 0.60
MIN_SCORE_GAIN_VS_CR008 = 4.0
MAX_SCORE_DEFICIT_VS_TOP19 = 2.0


def conversion(arm_score, control_score):
    if arm_score > control_score:
        return 1
    if arm_score < control_score:
        return -1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = sorted(glob.glob(args.input_glob, recursive=True))
    rows, errors = [], []
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        errors.extend(d.get("errors") or [])
        rows.extend(d.get("rows") or [])

    raw_fav = raw_unf = hybrid_fav = hybrid_unf = 0
    tp = fp = fn = tn = 0
    score_cr008 = score_raw = score_hybrid = 0.0
    by_opp = defaultdict(lambda: {"rows": 0, "raw_fav": 0, "raw_unf": 0, "hybrid_fav": 0, "hybrid_unf": 0, "guard_positive": 0})

    for r in rows:
        c = float(r["cr008"]["score"])
        raw = float(r["top19"]["score"])
        hyb = float(r["cr024a"]["score"])
        score_cr008 += c; score_raw += raw; score_hybrid += hyb
        rc = conversion(raw, c); hc = conversion(hyb, c)
        raw_fav += rc > 0; raw_unf += rc < 0
        hybrid_fav += hc > 0; hybrid_unf += hc < 0
        guard = bool(r.get("guard_positive"))
        harmful = rc < 0
        if guard and harmful: tp += 1
        elif guard and not harmful: fp += 1
        elif (not guard) and harmful: fn += 1
        else: tn += 1
        b = by_opp[r["opponent"]]
        b["rows"] += 1; b["raw_fav"] += rc > 0; b["raw_unf"] += rc < 0
        b["hybrid_fav"] += hc > 0; b["hybrid_unf"] += hc < 0; b["guard_positive"] += guard

    guard_recall = tp / max(1, tp + fn)
    guard_fpr = fp / max(1, fp + tn)
    hybrid_net = hybrid_fav - hybrid_unf
    raw_net = raw_fav - raw_unf
    max_allowed_hybrid_unf = math.ceil(MAX_HYBRID_RAW_HARM_FRAC * raw_unf)

    mechanical_ok = (len(files) == 7 and len(rows) == EXPECTED_ROWS and not errors)
    informative_guard = raw_unf >= MIN_RAW_HARMFUL
    gates = {
        "mechanical_168_rows_zero_errors": mechanical_ok,
        "stage_b_has_at_least_2_raw_harmful": informative_guard,
        "guard_recall_at_least_0_50": informative_guard and guard_recall >= MIN_GUARD_RECALL,
        "guard_fpr_at_most_0_15": guard_fpr <= MAX_GUARD_FPR,
        "hybrid_net_conversions_at_least_plus4": hybrid_net >= MIN_HYBRID_NET,
        "hybrid_unfavorable_at_most_60pct_raw": hybrid_unf <= max_allowed_hybrid_unf,
        "hybrid_score_at_least_cr008_plus4": score_hybrid >= score_cr008 + MIN_SCORE_GAIN_VS_CR008,
        "hybrid_score_no_more_than_2_below_top19": score_hybrid >= score_raw - MAX_SCORE_DEFICIT_VS_TOP19,
    }

    if not mechanical_ok:
        decision = "MECHANICAL_FAIL__NO_PACKAGE"
    elif not informative_guard:
        decision = "INCONCLUSIVE_GUARD__BUILD_CONSENSUS_BACKBONE"
    elif all(gates.values()):
        decision = "CR024A_STAGE_B_PASS__BUILD_NEW_STRATEGY_PACKAGE"
    else:
        decision = "CR024A_STAGE_B_FAIL__BUILD_CONSENSUS_BACKBONE"

    payload = {
        "experiment": "CR024A",
        "stage": "GUARDED_TOP19_STAGE_B",
        "decision": decision,
        "preregistered_gate": {
            "expected_rows": EXPECTED_ROWS,
            "min_raw_harmful": MIN_RAW_HARMFUL,
            "min_guard_recall": MIN_GUARD_RECALL,
            "max_guard_fpr": MAX_GUARD_FPR,
            "min_hybrid_net": MIN_HYBRID_NET,
            "max_hybrid_raw_harm_fraction": MAX_HYBRID_RAW_HARM_FRAC,
            "min_score_gain_vs_cr008": MIN_SCORE_GAIN_VS_CR008,
            "max_score_deficit_vs_top19": MAX_SCORE_DEFICIT_VS_TOP19,
        },
        "shard_count": len(files),
        "row_count": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "raw_top19": {"favorable": raw_fav, "unfavorable": raw_unf, "net": raw_net, "total_score": score_raw},
        "cr024a": {"favorable": hybrid_fav, "unfavorable": hybrid_unf, "net": hybrid_net, "total_score": score_hybrid},
        "cr008": {"total_score": score_cr008},
        "guard_validation": {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "recall": guard_recall,
            "false_positive_rate": guard_fpr,
            "positive_count": tp + fp,
        },
        "max_allowed_hybrid_unfavorable": max_allowed_hybrid_unf,
        "gates": gates,
        "by_opponent": dict(sorted(by_opp.items())),
        "adaptive_reserved_touched": False,
        "held_out_touched": False,
        "policy": "Threshold 11.5 is frozen. No Stage-B tuning. PASS builds a new package; FAIL or inconclusive routes to consensus/shrinkage.",
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "decision": decision,
        "row_count": len(rows),
        "raw_top19": payload["raw_top19"],
        "cr024a": payload["cr024a"],
        "cr008": payload["cr008"],
        "guard_validation": payload["guard_validation"],
        "gates": gates,
    }, indent=2, sort_keys=True))
    if not mechanical_ok:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
