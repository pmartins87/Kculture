#!/usr/bin/env python3
"""V27C2 collect compact stateful structural teacher data."""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from solver.programme_features import ITEMS,SHOPS,KINDS,features as programme_features
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79901,79902,79903,79904,79905,79906,79907,79908)
SEATS=(0,1)
MAX_UNITS=40
MARKET_SLOTS=10

def jkey(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

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

    def update(self,obs):
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
    mem=memory.vector(obs)
    out=np.concatenate([base,mem]).astype(np.float32,copy=False)
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

class Recorder:
    def __init__(self,teacher_main):
        purge_package_modules(teacher_main.parent)
        self.fn=load_public_agent(teacher_main)
        self.memory=LegalMemory()
        self.turn_global=[]
        self.steps=[]
        self.unit_local=[]
        self.unit_turn=[]
        self.unit_actor=[]
        self.unit_labels=[]
        self.farmer=[]
        self.hands=[]
        self.market=[]
        self.complete=[]

    def __call__(self,obs,config=None):
        ob=plain(obs)
        action=canonical_action(call_agent(self.fn,obs,config))
        tidx=len(self.turn_global)
        gf=global_features(ob,self.memory)
        self.turn_global.append(gf)
        self.steps.append(int(ob.get("step",tidx)))

        positions=[ob["farms"][int(ob["player"])]["farmer"]]+list(ob["farms"][int(ob["player"])].get("hands") or [])
        if len(action["hands"])!=max(0,len(positions)-1):
            raise RuntimeError(f"teacher hand alignment mismatch action={len(action['hands'])} observed={len(positions)-1}")
        unit_actions=[action["farmer"]]+list(action["hands"])
        for actor_idx,ua in enumerate(unit_actions):
            self.unit_local.append(actor_local_features(ob,actor_idx))
            self.unit_turn.append(tidx)
            self.unit_actor.append(actor_idx)
            self.unit_labels.append(jkey(ua))

        self.farmer.append(jkey(action["farmer"]))
        self.hands.append(jkey(action["hands"]))
        self.market.append(jkey(action["market"]))
        self.complete.append(jkey(action))
        return action

def run_episode(teacher_main,opp_main,seed,seat):
    purge_package_modules(teacher_main.parent);purge_package_modules(opp_main.parent)
    cand=Recorder(teacher_main)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(v) for v in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    if len(cand.steps)<719 or cand.steps[0]!=0 or cand.steps[-1]!=718:
        raise RuntimeError(f"incomplete candidate calls n={len(cand.steps)} first={cand.steps[:3]} last={cand.steps[-3:]}")
    return cand

def encode(values):
    vocab=sorted(set(values));mp={v:i for i,v in enumerate(vocab)}
    dtype=np.uint16 if len(vocab)<65536 else np.uint32
    return vocab,np.asarray([mp[v] for v in values],dtype=dtype)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=12)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(args.snapshot_dir)
    man=json.loads((root/"MANIFEST.json").read_text())
    sources=list(man["sources"])
    teacher_meta=next(s for s in sources if int(s["representative_rank"])==1)
    teacher=root/teacher_meta["path"]
    if sha256_bytes(teacher.read_bytes())!=TEACHER_SHA:
        raise SystemExit("teacher SHA mismatch")

    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]
    if len(selected)!=1:
        raise SystemExit(f"expected one source, got {len(selected)}")
    src=selected[0];opp=root/src["path"]
    if sha256_bytes(opp.read_bytes())!=str(src["sha"]):
        raise SystemExit("opponent SHA mismatch")

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    turn_global=[];steps=[];turn_ep=[]
    unit_local=[];unit_turn=[];unit_actor=[];unit_labels=[]
    farmer=[];hands=[];market=[];complete=[]
    episodes=[];failures=[]
    turn_cursor=0;unit_cursor=0

    for seed in SEEDS:
        for seat in SEATS:
            ep_index=len(episodes)
            try:
                rec=run_episode(teacher,opp,seed,seat)
                nt=len(rec.steps);nu=len(rec.unit_labels)

                turn_global.extend(rec.turn_global);steps.extend(rec.steps);turn_ep.extend([ep_index]*nt)
                unit_local.extend(rec.unit_local)
                unit_turn.extend(turn_cursor+int(x) for x in rec.unit_turn)
                unit_actor.extend(rec.unit_actor);unit_labels.extend(rec.unit_labels)
                farmer.extend(rec.farmer);hands.extend(rec.hands);market.extend(rec.market);complete.extend(rec.complete)

                episodes.append({
                    "episode_index":ep_index,
                    "source_rank":int(src["representative_rank"]),
                    "ref":src["representative_ref"],
                    "main_sha256":src["sha"],
                    "seed":int(seed),"seat":int(seat),
                    "turn_start":turn_cursor,"turn_end":turn_cursor+nt,
                    "unit_start":unit_cursor,"unit_end":unit_cursor+nu,
                    "turns":nt,"unit_samples":nu,
                })
                turn_cursor+=nt;unit_cursor+=nu
                print("V27C2_EPISODE",json.dumps({"rank":src["representative_rank"],"seed":seed,"seat":seat,"turns":nt,"unit_samples":nu},sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"rank":int(src["representative_rank"]),"ref":src["representative_ref"],"sha":src["sha"],"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge_package_modules(teacher.parent);purge_package_modules(opp.parent)

    uv,ui=encode(unit_labels);fv,fi=encode(farmer);hv,hi=encode(hands);mv,mi=encode(market);cv,ci=encode(complete)

    # Market slot labels are derived from canonical market lists, always 10 per turn.
    market_slot_labels=[]
    for s in market:
        arr=json.loads(s)
        for slot in range(MARKET_SLOTS):
            market_slot_labels.append(jkey(arr[slot]) if slot<len(arr) else "<NONE>")
    msv,msi=encode(market_slot_labels)
    msi=msi.reshape((-1,MARKET_SLOTS)) if len(market) else np.zeros((0,MARKET_SLOTS),dtype=np.uint16)

    outdir=Path(args.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    TG=np.stack(turn_global).astype(np.float32,copy=False) if turn_global else np.zeros((0,136),dtype=np.float32)
    UL=np.stack(unit_local).astype(np.float32,copy=False) if unit_local else np.zeros((0,104),dtype=np.float32)

    np.savez_compressed(
        outdir/"DATA.npz",
        turn_global=TG,
        steps=np.asarray(steps,dtype=np.int16),
        turn_episode_index=np.asarray(turn_ep,dtype=np.int16),
        unit_local=UL,
        unit_turn_index=np.asarray(unit_turn,dtype=np.int32),
        unit_actor_index=np.asarray(unit_actor,dtype=np.int8),
        unit_label_id=ui,
        farmer_id=fi,hands_id=hi,market_id=mi,complete_id=ci,
        market_slot_label_id=msi,
    )
    mech=not failures and len(episodes)==len(SEEDS)*len(SEATS) and TG.shape[0]==len(farmer) and UL.shape[0]==len(unit_labels)
    meta={
        "schema":"kculture-v27c2-structural-dataset-shard-v1",
        "mechanical_pass":mech,
        "shard_index":args.shard_index,"num_shards":args.num_shards,
        "teacher_sha":TEACHER_SHA,
        "source_rank":int(src["representative_rank"]),"source_ref":src["representative_ref"],"source_sha":src["sha"],
        "seeds":list(SEEDS),"seats":list(SEATS),
        "global_feature_dim":136,"unit_local_feature_dim":104,
        "episodes":episodes,"turn_rows":int(TG.shape[0]),"unit_rows":int(UL.shape[0]),
        "vocabs":{"unit":uv,"farmer":fv,"hands":hv,"market":mv,"market_slot":msv,"complete":cv},
        "failures":failures,
        "immutable_snapshot_used":True,"live_kaggle_reacquisition_used":False,"automatic_kaggle_submission":False,
    }
    (outdir/"META.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("V27C2_SHARD_RESULT",json.dumps({"shard":args.shard_index,"rank":src["representative_rank"],"mechanical_pass":mech,"episodes":len(episodes),"turn_rows":int(TG.shape[0]),"unit_rows":int(UL.shape[0]),"unit_classes":len(uv),"market_slot_classes":len(msv),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
