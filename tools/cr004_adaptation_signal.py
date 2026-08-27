"""CR-004: test whether opponent public state predicts near-future opponent behavior.

Strict temporal train/test on official Kaggriculture top-episode replays.
Deployment features never include team/agent/submission/episode/seed identity.
The adaptive model differs from the baseline only by opponent-public features.
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
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.tree import DecisionTreeClassifier

TRAIN_DATES = ("2026-08-23", "2026-08-24", "2026-08-25")
TEST_DATE = "2026-08-26"
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("COW", "SHEEP", "GOOSE")
SHOPS = ("BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET")
START = 48
LAST_START = 672
STRIDE = 24
HORIZON = 24
RANDOM_STATE = 20260827


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def num(d, key) -> float:
    try:
        v = float((d or {}).get(key, 0) or 0)
        return v if math.isfinite(v) else 0.0
    except (TypeError, ValueError, AttributeError):
        return 0.0


def tile_counts(farm: dict) -> dict[str, float]:
    c = collections.Counter()
    for row in farm.get("tiles", []) or []:
        if not isinstance(row, list):
            continue
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                c[f"crop_{tile.get('crop')}"] += 1
            if tile.get("animal"):
                c[f"animal_{tile.get('animal')}"] += 1
            if tile.get("kind") == "WEED":
                c["weeds"] += 1
            try:
                c["yield_units"] += max(0.0, float(tile.get("yield_units", 0) or 0))
            except (TypeError, ValueError):
                pass
    return dict(c)


def farm_public(farm: dict, prefix: str) -> dict[str, float]:
    c = tile_counts(farm or {})
    out = {
        f"{prefix}money": num(farm, "money"),
        f"{prefix}hands": float(len((farm or {}).get("hands", []) or [])),
        f"{prefix}quads": float(len((farm or {}).get("unlocked_quadrants", []) or [])),
        f"{prefix}weeds": float(c.get("weeds", 0)),
        f"{prefix}yield_units": float(c.get("yield_units", 0)),
    }
    for crop in CROPS:
        out[f"{prefix}crop_{crop.lower()}"] = float(c.get(f"crop_{crop}", 0))
    for animal in ANIMALS:
        out[f"{prefix}animal_{animal.lower()}"] = float(c.get(f"animal_{animal}", 0))
    return out


def public_features(obs: dict, prev_obs: dict, player: int) -> dict[str, float]:
    farms = obs.get("farms") or []
    prev_farms = prev_obs.get("farms") or []
    if len(farms) < 2 or len(prev_farms) < 2:
        return {}
    opp = 1 - player
    own_now = farm_public(farms[player], "self_")
    opp_now = farm_public(farms[opp], "opp_")
    own_prev = farm_public(prev_farms[player], "self_")
    opp_prev = farm_public(prev_farms[opp], "opp_")

    market = obs.get("market") or {}
    prev_market = prev_obs.get("market") or {}
    prices = market.get("prices") or {}
    inv = market.get("inventory") or {}
    prev_prices = prev_market.get("prices") or {}
    prev_inv = prev_market.get("inventory") or {}
    shops = set(((obs.get("town") or {}).get("unlocked_shops") or []))

    step = float(obs.get("step", 0) or 0)
    f: dict[str, float] = {
        "step": step,
        "day": step / 24.0,
        "shop_count": float(len(shops)),
    }
    f.update(own_now)
    f.update(opp_now)

    for k, v in own_now.items():
        f[f"d{k}"] = v - own_prev.get(k, 0.0)
    for k, v in opp_now.items():
        f[f"d{k}"] = v - opp_prev.get(k, 0.0)

    f["gap_money"] = own_now["self_money"] - opp_now["opp_money"]
    f["gap_hands"] = own_now["self_hands"] - opp_now["opp_hands"]
    f["gap_quads"] = own_now["self_quads"] - opp_now["opp_quads"]

    for product in PRODUCTS:
        lo = product.lower()
        p = num(prices, product)
        q = num(inv, product)
        f[f"market_price_{lo}"] = p
        f[f"market_inventory_{lo}"] = q
        f[f"dmarket_price_{lo}"] = p - num(prev_prices, product)
        f[f"dmarket_inventory_{lo}"] = q - num(prev_inv, product)
    for shop in SHOPS:
        f[f"shop_{shop.lower()}"] = 1.0 if shop in shops else 0.0
    return f


def target_names() -> list[str]:
    out = [f"SELL_{p}" for p in PRODUCTS]
    out += [f"BUY_SEED_{c}" for c in CROPS]
    out += [f"BUY_ANIMAL_{a}" for a in ANIMALS]
    out += ["HIRE", "BUY_LAND"]
    return out


def future_targets(steps: list, opponent: int, t: int) -> dict[str, int]:
    hit = {k: 0 for k in target_names()}
    end = min(t + HORIZON - 1, len(steps) - 2)
    for s in range(t, end + 1):
        action = steps[s + 1][opponent].get("action") if isinstance(steps[s + 1], list) else None
        if not isinstance(action, dict):
            continue
        for order in action.get("market", []) or []:
            if not (isinstance(order, list) and order):
                continue
            typ = str(order[0])
            item = str(order[1]) if len(order) > 1 else None
            if typ == "SELL" and item in PRODUCTS:
                hit[f"SELL_{item}"] = 1
            elif typ == "BUY_SEED" and item in CROPS:
                hit[f"BUY_SEED_{item}"] = 1
            elif typ == "BUY_ANIMAL" and item in ANIMALS:
                hit[f"BUY_ANIMAL_{item}"] = 1
            elif typ in ("HIRE", "BUY_LAND"):
                hit[typ] = 1
    return hit


def final_rewards(rep: dict) -> list[float | None]:
    try:
        final = rep["steps"][-1]
        return [float(final[p].get("reward")) for p in (0, 1)]
    except Exception:
        return [None, None]


def collect_date(date: str, top: int, root: Path) -> list[dict]:
    handle = f"kaggle/kaggriculture-episodes-{date}"
    manifest = sorted(
        read_csv(download(handle, "manifest.csv", root / date / "manifest")),
        key=lambda r: -float(r.get("avg_score") or 0),
    )[:top]
    rows: list[dict] = []
    for mr in manifest:
        eid = str(mr["episode_id"])
        path = download(handle, f"{eid}.json", root / date / "episodes" / eid)
        rep = json.loads(path.read_text(encoding="utf-8"))
        steps = rep.get("steps") or []
        rewards = final_rewards(rep)
        if len(steps) < 720 or any(x is None for x in rewards):
            continue
        for player in (0, 1):
            for t in range(START, LAST_START + 1, STRIDE):
                if t - STRIDE < 0 or t + HORIZON >= len(steps):
                    continue
                obs = steps[t][player].get("observation") or {}
                prev_obs = steps[t - STRIDE][player].get("observation") or {}
                feat = public_features(obs, prev_obs, player)
                if not feat:
                    continue
                rows.append({
                    "date": date,
                    "features": feat,
                    "targets": future_targets(steps, 1 - player, t),
                })
    return rows


def feature_names(rows: list[dict]) -> tuple[list[str], list[str]]:
    names = sorted({k for r in rows for k in r["features"].keys()})
    opponent_prefixes = ("opp_", "dopp_", "gap_")
    adaptive = names
    baseline = [n for n in names if not n.startswith(opponent_prefixes)]
    return baseline, adaptive


def matrix(rows: list[dict], names: list[str]) -> list[list[float]]:
    return [[float(r["features"].get(n, 0.0)) for n in names] for r in rows]


def labels(rows: list[dict], target: str) -> list[int]:
    return [int(r["targets"].get(target, 0)) for r in rows]


def positive_probability(clf: DecisionTreeClassifier, X: list[list[float]]) -> list[float]:
    probs = clf.predict_proba(X)
    classes = [int(x) for x in clf.classes_]
    if 1 not in classes:
        return [1.0 if classes and classes[0] == 1 else 0.0 for _ in X]
    j = classes.index(1)
    return [float(row[j]) for row in probs]


def evaluate(train: list[dict], test: list[dict], names: list[str], target: str) -> tuple[dict, DecisionTreeClassifier]:
    ytr = labels(train, target)
    yte = labels(test, target)
    clf = DecisionTreeClassifier(max_depth=5, min_samples_leaf=25, random_state=RANDOM_STATE)
    clf.fit(matrix(train, names), ytr)
    p = positive_probability(clf, matrix(test, names))
    brier = float(brier_score_loss(yte, p))
    auc = None
    if len(set(yte)) == 2:
        auc = float(roc_auc_score(yte, p))
    importances = sorted(
        ((names[i], float(v)) for i, v in enumerate(clf.feature_importances_) if v > 0),
        key=lambda kv: kv[1], reverse=True,
    )[:12]
    return {
        "brier": brier,
        "roc_auc": auc,
        "test_positive": int(sum(yte)),
        "test_negative": int(len(yte) - sum(yte)),
        "train_positive": int(sum(ytr)),
        "train_negative": int(len(ytr) - sum(ytr)),
        "top_feature_importances": importances,
    }, clf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-cr004-") as tmp:
        root = Path(tmp)
        all_rows: list[dict] = []
        for date in (*TRAIN_DATES, TEST_DATE):
            rs = collect_date(date, args.top, root)
            print(f"COLLECTED {date}: {len(rs)} samples")
            all_rows.extend(rs)

    train = [r for r in all_rows if r["date"] in TRAIN_DATES]
    test = [r for r in all_rows if r["date"] == TEST_DATE]
    base_names, adaptive_names = feature_names(all_rows)

    results = {}
    eligible = []
    for target in target_names():
        ytr = labels(train, target)
        yte = labels(test, target)
        counts = {
            "train_positive": sum(ytr), "train_negative": len(ytr) - sum(ytr),
            "test_positive": sum(yte), "test_negative": len(yte) - sum(yte),
        }
        ok = counts["train_positive"] >= 50 and counts["train_negative"] >= 50 and counts["test_positive"] >= 20 and counts["test_negative"] >= 20
        rec = {"eligible": bool(ok), "support": counts}
        if ok:
            b, _ = evaluate(train, test, base_names, target)
            a, _ = evaluate(train, test, adaptive_names, target)
            rel = (b["brier"] - a["brier"]) / b["brier"] if b["brier"] > 0 else 0.0
            rec.update({"baseline": b, "adaptive": a, "relative_brier_improvement": rel})
            eligible.append((target, rel))
        results[target] = rec

    rels = [x[1] for x in eligible]
    median_rel = statistics.median(rels) if rels else None
    improve5 = sum(rel >= 0.05 for _, rel in eligible)
    worsen5 = sum(rel <= -0.05 for _, rel in eligible)
    worsen_frac = worsen5 / len(eligible) if eligible else None
    gate = {
        "eligible_targets": len(eligible) >= 5,
        "median_relative_brier_improvement_ge_0_03": median_rel is not None and median_rel >= 0.03,
        "targets_improving_ge_0_05_at_least_4": improve5 >= 4,
        "worsen_gt_0_05_fraction_lt_0_25": worsen_frac is not None and worsen_frac < 0.25,
    }
    passed = all(gate.values())

    payload = {
        "experiment": "CR-004",
        "schema_version": "opponent-adaptation-signal-v1",
        "status": "ADAPTATION_SIGNAL_PASS" if passed else "ADAPTATION_SIGNAL_FAIL",
        "train_dates": list(TRAIN_DATES),
        "test_date": TEST_DATE,
        "top_episodes_per_day": args.top,
        "sample_protocol": {"start": START, "last_start": LAST_START, "stride": STRIDE, "horizon": HORIZON},
        "train_samples": len(train),
        "test_samples": len(test),
        "baseline_feature_count": len(base_names),
        "adaptive_feature_count": len(adaptive_names),
        "opponent_feature_count": len(adaptive_names) - len(base_names),
        "identity_features": [],
        "model": {"type": "DecisionTreeClassifier", "max_depth": 5, "min_samples_leaf": 25, "random_state": RANDOM_STATE},
        "eligibility": {"train_each_class_min": 50, "test_each_class_min": 20},
        "summary": {
            "eligible_target_count": len(eligible),
            "median_relative_brier_improvement": median_rel,
            "targets_improving_brier_ge_5pct": improve5,
            "targets_worsening_brier_gt_5pct": worsen5,
            "worsen_fraction": worsen_frac,
            "best_targets": sorted(eligible, key=lambda x: x[1], reverse=True)[:10],
            "worst_targets": sorted(eligible, key=lambda x: x[1])[:10],
        },
        "gate": gate,
        "targets": results,
        "interpretation": (
            "Opponent-public state carries robust temporal predictive signal; proceed to bounded value-tested best responses."
            if passed else
            "Broad opponent-public feature set did not pass the frozen predictive gate; narrow/refine history encoding before building a large adaptive controller."
        ),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "gate": gate}, indent=2))


if __name__ == "__main__":
    main()
