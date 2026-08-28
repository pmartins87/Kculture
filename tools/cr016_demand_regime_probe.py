"""CR-016: measure missed public-demand regimes before designing a new agent.

Runs frozen R4B against exact current-meta opponents on preregistered fresh seeds.
At one state per in-game day it measures town shop demand, market price, and a
simple public producer-capacity proxy for CARROT, TOMATO and EGG.  The goal is
to quantify whether the recent market/demand mechanics create recurrent niches
that R4B and opponents leave under-produced.  This script never changes actions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
CFG=ROOT/"configs/cr016_demand_regime_probe_v1.json"
R4B=ROOT/"candidates/r4b_ablation_market_only.py"
BASE_PRICE={"CARROT":35.0,"TOMATO":60.0,"EGG":50.0}


def load_agent(path:Path):
    spec=importlib.util.spec_from_file_location(f"cr016_{path.stem}_{time.time_ns()}",path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m.agent


def play(opponent:Path,seed:int,seat:int):
    a=load_agent(R4B); o=load_agent(opponent)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True)
    env.run([a,o] if seat==0 else [o,a]); return env.toJSON()


def get(o,k,d=None):
    try:return o.get(k,d)
    except Exception:return d


def producer_count(farm,product):
    total=0
    for row in get(farm,"tiles",[]) or []:
        if not isinstance(row,list): continue
        for tile in row:
            if not isinstance(tile,dict): continue
            if product in ("CARROT","TOMATO") and tile.get("kind")=="PLANT" and tile.get("crop")==product: total+=1
            if product=="EGG" and tile.get("animal")=="GOOSE": total+=1
    return total


def demand_score(shops,weights):
    return sum(float(weights.get(s,0)) for s in (shops or []))


def sample_episode(rep,seat,cfg):
    rows=[]
    # post-interpreter replay states expose the public observation in either player.
    for frame in rep.get("steps") or []:
        if len(frame)<2: continue
        o=frame[seat].get("observation") if isinstance(frame[seat],dict) else None
        if not isinstance(o,dict): continue
        day=int(get(o,"day",0) or 0); hour=int(get(o,"hour",0) or 0)
        if hour!=23: continue
        farms=get(o,"farms",[]) or []
        if len(farms)<2: continue
        market=get(o,"market",{}) or {}; prices=get(market,"prices",{}) or {}; inv=get(market,"inventory",{}) or {}
        shops=get(get(o,"town",{}) or {},"unlocked_shops",[]) or []
        for product in cfg["products"]:
            rows.append({
                "day":day,"product":product,
                "shop_demand":demand_score(shops,cfg["shop_weights"][product]),
                "price":float(get(prices,product,0) or 0),
                "price_ratio":float(get(prices,product,0) or 0)/BASE_PRICE[product],
                "inventory":float(get(inv,product,0) or 0),
                "self_producers":producer_count(farms[seat],product),
                "opp_producers":producer_count(farms[1-seat],product),
            })
    return rows


def product_summary(rows,product):
    xs=[r for r in rows if r["product"]==product]
    demand=[r for r in xs if r["shop_demand"]>0]
    high=[r for r in demand if r["price_ratio"]>=1.20]
    niche=[r for r in high if r["self_producers"]==0]
    empty=[r for r in high if r["self_producers"]==0 and r["opp_producers"]==0]
    late=[r for r in xs if r["day"]>=20]
    def frac(n,d): return n/d if d else 0.0
    return {
        "samples":len(xs),
        "demand_samples":len(demand),
        "high_price_demand_samples":len(high),
        "self_zero_in_high_price_demand":len(niche),
        "both_zero_in_high_price_demand":len(empty),
        "self_zero_fraction_high_price_demand":frac(len(niche),len(high)),
        "both_zero_fraction_high_price_demand":frac(len(empty),len(high)),
        "mean_price_ratio_when_demanded":statistics.mean(r["price_ratio"] for r in demand) if demand else None,
        "max_price_ratio":max((r["price_ratio"] for r in xs),default=None),
        "late_mean_price_ratio":statistics.mean(r["price_ratio"] for r in late) if late else None,
        "late_mean_self_producers":statistics.mean(r["self_producers"] for r in late) if late else None,
        "late_mean_opp_producers":statistics.mean(r["opp_producers"] for r in late) if late else None,
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--opponent-dir",required=True); ap.add_argument("--output",required=True)
    args=ap.parse_args(); cfg=json.loads(CFG.read_text()); od=Path(args.opponent_dir); od=od if od.is_absolute() else ROOT/od
    opponents=sorted(od.glob("*.py")); rows=[]; episodes=[]; errors=[]
    for seed in cfg["seeds"]:
        for opp in opponents:
            try:
                rep=play(opp,int(seed),int(cfg["seat"])); sr=sample_episode(rep,int(cfg["seat"]),cfg); rows.extend(sr)
                frame=rep["steps"][-1]; reward=float(frame[int(cfg["seat"])].get("reward")); other=float(frame[1-int(cfg["seat"])].get("reward"))
                episodes.append({"seed":seed,"opponent":opp.stem,"samples":len(sr),"r4b_delta":reward-other})
            except Exception as exc: errors.append({"seed":seed,"opponent":opp.stem,"error":repr(exc)})
    summary={p:product_summary(rows,p) for p in cfg["products"]}
    payload={
        "experiment":"CR-016","status":"PASS" if not errors else "ERRORS",
        "engine":"kaggle-environments==1.32.7","config":str(CFG.relative_to(ROOT)),
        "episodes":len(episodes),"expected_episodes":len(cfg["seeds"])*len(opponents),"errors":errors,
        "summary":summary,"episode_records":episodes,"daily_rows":rows,
        "interpretation_rule":"A product becomes an architecture candidate only if high-price demanded states recur across multiple seeds/opponents while R4B producer capacity is frequently zero. This probe alone cannot set a policy threshold or authorize hosted submission."
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in payload.items() if k not in ("daily_rows","episode_records","errors")}|{"error_count":len(errors)},indent=2,sort_keys=True))
    if errors: raise SystemExit(2)

if __name__=="__main__": main()
