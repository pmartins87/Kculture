"""CR-011: CR-008-equivalent adaptive sales, moved before base market orders.

Research candidate authorized by CR-010. Prediction model, thresholds, eligible
products, quantities and base action are identical to CR-008. The only intended
strategic change is order-list placement: adaptive sales that CR-008 would append
are prefixed, preserving their relative CARROT->STRAWBERRY order and preserving
all base market orders. No base order is dropped; adaptation is limited to free
market-order capacity exactly as in CR-008.
"""
from __future__ import annotations

import copy
from candidates import cr008_adaptive_frontrun as C

_HISTORY={0:{},1:{}}
_LAST_STEP={0:-1,1:-1}


def _reset_if_needed(player,step):
    if step==0 or step<_LAST_STEP[player]:
        _HISTORY[player].clear()
    _LAST_STEP[player]=step


def _remember(player,step,obs):
    _HISTORY[player][step]=C._snapshot(obs)
    cutoff=step-30
    for k in list(_HISTORY[player]):
        if k<cutoff:del _HISTORY[player][k]


def _prefix_adaptive_sales(obs,action,player,step):
    prev=_HISTORY[player].get(step-24)
    if prev is None:return action
    feat=C._public_features(obs,prev,player)
    if not feat:return action
    names=C._MODELS["feature_names"]
    market=list(action.get("market") or [])
    already={o[1] for o in market if isinstance(o,list) and len(o)>=2 and o[0]=="SELL"}
    shed=C._get(C._get(obs,"private",{}) or {},"shed",{}) or {}
    adaptive=[]
    capacity=max(0,10-len(market))
    for target,item in C.TARGET_TO_ITEM.items():
        if len(adaptive)>=capacity:break
        if item in already:continue
        try:qty=max(0,int(C._get(shed,item,0) or 0))
        except Exception:qty=0
        if qty<=0:continue
        prob=C._tree_prob(C._MODELS["models"][target],feat,names)
        threshold=float(C._MODELS["thresholds"][target])
        if prob>=threshold:
            adaptive.append(["SELL",item,qty]);already.add(item)
    if adaptive:
        action["market"]=adaptive+market
    return action


def agent(obs,config=None):
    player=int(C._get(obs,"player",0) or 0)
    step=C._clock_step(obs)
    _reset_if_needed(player,step)
    action=C._BASE.agent(obs,config)
    action=_prefix_adaptive_sales(obs,action,player,step)
    _remember(player,step,obs)
    return action
