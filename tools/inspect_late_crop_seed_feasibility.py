"""KEXP-025: measure whether bounded late WHEAT->CARROT swaps are seed-feasible.

Development plus exploratory live-meta environmental seeds only. Frozen R4B is
executed unchanged against starter. We inspect the mechanically clean crop
subwindows found by KEXP-023 and measure private CARROT seed headroom before
unit actions, plus nearby base seed-purchase orders. No policy mutation.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

SAFE_STEPS = frozenset(
    list(range(614, 619))
    + list(range(620, 624))
    + list(range(636, 648))
)
SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def demand_weights(shops):
    out = Counter()
    for shop in shops:
        products = SHOP_PRODUCTS.get(shop, ())
        mult = 2 if len(products) == 1 else 1
        for product in products:
            out[product] += mult
    return dict(out)


def live_seeds(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    found = []

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("seed"), int):
                found.append(value["seed"])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    return list(dict.fromkeys(found))


def unit_ops(action):
    if not isinstance(action, dict):
        return []
    return [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]


def plant_count(action, crop):
    return sum(
        isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", crop]
        for op in unit_ops(action)
    )


def buy_seed_qty(action, crop):
    total = 0
    for order in (action or {}).get("market", []) or []:
        if not (isinstance(order, list) and len(order) >= 3 and order[:2] == ["BUY_SEED", crop]):
            continue
        try:
            total += max(0, int(order[2] or 0))
        except (TypeError, ValueError):
            pass
    return total


def analyze_episode(replay, seed, source):
    steps = replay["steps"]
    rows = []
    prewindow = {"buy_wheat": 0, "buy_carrot": 0}
    for t in range(600, min(636, len(steps))):
        action = steps[t][0].get("action") or {}
        prewindow["buy_wheat"] += buy_seed_qty(action, "WHEAT")
        prewindow["buy_carrot"] += buy_seed_qty(action, "CARROT")

    for t in sorted(SAFE_STEPS):
        if t >= len(steps):
            continue
        entry = steps[t][0]
        obs = entry.get("observation") or {}
        action = entry.get("action") or {}
        wheat_plants = plant_count(action, "WHEAT")
        carrot_plants = plant_count(action, "CARROT")
        if wheat_plants <= 0 and carrot_plants <= 0:
            continue
        private = obs.get("private") or {}
        seeds = private.get("seeds") or {}
        try:
            carrot_stock = max(0, int(seeds.get("CARROT", 0) or 0))
        except (TypeError, ValueError):
            carrot_stock = 0
        try:
            wheat_stock = max(0, int(seeds.get("WHEAT", 0) or 0))
        except (TypeError, ValueError):
            wheat_stock = 0
        headroom = max(0, carrot_stock - carrot_plants)
        stock_only_swaps = min(wheat_plants, headroom)
        shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
        demand = demand_weights(shops)
        prices = (obs.get("market") or {}).get("prices") or {}
        try:
            wheat_price = float(prices.get("WHEAT", 0) or 0)
            carrot_price = float(prices.get("CARROT", 0) or 0)
        except (TypeError, ValueError):
            wheat_price, carrot_price = 0.0, 0.0
        rows.append({
            "seed": int(seed),
            "source": source,
            "step": t,
            "wheat_plants": int(wheat_plants),
            "carrot_plants": int(carrot_plants),
            "wheat_seed_stock": wheat_stock,
            "carrot_seed_stock": carrot_stock,
            "stock_only_swap_capacity": int(stock_only_swaps),
            "buy_wheat_this_step": buy_seed_qty(action, "WHEAT"),
            "buy_carrot_this_step": buy_seed_qty(action, "CARROT"),
            "shops": shops,
            "carrot_demand": int(demand.get("CARROT", 0)),
            "wheat_demand": int(demand.get("WHEAT", 0)),
            "wheat_price": wheat_price,
            "carrot_price": carrot_price,
            "carrot_wheat_price_ratio": (carrot_price / wheat_price) if wheat_price > 0 else None,
        })
    return rows, prewindow


def summarize(rows, episodes):
    out = {}
    for source in ("development", "live_meta", "all"):
        rr = rows if source == "all" else [r for r in rows if r["source"] == source]
        ee = episodes if source == "all" else [e for e in episodes if e["source"] == source]
        wheat = sum(r["wheat_plants"] for r in rr)
        capacity = sum(r["stock_only_swap_capacity"] for r in rr)
        per_episode = []
        for e in ee:
            er = [r for r in rr if r["seed"] == e["seed"] and r["source"] == e["source"]]
            per_episode.append(sum(r["stock_only_swap_capacity"] for r in er))
        ratios = [r["carrot_wheat_price_ratio"] for r in rr if isinstance(r["carrot_wheat_price_ratio"], (int, float))]
        out[source] = {
            "episodes": len(ee),
            "safe_window_wheat_plants": wheat,
            "stock_only_swap_capacity": capacity,
            "stock_only_capacity_fraction": (capacity / wheat) if wheat else None,
            "episodes_with_stock_only_capacity": sum(v > 0 for v in per_episode),
            "mean_stock_only_capacity_per_episode": statistics.mean(per_episode) if per_episode else None,
            "median_stock_only_capacity_per_episode": statistics.median(per_episode) if per_episode else None,
            "pre636_base_buy_wheat": sum(e["prewindow"]["buy_wheat"] for e in ee),
            "pre636_base_buy_carrot": sum(e["prewindow"]["buy_carrot"] for e in ee),
            "price_ratio_mean": statistics.mean(ratios) if ratios else None,
            "price_ratio_median": statistics.median(ratios) if ratios else None,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    rows = []
    episodes = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        candidate = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([candidate, "starter"])
        replay = env.toJSON()
        episode_rows, prewindow = analyze_episode(replay, int(seed), source)
        rows.extend(episode_rows)
        episodes.append({"seed": int(seed), "source": source, "prewindow": prewindow})

    report = {
        "schema_version": "late-crop-seed-feasibility-v1",
        "safe_steps": sorted(SAFE_STEPS),
        "summary": summarize(rows, episodes),
        "episodes": episodes,
        "rows": rows,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
