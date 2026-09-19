#!/usr/bin/env python3
"""O-PC1: first-party profit-dominant WHEAT->CARROT crop rotation on top of ALL3."""
from __future__ import annotations
import copy

from tools.bounded_transaction_oracle_v1 import canonical_action,plain
from tools.cq2_projected_queue_dev_matrix import as_int,getv

WHEAT_SEED_COST=10
WHEAT_MAX_YIELD=6
WHEAT_MAX_YIELD_DAY=4
CARROT_SEED_COST=20
CARROT_MAX_YIELD=4
CARROT_MAX_YIELD_DAY=3

def _plant_count(action,crop):
    a=canonical_action(action)
    total=0
    for u in [a["farmer"],*a["hands"]]:
        if isinstance(u,list) and len(u)>=2 and str(u[0])=="PLANT" and str(u[1])==crop:
            total+=1
    return total

def _replace_wheat_plants(action,carrot_surplus):
    a=canonical_action(action)
    left=max(0,int(carrot_surplus))

    def rewrite(u):
        nonlocal left
        x=copy.deepcopy(u)
        if left>0 and isinstance(x,list) and len(x)>=2 and str(x[0])=="PLANT" and str(x[1])=="WHEAT":
            x[1]="CARROT"
            left-=1
        return x

    return canonical_action({
        "farmer":rewrite(a["farmer"]),
        "hands":[rewrite(x) for x in a["hands"]],
        "market":copy.deepcopy(a["market"]),
    })

def _rewrite_seed_orders(action,max_orders):
    a=canonical_action(action)
    original=copy.deepcopy(a["market"])
    extra_needed=sum(
        1 for o in original
        if isinstance(o,list) and len(o)>=3 and str(o[0])=="BUY_SEED"
        and str(o[1])=="WHEAT" and max(0,as_int(o[2],0))>=2
    )
    capacity=max(0,int(max_orders)-len(original))
    split_budget=min(extra_needed,capacity)

    out=[]
    for o in original:
        if not (isinstance(o,list) and len(o)>=3 and str(o[0])=="BUY_SEED" and str(o[1])=="WHEAT"):
            out.append(copy.deepcopy(o))
            continue
        n=max(0,as_int(o[2],0))
        if n<=0:
            out.append(copy.deepcopy(o))
        elif n==1:
            out.append(["BUY_SEED","CARROT",1])
        elif split_budget>0:
            out.append(["BUY_SEED","WHEAT",n-1])
            out.append(["BUY_SEED","CARROT",1])
            split_budget-=1
        else:
            # Preserve the exact ALL3 order when a split would exceed the market-order cap.
            out.append(copy.deepcopy(o))
    return canonical_action({
        "farmer":copy.deepcopy(a["farmer"]),
        "hands":copy.deepcopy(a["hands"]),
        "market":out,
    })

def pc1_transform(obs,config,all3_action):
    base=canonical_action(all3_action)
    p=plain(obs)
    step=as_int(getv(p,"step",0),0)
    tpd=max(1,as_int(getv(config or {},"turnsPerDay",24),24))
    episode_steps=max(1,as_int(getv(config or {},"episodeSteps",720),720))
    day=as_int(getv(p,"day",step//tpd),step//tpd)
    final_day=(episode_steps-1)//tpd

    prices=getv(getv(p,"market",{}) or {},"prices",{}) or {}
    pw=max(0,as_int(getv(prices,"WHEAT",0),0))
    pc=max(0,as_int(getv(prices,"CARROT",0),0))
    wheat_value=WHEAT_MAX_YIELD*pw-WHEAT_SEED_COST
    carrot_value=CARROT_MAX_YIELD*pc-CARROT_SEED_COST

    meta={
        "fired":False,"step":step,"day":day,
        "wheat_price":pw,"carrot_price":pc,
        "wheat_value":wheat_value,"carrot_value":carrot_value,
        "plant_replacements":0,"seed_units_redirected":0,
    }

    if carrot_value<=wheat_value:
        return base,meta
    if day+CARROT_MAX_YIELD_DAY>final_day:
        return base,meta

    private=getv(p,"private",{}) or {}
    seeds=getv(private,"seeds",{}) or {}
    current_carrot=max(0,as_int(getv(seeds,"CARROT",0),0))
    reserved_carrot=_plant_count(base,"CARROT")
    carrot_surplus=max(0,current_carrot-reserved_carrot)

    physical=_replace_wheat_plants(base,carrot_surplus)
    before_wheat=_plant_count(base,"WHEAT")
    after_wheat=_plant_count(physical,"WHEAT")
    plant_replacements=max(0,before_wheat-after_wheat)

    max_orders=max(0,as_int(getv(config or {},"maxMarketOrdersPerTurn",10),10))
    out=_rewrite_seed_orders(physical,max_orders)

    seed_units_redirected=0
    for old,new in zip(base["market"],out["market"][:len(base["market"])]):
        if (
            isinstance(old,list) and len(old)>=3 and str(old[0])=="BUY_SEED"
            and str(old[1])=="WHEAT"
        ):
            # Exact count is easier to compute from aggregate market quantities below.
            pass
    old_w=sum(
        max(0,as_int(o[2],0)) for o in base["market"]
        if isinstance(o,list) and len(o)>=3 and str(o[0])=="BUY_SEED" and str(o[1])=="WHEAT"
    )
    new_w=sum(
        max(0,as_int(o[2],0)) for o in out["market"]
        if isinstance(o,list) and len(o)>=3 and str(o[0])=="BUY_SEED" and str(o[1])=="WHEAT"
    )
    seed_units_redirected=max(0,old_w-new_w)

    if out["farmer"]!=physical["farmer"] or out["hands"]!=physical["hands"]:
        raise RuntimeError("O-PC1 market rewrite changed physical actions")
    if len(out["market"])>max_orders:
        raise RuntimeError("O-PC1 exceeded max market orders")

    fired=(out!=base)
    meta.update({
        "fired":fired,
        "plant_replacements":plant_replacements,
        "seed_units_redirected":seed_units_redirected,
        "current_carrot_seeds":current_carrot,
        "reserved_carrot_plants":reserved_carrot,
    })
    return out,meta

def pc1_action(obs,config,all3_action):
    return pc1_transform(obs,config,all3_action)[0]
