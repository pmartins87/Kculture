"""KEXP-035: exact final-day marginal-value audit for frozen-R4B WATER intents.

Corrects the rejected KEXP-032 premise. One-time crop WATER can increase
`yield_units` immediately, even without another end-of-day refresh. This audit
classifies every R4B WATER in executable states 696..718 by exact immediate
yield gain and whether that gain has a later HARVEST->same-actor DROP path
before terminal liquidation.

Diagnostic only. Development + exploratory live-meta environmental seeds.
Replay alignment: state/observation t pairs with action stored on frame t+1.
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

START, END = 696, 718
CROPS = {
    "WHEAT": {"max_yield_day": 4, "max_yield": 6, "ongoing": False, "product": "WHEAT"},
    "CARROT": {"max_yield_day": 3, "max_yield": 4, "ongoing": False, "product": "CARROT"},
    "TOMATO": {"max_yield_day": 8, "max_yield": 4, "ongoing": True, "product": "TOMATO"},
    "STRAWBERRY": {"max_yield_day": 10, "max_yield": 4, "ongoing": True, "product": "STRAWBERRY"},
    "MELON": {"max_yield_day": 12, "max_yield": 6, "ongoing": False, "product": "MELON"},
}


def live_seeds(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8")); found=[]
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int): found.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v, list):
            for c in v: walk(c)
    walk(payload)
    return list(dict.fromkeys(found))


def obs_at(steps, t):
    return steps[t][0].get("observation") or {}


def paired_action(steps, t):
    return (steps[t+1][0].get("action") or {}) if t+1 < len(steps) else {}


def farm(obs):
    farms=obs.get("farms") or []
    return farms[0] if farms else {}


def actor_ops(obs, action):
    f=farm(obs); action=action or {}; out=[]
    if isinstance(f.get("farmer"), list):
        out.append((0, tuple(f["farmer"]), action.get("farmer") or ["PASS"]))
    hands=list(action.get("hands") or [])
    for i,pos in enumerate(f.get("hands") or [], start=1):
        out.append((i, tuple(pos), hands[i-1] if i-1 < len(hands) else ["PASS"]))
    return out


def tile_at(f, pos):
    try:
        x,y=int(pos[0]),int(pos[1]); return f["tiles"][y][x]
    except Exception: return None


def immediate_water_gain(tile: dict | None, day: int):
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
        return 0, "not_plant", None
    crop=tile.get("crop"); cd=CROPS.get(crop)
    if not cd: return 0, "unknown_crop", crop
    if bool(tile.get("watered_today", False)):
        return 0, "already_watered", crop
    if cd["ongoing"]:
        return 0, "ongoing_crop_no_immediate_water_yield", crop
    try:
        planted=int(tile.get("planted_day", day) or day)
        held=max(0,int(tile.get("yield_units",0) or 0))
        fert_until=int(tile.get("fertilized_until_day",-1) or -1)
    except Exception:
        return 0, "malformed_tile", crop
    age=day-planted
    window_start=(cd["max_yield_day"]+1)//2
    if not (window_start <= age <= cd["max_yield_day"]):
        return 0, "outside_bonus_window", crop
    cap=max(0, int(cd["max_yield"])-held)
    if cap <= 0: return 0, "yield_capped", crop
    bonus=2 if fert_until >= day else 1
    return min(cap,bonus), "immediate_bonus", crop


def future_harvest_drop_path(steps, water_t, pos):
    # Find first later same-tile HARVEST and then a later DROP by that actor.
    for h in range(water_t+1, min(END, len(steps)-2)+1):
        obs=obs_at(steps,h); action=paired_action(steps,h)
        for actor,hpos,op in actor_ops(obs,action):
            if hpos != pos or not (isinstance(op,list) and op and op[0] == "HARVEST"):
                continue
            for d in range(h+1, min(END, len(steps)-2)+1):
                dobs=obs_at(steps,d); dact=paired_action(steps,d)
                for dactor,_,dop in actor_ops(dobs,dact):
                    if dactor==actor and isinstance(dop,list) and dop and dop[0] == "DROP":
                        return h,d,actor
            return h,None,actor
    return None,None,None


def terminal_price(steps, product):
    if not product: return None
    t=min(END,len(steps)-2); obs=obs_at(steps,t)
    try: return float((((obs.get("market") or {}).get("prices") or {}).get(product)))
    except Exception: return None


def analyze(rep, seed, source):
    steps=rep.get("steps") or []; rows=[]
    for t in range(START,min(END,len(steps)-2)+1):
        obs=obs_at(steps,t); action=paired_action(steps,t); f=farm(obs)
        day=int(obs.get("day",0) or 0)
        for actor,pos,op in actor_ops(obs,action):
            if not (isinstance(op,list) and op and op[0] == "WATER"): continue
            tile=tile_at(f,pos)
            gain,reason,crop=immediate_water_gain(tile,day)
            h,d,hactor=future_harvest_drop_path(steps,t,pos) if gain>0 else (None,None,None)
            delivered = gain>0 and h is not None and d is not None
            p=terminal_price(steps,crop)
            value=(gain*p) if delivered and p is not None else 0.0
            rows.append({
                "step":t,"actor":actor,"position":list(pos),"crop":crop,
                "reason":reason,"immediate_yield_gain":gain,
                "future_harvest_step":h,"future_drop_step":d,"harvest_actor":hactor,
                "gain_reaches_shed_before_terminal":delivered,
                "terminal_price_proxy":p,"terminal_value_proxy":value,
                "zero_terminal_value_by_audit": not delivered,
            })
    return {"seed":int(seed),"source":source,"water_intents":len(rows),"rows":rows}


def summarize(episodes, source):
    ee=episodes if source=="all" else [e for e in episodes if e["source"]==source]
    rows=[r for e in ee for r in e["rows"]]
    zero=[r for r in rows if r["zero_terminal_value_by_audit"]]
    direct=[r for r in rows if r["immediate_yield_gain"]>0]
    delivered=[r for r in rows if r["gain_reaches_shed_before_terminal"]]
    per=[sum(r["zero_terminal_value_by_audit"] for r in e["rows"]) for e in ee]
    return {
        "episodes":len(ee),"water_intents":len(rows),
        "zero_terminal_value_water":len(zero),
        "zero_fraction":len(zero)/len(rows) if rows else None,
        "immediate_gain_water":len(direct),
        "delivered_gain_water":len(delivered),
        "episodes_with_at_least_3_zero":sum(x>=3 for x in per),
        "median_zero_per_episode":statistics.median(per) if per else None,
        "mean_zero_per_episode":statistics.mean(per) if per else None,
        "reason_counts":dict(Counter(r["reason"] for r in rows)),
        "crop_counts":dict(Counter(str(r["crop"]) for r in rows)),
        "delivered_terminal_value_proxy_sum":sum(r["terminal_value_proxy"] for r in delivered),
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    episodes=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        agent=resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True)
        env.run([agent,"starter"])
        episodes.append(analyze(env.toJSON(),int(seed),source))
    summary={s:summarize(episodes,s) for s in ("development","live_meta","all")}
    d,l=summary["development"],summary["live_meta"]
    gate={
        "terminal_replanner_headroom": bool(
            (d["median_zero_per_episode"] or 0)>=3 and (l["median_zero_per_episode"] or 0)>=3
            and d["episodes_with_at_least_3_zero"]>=8 and l["episodes_with_at_least_3_zero"]>=10
        ),
        "criteria":"median >=3 audited zero-terminal-value WATER per episode and >=50% of episodes with >=3 in both pools",
        "note":"Passing authorizes only a planner that preserves every WATER with a delivered marginal-yield path."
    }
    payload={"schema_version":"terminal-water-marginal-value-v1","window":[START,END],"summary":summary,"gate":gate,"episodes":episodes}
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"summary":summary,"gate":gate},indent=2,sort_keys=True))

if __name__=="__main__": main()
