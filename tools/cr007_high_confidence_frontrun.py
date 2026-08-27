"""CR-007: calibrate high-confidence opponent-aware front-run triggers without test leakage.

Train forecast models on Aug-23..24, choose per-product probability thresholds on
Aug-25 only, freeze thresholds, refit on Aug-23..25, then evaluate Aug-26.
Identity is never a feature. This remains a value proxy, not a deployable agent.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import tempfile
from pathlib import Path

from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr004_adaptation_signal import download, public_features, read_csv  # noqa: E402
from tools.cr005_short_horizon_sell_forecast import (  # noqa: E402
    END, HORIZON, RANDOM_STATE, START, TARGETS, X, collect_date, p1, split_features, y,
)
from tools.cr006_market_frontrun_headroom import sell_revenue, opponent_sell_qty  # noqa: E402

CAL_TRAIN_DATES = ("2026-08-23", "2026-08-24")
CAL_DATE = "2026-08-25"
FINAL_TRAIN_DATES = ("2026-08-23", "2026-08-24", "2026-08-25")
TEST_DATE = "2026-08-26"
ITEMS = tuple(t.replace("SELL_", "") for t in TARGETS)
THRESHOLDS = tuple(round(0.20 + 0.05 * i, 2) for i in range(15))  # 0.20..0.90


def final_rewards(rep):
    try:
        final = rep["steps"][-1]
        return [float(final[p].get("reward")) for p in (0, 1)]
    except Exception:
        return [None, None]


def fit_models(train_rows, names):
    out = {}
    for target in TARGETS:
        clf = DecisionTreeClassifier(max_depth=7, min_samples_leaf=40, random_state=RANDOM_STATE)
        clf.fit(X(train_rows, names), y(train_rows, target))
        out[target] = clf
    return out


def collect_value_events(date, top, root, models, names):
    handle = f"kaggle/kaggriculture-episodes-{date}"
    manifest = sorted(
        read_csv(download(handle, "manifest.csv", root / date / "manifest")),
        key=lambda r: -float(r.get("avg_score") or 0),
    )[:top]
    events = []
    episodes = 0
    for mr in manifest:
        eid = str(mr["episode_id"])
        path = download(handle, f"{eid}.json", root / date / "episodes" / eid)
        rep = json.loads(path.read_text(encoding="utf-8"))
        steps = rep.get("steps") or []
        rewards = final_rewards(rep)
        if len(steps) < 720 or any(r is None for r in rewards):
            continue
        episodes += 1
        for player in (0, 1):
            opp = 1 - player
            for t in range(START, END + 1):
                if t - 24 < 0 or t + HORIZON >= len(steps):
                    continue
                obs = steps[t][player].get("observation") or {}
                prev = steps[t - 24][player].get("observation") or {}
                feat = public_features(obs, prev, player)
                if not feat:
                    continue
                xrow = [[float(feat.get(n, 0.0)) for n in names]]
                private = obs.get("private") or {}
                shed = private.get("shed") or {}
                market = obs.get("market") or {}
                inv_map = market.get("inventory") or {}
                future_obs = steps[t + HORIZON][player].get("observation") or {}
                future_inv = ((future_obs.get("market") or {}).get("inventory") or {})
                for target, item in zip(TARGETS, ITEMS):
                    try:
                        own_q = max(0, int(shed.get(item, 0) or 0))
                        inv_now = int(inv_map.get(item, 0) or 0)
                        inv_t4 = int(future_inv.get(item, inv_now) or inv_now)
                    except (TypeError, ValueError):
                        continue
                    if own_q <= 0:
                        continue
                    prob = p1(models[target], xrow)[0]
                    opp_q = opponent_sell_qty(steps, opp, t, item)
                    rev_now, _ = sell_revenue(item, inv_now, own_q)
                    headroom = regret = 0.0
                    if opp_q > 0:
                        _, inv_after_opp = sell_revenue(item, inv_now, opp_q)
                        rev_after, _ = sell_revenue(item, inv_after_opp, own_q)
                        headroom = float(max(0, rev_now - rev_after))
                    else:
                        rev_wait, _ = sell_revenue(item, inv_t4, own_q)
                        regret = float(max(0, rev_wait - rev_now))
                    events.append({
                        "item": item, "prob": prob, "true_positive": opp_q > 0,
                        "headroom": headroom, "regret": regret,
                        "net": headroom - regret,
                    })
    return episodes, events


def summarize(events, thresholds):
    selected = [e for e in events if e["item"] in thresholds and e["prob"] >= thresholds[e["item"]]]
    per = {}
    for item in ITEMS:
        xs = [e for e in selected if e["item"] == item]
        tp = [e for e in xs if e["true_positive"]]
        h = sum(e["headroom"] for e in xs)
        r = sum(e["regret"] for e in xs)
        per[item] = {
            "threshold": thresholds.get(item), "triggers": len(xs), "true_positives": len(tp),
            "precision": len(tp)/len(xs) if xs else None,
            "headroom_sum": h, "regret_sum": r, "net_sum": h-r,
            "mean_net": (h-r)/len(xs) if xs else None,
        }
    tp = [e for e in selected if e["true_positive"]]
    h = sum(e["headroom"] for e in selected)
    r = sum(e["regret"] for e in selected)
    ratio = h/r if r > 0 else (math.inf if h > 0 else 0.0)
    return {
        "triggers": len(selected), "true_positives": len(tp),
        "precision": len(tp)/len(selected) if selected else None,
        "headroom_sum": h, "regret_sum": r, "net_sum": h-r,
        "mean_net": (h-r)/len(selected) if selected else None,
        "headroom_to_regret": ratio, "per_product": per,
    }


def choose_thresholds(cal_events):
    chosen = {}
    audit = {}
    for item in ITEMS:
        item_events = [e for e in cal_events if e["item"] == item]
        candidates = []
        for thr in THRESHOLDS:
            xs = [e for e in item_events if e["prob"] >= thr]
            if not xs:
                continue
            tp = sum(e["true_positive"] for e in xs)
            h = sum(e["headroom"] for e in xs)
            r = sum(e["regret"] for e in xs)
            candidates.append({
                "threshold": thr, "triggers": len(xs), "precision": tp/len(xs),
                "net_sum": h-r, "mean_net": (h-r)/len(xs),
            })
        eligible = [c for c in candidates if c["triggers"] >= 20 and c["precision"] >= 0.55 and c["mean_net"] >= 5.0]
        if eligible:
            best = max(eligible, key=lambda c: (c["mean_net"], c["precision"], c["triggers"]))
            chosen[item] = best["threshold"]
            audit[item] = {"status": "enabled", "selected": best, "candidates": candidates}
        else:
            audit[item] = {"status": "disabled", "selected": None, "candidates": candidates}
    return chosen, audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr007-") as tmp:
        root = Path(tmp)
        cal_train = []
        for d in CAL_TRAIN_DATES:
            cal_train.extend(collect_date(d, args.top, root / "feature-cal"))
        _, names = split_features(cal_train)
        cal_models = fit_models(cal_train, names)
        cal_eps, cal_events = collect_value_events(CAL_DATE, args.top, root / "value-cal", cal_models, names)
        thresholds, threshold_audit = choose_thresholds(cal_events)

        final_train = []
        for d in FINAL_TRAIN_DATES:
            final_train.extend(collect_date(d, args.top, root / "feature-final"))
        _, final_names = split_features(final_train)
        final_models = fit_models(final_train, final_names)
        test_eps, test_events = collect_value_events(TEST_DATE, args.top, root / "value-test", final_models, final_names)
        summary = summarize(test_events, thresholds)

    positive_products = sum(
        1 for d in summary["per_product"].values()
        if d["triggers"] >= 10 and d["net_sum"] > 0 and (d["precision"] or 0) >= 0.55
    )
    gate = {
        "enabled_products_ge_2": len(thresholds) >= 2,
        "test_triggers_ge_40": summary["triggers"] >= 40,
        "test_precision_ge_0_55": (summary["precision"] or 0) >= 0.55,
        "test_mean_net_ge_10": (summary["mean_net"] or 0) >= 10,
        "test_headroom_to_regret_ge_1_50": summary["headroom_to_regret"] >= 1.50,
        "positive_products_ge_2": positive_products >= 2,
    }
    passed = all(gate.values())
    payload = {
        "experiment": "CR-007", "schema_version": "high-confidence-frontrun-v1",
        "status": "HIGH_CONFIDENCE_FRONTRUN_PASS" if passed else "HIGH_CONFIDENCE_FRONTRUN_FAIL",
        "calibration_train_dates": list(CAL_TRAIN_DATES), "calibration_date": CAL_DATE,
        "final_train_dates": list(FINAL_TRAIN_DATES), "test_date": TEST_DATE,
        "top_episodes": args.top, "calibration_episodes": cal_eps, "test_episodes": test_eps,
        "threshold_grid": list(THRESHOLDS), "frozen_thresholds": thresholds,
        "threshold_audit": threshold_audit, "test_summary": summary,
        "positive_products": positive_products, "gate": gate,
        "identity_features": [],
        "interpretation": (
            "Training-only confidence calibration preserved enough future-day economic signal to justify exact causal agent tests."
            if passed else
            "High-confidence calibration did not generalize enough; keep adaptation predictive but do not deploy this front-run response."
        ),
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status":payload["status"],"thresholds":thresholds,"test":summary,"gate":gate}, indent=2))


if __name__ == "__main__":
    main()
