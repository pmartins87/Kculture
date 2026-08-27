"""Mechanical audit for KEXP-050 same-slot WHEAT->CARROT reallocation.

Compare KEXP-050 and frozen R4B separately against starter on development and
exploratory live-meta environmental seeds. Verify exact state-614 market delta
(+1 CARROT seed, -1 WHEAT seed), state-615 seed arrival, and exact +1 CARROT /
-1 WHEAT plant conversion. Diagnostic only; no validation/held-out access.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

CAND = "file:candidates/r4d_reallocate_614_carrot.py:agent"
BASE = "file:candidates/r4b_ablation_market_only.py:agent"
BUY_STEP, PLANT_STEP = 614, 615


def live_seeds(path):
    obj = json.loads(path.read_text(encoding="utf-8")); out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get("seed"),int): out.append(v["seed"])
            for x in v.values(): walk(x)
        elif isinstance(v,list):
            for x in v: walk(x)
    walk(obj); return list(dict.fromkeys(out))


def run(agent_ref, seed):
    a=resolve_agent(agent_ref)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=True)
    env.run([a,"starter"]); return env.toJSON()


def action(rep,t):
    return (rep["steps"][t+1][0].get("action") or {}) if t+1<len(rep["steps"]) else {}


def mq(a,op,item):
    q=0
    for r in list((a or {}).get("market") or []):
        if isinstance(r,list) and len(r)>=3 and r[:2]==[op,item]:
            try:q+=max(0,int(r[2] or 0))
            except Exception:pass
    return q


def pc(a,crop):
    ops=[(a or {}).get("farmer"),*list((a or {}).get("hands") or [])]
    return sum(isinstance(o,list) and len(o)>=2 and o[:2]==["PLANT",crop] for o in ops)


def status(rep): return rep["steps"][-1][0].get("status")


def seed_stock(rep,t,item):
    try:return int(rep["steps"][t][0]["observation"]["private"]["seeds"].get(item,0) or 0)
    except Exception:return 0


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    dev=json.loads((ROOT/"configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live=live_seeds(ROOT/"configs/exploratory_live_meta_seeds_20260825.json")
    rows=[]
    for seed,source in [(s,"development") for s in dev]+[(s,"live_meta") for s in live]:
        cr,br=run(CAND,seed),run(BASE,seed)
        ca,ba=action(cr,BUY_STEP),action(br,BUY_STEP); cp,bp=action(cr,PLANT_STEP),action(br,PLANT_STEP)
        row={
            "seed":int(seed),"source":source,"candidate_status":status(cr),"base_status":status(br),
            "delta_carrot_buy":mq(ca,"BUY_SEED","CARROT")-mq(ba,"BUY_SEED","CARROT"),
            "delta_wheat_buy":mq(ca,"BUY_SEED","WHEAT")-mq(ba,"BUY_SEED","WHEAT"),
            "extra_carrot_stock_615":seed_stock(cr,PLANT_STEP,"CARROT")-seed_stock(br,PLANT_STEP,"CARROT"),
            "delta_wheat_stock_615":seed_stock(cr,PLANT_STEP,"WHEAT")-seed_stock(br,PLANT_STEP,"WHEAT"),
            "delta_carrot_plants_615":pc(cp,"CARROT")-pc(bp,"CARROT"),
            "delta_wheat_plants_615":pc(cp,"WHEAT")-pc(bp,"WHEAT"),
        }
        row["reallocated"] = row["delta_carrot_buy"]==1 and row["delta_wheat_buy"]==-1
        row["converted"] = row["delta_carrot_plants_615"]==1 and row["delta_wheat_plants_615"]==-1
        rows.append(row)
    summary={}
    for source in ("development","live_meta","all"):
        rr=rows if source=="all" else [r for r in rows if r["source"]==source]
        summary[source]={
            "episodes":len(rr),
            "status_errors":sum(r["candidate_status"]!="DONE" or r["base_status"]!="DONE" for r in rr),
            "reallocated_episodes":sum(r["reallocated"] for r in rr),
            "purchase_arrived_episodes":sum(r["extra_carrot_stock_615"]>0 for r in rr),
            "converted_episodes":sum(r["converted"] for r in rr),
            "failed_after_reallocation":sum(r["reallocated"] and not r["converted"] for r in rr),
        }
    gate={"execution_matches_design":bool(
        summary["development"]["status_errors"]==0 and summary["live_meta"]["status_errors"]==0
        and summary["development"]["reallocated_episodes"]==summary["development"]["converted_episodes"]
        and summary["live_meta"]["reallocated_episodes"]==summary["live_meta"]["converted_episodes"]
        and summary["development"]["converted_episodes"]>=4
        and summary["live_meta"]["converted_episodes"]>=5
    )}
    payload={"schema_version":"kexp050-execution-v1","summary":summary,"gate":gate,"rows":rows}
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"summary":summary,"gate":gate},indent=2,sort_keys=True))

if __name__=="__main__": main()
