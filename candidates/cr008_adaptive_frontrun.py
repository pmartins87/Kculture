"""CR-008: high-confidence identity-free opponent-aware market front-run.

Research candidate. Frozen R4B remains untouched except that, when an exported
CR-007 pure decision tree predicts an imminent opponent SELL with high
confidence, we may append a same-turn SELL for current shed stock of CARROT or
STRAWBERRY. No opponent identity is used.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
MODEL_PATH = ROOT / "models/cr007_pure_models.json"
PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS = ("COW","SHEEP","GOOSE")
SHOPS = ("BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET")
TARGET_TO_ITEM = {"SELL_CARROT":"CARROT", "SELL_STRAWBERRY":"STRAWBERRY"}


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_cr008_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen base {BASE_PATH}")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

_BASE = _load_base()
_MODELS = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
_HISTORY = {0:{}, 1:{}}
_LAST_STEP = {0:-1, 1:-1}


def _get(obj,key,default=None):
    try: return obj.get(key,default)
    except AttributeError:
        try: return obj[key]
        except Exception: return default


def _num(d,key):
    try:
        v=float(_get(d,key,0) or 0)
        return v if math.isfinite(v) else 0.0
    except Exception: return 0.0


def _step(obs):
    raw=_get(obs,"step",None)
    try:
        if raw is not None: return max(0,int(raw))
    except Exception: pass
    try:
        day=max(1,int(_get(obs,"day",1) or 1)); hour=max(0,int(_get(obs,"hour",0) or 0))
        return (day-1)*24+hour
    except Exception: return 0


def _tile_counts(farm):
    out={}
    for row in _get(farm,"tiles",[]) or []:
        if not isinstance(row,list): continue
        for tile in row:
            if not isinstance(tile,dict): continue
            if tile.get("kind")=="PLANT":
                k=f"crop_{tile.get('crop')}"; out[k]=out.get(k,0.0)+1.0
            if tile.get("animal"):
                k=f"animal_{tile.get('animal')}"; out[k]=out.get(k,0.0)+1.0
            if tile.get("kind")=="WEED": out["weeds"]=out.get("weeds",0.0)+1.0
            try: out["yield_units"]=out.get("yield_units",0.0)+max(0.0,float(tile.get("yield_units",0) or 0))
            except Exception: pass
    return out


def _farm_public(farm,prefix):
    c=_tile_counts(farm or {})
    out={
        f"{prefix}money":_num(farm,"money"),
        f"{prefix}hands":float(len(_get(farm,"hands",[]) or [])),
        f"{prefix}quads":float(len(_get(farm,"unlocked_quadrants",[]) or [])),
        f"{prefix}weeds":float(c.get("weeds",0)),
        f"{prefix}yield_units":float(c.get("yield_units",0)),
    }
    for crop in CROPS: out[f"{prefix}crop_{crop.lower()}"]=float(c.get(f"crop_{crop}",0))
    for animal in ANIMALS: out[f"{prefix}animal_{animal.lower()}"]=float(c.get(f"animal_{animal}",0))
    return out


def _public_features(obs,prev,player):
    farms=_get(obs,"farms",[]) or []; pf=_get(prev,"farms",[]) or []
    if len(farms)<2 or len(pf)<2: return {}
    opp=1-player
    own=_farm_public(farms[player],"self_"); other=_farm_public(farms[opp],"opp_")
    own0=_farm_public(pf[player],"self_"); other0=_farm_public(pf[opp],"opp_")
    market=_get(obs,"market",{}) or {}; market0=_get(prev,"market",{}) or {}
    prices=_get(market,"prices",{}) or {}; inv=_get(market,"inventory",{}) or {}
    prices0=_get(market0,"prices",{}) or {}; inv0=_get(market0,"inventory",{}) or {}
    shops=set(_get(_get(obs,"town",{}) or {},"unlocked_shops",[]) or [])
    st=float(_step(obs)); f={"step":st,"day":st/24.0,"shop_count":float(len(shops))}
    f.update(own); f.update(other)
    for k,v in own.items(): f[f"d{k}"]=v-own0.get(k,0.0)
    for k,v in other.items(): f[f"d{k}"]=v-other0.get(k,0.0)
    f["gap_money"]=own["self_money"]-other["opp_money"]
    f["gap_hands"]=own["self_hands"]-other["opp_hands"]
    f["gap_quads"]=own["self_quads"]-other["opp_quads"]
    for product in PRODUCTS:
        lo=product.lower(); p=_num(prices,product); q=_num(inv,product)
        f[f"market_price_{lo}"]=p; f[f"market_inventory_{lo}"]=q
        f[f"dmarket_price_{lo}"]=p-_num(prices0,product)
        f[f"dmarket_inventory_{lo}"]=q-_num(inv0,product)
    for shop in SHOPS: f[f"shop_{shop.lower()}"]=1.0 if shop in shops else 0.0
    return f


def _tree_prob(model,features,names):
    node=0
    left=model["children_left"]; right=model["children_right"]
    feats=model["feature"]; th=model["threshold"]
    while left[node] != -1 and right[node] != -1:
        idx=feats[node]; val=float(features.get(names[idx],0.0))
        node=left[node] if val <= th[node] else right[node]
    vals=model["value"][node]; classes=model["classes"]
    total=sum(vals)
    if total<=0 or 1 not in classes: return 0.0
    return float(vals[classes.index(1)])/float(total)


def _snapshot(obs):
    return {
        "step":_step(obs), "day":_get(obs,"day",None), "hour":_get(obs,"hour",None),
        "farms":copy.deepcopy(_get(obs,"farms",[]) or []),
        "market":copy.deepcopy(_get(obs,"market",{}) or {}),
        "town":copy.deepcopy(_get(obs,"town",{}) or {}),
    }


def _reset_if_needed(player,step):
    if step==0 or step < _LAST_STEP[player]:
        _HISTORY[player].clear()
    _LAST_STEP[player]=step


def _remember(player,step,obs):
    _HISTORY[player][step]=_snapshot(obs)
    cutoff=step-30
    for k in list(_HISTORY[player]):
        if k<cutoff: del _HISTORY[player][k]


def _append_adaptive_sales(obs,action,player,step):
    prev=_HISTORY[player].get(step-24)
    if prev is None: return action
    feat=_public_features(obs,prev,player)
    if not feat: return action
    names=_MODELS["feature_names"]
    market=list(action.get("market") or [])
    already={o[1] for o in market if isinstance(o,list) and len(o)>=2 and o[0]=="SELL"}
    shed=_get(_get(obs,"private",{}) or {},"shed",{}) or {}
    for target,item in TARGET_TO_ITEM.items():
        if len(market)>=10: break
        if item in already: continue
        try: qty=max(0,int(_get(shed,item,0) or 0))
        except Exception: qty=0
        if qty<=0: continue
        prob=_tree_prob(_MODELS["models"][target],feat,names)
        threshold=float(_MODELS["thresholds"][target])
        if prob >= threshold:
            market.append(["SELL",item,qty]); already.add(item)
    action["market"]=market
    return action


def agent(obs,config=None):
    player=int(_get(obs,"player",0) or 0)
    step=_step(obs)
    _reset_if_needed(player,step)
    action=_BASE.agent(obs,config)
    action=_append_adaptive_sales(obs,action,player,step)
    _remember(player,step,obs)
    return action
