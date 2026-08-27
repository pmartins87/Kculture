"""CR-009: diagnose timing/value mismatch behind CR-008 causal failure.

CR-007 predicts whether an opponent will SELL a product somewhere in the next
24 turns. CR-008 responded by selling eligible own shed stock immediately.
This audit keeps the frozen CR-007 models/thresholds and asks a narrower
question on the strict Aug-26 out-of-time replays: when a high-confidence true
positive fires, how long until the first opponent sale and how does the market
revenue available for the *same current own quantity* evolve before that sale?

This is diagnostic only. It never tunes CR-007 thresholds and does not authorize
a candidate by itself.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cr004_adaptation_signal import download, public_features, read_csv  # noqa: E402
from tools.cr005_short_horizon_sell_forecast import (  # noqa: E402
    END, HORIZON, START, X, collect_date, p1, split_features,
)
from tools.cr006_market_frontrun_headroom import sell_revenue  # noqa: E402
from tools.cr007_high_confidence_frontrun import (  # noqa: E402
    FINAL_TRAIN_DATES, TEST_DATE, fit_models,
)

THRESHOLDS = {"CARROT": 0.90, "STRAWBERRY": 0.85}


def _num(d, key, default=0):
    try:
        return int((d or {}).get(key, default) or default)
    except (TypeError, ValueError, AttributeError):
        return int(default)


def _first_opp_sell(steps, opponent: int, t: int, item: str):
    """Return first sell state and quantity in [t, t+HORIZON-1].

    Kaggle replay alignment: action submitted from state s is stored on frame
    s+1, so steps[s+1][opponent]['action'] is the action chosen from state s.
    """
    last = min(t + HORIZON - 1, len(steps) - 2)
    for s in range(t, last + 1):
        frame = steps[s + 1][opponent]
        action = frame.get("action") if isinstance(frame, dict) else None
        if not isinstance(action, dict):
            continue
        qty = 0
        slots = []
        for i, order in enumerate(action.get("market", []) or []):
            if not (isinstance(order, list) and len(order) >= 3):
                continue
            if order[0] != "SELL" or order[1] != item:
                continue
            try:
                q = max(0, int(order[2] or 0))
            except (TypeError, ValueError):
                q = 0
            if q:
                qty += q
                slots.append(i)
        if qty:
            return {"state": s, "delay": s - t, "qty": qty, "slots": slots}
    return None


def _inventory_at(steps, player: int, state: int, item: str, fallback: int) -> int:
    if not (0 <= state < len(steps)):
        return fallback
    try:
        obs = steps[state][player].get("observation") or {}
        return int((((obs.get("market") or {}).get("inventory") or {}).get(item, fallback)) or fallback)
    except (TypeError, ValueError, AttributeError, IndexError):
        return fallback


def _revenue_series(steps, player: int, t: int, end_state: int, item: str, own_q: int):
    rows = []
    inv0 = _inventory_at(steps, player, t, item, 0)
    for s in range(t, min(end_state, len(steps) - 1) + 1):
        inv = _inventory_at(steps, player, s, item, inv0)
        rev, _ = sell_revenue(item, inv, own_q)
        rows.append({"state": s, "delay": s - t, "inventory": inv, "revenue": rev})
    return rows


def _q(values, frac):
    xs = sorted(values)
    if not xs:
        return None
    pos = (len(xs) - 1) * frac
    lo = int(pos)
    hi = min(len(xs) - 1, lo + 1)
    w = pos - lo
    return xs[lo] * (1 - w) + xs[hi] * w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr009-") as tmp:
        root = Path(tmp)
        train = []
        for d in FINAL_TRAIN_DATES:
            train.extend(collect_date(d, args.top, root / "train"))
        _, names = split_features(train)
        models = fit_models(train, names)

        handle = f"kaggle/kaggriculture-episodes-{TEST_DATE}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", root / "test" / "manifest")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[: args.top]

        events = []
        episodes = 0
        for mr in manifest:
            eid = str(mr["episode_id"])
            path = download(handle, f"{eid}.json", root / "test" / "episodes" / eid)
            rep = json.loads(path.read_text(encoding="utf-8"))
            steps = rep.get("steps") or []
            if len(steps) < 720:
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
                    shed = (obs.get("private") or {}).get("shed") or {}
                    inv_map = (obs.get("market") or {}).get("inventory") or {}
                    for item, thr in THRESHOLDS.items():
                        own_q = max(0, _num(shed, item, 0))
                        if own_q <= 0:
                            continue
                        prob = p1(models[f"SELL_{item}"], xrow)[0]
                        if prob < thr:
                            continue
                        inv_now = _num(inv_map, item, 0)
                        rev_now, _ = sell_revenue(item, inv_now, own_q)
                        first = _first_opp_sell(steps, opp, t, item)
                        horizon_end = min(t + HORIZON, len(steps) - 1)
                        end_state = first["state"] if first else horizon_end
                        series = _revenue_series(steps, player, t, end_state, item, own_q)
                        best = max(series, key=lambda r: (r["revenue"], -r["delay"]))
                        last_pre = series[-1]
                        after = None
                        if first and first["state"] + 1 < len(steps):
                            inv_after = _inventory_at(steps, player, first["state"] + 1, item, inv_now)
                            rev_after, _ = sell_revenue(item, inv_after, own_q)
                            after = {
                                "state": first["state"] + 1,
                                "inventory": inv_after,
                                "revenue": rev_after,
                            }
                        events.append({
                            "episode_id": eid,
                            "player": player,
                            "trigger_state": t,
                            "item": item,
                            "prob": prob,
                            "own_q": own_q,
                            "inventory_now": inv_now,
                            "revenue_now": rev_now,
                            "true_positive": first is not None,
                            "first_opponent_sell": first,
                            "best_pre_sell": best,
                            "last_pre_sell": last_pre,
                            "after_first_sell": after,
                            "best_wait_gain_vs_now": float(best["revenue"] - rev_now),
                            "last_pre_sell_gain_vs_now": float(last_pre["revenue"] - rev_now),
                            "series": series,
                        })

    selected = list(events)
    tp = [e for e in selected if e["true_positive"]]
    fp = [e for e in selected if not e["true_positive"]]
    delays = [e["first_opponent_sell"]["delay"] for e in tp]
    best_gains = [e["best_wait_gain_vs_now"] for e in tp]
    last_gains = [e["last_pre_sell_gain_vs_now"] for e in tp]

    per_product = {}
    for item in THRESHOLDS:
        xs = [e for e in selected if e["item"] == item]
        ys = [e for e in xs if e["true_positive"]]
        ds = [e["first_opponent_sell"]["delay"] for e in ys]
        gs = [e["best_wait_gain_vs_now"] for e in ys]
        per_product[item] = {
            "threshold": THRESHOLDS[item],
            "triggers": len(xs),
            "true_positives": len(ys),
            "precision": len(ys) / len(xs) if xs else None,
            "median_first_sell_delay": statistics.median(ds) if ds else None,
            "p25_first_sell_delay": _q(ds, 0.25),
            "p75_first_sell_delay": _q(ds, 0.75),
            "mean_best_wait_gain_vs_now": statistics.mean(gs) if gs else None,
            "median_best_wait_gain_vs_now": statistics.median(gs) if gs else None,
            "positive_wait_gain_fraction": sum(g > 0 for g in gs) / len(gs) if gs else None,
        }

    summary = {
        "triggers": len(selected),
        "true_positives": len(tp),
        "false_positives": len(fp),
        "precision": len(tp) / len(selected) if selected else None,
        "median_first_sell_delay": statistics.median(delays) if delays else None,
        "mean_first_sell_delay": statistics.mean(delays) if delays else None,
        "p25_first_sell_delay": _q(delays, 0.25),
        "p75_first_sell_delay": _q(delays, 0.75),
        "sell_within_3_fraction": sum(d <= 3 for d in delays) / len(delays) if delays else None,
        "sell_within_6_fraction": sum(d <= 6 for d in delays) / len(delays) if delays else None,
        "sell_within_12_fraction": sum(d <= 12 for d in delays) / len(delays) if delays else None,
        "mean_best_wait_gain_vs_now": statistics.mean(best_gains) if best_gains else None,
        "median_best_wait_gain_vs_now": statistics.median(best_gains) if best_gains else None,
        "mean_last_pre_sell_gain_vs_now": statistics.mean(last_gains) if last_gains else None,
        "positive_best_wait_gain_fraction": sum(g > 0 for g in best_gains) / len(best_gains) if best_gains else None,
        "best_wait_gain_ge_10_fraction": sum(g >= 10 for g in best_gains) / len(best_gains) if best_gains else None,
    }

    gate = {
        "true_positive_support_ge_40": len(tp) >= 40,
        "median_first_sell_delay_ge_4": (summary["median_first_sell_delay"] or 0) >= 4,
        "mean_best_wait_gain_positive": (summary["mean_best_wait_gain_vs_now"] or 0) > 0,
        "best_wait_gain_ge_10_fraction_ge_0_30": (summary["best_wait_gain_ge_10_fraction"] or 0) >= 0.30,
    }
    timing_mismatch = all(gate.values())
    payload = {
        "experiment": "CR-009",
        "schema_version": "trigger-timing-value-v1",
        "status": "TIMING_MISMATCH_SUPPORTED" if timing_mismatch else "TIMING_MISMATCH_NOT_SUPPORTED",
        "train_dates": list(FINAL_TRAIN_DATES),
        "test_date": TEST_DATE,
        "top_episodes": args.top,
        "episodes_used": episodes,
        "horizon": HORIZON,
        "thresholds": THRESHOLDS,
        "summary": summary,
        "per_product": per_product,
        "gate": gate,
        "events": events,
        "interpretation": (
            "High-confidence 24-turn forecasts often fire materially before the economically best pre-sale state; build a timing model before another causal response."
            if timing_mismatch else
            "Observed pre-sale timing does not explain CR-008 strongly enough; prioritize market-impact/stock-opportunity-cost attribution instead."
        ),
        "method_limit": "Observed replay market trajectory is not a full counterfactual because an early own sale would itself alter market inventory. This experiment diagnoses timing only.",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status":payload["status"],"summary":summary,"per_product":per_product,"gate":gate}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
