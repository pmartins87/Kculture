"""KEXP-043: classify frozen-R4B midgame PASS headroom.

Diagnostic only. For every R4B PASS at states 96..287, inspect the actor's
current legal public/private state and classify whether a useful same-tile
operation is immediately available. This distinguishes cheap local fallback
headroom from the need for a real dynamic task dispatcher.

Correct replay alignment: state t -> action on frame t+1.
Development + exploratory live-meta environmental seeds only.
"""
from __future__ import annotations

import argparse, collections, json, statistics, sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent

START,END=96,287
PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")


def live_seeds(path):
    x=json.loads(path.read_text(encoding="utf-8"));out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int):out.append(v["seed"])
            for c in v.values():walk(c)
        elif isinstance(v,list):
            for c in v:walk(c)
    walk(x);return list(dict.fromkeys(out))


def obs(rep,t): return rep["steps"][t][0].get("observation") or {}
def action(rep,t): return (rep["steps"][t+1][0].get("action") or {}) if t+1<len(rep["steps"]) else {}

def farm(o):
    fs=o.get("farms") or [];return fs[0] if fs else {}

def tile_at(f,pos):
    try:return f["tiles"][int(pos[1])][int(pos[0])]
    except Exception:return None

def shed_tiles(f):
    n=len(f.get("tiles",[]) or []) or 10;h=n//2
    return {(h-1,h-1),(h,h-1),(h-1,h),(h,h)}

def actors(o,a):
    f=farm(o);priv=o.get("private") or {};invs=list(priv.get("inventories") or [])
    out=[]
    if isinstance(f.get("farmer"),list):
        out.append((0,tuple(f["farmer"]),a.get("farmer") or ["PASS"],invs[0] if len(invs)>0 and isinstance(invs[0],dict) else {}))
    hops=list(a.get("hands") or [])
    for i,p in enumerate(f.get("hands") or [],start=1):
        out.append((i,tuple(p),hops[i-1] if i-1<len(hops) else ["PASS"],invs[i] if i<len(invs) and isinstance(invs[i],dict) else {}))
    return out

def positive_inventory(inv): return sum(max(0,int(inv.get(k,0) or 0)) for k in PRODUCTS)>0

def classify(o,pos,inv):
    f=farm(o);t=tile_at(f,pos);day=int(o.get("day",0) or 0);reasons=[]
    if tuple(pos) in shed_tiles(f) and positive_inventory(inv):reasons.append("DROP")
    if isinstance(t,dict):
        kind=t.get("kind")
        if kind=="WEED":reasons.append("DIG")
        elif kind=="PLANT":
            if not bool(t.get("watered_today",False)):reasons.append("WATER")
            if int(t.get("yield_units",0) or 0)>0:reasons.append("HARVEST_PLANT")
            if int(inv.get("FERTILIZER",0) or 0)>0 and int(t.get("fertilized_until_day",-1) or -1)<day+2:reasons.append("FERTILIZE")
        if t.get("animal"):
            if int(t.get("yield_units",0) or 0)>0:reasons.append("HARVEST_ANIMAL")
            if bool(t.get("fertilizer_available",False)):reasons.append("COLLECT_FERTILIZER")
            if not bool(t.get("fed_today",False)) and int(inv.get("WHEAT",0) or 0)>0:reasons.append("FEED")
            if not bool(t.get("cared_today",False)):reasons.append("CARE")
    return reasons

def nearest_task_distance(o,pos):
    f=farm(o);best=None;types=set()
    for y,row in enumerate(f.get("tiles",[]) or []):
        for x,t in enumerate(row or []):
            if not isinstance(t,dict):continue
            cand=[]
            if t.get("kind")=="WEED":cand.append("DIG")
            elif t.get("kind")=="PLANT":
                if not bool(t.get("watered_today",False)):cand.append("WATER")
                if int(t.get("yield_units",0) or 0)>0:cand.append("HARVEST_PLANT")
            if t.get("animal"):
                if int(t.get("yield_units",0) or 0)>0:cand.append("HARVEST_ANIMAL")
                if bool(t.get("fertilizer_available",False)):cand.append("COLLECT_FERTILIZER")
            if not cand:continue
            d=abs(int(pos[0])-x)+abs(int(pos[1])-y)
            if best is None or d<best:best=d;types=set(cand)
            elif d==best:types.update(cand)
    return best,sorted(types)

def analyze(rep,seed,source):
    rows=[]
    for t in range(START,min(END,len(rep.get("steps") or [])-2)+1):
        o=obs(rep,t);a=action(rep,t)
        for idx,pos,op,inv in actors(o,a):
            if not (isinstance(op,list) and op and op[0]=="PASS"):continue
            rs=classify(o,pos,inv);dist,near=nearest_task_distance(o,pos)
            rows.append({"seed":int(seed),"source":source,"step":t,"actor":idx,"position":list(pos),"same_tile_opportunities":rs,"nearest_task_distance":dist,"nearest_task_types":near,"carried_units":sum(max(0,int(inv.get(k,0) or 0)) for k in PRODUCTS)})
    return rows

def summarize(rows,source):
    rr=rows if source=="all" else [r for r in rows if r["source"]==source]
    same=[r for r in rr if r["same_tile_opportunities"]];dists=[r["nearest_task_distance"] for r in rr if isinstance(r["nearest_task_distance"],int)]
    rc=collections.Counter(x for r in rr for x in r["same_tile_opportunities"])
    return {"pass_intents":len(rr),"same_tile_useful":len(same),"same_tile_fraction":len(same)/len(rr) if rr else None,"same_tile_reason_counts":dict(rc),"median_nearest_task_distance":statistics.median(dists) if dists else None,"within_1_task_fraction":sum((r["nearest_task_distance"] is not None and r["nearest_task_distance"]<=1) for r in rr)/len(rr) if rr else None,"within_2_task_fraction":sum((r["nearest_task_distance"] is not None and r["nearest_task_distance"]<=2) for r in rr)/len(rr) if rr else None,"carrying_pass_fraction":sum(r["carried_units"]>0 for r in rr)/len(rr) if rr else None}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True);args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"];live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        a=resolve_agent("file:candidates/r4b_ablation_market_only.py:agent");env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True);env.run([a,"starter"]);rows.extend(analyze(env.toJSON(),seed,source))
    sm={s:summarize(rows,s) for s in ("development","live_meta","all")}
    gate={"local_fallback_headroom":bool((sm["development"]["same_tile_fraction"] or 0)>=0.20 and (sm["live_meta"]["same_tile_fraction"] or 0)>=0.20),"dispatcher_headroom":bool((sm["development"]["within_2_task_fraction"] or 0)>=0.50 and (sm["live_meta"]["within_2_task_fraction"] or 0)>=0.50),"interpretation":"same-tile >=20% supports a cheap PASS fallback; within-2 >=50% supports a bounded dynamic task dispatcher even if same-tile is sparse"}
    payload={"schema_version":"midgame-pass-headroom-v1","window":[START,END],"summary":sm,"gate":gate,"rows":rows};out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps({"summary":sm,"gate":gate},indent=2,sort_keys=True))
if __name__=="__main__":main()
