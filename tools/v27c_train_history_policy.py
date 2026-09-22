#!/usr/bin/env python3
"""V27C train/evaluate 256-step legal-history behavioral distillation."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier

LAGS=(1,2,4,8,16,32,64,128,256)
TRAIN_SEEDS={79901,79902,79903,79904,79905}
TRAIN_RANKS={1,2,4,5,6,7,9,10}
VAL_SEEDS={79906}
HOLD_SEEDS={79907,79908}
MARKET_VERBS=("BUY_PRODUCT","SELL","BUY_SEED","HIRE","EMPTY")

def load_shards(root: Path):
    shards=[]
    for mp in sorted(root.rglob("META.json")):
        meta=json.loads(mp.read_text())
        if meta.get("schema")!="kculture-v27c-teacher-dataset-shard-v1":
            continue
        data=np.load(mp.parent/"DATA.npz",allow_pickle=False)
        shards.append({"meta":meta,"data":data,"path":mp.parent})
    return shards

def decode(vocab, ids):
    vv=np.asarray(vocab,dtype=object)
    return vv[np.asarray(ids,dtype=np.int64)]

def first_verb(obj):
    if isinstance(obj,str):
        return obj
    if isinstance(obj,list):
        if obj and isinstance(obj[0],str):
            return str(obj[0])
        for x in obj:
            v=first_verb(x)
            if v is not None:
                return v
    if isinstance(obj,dict):
        for k in sorted(obj):
            v=first_verb(obj[k])
            if v is not None:
                return v
    return None

def hand_verbs(obj):
    if not isinstance(obj,list):
        v=first_verb(obj)
        return [] if v is None else [v]
    if obj and isinstance(obj[0],str):
        return [str(obj[0])]
    out=[]
    for x in obj:
        v=first_verb(x)
        if v is not None:
            out.append(v)
    return out

def market_counts(label):
    obj=json.loads(label)
    counts=Counter()
    if not obj:
        counts["EMPTY"]=1
    elif isinstance(obj,list) and obj and isinstance(obj[0],str):
        counts[str(obj[0])]+=1
    elif isinstance(obj,list):
        for order in obj:
            v=first_verb(order)
            if v is not None:
                counts[v]+=1
    else:
        v=first_verb(obj)
        if v is not None:
            counts[v]+=1
    return np.asarray([float(counts.get(v,0)) for v in MARKET_VERBS],dtype=np.float32)

def farmer_verb(label):
    return first_verb(json.loads(label))

def collect_train_action_vocabs(shards):
    farmers=set()
    hands=set()
    for sh in shards:
        m=sh["meta"]; d=sh["data"]
        fv=m["vocabs"]["farmer"]; hv=m["vocabs"]["hands"]
        for ep in m["episodes"]:
            if int(ep["seed"]) not in TRAIN_SEEDS or int(ep["source_rank"]) not in TRAIN_RANKS:
                continue
            a,b=int(ep["start"]),int(ep["end"])
            farmer_labels=decode(fv,d["farmer_id"][a:b])
            hands_labels=decode(hv,d["hands_id"][a:b])
            for s in farmer_labels:
                v=farmer_verb(str(s))
                if v is not None:
                    farmers.add(v)
            for s in hands_labels:
                for v in hand_verbs(json.loads(str(s))):
                    hands.add(v)
    return sorted(farmers),sorted(hands)

def prev_summary(market_label,farmer_label,hands_label,farmer_vocab,hand_vocab):
    out=[]
    out.extend(market_counts(market_label).tolist())
    fv=farmer_verb(farmer_label)
    out.extend([1.0 if fv==v else 0.0 for v in farmer_vocab])
    hc=Counter(hand_verbs(json.loads(hands_label)))
    out.extend([float(hc.get(v,0)) for v in hand_vocab])
    return np.asarray(out,dtype=np.float32)

def build_episode(sh, ep, farmer_vocab, hand_vocab):
    m=sh["meta"]; d=sh["data"]
    a,b=int(ep["start"]),int(ep["end"])
    F=np.asarray(d["current_features"][a:b],dtype=np.float32)
    steps=np.asarray(d["steps"][a:b],dtype=np.int16)
    market=decode(m["vocabs"]["market"],d["market_id"][a:b])
    farmer=decode(m["vocabs"]["farmer"],d["farmer_id"][a:b])
    hands=decode(m["vocabs"]["hands"],d["hands_id"][a:b])
    complete=decode(m["vocabs"]["complete"],d["complete_id"][a:b])

    n=len(F)
    if n==0:
        raise RuntimeError("empty episode")
    parts=[F]
    base_idx=np.arange(n,dtype=np.int32)
    for lag in LAGS:
        idx=np.maximum(0,base_idx-lag)
        LF=F[idx]
        avail=(base_idx>=lag).astype(np.float32)[:,None]
        parts.extend([LF,avail,F-LF])

    ps_dim=len(MARKET_VERBS)+len(farmer_vocab)+len(hand_vocab)
    prev=np.zeros((n,ps_dim),dtype=np.float32)
    cache={}
    for i in range(1,n):
        key=(str(market[i-1]),str(farmer[i-1]),str(hands[i-1]))
        vec=cache.get(key)
        if vec is None:
            vec=prev_summary(key[0],key[1],key[2],farmer_vocab,hand_vocab)
            cache[key]=vec
        prev[i]=vec
    parts.append(prev)

    X=np.concatenate(parts,axis=1).astype(np.float32,copy=False)
    return {
        "X":X,
        "steps":steps,
        "market":np.asarray(market,dtype=object),
        "farmer":np.asarray(farmer,dtype=object),
        "hands":np.asarray(hands,dtype=object),
        "complete":np.asarray(complete,dtype=object),
        "episode":ep,
    }

def fit_component(X,y,name):
    unique=np.unique(y)
    if len(unique)==1:
        return {"kind":"constant","value":str(unique[0]),"name":name}
    model=ExtraTreesClassifier(
        n_estimators=256,
        max_depth=None,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=20260921,
        n_jobs=-1,
    )
    model.fit(X,y)
    return {"kind":"model","model":model,"name":name}

def predict_component(spec,X):
    if spec["kind"]=="constant":
        return np.full(len(X),spec["value"],dtype=object)
    return spec["model"].predict(X)

class EvalStats:
    def __init__(self):
        self.total=0
        self.market=0
        self.farmer=0
        self.hands=0
        self.complete=0
        self.by_source=defaultdict(lambda:[0,0])
        self.by_stage=defaultdict(lambda:[0,0])
        self.episodes=0

    def add(self, epd, pm,pf,ph):
        ym,yf,yh=epd["market"],epd["farmer"],epd["hands"]
        cm=(pm==ym)
        cf=(pf==yf)
        ch=(ph==yh)
        cc=cm & cf & ch
        n=len(cc)
        self.total+=n
        self.market+=int(cm.sum())
        self.farmer+=int(cf.sum())
        self.hands+=int(ch.sum())
        self.complete+=int(cc.sum())
        sha=str(epd["episode"]["main_sha256"])
        self.by_source[sha][0]+=int(cc.sum())
        self.by_source[sha][1]+=n
        for step,ok in zip(epd["steps"],cc):
            bucket=int(step)//120
            self.by_stage[bucket][0]+=int(bool(ok))
            self.by_stage[bucket][1]+=1
        self.episodes+=1

    def result(self):
        if self.total==0:
            return {}
        src={k:v[0]/v[1] for k,v in sorted(self.by_source.items()) if v[1]}
        stage={str(k):v[0]/v[1] for k,v in sorted(self.by_stage.items()) if v[1]}
        return {
            "episodes":self.episodes,
            "turns":self.total,
            "complete_action_parity":self.complete/self.total,
            "market_parity":self.market/self.total,
            "farmer_parity":self.farmer/self.total,
            "hands_parity":self.hands/self.total,
            "by_source_complete_action_parity":src,
            "minimum_source_complete_action_parity":min(src.values()) if src else None,
            "by_120_turn_stage_complete_action_parity":stage,
            "minimum_stage_complete_action_parity":min(stage.values()) if stage else None,
        }

def split_of(ep):
    seed=int(ep["seed"]); rank=int(ep["source_rank"])
    if seed in TRAIN_SEEDS and rank in TRAIN_RANKS:
        return "train"
    if seed in VAL_SEEDS:
        return "validation"
    if seed in HOLD_SEEDS:
        return "holdout"
    return "unused"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()

    shards=load_shards(Path(args.input_dir))
    shard_ids={int(s["meta"].get("shard_index",-1)) for s in shards}
    mechanics=(
        len(shards)==12
        and shard_ids==set(range(12))
        and all(bool(s["meta"].get("mechanical_pass")) for s in shards)
        and all(not s["meta"].get("failures") for s in shards)
    )
    total_eps=sum(len(s["meta"]["episodes"]) for s in shards)
    mechanics=mechanics and total_eps==192

    farmer_vocab,hand_vocab=collect_train_action_vocabs(shards)

    train_X=[]
    train_m=[]
    train_f=[]
    train_h=[]
    split_counts=Counter()
    train_rows_full=0
    train_rows_kept=0

    for sh in shards:
        for ep in sh["meta"]["episodes"]:
            sp=split_of(ep)
            split_counts[sp]+=1
            if sp!="train":
                continue
            epd=build_episode(sh,ep,farmer_vocab,hand_vocab)
            n=len(epd["steps"])
            change=np.zeros(n,dtype=bool)
            if n>1:
                change[1:]=epd["complete"][1:]!=epd["complete"][:-1]
            keep=(epd["steps"]<=16) | ((epd["steps"]%4)==0) | change
            train_rows_full+=n
            train_rows_kept+=int(keep.sum())
            train_X.append(epd["X"][keep])
            train_m.append(epd["market"][keep])
            train_f.append(epd["farmer"][keep])
            train_h.append(epd["hands"][keep])

    if not train_X:
        raise SystemExit("no training rows")

    X=np.concatenate(train_X,axis=0).astype(np.float32,copy=False)
    ym=np.concatenate(train_m)
    yf=np.concatenate(train_f)
    yh=np.concatenate(train_h)

    print("V27C_TRAIN_MATRIX",json.dumps({
        "rows":int(X.shape[0]),"features":int(X.shape[1]),
        "full_training_turns":train_rows_full,
        "kept_training_turns":train_rows_kept,
        "market_classes":int(len(np.unique(ym))),
        "farmer_classes":int(len(np.unique(yf))),
        "hands_classes":int(len(np.unique(yh))),
        "farmer_verb_vocab":farmer_vocab,
        "hand_verb_vocab":hand_vocab,
        "split_episode_counts":dict(split_counts),
    },sort_keys=True),flush=True)

    market_model=fit_component(X,ym,"market")
    farmer_model=fit_component(X,yf,"farmer")
    hands_model=fit_component(X,yh,"hands")

    val=EvalStats()
    hold=EvalStats()
    validation_episodes_expected=24
    holdout_episodes_expected=48

    for sh in shards:
        for ep in sh["meta"]["episodes"]:
            sp=split_of(ep)
            if sp not in ("validation","holdout"):
                continue
            epd=build_episode(sh,ep,farmer_vocab,hand_vocab)
            pm=predict_component(market_model,epd["X"])
            pf=predict_component(farmer_model,epd["X"])
            ph=predict_component(hands_model,epd["X"])
            (val if sp=="validation" else hold).add(epd,pm,pf,ph)

    valr=val.result()
    holdr=hold.result()

    mechanics=(
        mechanics
        and split_counts["train"]==80
        and split_counts["validation"]==validation_episodes_expected
        and split_counts["holdout"]==holdout_episodes_expected
        and valr.get("episodes")==validation_episodes_expected
        and holdr.get("episodes")==holdout_episodes_expected
        and X.shape[1]>0
    )

    gate=(
        mechanics
        and holdr["complete_action_parity"]>=0.90
        and holdr["market_parity"]>=0.94
        and holdr["farmer_parity"]>=0.99
        and holdr["hands_parity"]>=0.98
        and holdr["minimum_source_complete_action_parity"]>=0.80
        and holdr["minimum_stage_complete_action_parity"]>=0.80
    )

    if not mechanics:
        decision="V27C_MECHANICS_INVALID"
    elif gate:
        decision="V27C_HISTORY_POLICY_DISTILLATION_VIABLE"
    else:
        decision="V27C_HISTORY_POLICY_DISTILLATION_NOT_VIABLE"

    outdir=Path(args.out_dir)
    outdir.mkdir(parents=True,exist_ok=True)

    model_bundle={
        "market":market_model,
        "farmer":farmer_model,
        "hands":hands_model,
        "farmer_verb_vocab":farmer_vocab,
        "hand_verb_vocab":hand_vocab,
        "lags":LAGS,
        "market_verbs":MARKET_VERBS,
        "history_window":256,
        "feature_dim":int(X.shape[1]),
        "random_state":20260921,
    }
    joblib.dump(model_bundle,outdir/"V27C_MODELS.joblib",compress=3)

    feature_meta={
        "schema":"kculture-v27c-feature-spec-v1",
        "history_window":256,
        "current_feature_dim":114,
        "lags":list(LAGS),
        "market_verbs":list(MARKET_VERBS),
        "farmer_verb_vocab":farmer_vocab,
        "hand_verb_vocab":hand_vocab,
        "feature_dim":int(X.shape[1]),
        "runtime_identity_features":False,
        "teacher_call_at_inference":False,
    }
    (outdir/"V27C_FEATURE_SPEC.json").write_text(json.dumps(feature_meta,indent=2,sort_keys=True)+"\n")

    result={
        "schema":"kculture-v27c-256-history-behavioral-distillation-v1",
        "mechanical_pass":mechanics,
        "decision":decision,
        "gate_pass":gate,
        "dataset_shards":len(shards),
        "episodes_total":total_eps,
        "split_episode_counts":dict(split_counts),
        "training_turns_full":train_rows_full,
        "training_turns_kept":train_rows_kept,
        "training_feature_dim":int(X.shape[1]),
        "training_classes":{
            "market":int(len(np.unique(ym))),
            "farmer":int(len(np.unique(yf))),
            "hands":int(len(np.unique(yh))),
        },
        "model_family":"ExtraTreesClassifier",
        "model_parameters":{
            "n_estimators":256,
            "max_depth":None,
            "min_samples_leaf":2,
            "max_features":"sqrt",
            "class_weight":"balanced_subsample",
            "random_state":20260921,
            "n_jobs":-1,
        },
        "validation":valr,
        "holdout":holdr,
        "history_window":256,
        "runtime_identity_features":False,
        "teacher_call_at_inference":False,
        "automatic_kaggle_submission":False,
    }
    (outdir/"V27C_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    print("V27C_RESULT",json.dumps({
        "decision":decision,
        "mechanical_pass":mechanics,
        "gate_pass":gate,
        "training_turns_kept":train_rows_kept,
        "feature_dim":int(X.shape[1]),
        "validation":valr,
        "holdout":holdr,
    },sort_keys=True),flush=True)

    if not mechanics:
        raise SystemExit(2)

if __name__=="__main__":
    main()
