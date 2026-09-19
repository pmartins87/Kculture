#!/usr/bin/env python3
"""First-party O-LQ2 Late Canonical SELL Queue operator."""
from __future__ import annotations
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action, plain
from tools.cq2_projected_queue_dev_matrix import (
    projected_shed_after_physical,
    apply_non_sell_inventory_effect,
    as_int,
    getv,
)

MIN_STEP=336

def is_sell(order):
    return isinstance(order,list) and len(order)>=3 and str(order[0])=="SELL"

def canonicalize_sell_run(run,shed):
    first_order=[]
    totals={}
    templates={}
    for raw in run:
        order=copy.deepcopy(list(raw))
        product=str(order[1])
        qty=max(0,as_int(order[2],0))
        if product not in totals:
            first_order.append(product)
            totals[product]=0
            templates[product]=order
        totals[product]+=qty

    emitted=[]
    for product in first_order:
        avail=max(0,as_int(shed.get(product,0),0))
        take=min(max(0,totals[product]),avail)
        shed[product]=max(0,avail-take)
        if take<=0:
            continue
        order=copy.deepcopy(templates[product])
        order[2]=take
        emitted.append(order)

    return emitted + [[] for _ in range(max(0,len(run)-len(emitted)))]

def lq2_action(obs,config,base_action,min_step=MIN_STEP):
    b=canonical_action(base_action)
    step=as_int(getv(plain(obs),"step",0),0)
    if step<min_step:
        return b

    shed=projected_shed_after_physical(obs,config,b)
    capacity=max(0,as_int(getv(config or {},"shedCapacity",100),100))
    market=copy.deepcopy(b["market"])
    out=[]
    i=0
    while i<len(market):
        order=market[i]
        if is_sell(order):
            j=i
            run=[]
            while j<len(market) and is_sell(market[j]):
                run.append(market[j])
                j+=1
            out.extend(canonicalize_sell_run(run,shed))
            i=j
            continue
        out.append(copy.deepcopy(order))
        apply_non_sell_inventory_effect(order,shed,capacity)
        i+=1

    result=canonical_action({
        "farmer":copy.deepcopy(b["farmer"]),
        "hands":copy.deepcopy(b["hands"]),
        "market":out,
    })
    if result["farmer"]!=b["farmer"] or result["hands"]!=b["hands"]:
        raise RuntimeError("O-LQ2 changed physical action")
    return result
