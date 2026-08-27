"""KEXP-029: infer a conservative late CARROT-vs-WHEAT trigger from live top-meta replays.

This is diagnostic/development-only.  It learns only from legal public state
(shop multiset + current market prices) and never uses team/episode/seed identity
as a deployable feature.

Important replay alignment: in Kaggle environment JSON, the action chosen from
observation at state t is stored on frame t+1.  This script therefore pairs
steps[t][p].observation with steps[t+1][p].action.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"
TRAIN_DATES = ("2026-08-22", "2026-08-23", "2026-08-24", "2026-08-25")
TEST_DATE = "2026-08-26"
START = 600
END = 647
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")
SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def demand_weights(shops: list[str]) -> dict[str, int]:
    out = collections.Counter({p: 0 for p in PRODUCTS})
    for shop in shops:
        products = SHOPS.get(shop, ())
        mult = 2 if len(products) == 1 else 1
        for product in products:
            out[product] += mult
    return dict(out)


def market_buys(action: dict | None) -> tuple[int, int]:
    wheat = carrot = 0
    if not isinstance(action, dict):
        return 0, 0
    for order in action.get("market", []) or []:
        if not (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_SEED"):
            continue
        try:
            qty = max(0, int(order[2] or 0))
        except (TypeError, ValueError):
            continue
        if order[1] == "WHEAT":
            wheat += qty
        elif order[1] == "CARROT":
            carrot += qty
    return wheat, carrot


def price(obs: dict, product: str) -> float | None:
    try:
        v = ((obs.get("market") or {}).get("prices") or {}).get(product)
        v = float(v)
        return v if math.isfinite(v) and v > 0 else None
    except (TypeError, ValueError, AttributeError):
        return None


def final_rewards(rep: dict) -> list[float | None]:
    if not rep.get("steps"):
        return [None, None]
    final = rep["steps"][-1]
    ans = []
    for p in (0, 1):
        try:
            r = final[p].get("reward")
            ans.append(float(r) if isinstance(r, (int, float)) else None)
        except Exception:
            ans.append(None)
    return ans


def collect_date(date: str, top: int, root: Path) -> list[dict]:
    handle = f"kaggle/kaggriculture-episodes-{date}"
    manifest = sorted(
        read_csv(download(handle, "manifest.csv", root / date / "manifest")),
        key=lambda r: -float(r["avg_score"]),
    )[:top]
    rows: list[dict] = []
    for mr in manifest:
        eid = str(mr["episode_id"])
        rep = json.loads(download(handle, f"{eid}.json", root / date / "episodes" / eid).read_text(encoding="utf-8"))
        steps = rep.get("steps") or []
        rewards = final_rewards(rep)
        if len(steps) < END + 2 or any(r is None for r in rewards):
            continue
        best = max(float(r) for r in rewards if r is not None)
        names = (rep.get("info") or {}).get("TeamNames") or ["p0", "p1"]
        for p in (0, 1):
            winner = float(rewards[p]) == best
            for t in range(START, END + 1):
                obs = steps[t][p].get("observation") or {}
                action = steps[t + 1][p].get("action")
                wb, cb = market_buys(action)
                if wb + cb <= 0:
                    continue
                shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
                dem = demand_weights(shops)
                pw, pc = price(obs, "WHEAT"), price(obs, "CARROT")
                if pw is None or pc is None:
                    continue
                ratio = pc / pw
                relative_demand = (float(dem["CARROT"]) + 0.5) / (float(dem["WHEAT"]) + 0.5)
                opportunity = relative_demand * ratio
                rows.append({
                    "date": date,
                    "episode_id": eid,
                    "avg_score": float(mr["avg_score"]),
                    "player": p,
                    "team": names[p] if p < len(names) else f"p{p}",
                    "winner": winner,
                    "step": t,
                    "shops": shops,
                    "demand_carrot": int(dem["CARROT"]),
                    "demand_wheat": int(dem["WHEAT"]),
                    "price_carrot": pc,
                    "price_wheat": pw,
                    "price_ratio_carrot_wheat": ratio,
                    "relative_demand_carrot_wheat": relative_demand,
                    "opportunity_index": opportunity,
                    "buy_wheat": wb,
                    "buy_carrot": cb,
                    "carrot_positive": cb > 0,
                    "carrot_share": cb / (wb + cb),
                })
    return rows


def metrics(rows: list[dict], pred) -> dict:
    tp = fp = tn = fn = 0
    pred_rows = []
    for r in rows:
        y = bool(r["carrot_positive"])
        p = bool(pred(r))
        if p:
            pred_rows.append(r)
        if p and y: tp += 1
        elif p and not y: fp += 1
        elif not p and not y: tn += 1
        else: fn += 1
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    accuracy = (tp + tn) / len(rows) if rows else None
    dates = sorted(set(r["date"] for r in pred_rows))
    return {
        "rows": len(rows), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": precision, "recall": recall, "accuracy": accuracy,
        "predicted_positive": tp + fp, "predicted_positive_dates": dates,
    }


def threshold_candidates(values: list[float], coarse_step: float | None = None) -> list[float]:
    if not values:
        return []
    if coarse_step:
        lo = math.floor(min(values) / coarse_step) * coarse_step
        hi = math.ceil(max(values) / coarse_step) * coarse_step
        n = int(round((hi - lo) / coarse_step))
        return [round(lo + i * coarse_step, 6) for i in range(n + 1)]
    vals = sorted(set(float(v) for v in values))
    if len(vals) <= 80:
        return vals
    return sorted(set(vals[round(i * (len(vals) - 1) / 79)] for i in range(80)))


def choose_rule(train: list[dict]) -> dict | None:
    eligible = []
    dmax = max((r["demand_carrot"] for r in train), default=0)
    ratios = threshold_candidates([r["price_ratio_carrot_wheat"] for r in train], 0.05)
    for dmin in range(0, dmax + 1):
        for rmin in ratios:
            m = metrics(train, lambda x, dmin=dmin, rmin=rmin: x["demand_carrot"] >= dmin and x["price_ratio_carrot_wheat"] >= rmin)
            if m["predicted_positive"] < 12 or len(m["predicted_positive_dates"]) < 3:
                continue
            if m["precision"] is None:
                continue
            eligible.append({"family": "demand_and_price", "demand_carrot_min": dmin, "price_ratio_min": rmin, "train": m})

    opps = threshold_candidates([r["opportunity_index"] for r in train])
    for q in opps:
        m = metrics(train, lambda x, q=q: x["opportunity_index"] >= q)
        if m["predicted_positive"] < 12 or len(m["predicted_positive_dates"]) < 3:
            continue
        if m["precision"] is None:
            continue
        eligible.append({"family": "opportunity_index", "threshold": q, "train": m})

    if not eligible:
        return None
    # Conservative policy discovery: prioritize precision, then recall, then support.
    eligible.sort(key=lambda z: (
        z["train"]["precision"] if z["train"]["precision"] is not None else -1.0,
        z["train"]["recall"] if z["train"]["recall"] is not None else -1.0,
        z["train"]["predicted_positive"],
    ), reverse=True)
    return eligible[0]


def predicate(rule: dict):
    if rule["family"] == "demand_and_price":
        dmin = int(rule["demand_carrot_min"]); rmin = float(rule["price_ratio_min"])
        return lambda x: x["demand_carrot"] >= dmin and x["price_ratio_carrot_wheat"] >= rmin
    q = float(rule["threshold"])
    return lambda x: x["opportunity_index"] >= q


def day_summary(rows: list[dict]) -> dict:
    out = {}
    for date in sorted(set(r["date"] for r in rows)):
        rr = [r for r in rows if r["date"] == date]
        wr = [r for r in rr if r["winner"]]
        out[date] = {
            "events": len(rr),
            "winner_events": len(wr),
            "winner_carrot_positive_rate": statistics.mean(1.0 if r["carrot_positive"] else 0.0 for r in wr) if wr else None,
            "winner_mean_carrot_share": statistics.mean(r["carrot_share"] for r in wr) if wr else None,
            "winner_mean_price_ratio": statistics.mean(r["price_ratio_carrot_wheat"] for r in wr) if wr else None,
            "winner_mean_demand_carrot": statistics.mean(r["demand_carrot"] for r in wr) if wr else None,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if not 1 <= args.top <= 50:
        raise SystemExit("--top must be 1..50")

    with tempfile.TemporaryDirectory(prefix="kculture-kexp029-") as tmp:
        root = Path(tmp)
        # Confirm requested dates exist before downloads.
        idx = read_csv(download(INDEX_HANDLE, "manifest.csv", root / "index"))
        dates = {r["date"] for r in idx}
        missing = [d for d in (*TRAIN_DATES, TEST_DATE) if d not in dates]
        if missing:
            raise RuntimeError(f"dates absent from official index: {missing}")
        rows = []
        for date in (*TRAIN_DATES, TEST_DATE):
            rows.extend(collect_date(date, args.top, root))

    train_all = [r for r in rows if r["date"] in TRAIN_DATES]
    test_all = [r for r in rows if r["date"] == TEST_DATE]
    train = [r for r in train_all if r["winner"]]
    test = [r for r in test_all if r["winner"]]
    rule = choose_rule(train)
    if rule is None:
        selected = None
        gate = {"eligible_for_policy_prototype": False, "reason": "no threshold met minimum training support"}
    else:
        pred = predicate(rule)
        rule["test"] = metrics(test, pred)
        rule["all_player_train"] = metrics(train_all, pred)
        rule["all_player_test"] = metrics(test_all, pred)
        test_precision = rule["test"]["precision"]
        eligible = (
            rule["train"]["precision"] is not None and rule["train"]["precision"] >= 0.75
            and rule["test"]["predicted_positive"] >= 3
            and test_precision is not None and test_precision >= 0.70
        )
        gate = {
            "eligible_for_policy_prototype": eligible,
            "criteria": "train precision >=0.75; Aug-26 winner predicted-positive support >=3; Aug-26 winner precision >=0.70",
        }
        selected = rule

    payload = {
        "schema_version": "late-crop-decision-surface-v1",
        "alignment": "observation frame t paired with action frame t+1",
        "window": [START, END],
        "top_n_per_date": args.top,
        "train_dates": list(TRAIN_DATES),
        "test_date": TEST_DATE,
        "day_summary": day_summary(rows),
        "selected_rule": selected,
        "gate": gate,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "day_summary": payload["day_summary"],
        "selected_rule": selected,
        "gate": gate,
        "row_counts": {"train_winner": len(train), "test_winner": len(test), "all": len(rows)},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
