#!/usr/bin/env python3
"""O-TM1: P2 cross-source consensus market schedule."""
from __future__ import annotations
import copy,json
from tools.bounded_transaction_oracle_v1 import canonical_action,plain

START=464
END=591

def own_available(obs):
    p=plain(obs)
    private=p.get("private") or {}
    shed=private.get("shed") or {}
    carried={}
    for bag in private.get("inventories") or []:
        if isinstance(bag,dict):
            for k,v in bag.items():
                try:carried[str(k)]=carried.get(str(k),0)+int(v or 0)
                except:pass
    out={}
    for k in set(shed)|set(carried):
        try:out[str(k)]=max(0,int(shed.get(k,0) or 0)+int(carried.get(k,0) or 0))
        except:out[str(k)]=max(0,int(carried.get(k,0) or 0))
    return out

def project_sells(schedule_market,obs):
    m=copy.deepcopy(list(schedule_market or []))
    avail=own_available(obs)
    by_product={}
    for i,o in enumerate(m):
        if isinstance(o,list) and len(o)>=3 and str(o[0])=="SELL":
            p=str(o[1])
            try:q=max(0,int(o[2] or 0))
            except:q=0
            by_product.setdefault(p,[]).append((i,q))
    for product,items in by_product.items():
        cap=max(0,int(avail.get(product,0)))
        remaining=cap
        for i,q in items:
            take=min(q,remaining)
            remaining-=take
            if take<=0:m[i]=[]
            else:m[i]=["SELL",product,take]
    return m

def schedule_action(obs,base_action,turn:int,schedule:dict):
    b=canonical_action(base_action)
    t=int(turn)
    if t<START or t>END:
        return b,{"fired":False,"turn":t,"reason":"outside_scope"}
    entry=schedule.get(str(t))
    if entry is None:
        return b,{"fired":False,"turn":t,"reason":"unscheduled"}
    market=entry.get("market") if isinstance(entry,dict) else entry
    projected=project_sells(market,obs)
    out=canonical_action({
      "farmer":copy.deepcopy(b["farmer"]),
      "hands":copy.deepcopy(b["hands"]),
      "market":projected,
    })
    if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
        raise RuntimeError("O-TM1 changed physical action")
    changed=(out["market"]!=b["market"])
    return out,{
      "fired":changed,"turn":t,"reason":"scheduled","projected_market":out["market"],
      "raw_market":copy.deepcopy(market),
    }
