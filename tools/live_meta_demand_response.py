"""Analyze late crop demand-response in official high-Elo Kaggriculture episodes.

Prize-first observational study.  At step 600 all eight shop instances should
normally be visible.  We measure public demand intensity, each player's seed
purchases during 600..671, later sales, and W/L outcome.  No submitted policy
is changed and no validation/held-out seeds are used.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"
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


def shops_at(steps: list, idx: int) -> list[str]:
    idx = min(idx, len(steps) - 1)
    obs = steps[idx][0].get("observation", {}) or {}
    return list(((obs.get("town") or {}).get("unlocked_shops") or []))


def demand_weights(shops: list[str]) -> dict[str, int]:
    out = collections.Counter({p: 0 for p in PRODUCTS})
    for shop in shops:
        products = SHOPS.get(shop, ())
        mult = 2 if len(products) == 1 else 1
        for product in products:
            out[product] += mult
    return dict(out)


def market_qty(steps: list, player: int, start: int, end: int, op: str) -> dict[str, int]:
    q = collections.Counter()
    for idx in range(start, min(end + 1, len(steps))):
        action = steps[idx][player].get("action")
        if not isinstance(action, dict):
            continue
        for order in action.get("market", []) or []:
            if not (isinstance(order, list) and len(order) >= 3 and order[0] == op):
                continue
            try:
                q[str(order[1])] += int(order[2])
            except (TypeError, ValueError):
                pass
    return dict(q)


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    denx = sum((x-mx)**2 for x in xs) ** 0.5
    deny = sum((y-my)**2 for y in ys) ** 0.5
    return num/(denx*deny) if denx and deny else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if not 1 <= args.top <= 50:
        raise SystemExit("--top must be 1..50")

    rows_out = []
    with tempfile.TemporaryDirectory(prefix="kculture-demand-meta-") as tmp:
        root = Path(tmp)
        index = sorted(read_csv(download(INDEX_HANDLE, "manifest.csv", root/"index")), key=lambda r:r["date"])
        date = args.date or index[-1]["date"]
        idx_row = next(r for r in index if r["date"] == date)
        handle = f"kaggle/kaggriculture-episodes-{date}"
        manifest = sorted(read_csv(download(handle, "manifest.csv", root/"day")), key=lambda r:-float(r["avg_score"]))[:args.top]

        for mr in manifest:
            eid = str(mr["episode_id"])
            rep = json.loads(download(handle, f"{eid}.json", root/"episodes"/eid).read_text(encoding="utf-8"))
            steps = rep["steps"]
            names = (rep.get("info") or {}).get("TeamNames") or ["p0","p1"]
            seed = (rep.get("info") or {}).get("seed")
            shops600 = shops_at(steps, 600)
            shops672 = shops_at(steps, 672)
            demand600 = demand_weights(shops600)
            rewards = [steps[-1][p].get("reward") for p in (0,1)]
            best = max(float(x) for x in rewards if isinstance(x,(int,float)))
            for p in (0,1):
                reward = float(rewards[p])
                buys = market_qty(steps,p,600,671,"BUY_SEED")
                sells_600_718 = market_qty(steps,p,600,718,"SELL")
                sells_696_718 = market_qty(steps,p,696,718,"SELL")
                rows_out.append({
                    "episode_id": eid,
                    "avg_score": float(mr["avg_score"]),
                    "seed": seed,
                    "player": p,
                    "team": names[p] if p < len(names) else f"p{p}",
                    "winner": reward == best,
                    "reward": reward,
                    "shops600": shops600,
                    "shops672": shops672,
                    "demand600": demand600,
                    "buy_seed_600_671": {k:int(buys.get(k,0)) for k in PRODUCTS},
                    "sell_600_718": {k:int(sells_600_718.get(k,0)) for k in PRODUCTS},
                    "sell_696_718": {k:int(sells_696_718.get(k,0)) for k in PRODUCTS},
                })

    winners = [r for r in rows_out if r["winner"]]
    losers = [r for r in rows_out if not r["winner"]]
    products = {}
    for product in PRODUCTS:
        xs = [float(r["demand600"][product]) for r in rows_out]
        ys = [float(r["buy_seed_600_671"][product]) for r in rows_out]
        levels = {}
        for level in sorted(set(int(x) for x in xs)):
            same = [r for r in rows_out if int(r["demand600"][product]) == level]
            ws = [r for r in same if r["winner"]]
            ls = [r for r in same if not r["winner"]]
            levels[str(level)] = {
                "player_games": len(same),
                "winner_mean_seed_buy": statistics.mean([r["buy_seed_600_671"][product] for r in ws]) if ws else None,
                "loser_mean_seed_buy": statistics.mean([r["buy_seed_600_671"][product] for r in ls]) if ls else None,
                "winner_mean_finalday_sell": statistics.mean([r["sell_696_718"][product] for r in ws]) if ws else None,
                "loser_mean_finalday_sell": statistics.mean([r["sell_696_718"][product] for r in ls]) if ls else None,
            }
        products[product] = {
            "demand_seedbuy_pearson_all_player_games": pearson(xs,ys),
            "winner_mean_seed_buy": statistics.mean([r["buy_seed_600_671"][product] for r in winners]) if winners else None,
            "loser_mean_seed_buy": statistics.mean([r["buy_seed_600_671"][product] for r in losers]) if losers else None,
            "winner_mean_finalday_sell": statistics.mean([r["sell_696_718"][product] for r in winners]) if winners else None,
            "loser_mean_finalday_sell": statistics.mean([r["sell_696_718"][product] for r in losers]) if losers else None,
            "by_demand_level": levels,
        }

    team_summary = {}
    for team in sorted(set(r["team"] for r in rows_out)):
        rr=[r for r in rows_out if r["team"]==team]
        team_summary[team]={
            "games":len(rr),
            "wins":sum(1 for r in rr if r["winner"]),
            "mean_reward":statistics.mean(r["reward"] for r in rr),
            "mean_seed_buys_600_671":{p:statistics.mean(r["buy_seed_600_671"][p] for r in rr) for p in PRODUCTS},
        }

    report={
        "schema_version":"live-meta-demand-response-v1",
        "source":{"date":date,"index_row":idx_row,"top_n":args.top},
        "products":products,
        "teams":team_summary,
        "rows":rows_out,
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"source":report["source"],"products":products,"teams":team_summary},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
