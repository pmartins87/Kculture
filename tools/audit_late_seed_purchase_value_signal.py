"""KEXP-038: purchase-time transport of exact late crop route value.

KEXP-034 found that in the audited mechanically safe late WHEAT route slots,
WHEAT and counterfactual CARROT produce the same units under the copied route:
3 vs 3 in the earlier safe block and 2 vs 2 in the later block. Therefore the
same-route gross comparative value at any public market state is exactly

    q * (CARROT_price - WHEAT_price) - 10

where q is route yield and 10 is the extra CARROT seed cost.

This diagnostic asks whether that sign is already informative at the latest
preceding R4B WHEAT seed-purchase state, where a deployable controller could
actually reallocate part of the purchase. No top-agent action labels are used.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

SAFE_STEPS = set(range(614, 619)) | set(range(620, 624)) | set(range(636, 648))
BUY_START, BUY_END = 580, 635


def live_seeds(path: Path) -> list[int]:
    payload=json.loads(path.read_text(encoding="utf-8")); found=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int): found.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v,list):
            for c in v: walk(c)
    walk(payload)
    return list(dict.fromkeys(found))


def obs_at(steps,t): return steps[t][0].get("observation") or {}
def paired_action(steps,t): return (steps[t+1][0].get("action") or {}) if t+1 < len(steps) else {}

def farm(obs):
    fs=obs.get("farms") or []
    return fs[0] if fs else {}


def actor_ops(obs,action):
    f=farm(obs); action=action or {}; out=[]
    if isinstance(f.get("farmer"),list): out.append((0,tuple(f["farmer"]),action.get("farmer") or ["PASS"]))
    hops=list(action.get("hands") or [])
    for i,pos in enumerate(f.get("hands") or [],start=1):
        out.append((i,tuple(pos),hops[i-1] if i-1 < len(hops) else ["PASS"]))
    return out


def tile_at(f,pos):
    try: return f["tiles"][int(pos[1])][int(pos[0])]
    except Exception: return None


def price(obs,item):
    try:
        x=float((((obs.get("market") or {}).get("prices") or {}).get(item)))
        return x if math.isfinite(x) and x>0 else None
    except Exception: return None


def wheat_buys(action):
    q=0
    for order in list((action or {}).get("market") or []):
        if isinstance(order,list) and len(order)>=3 and order[:2]==["BUY_SEED","WHEAT"]:
            try: q+=max(0,int(order[2] or 0))
            except Exception: pass
    return q


def harvest_info(steps,plant_t,pos):
    for h in range(plant_t+1,min(719,len(steps)-1)):
        obs=obs_at(steps,h); act=paired_action(steps,h)
        for _,hpos,op in actor_ops(obs,act):
            if hpos!=pos or not (isinstance(op,list) and op and op[0]=="HARVEST"): continue
            tile=tile_at(farm(obs),pos)
            if not (isinstance(tile,dict) and tile.get("kind")=="PLANT" and tile.get("crop")=="WHEAT"):
                continue
            try: q=max(0,int(tile.get("yield_units",0) or 0))
            except Exception: q=0
            return h,q
    return None,None


def analyze(rep,seed,source):
    steps=rep.get("steps") or []
    buys=[]
    for t in range(BUY_START,min(BUY_END,len(steps)-2)+1):
        q=wheat_buys(paired_action(steps,t))
        if q<=0: continue
        obs=obs_at(steps,t); pw=price(obs,"WHEAT"); pc=price(obs,"CARROT")
        if pw is None or pc is None: continue
        buys.append({"step":t,"qty":q,"pw":pw,"pc":pc})

    rows=[]
    for t in sorted(SAFE_STEPS):
        if t+1>=len(steps): continue
        obs=obs_at(steps,t); act=paired_action(steps,t)
        for actor,pos,op in actor_ops(obs,act):
            if not (isinstance(op,list) and len(op)>1 and op[:2]==["PLANT","WHEAT"]): continue
            preceding=[b for b in buys if b["step"]<t]
            if not preceding: continue
            b=max(preceding,key=lambda x:x["step"])
            h,q=harvest_info(steps,t,pos)
            if h is None or not q: continue
            hpw=price(obs_at(steps,h),"WHEAT"); hpc=price(obs_at(steps,h),"CARROT")
            ppw=price(obs,"WHEAT"); ppc=price(obs,"CARROT")
            if None in (hpw,hpc,ppw,ppc): continue
            buy_margin=q*(b["pc"]-b["pw"])-10.0
            plant_margin=q*(ppc-ppw)-10.0
            oracle_margin=q*(hpc-hpw)-10.0
            rows.append({
                "seed":int(seed),"source":source,"plant_step":t,"actor":actor,"position":list(pos),
                "purchase_step":b["step"],"purchase_qty":b["qty"],"route_yield":q,"harvest_step":h,
                "purchase_price_wheat":b["pw"],"purchase_price_carrot":b["pc"],
                "plant_price_wheat":ppw,"plant_price_carrot":ppc,
                "harvest_price_wheat":hpw,"harvest_price_carrot":hpc,
                "purchase_value_margin":buy_margin,"plant_value_margin":plant_margin,
                "oracle_harvest_margin":oracle_margin,
                "purchase_positive":buy_margin>0,"plant_positive":plant_margin>0,"oracle_positive":oracle_margin>0,
            })
    return {"seed":int(seed),"source":source,"buy_events":buys,"rows":rows}


def summarize(episodes,source):
    ee=episodes if source=="all" else [e for e in episodes if e["source"]==source]
    rows=[r for e in ee for r in e["rows"]]; pos=[r for r in rows if r["purchase_positive"]]
    by_ep={e["seed"]:e for e in ee}
    return {
        "episodes":len(ee),"mapped_safe_plant_events":len(rows),
        "episodes_with_purchase_positive":sum(any(r["purchase_positive"] for r in e["rows"]) for e in ee),
        "purchase_positive_events":len(pos),
        "purchase_positive_oracle_precision":(sum(r["oracle_positive"] for r in pos)/len(pos)) if pos else None,
        "purchase_positive_plant_precision":(sum(r["plant_positive"] for r in pos)/len(pos)) if pos else None,
        "purchase_positive_mean_oracle_margin":statistics.mean(r["oracle_harvest_margin"] for r in pos) if pos else None,
        "purchase_positive_median_oracle_margin":statistics.median(r["oracle_harvest_margin"] for r in pos) if pos else None,
        "purchase_step_counts":dict(Counter(r["purchase_step"] for r in rows)),
        "route_yield_counts":dict(Counter(r["route_yield"] for r in rows)),
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
        "eligible_for_bounded_purchase_reallocation":bool(
            d["episodes_with_purchase_positive"]>=4 and l["episodes_with_purchase_positive"]>=5
            and d["purchase_positive_events"]>=10 and l["purchase_positive_events"]>=10
            and (d["purchase_positive_oracle_precision"] or 0)>=0.70
            and (l["purchase_positive_oracle_precision"] or 0)>=0.70
            and (d["purchase_positive_mean_oracle_margin"] or 0)>0
            and (l["purchase_positive_mean_oracle_margin"] or 0)>0
        ),
        "deployable_rule":"at WHEAT purchase state, route-yield q * (CARROT_price - WHEAT_price) - 10 > 0",
        "criteria":"support in both pools; >=70% later oracle-positive among sign-positive purchase events; positive mean oracle margin",
    }
    payload={"schema_version":"late-seed-purchase-value-signal-v1","safe_steps":sorted(SAFE_STEPS),"summary":summary,"gate":gate,"episodes":episodes}
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"summary":summary,"gate":gate},indent=2,sort_keys=True))

if __name__=="__main__": main()
