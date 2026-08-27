"""CR-006: screen economic headroom from opponent-aware imminent SELL forecasts.

This is a strict future-day observational/value proxy. It does not modify an
agent and does not use identity features. A PASS only authorizes a later exact
counterfactual replay test.
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

from kaggle_environments.envs.kaggriculture.kaggriculture import market_price  # noqa: E402
from tools.cr004_adaptation_signal import (  # noqa: E402
    TRAIN_DATES,
    TEST_DATE,
    download,
    public_features,
    read_csv,
)
from tools.cr005_short_horizon_sell_forecast import (  # noqa: E402
    END,
    HORIZON,
    RANDOM_STATE,
    START,
    TARGETS,
    X,
    collect_date,
    p1,
    split_features,
    y,
)

PROB_TRIGGER = 0.20
ITEMS = tuple(t.replace("SELL_", "") for t in TARGETS)


def sell_revenue(item: str, inventory: int, quantity: int) -> tuple[int, int]:
    """Exact official per-unit SELL revenue/inventory transition."""
    inv = int(inventory)
    total = 0
    for _ in range(max(0, int(quantity))):
        price = int(market_price(item, inv))
        total += price
        # Official engine: sales at price floor $1 do not increase supply.
        if price > 1:
            inv += 1
    return total, inv


def opponent_sell_qty(steps, opponent: int, t: int, item: str) -> int:
    total = 0
    last = min(t + HORIZON - 1, len(steps) - 2)
    for s in range(t, last + 1):
        frame = steps[s + 1][opponent]
        action = frame.get("action") if isinstance(frame, dict) else None
        if not isinstance(action, dict):
            continue
        for order in action.get("market", []) or []:
            if not (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL" and order[1] == item):
                continue
            try:
                total += max(0, int(order[2] or 0))
            except (TypeError, ValueError):
                pass
    return total


def final_rewards(rep):
    try:
        final = rep["steps"][-1]
        return [float(final[p].get("reward")) for p in (0, 1)]
    except Exception:
        return [None, None]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr006-") as tmp:
        root = Path(tmp)

        # Train exactly the adaptive CR-005 model family on the frozen train days.
        train = []
        for date in TRAIN_DATES:
            rs = collect_date(date, args.top, root / "train")
            print(f"TRAIN {date}: {len(rs)}")
            train.extend(rs)
        _, adaptive_names = split_features(train)
        models = {}
        for target in TARGETS:
            clf = DecisionTreeClassifier(max_depth=7, min_samples_leaf=40, random_state=RANDOM_STATE)
            clf.fit(X(train, adaptive_names), y(train, target))
            models[target] = clf

        # Strict test day, retaining private own shed only for self-inventory feasibility.
        handle = f"kaggle/kaggriculture-episodes-{TEST_DATE}"
        manifest = sorted(
            read_csv(download(handle, "manifest.csv", root / "test" / "manifest")),
            key=lambda r: -float(r.get("avg_score") or 0),
        )[: args.top]

        events = []
        episodes_used = 0
        for mr in manifest:
            eid = str(mr["episode_id"])
            path = download(handle, f"{eid}.json", root / "test" / "episodes" / eid)
            rep = json.loads(path.read_text(encoding="utf-8"))
            steps = rep.get("steps") or []
            rewards = final_rewards(rep)
            if len(steps) < 720 or any(r is None for r in rewards):
                continue
            episodes_used += 1
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
                    xrow = [[float(feat.get(n, 0.0)) for n in adaptive_names]]
                    private = obs.get("private") or {}
                    shed = private.get("shed") or {}
                    market = obs.get("market") or {}
                    inv_map = market.get("inventory") or {}
                    future_obs = steps[t + HORIZON][player].get("observation") or {}
                    future_inv_map = ((future_obs.get("market") or {}).get("inventory") or {})

                    for target, item in zip(TARGETS, ITEMS):
                        prob = p1(models[target], xrow)[0]
                        if prob < PROB_TRIGGER:
                            continue
                        try:
                            own_q = max(0, int(shed.get(item, 0) or 0))
                            inv_now = int(inv_map.get(item, 0) or 0)
                            inv_future = int(future_inv_map.get(item, inv_now) or inv_now)
                        except (TypeError, ValueError):
                            continue
                        if own_q <= 0:
                            continue

                        opp_q = opponent_sell_qty(steps, opp, t, item)
                        rev_now, _ = sell_revenue(item, inv_now, own_q)
                        true_positive_headroom = 0.0
                        false_positive_regret = 0.0
                        if opp_q > 0:
                            _, inv_after_opp = sell_revenue(item, inv_now, opp_q)
                            rev_after_opp, _ = sell_revenue(item, inv_after_opp, own_q)
                            true_positive_headroom = float(max(0, rev_now - rev_after_opp))
                        else:
                            rev_wait_proxy, _ = sell_revenue(item, inv_future, own_q)
                            false_positive_regret = float(max(0, rev_wait_proxy - rev_now))

                        events.append({
                            "episode_id": eid,
                            "player": player,
                            "step": t,
                            "item": item,
                            "prob": prob,
                            "own_stock": own_q,
                            "market_inventory_now": inv_now,
                            "market_inventory_t_plus_4": inv_future,
                            "opponent_sell_qty_horizon": opp_q,
                            "true_positive": opp_q > 0,
                            "true_positive_headroom": true_positive_headroom,
                            "false_positive_regret_proxy": false_positive_regret,
                            "net_proxy": true_positive_headroom - false_positive_regret,
                        })

    per_product = {}
    for item in ITEMS:
        xs = [e for e in events if e["item"] == item]
        tp = [e for e in xs if e["true_positive"]]
        fp = [e for e in xs if not e["true_positive"]]
        h = sum(e["true_positive_headroom"] for e in tp)
        r = sum(e["false_positive_regret_proxy"] for e in fp)
        per_product[item] = {
            "triggers": len(xs),
            "true_positives": len(tp),
            "precision": len(tp) / len(xs) if xs else None,
            "headroom_sum": h,
            "false_positive_regret_sum": r,
            "net_proxy_sum": h - r,
            "mean_net_proxy": (h - r) / len(xs) if xs else None,
            "median_true_positive_headroom": statistics.median([e["true_positive_headroom"] for e in tp]) if tp else None,
            "mean_own_stock": statistics.mean([e["own_stock"] for e in xs]) if xs else None,
        }

    triggers = len(events)
    tps = [e for e in events if e["true_positive"]]
    fps = [e for e in events if not e["true_positive"]]
    headroom = sum(e["true_positive_headroom"] for e in tps)
    regret = sum(e["false_positive_regret_proxy"] for e in fps)
    ratio = (headroom / regret) if regret > 0 else (math.inf if headroom > 0 else 0.0)
    positive_products = sum(
        1 for d in per_product.values()
        if d["triggers"] >= 10 and d["net_proxy_sum"] > 0
    )

    gate = {
        "stock_eligible_triggers_ge_50": triggers >= 50,
        "precision_ge_0_55": (len(tps) / triggers) >= 0.55 if triggers else False,
        "headroom_to_fp_regret_ratio_ge_1_50": ratio >= 1.50,
        "mean_net_proxy_per_trigger_ge_10": ((headroom - regret) / triggers) >= 10.0 if triggers else False,
        "positive_products_ge_2": positive_products >= 2,
    }
    passed = all(gate.values())

    payload = {
        "experiment": "CR-006",
        "schema_version": "market-frontrun-headroom-v1",
        "status": "FRONTRUN_HEADROOM_PASS" if passed else "FRONTRUN_HEADROOM_FAIL",
        "train_dates": list(TRAIN_DATES),
        "test_date": TEST_DATE,
        "top_episodes": args.top,
        "episodes_used": episodes_used,
        "states": [START, END],
        "horizon": HORIZON,
        "probability_trigger": PROB_TRIGGER,
        "products": list(ITEMS),
        "identity_features": [],
        "summary": {
            "stock_eligible_triggers": triggers,
            "true_positives": len(tps),
            "precision": len(tps) / triggers if triggers else None,
            "headroom_sum": headroom,
            "false_positive_regret_sum": regret,
            "net_proxy_sum": headroom - regret,
            "mean_net_proxy_per_trigger": (headroom - regret) / triggers if triggers else None,
            "headroom_to_fp_regret_ratio": ratio,
            "positive_products_with_ge10_triggers": positive_products,
        },
        "per_product": per_product,
        "gate": gate,
        "interpretation": (
            "Forecast-triggered front-running has enough isolated economic headroom to justify exact CR-007 replay counterfactual testing."
            if passed else
            "The broad four-turn front-run screen did not pass; do not ship a generic opponent-aware early-sell rule."
        ),
        "method_limit": "Value is an isolated market-race/false-positive proxy, not a full causal replay. Early selling would alter later market state; exact counterfactual simulation remains required.",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "per_product": per_product, "gate": gate}, indent=2))


if __name__ == "__main__":
    main()
