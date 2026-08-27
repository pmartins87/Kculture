"""R4D terminal market race candidate: reorder only step-718 SELL slots.

Frozen R4B determines all unit actions, projected shed quantities and terminal
SELL quantities unchanged. At executable step 718 this wrapper only reorders
those SELL orders so resources with the largest self price-impact exposure are
placed in earlier market slots.

The official market resolves slot 0 for both players, then slot 1, etc. Per-unit
quotes within one slot use the same pre-commit inventory for both players.
Therefore earlier placement matters when the opponent sells the same resource
in a later slot. No future/opponent-private information is used.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
TERMINAL_STEP = 718
I0 = 10000
FLOOR = 1
HINGE_GAIN = 8.0
MP = {
    "WHEAT":      {"base":25,"T":400,"below_func":"sqrt","below_target":0.80,"above_func":"log","above_target":0.20},
    "CARROT":     {"base":35,"T":450,"below_func":"hinge","below_target":1.00,"above_func":"sqrt","above_target":0.70},
    "TOMATO":     {"base":60,"T":200,"below_func":"hinge","below_target":0.40,"above_func":"sqrt","above_target":0.60},
    "STRAWBERRY": {"base":120,"T":100,"below_func":"sqrt","below_target":0.70,"above_func":"linear","above_target":1.60},
    "MELON":      {"base":250,"T":300,"below_func":"log","below_target":0.20,"above_func":"sq","above_target":3.60},
    "EGG":        {"base":50,"T":332,"below_func":"hinge","below_target":0.40,"above_func":"log","above_target":0.20},
    "MILK":       {"base":160,"T":122,"below_func":"sqrt","below_target":0.60,"above_func":"linear","above_target":1.60},
    "WOOL":       {"base":200,"T":105,"below_func":"log","below_target":0.20,"above_func":"sq","above_target":3.20},
    "FERTILIZER": {"base":100,"T":200,"below_func":"linear","below_target":0.40,"above_func":"linear","above_target":0.40},
}


def _load_base():
    spec=importlib.util.spec_from_file_location("kculture_r4d_sell_base",BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError(f"Unable to load {BASE_PATH}")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

_BASE=_load_base()


def _get(obj,key,default=None):
    try: return obj.get(key,default)
    except AttributeError:
        try: return obj[key]
        except Exception: return default


def _shape(func,x,T):
    x=max(0.0,float(x))
    if func=="linear": return x
    if func=="sq": return x*x
    if func=="sqrt": return math.sqrt(x)
    if func=="log": return math.log(1.0+x)
    if func=="log10": return math.log10(1.0+x)
    if func=="hinge":
        u=x/T if T>0 else x
        return u + HINGE_GAIN*max(0.0,u-1.0)**2
    return x


def _price(item,inventory):
    p=MP[item]; base=p["base"]; T=p["T"]
    if inventory < I0:
        f=p["below_func"]; denom=_shape(f,T,T); amp=p["below_target"]*base/denom
        value=base+amp*_shape(f,I0-inventory,T)
    else:
        f=p["above_func"]; denom=_shape(f,T,T); amp=p["above_target"]*base/denom
        value=base-amp*_shape(f,inventory-I0,T)
    return max(FLOOR,int(round(value)))


def _priority(order,obs):
    if not (isinstance(order,list) and len(order)>=3 and order[0]=="SELL" and order[1] in MP):
        return (-1.0,-1.0,-1.0)
    item=order[1]
    try: qty=max(0,int(order[2] or 0))
    except Exception: qty=0
    invs=_get(_get(obs,"market",{}) or {},"inventory",{}) or {}
    try: inv=int(_get(invs,item,I0) or I0)
    except Exception: inv=I0
    p0=_price(item,inv); p1=_price(item,inv+qty)
    impact=float(qty)*float(max(0,p0-p1))
    gross=float(qty)*float(p0)
    return (impact,gross,float(p0))


def agent(obs,config=None):
    action=_BASE.agent(obs,config)
    try: step=int(_get(obs,"step",0) or 0)
    except Exception: return action
    if step != TERMINAL_STEP: return action
    orders=list(action.get("market") or [])
    if not orders: return action
    indexed=list(enumerate(orders))
    indexed.sort(key=lambda z: (_priority(z[1],obs),-z[0]),reverse=True)
    action["market"]=[o for _,o in indexed]
    return action
