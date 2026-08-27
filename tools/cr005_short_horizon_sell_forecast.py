"""CR-005: predict opponent SELL events within the next four turns.

Uses the frozen CR-004 public feature encoder. Identity is never a model feature.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr004_adaptation_signal import (  # noqa: E402
    TRAIN_DATES, TEST_DATE, download, read_csv, public_features,
)

TARGETS = ("SELL_CARROT", "SELL_TOMATO", "SELL_STRAWBERRY", "SELL_MELON")
START = 96
END = 695
HORIZON = 4
RANDOM_STATE = 20260827


def final_rewards(rep):
    try:
        final = rep["steps"][-1]
        return [float(final[p].get("reward")) for p in (0, 1)]
    except Exception:
        return [None, None]


def imminent_sell_targets(steps, opponent: int, t: int):
    hit = {k: 0 for k in TARGETS}
    last = min(t + HORIZON - 1, len(steps) - 2)
    for s in range(t, last + 1):
        frame = steps[s + 1][opponent]
        action = frame.get("action") if isinstance(frame, dict) else None
        if not isinstance(action, dict):
            continue
        for order in action.get("market", []) or []:
            if not (isinstance(order, list) and len(order) >= 2 and order[0] == "SELL"):
                continue
            key = f"SELL_{order[1]}"
            if key in hit:
                hit[key] = 1
    return hit


def collect_date(date: str, top: int, root: Path):
    handle = f"kaggle/kaggriculture-episodes-{date}"
    manifest = sorted(
        read_csv(download(handle, "manifest.csv", root / date / "manifest")),
        key=lambda r: -float(r.get("avg_score") or 0),
    )[:top]
    rows = []
    for mr in manifest:
        eid = str(mr["episode_id"])
        p = download(handle, f"{eid}.json", root / date / "episodes" / eid)
        rep = json.loads(p.read_text(encoding="utf-8"))
        steps = rep.get("steps") or []
        rewards = final_rewards(rep)
        if len(steps) < 720 or any(x is None for x in rewards):
            continue
        for player in (0, 1):
            for t in range(START, END + 1):
                if t - 24 < 0 or t + HORIZON >= len(steps):
                    continue
                obs = steps[t][player].get("observation") or {}
                prev = steps[t - 24][player].get("observation") or {}
                feat = public_features(obs, prev, player)
                if not feat:
                    continue
                rows.append({
                    "date": date,
                    "features": feat,
                    "targets": imminent_sell_targets(steps, 1 - player, t),
                })
    return rows


def split_features(rows):
    names = sorted({k for r in rows for k in r["features"]})
    adaptive = names
    baseline = [n for n in names if not n.startswith(("opp_", "dopp_", "gap_"))]
    return baseline, adaptive


def X(rows, names):
    return [[float(r["features"].get(n, 0.0)) for n in names] for r in rows]


def y(rows, target):
    return [int(r["targets"].get(target, 0)) for r in rows]


def p1(clf, xs):
    probs = clf.predict_proba(xs)
    classes = [int(v) for v in clf.classes_]
    if 1 not in classes:
        return [0.0 for _ in xs]
    j = classes.index(1)
    return [float(row[j]) for row in probs]


def fit_eval(train, test, names, target):
    yt = y(train, target)
    ye = y(test, target)
    clf = DecisionTreeClassifier(max_depth=7, min_samples_leaf=40, random_state=RANDOM_STATE)
    clf.fit(X(train, names), yt)
    pred = p1(clf, X(test, names))
    auc = float(roc_auc_score(ye, pred)) if len(set(ye)) == 2 else None
    imp = sorted(
        ((names[i], float(v)) for i, v in enumerate(clf.feature_importances_) if v > 0),
        key=lambda kv: kv[1], reverse=True,
    )[:15]
    return {
        "brier": float(brier_score_loss(ye, pred)),
        "roc_auc": auc,
        "train_positive": int(sum(yt)),
        "train_negative": int(len(yt) - sum(yt)),
        "test_positive": int(sum(ye)),
        "test_negative": int(len(ye) - sum(ye)),
        "top_feature_importances": imp,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr005-") as tmp:
        root = Path(tmp)
        rows = []
        for date in (*TRAIN_DATES, TEST_DATE):
            rs = collect_date(date, args.top, root)
            print(f"COLLECTED {date}: {len(rs)} samples")
            rows.extend(rs)

    train = [r for r in rows if r["date"] in TRAIN_DATES]
    test = [r for r in rows if r["date"] == TEST_DATE]
    base_names, adapt_names = split_features(rows)

    details = {}
    eligible = []
    for target in TARGETS:
        yt, ye = y(train, target), y(test, target)
        support = {
            "train_positive": sum(yt), "train_negative": len(yt)-sum(yt),
            "test_positive": sum(ye), "test_negative": len(ye)-sum(ye),
        }
        ok = support["train_positive"] >= 100 and support["train_negative"] >= 100 and support["test_positive"] >= 40 and support["test_negative"] >= 40
        rec = {"eligible": bool(ok), "support": support}
        if ok:
            b = fit_eval(train, test, base_names, target)
            a = fit_eval(train, test, adapt_names, target)
            rel = (b["brier"] - a["brier"]) / b["brier"] if b["brier"] > 0 else 0.0
            rec.update({"baseline": b, "adaptive": a, "relative_brier_improvement": rel})
            eligible.append((target, rel, a["roc_auc"]))
        details[target] = rec

    rels = [r for _, r, _ in eligible]
    median_rel = statistics.median(rels) if rels else None
    improve10 = sum(r >= 0.10 for _, r, _ in eligible)
    auc85 = sum((auc is not None and auc >= 0.85) for _, _, auc in eligible)
    worsen5 = sum(r < -0.05 for _, r, _ in eligible)
    gate = {
        "eligible_targets_at_least_2": len(eligible) >= 2,
        "targets_improve_brier_ge_10pct_at_least_2": improve10 >= 2,
        "median_relative_brier_improvement_ge_8pct": median_rel is not None and median_rel >= 0.08,
        "adaptive_auc_ge_0_85_at_least_2": auc85 >= 2,
        "targets_worsen_brier_gt_5pct_at_most_1": worsen5 <= 1,
    }
    passed = all(gate.values())
    payload = {
        "experiment": "CR-005",
        "schema_version": "short-horizon-sell-forecast-v1",
        "status": "SHORT_HORIZON_SELL_SIGNAL_PASS" if passed else "SHORT_HORIZON_SELL_SIGNAL_FAIL",
        "train_dates": list(TRAIN_DATES), "test_date": TEST_DATE,
        "top_episodes_per_day": args.top,
        "states": [START, END], "horizon": HORIZON,
        "train_samples": len(train), "test_samples": len(test),
        "model": {"type":"DecisionTreeClassifier","max_depth":7,"min_samples_leaf":40,"random_state":RANDOM_STATE},
        "baseline_feature_count": len(base_names), "adaptive_feature_count": len(adapt_names),
        "identity_features": [],
        "summary": {
            "eligible_target_count": len(eligible),
            "median_relative_brier_improvement": median_rel,
            "targets_improving_brier_ge_10pct": improve10,
            "adaptive_auc_ge_0_85_count": auc85,
            "targets_worsening_brier_gt_5pct": worsen5,
            "ranking": sorted(eligible, key=lambda x: x[1], reverse=True),
        },
        "gate": gate,
        "targets": details,
        "interpretation": (
            "Imminent opponent sales are predictable enough from public opponent state to justify a market best-response value experiment."
            if passed else
            "Four-turn opponent SELL forecast did not pass the frozen gate; do not build a broad market-reactive wrapper from this signal yet."
        ),
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status":payload["status"],**payload["summary"],"gate":gate},indent=2))

if __name__ == "__main__":
    main()
