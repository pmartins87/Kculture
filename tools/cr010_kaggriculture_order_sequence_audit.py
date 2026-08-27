"""CR-010: Kaggriculture shared-inventory order-sequence diagnostic.

This analyzes only the Kaggriculture game simulator. Using frozen CR-007 signals
and strict Aug-26 game replays, it measures the in-game revenue difference
between placing a CARROT/STRAWBERRY SELL in sequence position 0 and placing it
after the other player's first same-product SELL. Same-position transactions
follow the official per-unit lockstep rule.

Diagnostic only; no model thresholds are changed and no agent is promoted here.
"""
from __future__ import annotations

import argparse, json, statistics, sys, tempfile
from pathlib import Path
from kaggle_environments.envs.kaggriculture.kaggriculture import market_price

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.cr004_adaptation_signal import download, public_features, read_csv
from tools.cr005_short_horizon_sell_forecast import END,HORIZON,START,collect_date,p1,split_features
from tools.cr007_high_confidence_frontrun import FINAL_TRAIN_DATES,TEST_DATE,fit_models

THRESHOLDS={"CARROT":0.90,"STRAWBERRY":0.85}

def num(d,k,default=0):
    try:return int((d or {}).get(k,default) or default)
    except Exception:return int(default)

def same_turn_orders(steps,opponent,state,item):
    if state+1>=len(steps):return []
    frame=steps[state+1][opponent]
    action=frame.get("action") if isinstance(frame,dict) else None
    if not isinstance(action,dict):return []
    out=[]
    for slot,order in enumerate(action.get("market",[]) or []):
        if not(isinstance(order,list) and len(order)>=3 and order[0]=="SELL" and order[1]==item):continue
        try:q=max(0,int(order[2] or 0))
        except Exception:q=0
        if q:out.append({"slot":slot,"qty":q})
    return out

def sell_alone(item,inventory,qty):
    inv=int(inventory);revenue=0
    for _ in range(max(0,int(qty))):
        price=int(market_price(item,inv));revenue+=price
        if price>1:inv+=1
    return revenue,inv

def sell_lockstep(item,inventory,own_qty,other_qty):
    inv=int(inventory);own=max(0,int(own_qty));other=max(0,int(other_qty));revenue=0
    while own>0 or other>0:
        price=int(market_price(item,inv));commits=0
        if own>0:revenue+=price;own-=1;commits+=1
        if other>0:other-=1;commits+=1
        if price>1:inv+=commits
    return revenue,inv

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--top",type=int,default=20);ap.add_argument("--output",required=True);args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="kculture-cr010-") as tmp:
        root=Path(tmp);train=[]
        for date in FINAL_TRAIN_DATES:train.extend(collect_date(date,args.top,root/"train"))
        _,names=split_features(train);models=fit_models(train,names)
        handle=f"kaggle/kaggriculture-episodes-{TEST_DATE}"
        manifest=sorted(read_csv(download(handle,"manifest.csv",root/"test"/"manifest")),key=lambda r:-float(r.get("avg_score") or 0))[:args.top]
        rows=[];episodes=0
        for mr in manifest:
            eid=str(mr["episode_id"]);path=download(handle,f"{eid}.json",root/"test"/"episodes"/eid);rep=json.loads(path.read_text(encoding="utf-8"));steps=rep.get("steps") or []
            if len(steps)<720:continue
            episodes+=1
            for player in (0,1):
                other=1-player
                for t in range(START,END+1):
                    if t-24<0 or t+HORIZON>=len(steps):continue
                    obs=steps[t][player].get("observation") or {};prev=steps[t-24][player].get("observation") or {};feat=public_features(obs,prev,player)
                    if not feat:continue
                    xrow=[[float(feat.get(n,0.0)) for n in names]];shed=(obs.get("private") or {}).get("shed") or {};invmap=(obs.get("market") or {}).get("inventory") or {}
                    for item,thr in THRESHOLDS.items():
                        own=max(0,num(shed,item,0))
                        if own<=0:continue
                        prob=p1(models[f"SELL_{item}"],xrow)[0]
                        if prob<thr:continue
                        orders=same_turn_orders(steps,other,t,item)
                        if not orders:continue
                        first=orders[0];inv=num(invmap,item,0);oq=first["qty"]
                        if first["slot"]==0:early,_=sell_lockstep(item,inv,own,oq)
                        else:early,_=sell_alone(item,inv,own)
                        _,inv2=sell_alone(item,inv,oq);late,_=sell_alone(item,inv2,own);gain=float(early-late)
                        rows.append({"episode_id":eid,"player":player,"state":t,"item":item,"prob":prob,"own_qty":own,"inventory":inv,"other_first_sell_slot":first["slot"],"other_first_sell_qty":oq,"other_same_turn_orders":orders,"position0_revenue":early,"after_first_other_order_revenue":late,"position0_gain":gain})
    gains=[r["position0_gain"] for r in rows];slot0=sum(r["other_first_sell_slot"]==0 for r in rows)
    summary={"same_turn_high_confidence_events":len(rows),"other_first_sell_position0":slot0,"other_first_sell_position0_fraction":slot0/len(rows) if rows else None,"mean_position0_gain":statistics.mean(gains) if gains else None,"median_position0_gain":statistics.median(gains) if gains else None,"positive_position0_gain_fraction":sum(x>0 for x in gains)/len(gains) if gains else None,"gain_ge_10_fraction":sum(x>=10 for x in gains)/len(gains) if gains else None,"total_position0_gain":sum(gains)}
    per={}
    for item in THRESHOLDS:
        xs=[r for r in rows if r["item"]==item];gs=[r["position0_gain"] for r in xs]
        per[item]={"events":len(xs),"position0_fraction":sum(r["other_first_sell_slot"]==0 for r in xs)/len(xs) if xs else None,"mean_gain":statistics.mean(gs) if gs else None,"median_gain":statistics.median(gs) if gs else None,"positive_gain_fraction":sum(g>0 for g in gs)/len(gs) if gs else None,"total_gain":sum(gs)}
    gate={"same_turn_support_ge_50":len(rows)>=50,"position0_fraction_ge_0_75":(summary["other_first_sell_position0_fraction"] or 0)>=0.75,"mean_gain_ge_20":(summary["mean_position0_gain"] or 0)>=20,"median_gain_ge_10":(summary["median_position0_gain"] or 0)>=10,"positive_gain_fraction_ge_0_80":(summary["positive_position0_gain_fraction"] or 0)>=0.80}
    passed=all(gate.values());payload={"experiment":"CR-010","schema_version":"kaggriculture-order-sequence-v1","status":"ORDER_SEQUENCE_VALUE_SUPPORTED" if passed else "ORDER_SEQUENCE_VALUE_NOT_SUPPORTED","train_dates":list(FINAL_TRAIN_DATES),"test_date":TEST_DATE,"top_episodes":args.top,"episodes_used":episodes,"thresholds":THRESHOLDS,"summary":summary,"per_product":per,"gate":gate,"rows":rows,"interpretation":"Earlier in-turn order placement has enough game-value signal for a bounded causal agent test." if passed else "Order placement does not explain enough game-value loss for another candidate.","method_limit":"Exact Kaggriculture transaction mechanics conditional on observed same-turn game actions; not a full-game counterfactual."}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps({"status":payload["status"],"summary":summary,"per_product":per,"gate":gate},indent=2,sort_keys=True))
if __name__=="__main__":main()
