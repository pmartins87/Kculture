#!/usr/bin/env python3
"""O-LQ4E: early SELL FERTILIZER before HIRE target-slot precedence.

Derived from the binding V14B selected EARLY|REORDER phenotype and its deterministic
pairwise translation.  The operator is first-party, identity-free, and market-multiset
preserving.
"""
from __future__ import annotations
import copy,json
from tools.bounded_transaction_oracle_v1 import canonical_action

MAX_STEP_EXCLUSIVE=336

def is_sell_fertilizer(order):
    return (
        isinstance(order,list) and len(order)>=3
        and str(order[0])=="SELL" and str(order[1])=="FERTILIZER"
    )

def is_hire(order):
    return isinstance(order,list) and len(order)>=1 and str(order[0])=="HIRE"

def lq4e_action(base_action,turn:int,max_step_exclusive:int=MAX_STEP_EXCLUSIVE):
    b=canonical_action(base_action)
    if int(turn)>=int(max_step_exclusive):
        return b,{"fired":False,"turn":int(turn),"reason":"late"}

    market=copy.deepcopy(b["market"])
    slots=[i for i,o in enumerate(market) if is_sell_fertilizer(o) or is_hire(o)]
    if not slots:
        return b,{"fired":False,"turn":int(turn),"reason":"no_targets"}

    fert=[copy.deepcopy(market[i]) for i in slots if is_sell_fertilizer(market[i])]
    hires=[copy.deepcopy(market[i]) for i in slots if is_hire(market[i])]
    if not fert or not hires:
        return b,{"fired":False,"turn":int(turn),"reason":"incomplete_pair"}

    before=[copy.deepcopy(market[i]) for i in slots]
    after=fert+hires
    if before==after:
        return b,{"fired":False,"turn":int(turn),"reason":"already_ordered","slots":slots}

    for i,o in zip(slots,after):
        market[i]=copy.deepcopy(o)

    out=canonical_action({
      "farmer":copy.deepcopy(b["farmer"]),
      "hands":copy.deepcopy(b["hands"]),
      "market":market,
    })
    if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
        raise RuntimeError("O-LQ4E changed physical action")

    def ms(x):
        return sorted(json.dumps(o,sort_keys=True,separators=(",",":")) for o in x)
    if ms(out["market"])!=ms(b["market"]):
        raise RuntimeError("O-LQ4E changed market multiset")

    # Hard precedence invariant among target slots.
    seen_hire=False
    for i in slots:
        o=out["market"][i]
        if is_hire(o):
            seen_hire=True
        elif is_sell_fertilizer(o) and seen_hire:
            raise RuntimeError("O-LQ4E precedence invariant failed")

    return out,{
      "fired":True,
      "turn":int(turn),
      "slots":slots,
      "before":before,
      "after":[copy.deepcopy(out["market"][i]) for i in slots],
      "fertilizer_orders":len(fert),
      "hire_orders":len(hires),
    }
