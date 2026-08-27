"""R4D terminal market front-run: sell non-input shed goods at step 717.

Frozen R4B is unchanged except for extra SELL orders on executable step 717.
Only products that cannot be bought back or used as farm inputs are eligible:
CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL.

At default town intervals, step 716 is the last town-consumption tick before the
final executable step 718; neither 717 nor 718 has a town tick. These products
also cannot be BUY_PRODUCT targets. Thus after step 717 their market inventory
cannot decrease before 718; their price can only stay flat or fall from sales.
Selling already-available projected shed stock one turn earlier weakly
front-runs later liquidation without removing a usable input.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"candidates/r4b_ablation_market_only.py"
EARLY_STEP=717
EARLY_ITEMS=("CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL")


def _load_base():
    spec=importlib.util.spec_from_file_location("kculture_r4d_early_sell_base",BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError(f"Unable to load {BASE_PATH}")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

_BASE=_load_base()


def _get(obj,key,default=None):
    try: return obj.get(key,default)
    except AttributeError:
        try: return obj[key]
        except Exception: return default


def _projected_shed(obs,action):
    # Frozen R4B itself uses this exact frozen-COK projection on terminal step.
    return _BASE._BASE._v5_projected_shed(obs,action)


def _early_noninput_sell(obs,action):
    projected=_projected_shed(obs,action)
    existing=list(action.get("market") or [])
    already={}
    for order in existing:
        if isinstance(order,list) and len(order)>=3 and order[0]=="SELL":
            try: q=max(0,int(order[2] or 0))
            except Exception: q=0
            already[order[1]]=already.get(order[1],0)+q
    prices=_get(_get(obs,"market",{}) or {},"prices",{}) or {}
    rows=[]
    for item in EARLY_ITEMS:
        try:
            qty=max(0,int(projected.get(item,0) or 0)-already.get(item,0))
            p=max(1.0,float(_get(prices,item,1) or 1))
        except Exception:
            continue
        if qty>0: rows.append((p*qty,p,item,qty))
    rows.sort(reverse=True)
    market=existing[:]
    for _gross,_p,item,qty in rows:
        if len(market)>=10: break
        market.append(["SELL",item,qty])
    action["market"]=market
    return action


def agent(obs,config=None):
    action=_BASE.agent(obs,config)
    try: step=int(_get(obs,"step",0) or 0)
    except Exception: return action
    if step==EARLY_STEP:
        return _early_noninput_sell(obs,action)
    return action
