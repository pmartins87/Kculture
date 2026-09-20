#!/usr/bin/env python3
"""O-LQ3: conservative product-priority refinement after LQ2.

Within each consecutive SELL run, only SELL orders for MILK/WOOL/FERTILIZER
are re-ordered. Their occupied slots are preserved; non-target orders and all
quantities remain unchanged.
"""
from __future__ import annotations
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action

PRIORITY={"MILK":0,"WOOL":1,"FERTILIZER":2}

def is_sell(order):
    return isinstance(order,list) and len(order)>=3 and str(order[0])=="SELL"

def lq3_action(base_action):
    b=canonical_action(base_action)
    market=copy.deepcopy(b["market"])
    changed=False
    moves=[]
    i=0
    while i<len(market):
        if not is_sell(market[i]):
            i+=1;continue
        j=i
        while j<len(market) and is_sell(market[j]):
            j+=1
        slots=[k for k in range(i,j) if str(market[k][1]) in PRIORITY]
        before=[copy.deepcopy(market[k]) for k in slots]
        after=sorted(before,key=lambda o:PRIORITY[str(o[1])])
        if before!=after:
            for k,o in zip(slots,after):
                market[k]=copy.deepcopy(o)
            changed=True
            moves.append({
              "run_start":i,"run_end":j-1,"slots":slots,
              "before":[str(o[1]) for o in before],
              "after":[str(o[1]) for o in after],
            })
        i=j
    out=canonical_action({
      "farmer":copy.deepcopy(b["farmer"]),
      "hands":copy.deepcopy(b["hands"]),
      "market":market,
    })
    if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
        raise RuntimeError("O-LQ3 changed physical action")
    # Market multiset must be unchanged.
    def ms(x):
        import json
        return sorted(json.dumps(o,sort_keys=True) for o in x)
    if ms(out["market"])!=ms(b["market"]):
        raise RuntimeError("O-LQ3 changed market multiset")
    return out,{"fired":changed,"moves":moves}

