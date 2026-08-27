"""KEXP-040: one-step-ahead JIT CARROT value signal for safe late WHEAT slots.

Unlike purchase-reallocation, this branch treats the prior WHEAT purchase as a
sunk cost. A controller may buy one new CARROT seed on state t-1 and replace a
safe R4B WHEAT PLANT on t. Comparative incremental value is therefore

    q * (CARROT_price - WHEAT_price) - 20

using equal same-route yield q found by KEXP-034. This audit asks whether the
sign at t-1 predicts positive value at later harvest pricing. No policy change.
"""
from __future__ import annotations

import argparse, json, math, statistics, sys
from collections import Counter
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent

SAFE_STEPS=set(range(614,619))|set(range(620,624))|set(range(636,648))


def live_seeds(path):
    x=json.loads(path.read_text(encoding="utf-8")); out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int): out.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v,list):
            for c in v: walk(c)
    walk(x); return list(dict.fromkeys(out))


def obs(steps,t): return steps[t][0].get("observation") or {}
def act(steps,t): return (steps[t+1][0].get("action") or {}) if t+1<len(steps) else {}
def farm(o):
    fs=o.get("farms") or []; return fs[0] if fs else {}

def actor_ops(o,a):
    f=farm(o); a=a or {}; out=[]
    if isinstance(f.get("farmer"),list): out.append((0,tuple(f["farmer"]),a.get("farmer") or ["PASS"]))
    hs=list(a.get("hands") or [])
    for i,p in enumerate(f.get("hands") or [],start=1): out.append((i,tuple(p),hs[i-1] if i-1<len(hs) else ["PASS"]))
    return out

def tile(f,p):
    try: return f["tiles"][int(p[1])][int(p[0])]
    except Exception: return None

def price(o,item):
    try:
        v=float((((o.get("market") or {}).get("prices") or {}).get(item)))
        return v if math.isfinite(v) and v>0 else None
    except Exception: return None

def harvest_info(steps,t,p):
    for h in range(t+1,min(719,len(steps)-1)):
        o=obs(steps,h)
        for _,hp,op in actor_ops(o,act(steps,h)):
            if hp!=p or not (isinstance(op,list) and op and op[0]=="HARVEST"): continue
            tt=tile(farm(o),p)
            if isinstance(tt,dict) and tt.get("kind")=="PLANT" and tt.get("crop")=="WHEAT":
                try: q=max(0,int(tt.get("yield_units",0) or 0))
                except Exception: q=0
                return h,q
    return None,None

def analyze(rep,seed,source):
    steps=rep.get("steps") or []; rows=[]
    for t in sorted(SAFE_STEPS):
        if t<1 or t+1>=len(steps): continue
        o=obs(steps,t)
        for actor,p,op in actor_ops(o,act(steps,t)):
            if not (isinstance(op,list) and len(op)>1 and op[:2]==["PLANT","WHEAT"]): continue
            h,q=harvest_info(steps,t,p)
            if h is None or not q: continue
            pre=obs(steps,t-1); ho=obs(steps,h)
            ppw,ppc=price(pre,"WHEAT"),price(pre,"CARROT"); hpw,hpc=price(ho,"WHEAT"),price(ho,"CARROT")
            tpw,tpc=price(o,"WHEAT"),price(o,"CARROT")
            if None in (ppw,ppc,hpw,hpc,tpw,tpc): continue
            prior=q*(ppc-ppw)-20.0; plant=q*(tpc-tpw)-20.0; oracle=q*(hpc-hpw)-20.0
            rows.append({"seed":int(seed),"source":source,"plant_step":t,"actor":actor,"position":list(p),"route_yield":q,"harvest_step":h,
                         "prior_price_wheat":ppw,"prior_price_carrot":ppc,"plant_price_wheat":tpw,"plant_price_carrot":tpc,
                         "harvest_price_wheat":hpw,"harvest_price_carrot":hpc,"prior_jit_margin":prior,"plant_jit_margin":plant,"oracle_jit_margin":oracle,
                         "prior_positive":prior>0,"plant_positive":plant>0,"oracle_positive":oracle>0})
    return {"seed":int(seed),"source":source,"rows":rows}

def summary(eps,source):
    ee=eps if source=="all" else [e for e in eps if e["source"]==source]; rows=[r for e in ee for r in e["rows"]]; pos=[r for r in rows if r["prior_positive"]]
    return {"episodes":len(ee),"events":len(rows),"episodes_with_prior_positive":sum(any(r["prior_positive"] for r in e["rows"]) for e in ee),
            "prior_positive_events":len(pos),"prior_positive_oracle_precision":sum(r["oracle_positive"] for r in pos)/len(pos) if pos else None,
            "prior_positive_plant_precision":sum(r["plant_positive"] for r in pos)/len(pos) if pos else None,
            "prior_positive_mean_oracle_margin":statistics.mean(r["oracle_jit_margin"] for r in pos) if pos else None,
            "prior_positive_median_oracle_margin":statistics.median(r["oracle_jit_margin"] for r in pos) if pos else None,
            "route_yield_counts":dict(Counter(r["route_yield"] for r in rows))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    eps=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        a=resolve_agent("file:candidates/r4b_ablation_market_only.py:agent"); env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True); env.run([a,"starter"])
        eps.append(analyze(env.toJSON(),int(seed),source))
    sm={s:summary(eps,s) for s in ("development","live_meta","all")}; d,l=sm["development"],sm["live_meta"]
    gate={"eligible_for_jit_candidate":bool(d["episodes_with_prior_positive"]>=4 and l["episodes_with_prior_positive"]>=5 and d["prior_positive_events"]>=10 and l["prior_positive_events"]>=10 and (d["prior_positive_oracle_precision"] or 0)>=0.70 and (l["prior_positive_oracle_precision"] or 0)>=0.70 and (d["prior_positive_mean_oracle_margin"] or 0)>0 and (l["prior_positive_mean_oracle_margin"] or 0)>0),
          "deployable_rule":"one step before safe WHEAT slot, q*(CARROT_price-WHEAT_price)-20 > 0","criteria":"support both pools; >=70% later oracle-positive; positive mean oracle margin"}
    payload={"schema_version":"jit-carrot-value-signal-v1","safe_steps":sorted(SAFE_STEPS),"summary":sm,"gate":gate,"episodes":eps}
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"summary":sm,"gate":gate},indent=2,sort_keys=True))
if __name__=="__main__": main()
