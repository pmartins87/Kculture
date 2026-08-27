"""Mechanical execution audit for KEXP-041.

Runs candidate and frozen R4B separately on development + exploratory live-meta
seeds against starter and compares corrected state->action frames at 614/615.
Diagnostic only; no validation/held-out access.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path
from collections import Counter
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent

BUY_STEP=614
PLANT_STEP=615


def live_seeds(path):
    x=json.loads(path.read_text(encoding="utf-8")); out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int): out.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v,list):
            for c in v: walk(c)
    walk(x); return list(dict.fromkeys(out))


def paired_action(rep,t):
    steps=rep.get("steps") or []
    return (steps[t+1][0].get("action") or {}) if t+1<len(steps) else {}


def count_market(action,op,item):
    q=0
    for o in list((action or {}).get("market") or []):
        if isinstance(o,list) and len(o)>=3 and o[:2]==[op,item]:
            try:q+=max(0,int(o[2] or 0))
            except Exception:pass
    return q


def count_plant(action,item):
    n=0
    ops=[(action or {}).get("farmer")]+list((action or {}).get("hands") or [])
    for o in ops:
        if isinstance(o,list) and len(o)>=2 and o[:2]==["PLANT",item]: n+=1
    return n


def run(agent_ref,seed):
    a=resolve_agent(agent_ref)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True)
    env.run([a,"starter"])
    rep=env.toJSON()
    final=rep["steps"][-1][0]
    return rep, final.get("status"), final.get("reward")


def pattern_counts(rr):
    c=Counter((r["added_carrot_buy_intent_614"],r["extra_carrot_stock_615"],r["delta_carrot_plants_615"],r["delta_wheat_plants_615"]) for r in rr)
    return {"|".join(map(str,k)):v for k,v in sorted(c.items())}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        cr,cs,creward=run("file:candidates/r4d_jit_carrot_one.py:agent",seed)
        br,bs,breward=run("file:candidates/r4b_ablation_market_only.py:agent",seed)
        ca614,ba614=paired_action(cr,BUY_STEP),paired_action(br,BUY_STEP)
        ca615,ba615=paired_action(cr,PLANT_STEP),paired_action(br,PLANT_STEP)
        added_buy=count_market(ca614,"BUY_SEED","CARROT")-count_market(ba614,"BUY_SEED","CARROT")
        delta_carrot=count_plant(ca615,"CARROT")-count_plant(ba615,"CARROT")
        delta_wheat=count_plant(ca615,"WHEAT")-count_plant(ba615,"WHEAT")
        try:
            cseed=int(cr["steps"][PLANT_STEP][0]["observation"]["private"]["seeds"].get("CARROT",0) or 0)
            bseed=int(br["steps"][PLANT_STEP][0]["observation"]["private"]["seeds"].get("CARROT",0) or 0)
        except Exception:
            cseed=bseed=0
        rows.append({"seed":int(seed),"source":source,"candidate_status":cs,"base_status":bs,
                     "added_carrot_buy_intent_614":added_buy,"extra_carrot_stock_615":cseed-bseed,
                     "delta_carrot_plants_615":delta_carrot,"delta_wheat_plants_615":delta_wheat,
                     "terminal_reward_delta_vs_separate_base":(float(creward)-float(breward)) if isinstance(creward,(int,float)) and isinstance(breward,(int,float)) else None})
    sm={}
    for source in ("development","live_meta","all"):
        rr=rows if source=="all" else [r for r in rows if r["source"]==source]
        sm[source]={"episodes":len(rr),"added_buy_episodes":sum(r["added_carrot_buy_intent_614"]>0 for r in rr),
                    "purchase_committed_episodes":sum(r["extra_carrot_stock_615"]>0 for r in rr),
                    "converted_episodes":sum(r["delta_carrot_plants_615"]>0 and r["delta_wheat_plants_615"]<0 for r in rr),
                    "status_errors":sum(r["candidate_status"]!="DONE" for r in rr),
                    "pattern_counts":pattern_counts(rr)}
    gate={"execution_matches_design":bool(sm["development"]["status_errors"]==0 and sm["live_meta"]["status_errors"]==0 and sm["development"]["converted_episodes"]==sm["development"]["purchase_committed_episodes"] and sm["live_meta"]["converted_episodes"]==sm["live_meta"]["purchase_committed_episodes"] and sm["development"]["converted_episodes"]>=4 and sm["live_meta"]["converted_episodes"]>=5)}
    payload={"schema_version":"kexp041-execution-audit-v1","summary":sm,"gate":gate,"rows":rows}
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"summary":sm,"gate":gate},indent=2,sort_keys=True))
if __name__=="__main__": main()
