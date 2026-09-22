"""Runtime for V27C2 structural first-party policy.

No teacher calls. No opponent/source identity. Uses only legal player observation
plus explicit legal episode memory.
"""
from __future__ import annotations

import json
import numpy as np

from solver.programme_features import ITEMS,SHOPS,KINDS,features as programme_features

MAX_UNITS=40
MARKET_SLOTS=10

def tile_kind(tile):
    if tile is None:
        return "EMPTY"
    if isinstance(tile,str):
        return tile if tile in KINDS else "EMPTY"
    if isinstance(tile,dict):
        return str(tile.get("kind","EMPTY"))
    return "EMPTY"

def tile_features(tile):
    kind=tile_kind(tile)
    out=[1.0 if kind==k else 0.0 for k in KINDS]
    what=None
    if isinstance(tile,dict):
        if kind=="PLANT":
            what=tile.get("crop")
        elif kind in ("COOP","PASTURE"):
            what=tile.get("animal")
    out.extend(1.0 if what==i else 0.0 for i in ITEMS)
    if isinstance(tile,dict):
        vals=[
            tile.get("yield_units",0),
            tile.get("consecutive_unwatered",0),
            tile.get("consecutive_unfed",0),
            int(bool(tile.get("watered_today",False))),
            int(bool(tile.get("fed_today",False))),
            int(bool(tile.get("cared_today",False))),
            int(bool(tile.get("fertilizer_available",False))),
        ]
    else:
        vals=[0,0,0,0,0,0,0]
    out.extend(float(v or 0) for v in vals)
    return out

class LegalMemory:
    def __init__(self):
        self.rkey_seen=False
        self.rkey_money=0.0
        self.rkey_wheat=0.0
        self.shops_seen=False
        self.shop1=None
        self.shop2=None
        self.last_step=-1

    def reset_if_needed(self,obs):
        step=int(obs.get("step",0))
        if step==0 or step<=self.last_step:
            self.__init__()
        self.last_step=step

    def update(self,obs):
        self.reset_if_needed(obs)
        step=int(obs.get("step",0))
        me=int(obs["player"])
        if step==2 and not self.rkey_seen:
            try:
                self.rkey_money=float(obs["farms"][1-me]["money"])
                self.rkey_wheat=float(obs["market"]["inventory"]["WHEAT"])
                self.rkey_seen=True
            except Exception:
                pass
        if step>=144 and not self.shops_seen:
            shops=list((obs.get("town") or {}).get("unlocked_shops") or [])
            if len(shops)>=2:
                self.shop1=str(shops[0]);self.shop2=str(shops[1]);self.shops_seen=True

    def vector(self,obs):
        step=int(obs.get("step",0))
        out=[
            1.0 if self.rkey_seen else 0.0,
            float(self.rkey_money),
            float(self.rkey_wheat),
            1.0 if self.shops_seen else 0.0,
        ]
        out.extend(1.0 if self.shop1==s else 0.0 for s in SHOPS)
        out.extend(1.0 if self.shop2==s else 0.0 for s in SHOPS)
        out.extend([1.0 if step>=144 else 0.0,1.0 if step>=648 else 0.0])
        return np.asarray(out,dtype=np.float32)

def global_features(obs,memory):
    memory.update(obs)
    base=np.asarray(programme_features(obs),dtype=np.float32)
    out=np.concatenate([base,memory.vector(obs)]).astype(np.float32,copy=False)
    if out.shape!=(136,):
        raise RuntimeError(f"unexpected global feature shape {out.shape}")
    return out

def actor_local_features(obs,actor_index):
    me=int(obs["player"])
    own=obs["farms"][me]
    positions=[own["farmer"]]+list(own.get("hands") or [])
    if not (0<=actor_index<len(positions)):
        raise RuntimeError("actor index out of range")
    if actor_index>=MAX_UNITS:
        raise RuntimeError(f"actor index exceeds encoding limit: {actor_index}")

    pos=positions[actor_index]
    x=int(pos[0]);y=int(pos[1])
    invs=list((obs.get("private") or {}).get("inventories") or [])
    inv=invs[actor_index] if actor_index<len(invs) else {}

    onehot=[0.0]*MAX_UNITS
    onehot[actor_index]=1.0
    out=onehot+[1.0 if actor_index==0 else 0.0,float(x),float(y)]
    out.extend(float((inv or {}).get(i,0) or 0) for i in ITEMS)

    tiles=own["tiles"]
    h=len(tiles);w=len(tiles[0]) if h else 0
    tile=tiles[y][x] if 0<=y<h and 0<=x<w else "LOCKED"
    out.extend(tile_features(tile))

    for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
        nx,ny=x+dx,y+dy
        nt=tiles[ny][nx] if 0<=ny<h and 0<=nx<w else "LOCKED"
        nk=tile_kind(nt)
        out.extend(1.0 if nk==k else 0.0 for k in KINDS)

    arr=np.asarray(out,dtype=np.float32)
    if arr.shape!=(104,):
        raise RuntimeError(f"unexpected actor feature shape {arr.shape}")
    return arr

class StructuralPolicy:
    def __init__(self,models):
        self.unit_model=models["unit_model"]
        self.market_model=models["market_model"]
        self.memory=LegalMemory()

    def __call__(self,obs,config=None):
        gf=global_features(obs,self.memory)
        me=int(obs["player"])
        own=obs["farms"][me]
        actor_count=1+len(own.get("hands") or [])

        UX=[]
        for actor in range(actor_count):
            UX.append(np.concatenate([gf,actor_local_features(obs,actor)]))
        unit_pred=self.unit_model.predict(np.asarray(UX,dtype=np.float32))
        farmer=json.loads(str(unit_pred[0]))
        hands=[json.loads(str(x)) for x in unit_pred[1:]]

        base=np.repeat(gf.reshape(1,-1),MARKET_SLOTS,axis=0)
        slot=np.eye(MARKET_SLOTS,dtype=np.float32)
        MX=np.concatenate([base,slot],axis=1)
        market_pred=self.market_model.predict(MX)
        market=[]
        for lab in market_pred:
            s=str(lab)
            if s=="<NONE>":
                break
            market.append(json.loads(s))

        return {"farmer":farmer,"hands":hands,"market":market}
