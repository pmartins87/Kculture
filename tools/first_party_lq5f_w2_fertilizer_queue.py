#!/usr/bin/env python3
"""O-LQ5F: one-shot W2 FERTILIZER SELL quantity +2."""
from __future__ import annotations
from dataclasses import dataclass
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action

W2_START=336
W2_END_EXCLUSIVE=504

@dataclass
class LQ5FState:
    used: bool=False

def is_sell_fertilizer(order):
    return (
      isinstance(order,list) and len(order)>=3
      and str(order[0])=="SELL" and str(order[1])=="FERTILIZER"
    )

def lq5f_action(base_action,turn:int,state:LQ5FState):
    b=canonical_action(base_action)
    t=int(turn)
    if state.used:
        return b,{"fired":False,"turn":t,"reason":"used"}
    if t<W2_START or t>=W2_END_EXCLUSIVE:
        return b,{"fired":False,"turn":t,"reason":"outside_w2"}

    market=copy.deepcopy(b["market"])
    idx=None
    for i,o in enumerate(market):
        if is_sell_fertilizer(o):
            idx=i;break
    if idx is None:
        return b,{"fired":False,"turn":t,"reason":"no_sell_fertilizer"}

    try:
        before_qty=int(market[idx][2])
    except Exception as exc:
        raise RuntimeError(f"O-LQ5F invalid FERTILIZER quantity: {market[idx]}") from exc
    after_qty=before_qty+2
    market[idx][2]=after_qty
    out=canonical_action({
      "farmer":copy.deepcopy(b["farmer"]),
      "hands":copy.deepcopy(b["hands"]),
      "market":market,
    })
    if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
        raise RuntimeError("O-LQ5F changed physical action")
    if len(out["market"])!=len(b["market"]):
        raise RuntimeError("O-LQ5F changed market cardinality")
    for j,(x,y) in enumerate(zip(b["market"],out["market"])):
        if j==idx:
            xx=copy.deepcopy(x);yy=copy.deepcopy(y)
            if len(xx)<3 or len(yy)<3:raise RuntimeError("O-LQ5F target malformed")
            xx[2]=yy[2]
            if xx!=yy:raise RuntimeError("O-LQ5F changed target fields beyond quantity")
            if int(yy[2])-int(x[2])!=2:raise RuntimeError("O-LQ5F quantity delta is not +2")
        elif x!=y:
            raise RuntimeError("O-LQ5F changed non-target market order")
    state.used=True
    return out,{
      "fired":True,"turn":t,"index":idx,
      "before_qty":before_qty,"after_qty":after_qty,"delta":2,
    }
