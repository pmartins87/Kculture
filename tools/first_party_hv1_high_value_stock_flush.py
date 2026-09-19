#!/usr/bin/env python3
"""O-HV1: add one missed high-value finished-good SELL to an ALL3 action."""
from __future__ import annotations
import copy

from tools.bounded_transaction_oracle_v1 import canonical_action,plain
from tools.cq2_projected_queue_dev_matrix import (
    projected_shed_after_physical,as_int,getv,
)

PRODUCTS=("MILK","WOOL","EGG","CARROT","STRAWBERRY","MELON","TOMATO")

def is_sell(order):
    return isinstance(order,list) and len(order)>=3 and str(order[0])=="SELL"

def hv1_transform(obs,config,all3_action,*,min_step:int,min_price:int):
    a=canonical_action(all3_action)
    step=as_int(getv(plain(obs),"step",0),0)
    meta={
        "fired":False,"step":step,"product":None,"quantity":0,"price":None,
        "gross_value":0,
    }
    if step<min_step:
        return a,meta

    p=plain(obs)
    market_obs=getv(p,"market",{}) or {}
    prices=getv(market_obs,"prices",{}) or {}

    # Only pre-existing/current-turn physically deposited stock is eligible.
    # Existing ALL3 SELLs reserve inventory first. HV1 never relies on same-turn BUYs.
    shed=projected_shed_after_physical(obs,config,a)
    remaining={str(k):max(0,as_int(v,0)) for k,v in shed.items()}
    for order in list(a["market"] or []):
        if not is_sell(order):
            continue
        product=str(order[1])
        qty=max(0,as_int(order[2],0))
        take=min(qty,max(0,remaining.get(product,0)))
        remaining[product]=max(0,remaining.get(product,0)-take)

    candidates=[]
    for product in PRODUCTS:
        qty=max(0,remaining.get(product,0))
        price=max(0,as_int(getv(prices,product,0),0))
        if qty<=0 or price<min_price:
            continue
        candidates.append((price*qty,price,qty,product))
    if not candidates:
        return a,meta

    gross,price,qty,product=max(candidates)
    extra=["SELL",product,qty]

    # Insert after the current leading SELL run so realized cash precedes later BUY/HIRE slots.
    market=copy.deepcopy(a["market"])
    idx=0
    while idx<len(market) and is_sell(market[idx]):
        idx+=1
    market.insert(idx,extra)

    out=canonical_action({
        "farmer":copy.deepcopy(a["farmer"]),
        "hands":copy.deepcopy(a["hands"]),
        "market":market,
    })
    if out["farmer"]!=a["farmer"] or out["hands"]!=a["hands"]:
        raise RuntimeError("O-HV1 changed physical action")

    meta.update({
        "fired":True,"product":product,"quantity":qty,
        "price":price,"gross_value":gross,
    })
    return out,meta

def hv1_action(obs,config,all3_action,*,min_step:int=240,min_price:int=175):
    return hv1_transform(
        obs,config,all3_action,min_step=min_step,min_price=min_price
    )[0]
