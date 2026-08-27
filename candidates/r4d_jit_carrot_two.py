"""KEXP-045: two bounded state-adaptive JIT CARROT substitutions.

Extends KEXP-041 by adding one second mechanically safe block. Frozen R4B is
unchanged except at two buy/plant pairs:

  state 614 -> 615, q=3
  state 619 -> 620, q=3

At each buy state, append one BUY_SEED CARROT only when
    3 * (CARROT_price - WHEAT_price) - 20 > 0
and a market slot is free. At the corresponding plant state, convert exactly
one frozen-R4B PLANT WHEAT only if observed CARROT seed stock proves that the
extra purchase actually arrived above the conservative base-stock expectation.

KEXP-040 found the same sign-positive episode set at both blocks across the 36
development/exploratory episodes. No seed/opponent/episode identity is used.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"candidates/r4b_ablation_market_only.py"
BUY_TO_PLANT={614:615,619:620}
PLANT_TO_BUY={v:k for k,v in BUY_TO_PLANT.items()}
MAX_MARKET_ORDERS=10
Q=3.0


def _load_base():
    spec=importlib.util.spec_from_file_location("kculture_r4d_jit2_base",BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError(f"Unable to load {BASE_PATH}")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

_BASE=_load_base()
_STATE={}


def _get(obj,key,default=None):
    try:return obj.get(key,default)
    except AttributeError:
        try:return obj[key]
        except Exception:return default

def _step(obs):
    try:return int(_get(obs,"step",0) or 0)
    except Exception:return 0

def _player(obs):
    try:return int(_get(obs,"player",0) or 0)
    except Exception:return 0

def _seeds(obs):return _get(_get(obs,"private",{}) or {},"seeds",{}) or {}

def _price(obs,item):
    try:
        v=float(_get(_get(_get(obs,"market",{}) or {},"prices",{}) or {},item,0) or 0)
        return v if v>0 else None
    except Exception:return None

def _unit_ops(action):
    yield action.get("farmer")
    for op in list(action.get("hands") or []):yield op

def _count_carrot_plants(action):
    return sum(isinstance(op,list) and len(op)>=2 and op[:2]==["PLANT","CARROT"] for op in _unit_ops(action))

def _count_carrot_buys(action):
    n=0
    for o in list(action.get("market") or []):
        if isinstance(o,list) and len(o)>=3 and o[:2]==["BUY_SEED","CARROT"]:
            try:n+=max(0,int(o[2] or 0))
            except Exception:pass
    return n

def _replace_one(action):
    op=action.get("farmer")
    if isinstance(op,list) and len(op)>=2 and op[:2]==["PLANT","WHEAT"]:
        action["farmer"]=["PLANT","CARROT"];return True
    hs=list(action.get("hands") or [])
    for i,op in enumerate(hs):
        if isinstance(op,list) and len(op)>=2 and op[:2]==["PLANT","WHEAT"]:
            hs[i]=["PLANT","CARROT"];action["hands"]=hs;return True
    return False

def _fresh(step):return {"last_step":step,"pending":None}


def agent(obs,config=None):
    base=_BASE.agent(obs,config);action=copy.deepcopy(base);step=_step(obs);pid=_player(obs)
    st=_STATE.get(pid)
    if st is None or step==0 or step<=int(st.get("last_step",-1)):
        st=_fresh(step);_STATE[pid]=st
    st["last_step"]=step

    if step in BUY_TO_PLANT:
        pw,pc=_price(obs,"WHEAT"),_price(obs,"CARROT")
        margin=None if pw is None or pc is None else Q*(pc-pw)-20.0
        market=list(action.get("market") or [])
        if margin is not None and margin>0 and len(market)<MAX_MARKET_ORDERS:
            try:before=max(0,int(_get(_seeds(obs),"CARROT",0) or 0))
            except Exception:before=0
            expected=max(0,before-_count_carrot_plants(base))+_count_carrot_buys(base)
            market.append(["BUY_SEED","CARROT",1]);action["market"]=market
            st["pending"]={"plant_step":BUY_TO_PLANT[step],"expected":expected}
        else:
            st["pending"]=None
        return action

    pending=st.get("pending")
    if isinstance(pending,dict) and step==int(pending.get("plant_step",-1)):
        try:
            actual=max(0,int(_get(_seeds(obs),"CARROT",0) or 0));expected=max(0,int(pending.get("expected",0) or 0))
        except Exception:actual=expected=0
        if actual>expected:_replace_one(action)
        st["pending"]=None
        return action

    # Expire a missed purchase/plant handshake; never carry it into another block.
    if isinstance(pending,dict) and step>int(pending.get("plant_step",-1)):
        st["pending"]=None
    return action
