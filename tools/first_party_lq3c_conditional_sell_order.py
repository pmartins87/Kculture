#!/usr/bin/env python3
"""O-LQ3C: frozen conditional SELL-priority option derived from V8C.

Eligibility is a structural post-LQ2 market signature:
exactly 4 SELL + 6 HIRE, no BUY/other operations, with MILK/WOOL/FERTILIZER
all represented and the unchanged O-LQ3 transform actually changing the action.
"""
from __future__ import annotations
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action
from tools.first_party_lq3_priority_sell_order import lq3_action

TARGETS={"MILK","WOOL","FERTILIZER"}

def classify_order(order):
    if not isinstance(order,list) or not order:
        return "EMPTY"
    op=str(order[0])
    if op=="SELL": return "SELL"
    if op=="HIRE": return "HIRE"
    if op.startswith("BUY"): return "BUY"
    return "OTHER"

def lq3c_action(all3_action):
    base=canonical_action(all3_action)
    kinds=[classify_order(x) for x in base["market"]]
    sell_count=sum(x=="SELL" for x in kinds)
    hire_count=sum(x=="HIRE" for x in kinds)
    buy_count=sum(x=="BUY" for x in kinds)
    other_count=sum(x=="OTHER" for x in kinds)
    products={
        str(x[1]) for x in base["market"]
        if isinstance(x,list) and len(x)>=3 and str(x[0])=="SELL"
    }
    structural=(
        sell_count==4 and hire_count==6 and buy_count==0 and other_count==0
        and TARGETS.issubset(products)
    )
    if not structural:
        return base,{
            "fired":False,"reason":"shape_ineligible",
            "sell_count":sell_count,"hire_count":hire_count,
            "buy_count":buy_count,"other_count":other_count,
            "target_products":sorted(TARGETS & products),
        }
    out,meta=lq3_action(base)
    if not meta.get("fired"):
        return base,{
            "fired":False,"reason":"lq3_no_change",
            "sell_count":sell_count,"hire_count":hire_count,
            "buy_count":buy_count,"other_count":other_count,
            "target_products":sorted(TARGETS & products),
        }
    if out["farmer"]!=base["farmer"] or out["hands"]!=base["hands"]:
        raise RuntimeError("O-LQ3C changed physical action")
    return out,{
        "fired":True,"reason":"eligible",
        "sell_count":sell_count,"hire_count":hire_count,
        "buy_count":buy_count,"other_count":other_count,
        "target_products":sorted(TARGETS & products),
        "moves":copy.deepcopy(meta.get("moves",[])),
    }
