"""Export CR-007 final CARROT/STRAWBERRY trees to pure-JSON inference data."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr005_short_horizon_sell_forecast import collect_date, split_features
from tools.cr007_high_confidence_frontrun import FINAL_TRAIN_DATES, fit_models

TARGETS = ("SELL_CARROT", "SELL_STRAWBERRY")
THRESHOLDS = {"SELL_CARROT": 0.90, "SELL_STRAWBERRY": 0.85}


def export_tree(clf):
    tree = clf.tree_
    return {
        "classes": [int(x) for x in clf.classes_],
        "children_left": [int(x) for x in tree.children_left],
        "children_right": [int(x) for x in tree.children_right],
        "feature": [int(x) for x in tree.feature],
        "threshold": [float(x) for x in tree.threshold],
        "value": [[float(v) for v in row[0]] for row in tree.value],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr007-export-") as tmp:
        root = Path(tmp)
        train = []
        for d in FINAL_TRAIN_DATES:
            train.extend(collect_date(d, args.top, root / "train"))
        _, names = split_features(train)
        models = fit_models(train, names)

    payload = {
        "schema_version": "cr007-pure-trees-v1",
        "train_dates": list(FINAL_TRAIN_DATES),
        "top_episodes_per_day": args.top,
        "feature_names": names,
        "thresholds": THRESHOLDS,
        "models": {t: export_tree(models[t]) for t in TARGETS},
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"features": len(names), "nodes": {t: len(payload['models'][t]['feature']) for t in TARGETS}}, indent=2))


if __name__ == "__main__":
    main()
