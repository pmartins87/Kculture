"""KEXP-034: mechanics-first late WHEAT->CARROT value-margin audit.

Diagnostic only. Runs frozen R4B on development + exploratory live-meta seeds.
Uses corrected replay alignment: observation/state t pairs with action frame t+1.
For every R4B WHEAT plant in the KEXP-023 mechanically clean windows, replay the
same same-tile WATER/FERTILIZE/HARVEST schedule on a counterfactual CARROT tile
and compare current-price and harvest-price economics. No top-player action
labels are used.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import statistics
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

SAFE_STEPS = set(range(614, 619)) | set(range(620, 624)) | set(range(636, 648))
BUY_WINDOW = range(600, 636)
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
TRIGGER_MARGIN = 20.0


def live_seeds(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    found: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int):
                found.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v, list):
            for c in v: walk(c)
    walk(payload)
    return list(dict.fromkeys(found))


def farm(obs: dict) -> dict:
    farms = obs.get("farms") or []
    return farms[0] if farms else {}


def tile_at(f: dict, pos):
    if not (isinstance(pos, (list, tuple)) and len(pos) == 2): return None
    try:
        x, y = int(pos[0]), int(pos[1])
        return f["tiles"][y][x]
    except Exception:
        return None


def actor_ops(obs: dict, action: dict | None):
    f = farm(obs); action = action or {}
    out = []
    if isinstance(f.get("farmer"), list):
        out.append((0, tuple(f["farmer"]), action.get("farmer") or ["PASS"]))
    hops = list(action.get("hands") or [])
    for i, pos in enumerate(f.get("hands") or [], start=1):
        out.append((i, tuple(pos), hops[i-1] if i-1 < len(hops) else ["PASS"]))
    return out


def paired_action(steps, t: int) -> dict:
    if t + 1 >= len(steps): return {}
    return steps[t + 1][0].get("action") or {}


def price(obs: dict, item: str) -> float | None:
    try:
        x = float((((obs.get("market") or {}).get("prices") or {}).get(item)))
        return x if math.isfinite(x) and x > 0 else None
    except Exception:
        return None


def demand(obs: dict) -> tuple[int, int]:
    c = collections.Counter()
    for shop in list(((obs.get("town") or {}).get("unlocked_shops") or [])):
        ps = SHOPS.get(shop, ())
        mult = 2 if len(ps) == 1 else 1
        for p in ps: c[p] += mult
    return int(c["WHEAT"]), int(c["CARROT"])


def market_seed_buys(action: dict | None) -> tuple[int, int]:
    w = c = 0
    for order in list((action or {}).get("market") or []):
        if not (isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_SEED"):
            continue
        try: q = max(0, int(order[2] or 0))
        except Exception: continue
        if order[1] == "WHEAT": w += q
        elif order[1] == "CARROT": c += q
    return w, c


def refresh_carrot(state: dict, next_day: int):
    while state["alive"] and state["day"] < next_day:
        if state["watered_today"]:
            state["consecutive_unwatered"] = 0
        else:
            state["consecutive_unwatered"] += 1
        state["watered_today"] = False
        if state["consecutive_unwatered"] >= 2:
            state["alive"] = False
            state["yield_units"] = 0
            break
        state["day"] += 1
    if state["day"] < next_day:
        state["day"] = next_day


def simulate_same_route_carrot(steps, plant_t: int, pos: tuple[int, int]):
    obs0 = steps[plant_t][0].get("observation") or {}
    plant_day = int(obs0.get("day", 0) or 0)
    st = {
        "day": plant_day, "planted_day": plant_day, "watered_today": False,
        "consecutive_unwatered": 1, "yield_units": 1,
        "fertilized_until_day": -1, "alive": True,
    }
    harvest_step = None
    actual_wheat_units = None
    fertilize_count = water_count = 0
    started = False

    for u in range(plant_t, min(719, len(steps) - 1)):
        obs = steps[u][0].get("observation") or {}
        day = int(obs.get("day", 0) or 0)
        if started:
            refresh_carrot(st, day)
        ops = actor_ops(obs, paired_action(steps, u))
        for _, upos, op in ops:
            if upos != pos or not (isinstance(op, list) and op):
                continue
            if not started:
                if u == plant_t and len(op) > 1 and op[:2] == ["PLANT", "WHEAT"]:
                    started = True
                continue
            if not st["alive"]:
                if op[0] == "HARVEST":
                    harvest_step = u
                    return st, harvest_step, 0, water_count, fertilize_count
                continue
            if op[0] == "FERTILIZE":
                st["fertilized_until_day"] = max(st["fertilized_until_day"], day + 2)
                fertilize_count += 1
            elif op[0] == "WATER" and not st["watered_today"]:
                st["watered_today"] = True
                water_count += 1
                age = day - st["planted_day"]
                if 2 <= age <= 3:
                    bonus = 2 if st["fertilized_until_day"] >= day else 1
                    st["yield_units"] = min(4, st["yield_units"] + bonus)
            elif op[0] == "HARVEST":
                harvest_step = u
                wt = tile_at(farm(obs), pos)
                if isinstance(wt, dict) and wt.get("kind") == "PLANT" and wt.get("crop") == "WHEAT":
                    try: actual_wheat_units = max(0, int(wt.get("yield_units", 0) or 0))
                    except Exception: actual_wheat_units = 0
                return st, harvest_step, actual_wheat_units, water_count, fertilize_count
    return st, None, None, water_count, fertilize_count


def analyze(rep: dict, seed: int, source: str) -> dict:
    steps = rep.get("steps") or []
    rows = []
    wheat_buys = carrot_buys = 0
    for t in BUY_WINDOW:
        if t + 1 >= len(steps): break
        w, c = market_seed_buys(paired_action(steps, t)); wheat_buys += w; carrot_buys += c

    for t in sorted(SAFE_STEPS):
        if t + 1 >= len(steps): continue
        obs = steps[t][0].get("observation") or {}
        act = paired_action(steps, t)
        for actor, pos, op in actor_ops(obs, act):
            if not (isinstance(op, list) and len(op) > 1 and op[:2] == ["PLANT", "WHEAT"]):
                continue
            sim, h, wunits, waters, ferts = simulate_same_route_carrot(steps, t, pos)
            pw0, pc0 = price(obs, "WHEAT"), price(obs, "CARROT")
            if h is None or wunits is None or pw0 is None or pc0 is None or h >= len(steps):
                continue
            hobs = steps[h][0].get("observation") or {}
            pwh, pch = price(hobs, "WHEAT"), price(hobs, "CARROT")
            if pwh is None or pch is None: continue
            cunits = int(sim.get("yield_units", 0) or 0) if sim.get("alive") else 0
            dw, dc = demand(obs)
            simple_proxy = 3.0 * pc0 - 20.0 - (4.0 * pw0 - 10.0)
            route_proxy = cunits * pc0 - 20.0 - (wunits * pw0 - 10.0)
            oracle = cunits * pch - 20.0 - (wunits * pwh - 10.0)
            rows.append({
                "seed": seed, "source": source, "plant_step": t, "actor": actor,
                "position": list(pos), "plant_day": int(obs.get("day", 0) or 0),
                "harvest_step": h, "delay": h - t,
                "wheat_units_actual": wunits, "carrot_units_same_route": cunits,
                "carrot_survives": bool(sim.get("alive")), "water_count": waters,
                "fertilize_count": ferts, "price_wheat_now": pw0, "price_carrot_now": pc0,
                "price_wheat_harvest": pwh, "price_carrot_harvest": pch,
                "demand_wheat": dw, "demand_carrot": dc,
                "simple_proxy_margin_now": simple_proxy,
                "route_proxy_margin_now": route_proxy,
                "oracle_margin_harvest_price": oracle,
                "trigger": simple_proxy >= TRIGGER_MARGIN,
                "oracle_positive": oracle > 0,
            })
    tr = [r for r in rows if r["trigger"]]
    return {
        "seed": seed, "source": source, "wheat_seed_buys_600_635": wheat_buys,
        "carrot_seed_buys_600_635": carrot_buys, "events": len(rows),
        "trigger_events": len(tr), "rows": rows,
    }


def summarize(episodes: list[dict], source: str) -> dict:
    ee = episodes if source == "all" else [e for e in episodes if e["source"] == source]
    rows = [r for e in ee for r in e["rows"]]
    tr = [r for r in rows if r["trigger"]]
    wb = [e["wheat_seed_buys_600_635"] for e in ee]
    return {
        "episodes": len(ee), "events": len(rows),
        "episodes_with_trigger": sum(e["trigger_events"] > 0 for e in ee),
        "trigger_events": len(tr),
        "carrot_survival_fraction_all_events": (sum(r["carrot_survives"] for r in rows) / len(rows)) if rows else None,
        "trigger_oracle_positive_fraction": (sum(r["oracle_positive"] for r in tr) / len(tr)) if tr else None,
        "trigger_mean_oracle_margin": statistics.mean(r["oracle_margin_harvest_price"] for r in tr) if tr else None,
        "trigger_median_oracle_margin": statistics.median(r["oracle_margin_harvest_price"] for r in tr) if tr else None,
        "median_wheat_seed_buys_600_635": statistics.median(wb) if wb else None,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    episodes = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        agent = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([agent, "starter"])
        episodes.append(analyze(env.toJSON(), int(seed), source))

    summary = {s: summarize(episodes, s) for s in ("development", "live_meta", "all")}
    d, l = summary["development"], summary["live_meta"]
    gate = {
        "eligible_for_seed_reallocation_candidate": bool(
            d["episodes_with_trigger"] >= 4 and l["episodes_with_trigger"] >= 5
            and d["trigger_events"] >= 8 and l["trigger_events"] >= 10
            and (d["trigger_oracle_positive_fraction"] or 0) >= 0.70
            and (l["trigger_oracle_positive_fraction"] or 0) >= 0.70
            and (d["trigger_mean_oracle_margin"] or 0) > 0
            and (l["trigger_mean_oracle_margin"] or 0) > 0
            and (d["median_wheat_seed_buys_600_635"] or 0) >= 4
            and (l["median_wheat_seed_buys_600_635"] or 0) >= 4
        ),
        "trigger": "3*current_carrot_price - 20 - (4*current_wheat_price - 10) >= 20",
        "criteria": "support in both pools; >=70% future-price oracle sign precision; positive mean oracle margin; median >=4 WHEAT seed buys available for reallocation",
    }
    payload = {"schema_version": "late-crop-value-margin-v1", "safe_steps": sorted(SAFE_STEPS),
               "trigger_margin": TRIGGER_MARGIN, "summary": summary, "gate": gate, "episodes": episodes}
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"summary": summary, "gate": gate}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
