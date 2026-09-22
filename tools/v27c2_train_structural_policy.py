#!/usr/bin/env python3
"""Train/evaluate V27C2 stateful structural action distillation."""
from __future__ import annotations

import argparse
import gc
import json
from collections import Counter,defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

TRAIN_SEEDS={79901,79902,79903,79904,79905}
TRAIN_RANKS={1,2,4,5,6,7,9,10}
VAL_SEEDS={79906}
HOLD_SEEDS={79907,79908}
MARKET_SLOTS=10

def jkey(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def load_shards(root):
    out=[]
    for mp in sorted(Path(root).rglob("META.json")):
        try:m=json.loads(mp.read_text())
        except Exception:continue
        if m.get("schema")!="kculture-v27c2-structural-dataset-shard-v1":
            continue
        d=np.load(mp.parent/"DATA.npz",allow_pickle=False)
        out.append({"meta":m,"data":d,"path":mp.parent})
    return out

def split_of(ep):
    seed=int(ep["seed"]);rank=int(ep["source_rank"])
    if seed in TRAIN_SEEDS and rank in TRAIN_RANKS:return "train"
    if seed in VAL_SEEDS:return "validation"
    if seed in HOLD_SEEDS:return "holdout"
    return "unused"

def decode(vocab,ids):
    vv=np.asarray(vocab,dtype=object)
    return vv[np.asarray(ids,dtype=np.int64)]

def episode_turn_split_mask(meta,nturn):
    arr=np.full(nturn,-1,dtype=np.int8)
    # 0 train,1 val,2 hold,3 unused
    code={"train":0,"validation":1,"holdout":2,"unused":3}
    for ep in meta["episodes"]:
        arr[int(ep["turn_start"]):int(ep["turn_end"])]=code[split_of(ep)]
    if np.any(arr<0):raise RuntimeError("unassigned turn rows")
    return arr

def unit_matrix(sh,mask_code):
    m=sh["meta"];d=sh["data"]
    TG=np.asarray(d["turn_global"],dtype=np.float32)
    UL=np.asarray(d["unit_local"],dtype=np.float32)
    uti=np.asarray(d["unit_turn_index"],dtype=np.int64)
    split=episode_turn_split_mask(m,len(TG))
    keep=split[uti]==mask_code
    X=np.concatenate([TG[uti[keep]],UL[keep]],axis=1).astype(np.float32,copy=False)
    y=decode(m["vocabs"]["unit"],d["unit_label_id"][keep])
    return X,y

def market_matrix(sh,mask_code):
    m=sh["meta"];d=sh["data"]
    TG=np.asarray(d["turn_global"],dtype=np.float32)
    split=episode_turn_split_mask(m,len(TG))
    keep=np.flatnonzero(split==mask_code)
    if len(keep)==0:
        return np.zeros((0,TG.shape[1]+MARKET_SLOTS),dtype=np.float32),np.asarray([],dtype=object)
    base=np.repeat(TG[keep],MARKET_SLOTS,axis=0)
    slot=np.tile(np.eye(MARKET_SLOTS,dtype=np.float32),(len(keep),1))
    X=np.concatenate([base,slot],axis=1).astype(np.float32,copy=False)
    ids=np.asarray(d["market_slot_label_id"])[keep].reshape(-1)
    y=decode(m["vocabs"]["market_slot"],ids)
    return X,y

def new_tree():
    return DecisionTreeClassifier(
        criterion="gini",
        splitter="best",
        max_depth=32,
        min_samples_split=2,
        min_samples_leaf=2,
        max_features=None,
        class_weight=None,
        random_state=20260921,
    )

class EvalStats:
    def __init__(self):
        self.total=0;self.farmer=0;self.hands=0;self.market=0;self.complete=0;self.episodes=0
        self.by_source=defaultdict(lambda:[0,0])
        self.by_stage=defaultdict(lambda:[0,0])

    def add(self,sha,steps,farmer_ok,hands_ok,market_ok):
        complete=farmer_ok & hands_ok & market_ok
        n=len(complete)
        self.total+=n
        self.farmer+=int(farmer_ok.sum());self.hands+=int(hands_ok.sum());self.market+=int(market_ok.sum());self.complete+=int(complete.sum())
        self.by_source[sha][0]+=int(complete.sum());self.by_source[sha][1]+=n
        for st,ok in zip(steps,complete):
            b=int(st)//120
            self.by_stage[b][0]+=int(bool(ok));self.by_stage[b][1]+=1
        self.episodes+=1

    def result(self):
        src={k:v[0]/v[1] for k,v in sorted(self.by_source.items()) if v[1]}
        stage={str(k):v[0]/v[1] for k,v in sorted(self.by_stage.items()) if v[1]}
        return {
            "episodes":self.episodes,"turns":self.total,
            "complete_action_parity":self.complete/self.total if self.total else None,
            "market_parity":self.market/self.total if self.total else None,
            "farmer_parity":self.farmer/self.total if self.total else None,
            "hands_parity":self.hands/self.total if self.total else None,
            "by_source_complete_action_parity":src,
            "minimum_source_complete_action_parity":min(src.values()) if src else None,
            "by_120_turn_stage_complete_action_parity":stage,
            "minimum_stage_complete_action_parity":min(stage.values()) if stage else None,
        }

def evaluate_episode(sh,ep,unit_model,market_model):
    m=sh["meta"];d=sh["data"]
    ts,te=int(ep["turn_start"]),int(ep["turn_end"])
    TG=np.asarray(d["turn_global"][ts:te],dtype=np.float32)
    steps=np.asarray(d["steps"][ts:te],dtype=np.int16)

    uti=np.asarray(d["unit_turn_index"],dtype=np.int64)
    lo=int(np.searchsorted(uti,ts,side="left"));hi=int(np.searchsorted(uti,te,side="left"))
    local=np.asarray(d["unit_local"][lo:hi],dtype=np.float32)
    uturn=uti[lo:hi]-ts
    actor=np.asarray(d["unit_actor_index"][lo:hi],dtype=np.int64)
    UX=np.concatenate([TG[uturn],local],axis=1).astype(np.float32,copy=False)
    upred=unit_model.predict(UX)

    pred_farmer=[None]*len(TG);pred_hands=[None]*len(TG)
    for t in range(len(TG)):
        idx=np.flatnonzero(uturn==t)
        if len(idx)==0:raise RuntimeError("turn has no unit samples")
        order=idx[np.argsort(actor[idx])]
        labels=[str(upred[i]) for i in order]
        if int(actor[order[0]])!=0:raise RuntimeError("farmer actor missing")
        pred_farmer[t]=labels[0]
        pred_hands[t]=jkey([json.loads(x) for x in labels[1:]])

    base=np.repeat(TG,MARKET_SLOTS,axis=0)
    slot=np.tile(np.eye(MARKET_SLOTS,dtype=np.float32),(len(TG),1))
    MX=np.concatenate([base,slot],axis=1).astype(np.float32,copy=False)
    mpred=market_model.predict(MX).reshape((len(TG),MARKET_SLOTS))
    pred_market=[]
    for row in mpred:
        orders=[]
        for lab in row:
            lab=str(lab)
            if lab=="<NONE>":break
            orders.append(json.loads(lab))
        pred_market.append(jkey(orders))

    true_farmer=decode(m["vocabs"]["farmer"],d["farmer_id"][ts:te])
    true_hands=decode(m["vocabs"]["hands"],d["hands_id"][ts:te])
    true_market=decode(m["vocabs"]["market"],d["market_id"][ts:te])

    return {
        "steps":steps,
        "farmer_ok":np.asarray(pred_farmer,dtype=object)==true_farmer,
        "hands_ok":np.asarray(pred_hands,dtype=object)==true_hands,
        "market_ok":np.asarray(pred_market,dtype=object)==true_market,
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out-dir",required=True);a=ap.parse_args()
    shards=load_shards(a.input_dir)
    shard_ids={int(s["meta"].get("shard_index",-1)) for s in shards}
    mechanics=len(shards)==12 and shard_ids==set(range(12)) and all(s["meta"].get("mechanical_pass") for s in shards) and all(not s["meta"].get("failures") for s in shards)
    total_eps=sum(len(s["meta"]["episodes"]) for s in shards)
    mechanics=mechanics and total_eps==192

    split_counts=Counter(split_of(ep) for sh in shards for ep in sh["meta"]["episodes"])
    mechanics=mechanics and split_counts==Counter({"train":80,"validation":24,"holdout":48,"unused":40})

    unit_X=[];unit_y=[]
    for sh in shards:
        X,y=unit_matrix(sh,0)
        if len(y):unit_X.append(X);unit_y.append(y)
    UX=np.concatenate(unit_X,axis=0);UY=np.concatenate(unit_y)
    del unit_X,unit_y;gc.collect()

    print("V27C2_UNIT_TRAIN",json.dumps({"rows":int(UX.shape[0]),"features":int(UX.shape[1]),"classes":int(len(np.unique(UY)))},sort_keys=True),flush=True)
    unit_model=new_tree();unit_model.fit(UX,UY)
    del UX,UY;gc.collect()

    market_X=[];market_y=[]
    for sh in shards:
        X,y=market_matrix(sh,0)
        if len(y):market_X.append(X);market_y.append(y)
    MX=np.concatenate(market_X,axis=0);MY=np.concatenate(market_y)
    del market_X,market_y;gc.collect()

    print("V27C2_MARKET_TRAIN",json.dumps({"rows":int(MX.shape[0]),"features":int(MX.shape[1]),"classes":int(len(np.unique(MY)))},sort_keys=True),flush=True)
    market_model=new_tree();market_model.fit(MX,MY)
    del MX,MY;gc.collect()

    val=EvalStats();hold=EvalStats()
    for sh in shards:
        for ep in sh["meta"]["episodes"]:
            sp=split_of(ep)
            if sp not in ("validation","holdout"):continue
            rr=evaluate_episode(sh,ep,unit_model,market_model)
            (val if sp=="validation" else hold).add(str(ep["main_sha256"]),rr["steps"],rr["farmer_ok"],rr["hands_ok"],rr["market_ok"])

    vr=val.result();hr=hold.result()
    mechanics=mechanics and vr.get("episodes")==24 and hr.get("episodes")==48

    gate=(
        mechanics
        and hr["complete_action_parity"]>=0.90
        and hr["market_parity"]>=0.94
        and hr["farmer_parity"]>=0.99
        and hr["hands_parity"]>=0.98
        and hr["minimum_source_complete_action_parity"]>=0.80
        and hr["minimum_stage_complete_action_parity"]>=0.80
    )
    if not mechanics:decision="V27C2_MECHANICS_INVALID"
    elif gate:decision="V27C2_STRUCTURAL_POLICY_DISTILLATION_VIABLE"
    else:decision="V27C2_STRUCTURAL_POLICY_DISTILLATION_NOT_VIABLE"

    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    joblib.dump({"unit_model":unit_model,"market_model":market_model},outdir/"V27C2_MODELS.joblib",compress=3)
    spec={
        "schema":"kculture-v27c2-feature-spec-v1",
        "global_feature_dim":136,"unit_local_feature_dim":104,
        "unit_model_feature_dim":240,"market_model_feature_dim":146,
        "max_units":40,"market_slots":10,
        "legal_memory":["step2_opponent_money","step2_wheat_inventory","ordered_first_two_shops","phase_ge_144","phase_ge_648"],
        "runtime_identity_features":False,"teacher_call_at_inference":False,
        "tree_parameters":{"criterion":"gini","splitter":"best","max_depth":32,"min_samples_split":2,"min_samples_leaf":2,"max_features":None,"class_weight":None,"random_state":20260921},
    }
    (outdir/"V27C2_FEATURE_SPEC.json").write_text(json.dumps(spec,indent=2,sort_keys=True)+"\n")
    result={
        "schema":"kculture-v27c2-structural-distillation-v1",
        "mechanical_pass":mechanics,"decision":decision,"gate_pass":gate,
        "dataset_shards":len(shards),"episodes_total":total_eps,"split_episode_counts":dict(split_counts),
        "unit_training_rows":sum(len(unit_matrix(sh,0)[1]) for sh in shards),
        "market_training_rows":sum(len(market_matrix(sh,0)[1]) for sh in shards),
        "unit_classes":int(len(unit_model.classes_)),"market_slot_classes":int(len(market_model.classes_)),
        "unit_tree_depth":int(unit_model.get_depth()),"unit_tree_leaves":int(unit_model.get_n_leaves()),
        "market_tree_depth":int(market_model.get_depth()),"market_tree_leaves":int(market_model.get_n_leaves()),
        "validation":vr,"holdout":hr,
        "runtime_identity_features":False,"teacher_call_at_inference":False,
        "automatic_kaggle_submission":False,
    }
    (outdir/"V27C2_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V27C2_RESULT",json.dumps({"decision":decision,"mechanical_pass":mechanics,"gate_pass":gate,"unit_classes":result["unit_classes"],"market_slot_classes":result["market_slot_classes"],"unit_tree_depth":result["unit_tree_depth"],"unit_tree_leaves":result["unit_tree_leaves"],"market_tree_depth":result["market_tree_depth"],"market_tree_leaves":result["market_tree_leaves"],"validation":vr,"holdout":hr},sort_keys=True),flush=True)
    if not mechanics:raise SystemExit(2)

if __name__=="__main__":main()
