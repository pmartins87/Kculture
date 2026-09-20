#!/usr/bin/env python3
"""O-LQ6S: W2 STRAWBERRY first-free SELL2 under frozen V17A4 rising-edge trigger."""
from __future__ import annotations
from dataclasses import dataclass
import copy
from tools.bounded_transaction_oracle_v1 import canonical_action,plain

W2_START=336
W2_END_EXCLUSIVE=504
ALLOWED_TRIGGERS={
  "E0_AVAILABLE_RISING",
  "E1_CARRIED20_RISING",
  "E2_SHED2_RISING",
  "E3_CARRIED20_OR_SHED2_RISING",
}
BASE_TRIGGER={
  "E0_AVAILABLE_RISING":"T0_AVAILABLE",
  "E1_CARRIED20_RISING":"T1_CARRIED20",
  "E2_SHED2_RISING":"T2_SHED2",
  "E3_CARRIED20_OR_SHED2_RISING":"T3_CARRIED20_OR_SHED2",
}

@dataclass
class LQ6SState:
    previous_condition: bool=False

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

def stateless_condition(obs,base_action,turn:int,base_trigger:str):
    t=int(turn)
    if t<W2_START or t>=W2_END_EXCLUSIVE:
        return False,{"reason":"outside_w2","shed":0,"carried":0,"total":0}
    b=canonical_action(base_action)
    if market_has_nonempty(b):
        shed,carried=own_strawberry(obs)
        return False,{"reason":"market_nonempty","shed":shed,"carried":carried,"total":shed+carried}
    shed,carried=own_strawberry(obs);total=shed+carried
    if total<2:
        return False,{"reason":"insufficient_strawberry","shed":shed,"carried":carried,"total":total}
    if base_trigger=="T0_AVAILABLE":ok=True
    elif base_trigger=="T1_CARRIED20":ok=carried>=20
    elif base_trigger=="T2_SHED2":ok=shed>=2
    elif base_trigger=="T3_CARRIED20_OR_SHED2":ok=(carried>=20 or shed>=2)
    else:raise ValueError(f"unknown base trigger {base_trigger}")
    return ok,{"reason":"eligible" if ok else "trigger_false","shed":shed,"carried":carried,"total":total}

def lq6s_action(obs,base_action,turn:int,trigger_name:str,state:LQ6SState):
    if trigger_name not in ALLOWED_TRIGGERS:
        raise ValueError(f"unknown O-LQ6S trigger {trigger_name}")
    b=canonical_action(base_action)
    base_trigger=BASE_TRIGGER[trigger_name]
    cond,meta=stateless_condition(obs,b,turn,base_trigger)
    prev=bool(state.previous_condition)
    rising=bool(cond and not prev)
    state.previous_condition=bool(cond)
    if not rising:
        return b,{
          "fired":False,"turn":int(turn),"trigger":trigger_name,"base_trigger":base_trigger,
          "condition":bool(cond),"previous_condition":prev,**meta
        }

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

    expected=copy.deepcopy(b["market"])
    if idx==len(expected):
        expected.append(["SELL","STRAWBERRY",2])
    else:
        if bool(list(expected[idx] or [])):
            raise RuntimeError("O-LQ6S target slot was not free")
        expected[idx]=["SELL","STRAWBERRY",2]
    expected_market=canonical_action({"farmer":b["farmer"],"hands":b["hands"],"market":expected})["market"]
    if out["market"]!=expected_market:
        raise RuntimeError("O-LQ6S changed market beyond first-free STRAWBERRY insertion")

    return out,{
      "fired":True,"turn":int(turn),"trigger":trigger_name,"base_trigger":base_trigger,
      "condition":True,"previous_condition":prev,
      "index":idx,"mode":mode,"quantity":2,
      "shed_strawberry":meta["shed"],"carried_strawberry":meta["carried"],"total_strawberry":meta["total"],
    }
