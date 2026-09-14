#!/usr/bin/env python3
"""E2C diagnostic: explain E2B nonlinear deltas without modifying policy bytes."""
from __future__ import annotations
import sys
from collections import Counter, defaultdict
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates.fp001_e2_dedicated_strawberry_hand import make_agent
from candidates.fp001_h10_cow_scale_module import TARGET_POSITIONS

SEEDS = (69304, 69305, 69306)  # one positive, two catastrophic E2B COW5_DAILY cases
CFG = {"episodeSteps": 720, "startingMoney": 3000, "weedSpawnChance": 0}


def _get(o, k, d=None):
    try: return o.get(k, d)
    except Exception:
        try: return o[k]
        except Exception: return d


def pass_agent(obs, config=None):
    return {"farmer": ["PASS"], "hands": [], "market": []}


def snap(obs, action):
    farm = obs.farms[obs.player]
    private = obs.private
    day, hour = int(obs.day), int(obs.hour)
    inv0 = private.inventories[0] if private.inventories else {}
    cows = []
    for pos in TARGET_POSITIONS[:5]:
        x, y = pos
        t = farm.tiles[y][x]
        if isinstance(t, dict) and t.get("animal") == "COW":
            cows.append({
                "pos": pos,
                "placed": int(t.get("placed_day", -1)),
                "yield": int(t.get("yield_units", 0)),
                "unfed": int(t.get("consecutive_unfed", 0)),
                "fed": bool(t.get("fed_today", False)),
                "care": bool(t.get("cared_today", False)),
                "pending": int(t.get("pending_care_bonus", 0)),
            })
    market = [list(x) for x in (action.get("market") or [])]
    return {
        "step": day * 24 + hour,
        "day": day,
        "hour": hour,
        "money": float(farm.money),
        "hands": len(farm.hands),
        "main": list(action.get("farmer") or ["PASS"]),
        "market": market,
        "wheat_shed": int(private.shed.get("WHEAT", 0)),
        "wheat_inv": int(inv0.get("WHEAT", 0)),
        "milk_shed": int(private.shed.get("MILK", 0)),
        "fert_shed": int(private.shed.get("FERTILIZER", 0)),
        "straw_shed": int(private.shed.get("STRAWBERRY", 0)),
        "cow_count": len(cows),
        "cow_yield": sum(c["yield"] for c in cows),
        "cow_pending": sum(c["pending"] for c in cows),
        "cow_fed": sum(c["fed"] for c in cows),
        "cow_care": sum(c["care"] for c in cows),
    }


def run(seed, treatment):
    hist = []
    base = make_agent(5, "DAILY", treatment, treatment)
    def rec(obs, config=None):
        a = base(obs, config)
        hist.append(snap(obs, a))
        return a
    env = make("kaggriculture", configuration={**CFG, "seed": seed}, debug=True)
    env.run([rec, pass_agent])
    reward = float(env.toJSON()["rewards"][0])
    return reward, hist


def orders(hist, op=None, item=None):
    out = []
    for s in hist:
        for o in s["market"]:
            if not o: continue
            if op is not None and o[0] != op: continue
            if item is not None and (len(o) < 2 or o[1] != item): continue
            out.append((s["step"], o, s["money"]))
    return out


def summarize(label, reward, hist):
    acts = Counter(s["main"][0] for s in hist)
    first5 = next((s["step"] for s in hist if s["cow_count"] == 5), None)
    min_money = min(s["money"] for s in hist)
    max_pending = max(s["cow_pending"] for s in hist)
    print("SUMMARY", label, {
        "reward": reward,
        "first_5_cows_step": first5,
        "min_money": min_money,
        "main_FEED": acts["FEED"],
        "main_CARE": acts["CARE"],
        "main_HARVEST": acts["HARVEST"],
        "main_COLLECT": acts["COLLECT_FERTILIZER"],
        "main_moves": sum(acts[d] for d in ("NORTH","SOUTH","EAST","WEST")),
        "max_pending_care": max_pending,
        "wheat_buy_orders": orders(hist, "BUY_PRODUCT", "WHEAT"),
        "milk_sell_orders": orders(hist, "SELL", "MILK"),
    })


def main():
    for seed in SEEDS:
        r0, h0 = run(seed, False)
        r1, h1 = run(seed, True)
        summarize(f"seed{seed}_S0", r0, h0)
        summarize(f"seed{seed}_S1H1", r1, h1)
        print("DELTA", seed, r1-r0)

        # First points where animal-facing state/action diverges. Market extras alone
        # are omitted unless they induce cash/wheat/animal-state divergence.
        shown = 0
        for a, b in zip(h0, h1):
            diffs = {}
            for k in ("money","cow_count","wheat_shed","wheat_inv","milk_shed","cow_yield","cow_pending","cow_fed","cow_care","main"):
                if a[k] != b[k]: diffs[k] = (a[k], b[k])
            if diffs:
                print("DIVERGE", seed, a["step"], diffs, "base_market", a["market"], "treat_market", b["market"])
                shown += 1
                if shown >= 24:
                    break
        print("END_SEED", seed)

if __name__ == "__main__":
    main()
