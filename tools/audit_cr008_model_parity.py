"""Verify exported CR-007 pure trees exactly reproduce sklearn inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr005_short_horizon_sell_forecast import collect_date, split_features, X, p1
from tools.cr007_high_confidence_frontrun import FINAL_TRAIN_DATES, TEST_DATE, fit_models

TARGETS = ("SELL_CARROT", "SELL_STRAWBERRY")
EXPECTED_SHA256 = "6f12e86d0b19c5ba39c2ab4131e186ea14b49f42cc33b33a2ad895fab55783bb"


def pure_prob(model, row, names):
    node = 0
    left, right = model["children_left"], model["children_right"]
    feat, thr = model["feature"], model["threshold"]
    while left[node] != -1 and right[node] != -1:
        i = feat[node]
        v = float(row.get(names[i], 0.0))
        node = left[node] if v <= thr[node] else right[node]
    vals = model["value"][node]
    classes = model["classes"]
    total = float(sum(vals))
    return (float(vals[classes.index(1)]) / total) if total > 0 and 1 in classes else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="models/cr007_pure_models.json")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    mp = Path(args.model)
    raw = mp.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    exported = json.loads(raw)

    with tempfile.TemporaryDirectory(prefix="kculture-cr008-parity-") as tmp:
        root = Path(tmp)
        train = []
        for d in FINAL_TRAIN_DATES:
            train.extend(collect_date(d, args.top, root / "train"))
        test = collect_date(TEST_DATE, args.top, root / "test")
        _, names = split_features(train)
        models = fit_models(train, names)

    details = {}
    max_all = 0.0
    trigger_total = trigger_match = 0
    for target in TARGETS:
        sk = p1(models[target], X(test, names))
        pu = [pure_prob(exported["models"][target], r["features"], exported["feature_names"]) for r in test]
        diffs = [abs(a-b) for a,b in zip(sk,pu)]
        mx = max(diffs) if diffs else 0.0
        max_all = max(max_all, mx)
        threshold = float(exported["thresholds"][target])
        matches = sum((a >= threshold) == (b >= threshold) for a,b in zip(sk,pu))
        trigger_total += len(sk); trigger_match += matches
        details[target] = {
            "samples": len(sk),
            "max_abs_probability_error": mx,
            "mean_abs_probability_error": sum(diffs)/len(diffs) if diffs else 0.0,
            "trigger_matches": matches,
            "trigger_total": len(sk),
            "trigger_agreement": matches/len(sk) if sk else None,
            "threshold": threshold,
        }

    gate = {
        "sha256_exact": sha == EXPECTED_SHA256,
        "feature_names_exact": exported.get("feature_names") == names,
        "max_abs_probability_error_le_1e_12": max_all <= 1e-12,
        "trigger_agreement_100pct": trigger_total > 0 and trigger_match == trigger_total,
    }
    passed = all(gate.values())
    payload = {
        "experiment":"CR-008-model-parity",
        "status":"PURE_MODEL_PARITY_PASS" if passed else "PURE_MODEL_PARITY_FAIL",
        "model_sha256":sha,
        "expected_sha256":EXPECTED_SHA256,
        "feature_count":len(names),
        "test_samples":len(test),
        "max_abs_probability_error":max_all,
        "trigger_agreement":trigger_match/trigger_total if trigger_total else None,
        "details":details,
        "gate":gate,
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(payload,indent=2,sort_keys=True))
    if not passed: raise SystemExit(2)


if __name__ == "__main__":
    main()
