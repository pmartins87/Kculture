"""R4D terminal-throughput candidate: reclaim mechanically worthless final-day WATER.

Frozen R4B remains the policy everywhere except executable states 696..718.
When R4B asks an actor to WATER during that final partial day, there is no later
daily production refresh before terminal scoring.  The WATER therefore cannot
increase terminal crop output.

This bounded candidate replaces only such WATER actions:
- HARVEST when the actor is already standing on a tile with positive yield;
- DROP when the actor is standing on the shed and carries sellable inventory;
- otherwise PASS.

No route movement, market choice, FEED, CARE, seed purchase, or earlier action is
changed.  R4B's step-718 projected-shed liquidation remains intact.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
START, END = 696, 718
SELLABLE = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4d_terminal_water_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen R4B base: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BASE = _load_base()


def _get(obj, key, default=None):
    try: return obj.get(key, default)
    except AttributeError:
        try: return obj[key]
        except Exception: return default


def _tile_at(farm, pos):
    if not (isinstance(pos, (list,tuple)) and len(pos)==2): return None
    try:
        x,y=int(pos[0]),int(pos[1]); rows=_get(farm,"tiles",[]) or []
        if y<0 or y>=len(rows) or x<0 or x>=len(rows[y]): return None
        return rows[y][x]
    except Exception: return None


def _actor_pos(farm, actor):
    if actor == 0: return _get(farm,"farmer")
    hands=_get(farm,"hands",[]) or []
    return hands[actor-1] if actor-1 < len(hands) else None


def _inventory(private, actor):
    invs=_get(private,"inventories",[]) or []
    return invs[actor] if actor < len(invs) else {}


def _has_inventory(inv):
    if not isinstance(inv,dict): return False
    return any(int(_get(inv,p,0) or 0) > 0 for p in SELLABLE)


def _is_shed(tile):
    if not isinstance(tile,dict): return False
    return tile.get("kind") == "SHED" or bool(tile.get("shed",False))


def _replacement(tile, inv):
    if isinstance(tile,dict):
        try: units=max(0,int(tile.get("yield_units",0) or 0))
        except (TypeError,ValueError): units=0
        if units > 0:
            return ["HARVEST"]
        if _is_shed(tile) and _has_inventory(inv):
            return ["DROP"]
    return ["PASS"]


def agent(obs, config=None):
    base_action=_BASE.agent(obs, config)
    try: step=int(_get(obs,"step",0) or 0)
    except (TypeError,ValueError): return base_action
    if step < START or step > END:
        return base_action

    action=copy.deepcopy(base_action)
    farms=_get(obs,"farms",[]) or []
    try: player=int(_get(obs,"player",0) or 0)
    except (TypeError,ValueError): player=0
    if player<0 or player>=len(farms): return action
    farm=farms[player]; private=_get(obs,"private",{}) or {}

    ops=[action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]
    for actor,op in enumerate(ops):
        if not (isinstance(op,list) and op and op[0] == "WATER"):
            continue
        pos=_actor_pos(farm,actor); tile=_tile_at(farm,pos); inv=_inventory(private,actor)
        repl=_replacement(tile,inv)
        if actor == 0:
            action["farmer"] = repl
        else:
            hands=list(action.get("hands") or [])
            if actor-1 < len(hands): hands[actor-1] = repl
            action["hands"] = hands
    return action
