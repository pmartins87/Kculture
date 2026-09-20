#!/usr/bin/env python3
"""O-LQ6S: W2 STRAWBERRY first-free SELL2 under a frozen V17A3 trigger."""
from __future__ import annotations
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action,plain

W2_START=336
W2_END_EXCLUSIVE=504
ALLOWED_TRIGGERS={"T0_AVAILABLE","T1_CARRIED20","T2_SHED2","T3_CARRIED20_OR_SHED2"}

def own_strawberry(obs):
    p=plain(obs)
    private=p.get("private") or {}
    shed=private.get("shed") or {}
    try:shed_q=int(shed.get("STRAWBERRY",0) or 0)
    except:shed_q=0
    carried=0
    for bag in private.get("inventories") or []:
        if isinstance(bag,dict):
            try:carried+=int(bag.get("STRAWBERRY",0) or 0)
            except:pass
    return shed_q,carried

def market_has_nonempty(action):
    return any(bool(list(x or [])) for x in (action.get("market") or []))

def trigger_eligible(obs,base_action,turn:int,trigger_name:str):
    if trigger_name not in ALLOWED_TRIGGERS:
        raise ValueError(f"unknown O-LQ6S trigger {trigger_name}")
    t=int(turn)
    if t<W2_START or t>=W2_END_EXCLUSIVE:return False,{"reason":"outside_w2"}
    b=canonical_action(base_action)
    if market_has_nonempty(b):return False,{"reason":"market_nonempty"}
    shed,carried=own_strawberry(obs);total=shed+carried
    if total<2:return False,{"reason":"insufficient_strawberry","shed":shed,"carried":carried,"total":total}
    ok=False
    if trigger_name=="T0_AVAILABLE":ok=True
    elif trigger_name=="T1_CARRIED20":ok=carried>=20
    elif trigger_name=="T2_SHED2":ok=shed>=2
    elif trigger_name=="T3_CARRIED20_OR_SHED2":ok=(carried>=20 or shed>=2)
    return ok,{"reason":"eligible" if ok else "trigger_false","shed":shed,"carried":carried,"total":total}

def lq6s_action(obs,base_action,turn:int,trigger_name:str):
    b=canonical_action(base_action)
    ok,meta=trigger_eligible(obs,b,turn,trigger_name)
    if not ok:return b,{"fired":False,"turn":int(turn),"trigger":trigger_name,**meta}

    market=copy.deepcopy(b["market"])
    idx=None
    for i,o in enumerate(market):
        if not bool(list(o or [])):
            idx=i;break
    if idx is None:
        idx=len(market)
        market.append(["SELL","STRAWBERRY",2])
        mode="append"
    else:
        market[idx]=["SELL","STRAWBERRY",2]
        mode="replace_empty"

    out=canonical_action({
      "farmer":copy.deepcopy(b["farmer"]),
      "hands":copy.deepcopy(b["hands"]),
      "market":market,
    })
    if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
        raise RuntimeError("O-LQ6S changed physical action")

    # Verify only semantic first-free insertion occurred.
    expected=copy.deepcopy(b["market"])
    if idx==len(expected):
        expected.append(["SELL","STRAWBERRY",2])
    else:
        if bool(list(expected[idx] or [])):
            raise RuntimeError("O-LQ6S target slot was not free")
        expected[idx]=["SELL","STRAWBERRY",2]
    if out["market"]!=canonical_action({"farmer":b["farmer"],"hands":b["hands"],"market":expected})["market"]:
        raise RuntimeError("O-LQ6S changed market beyond first-free STRAWBERRY insertion")

    return out,{
      "fired":True,"turn":int(turn),"trigger":trigger_name,
      "index":idx,"mode":mode,"quantity":2,
      "shed_strawberry":meta["shed"],"carried_strawberry":meta["carried"],"total_strawberry":meta["total"],
    }
