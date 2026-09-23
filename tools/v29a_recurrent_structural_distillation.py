#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
import math
import os
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

TRAIN_SEEDS={79901,79902,79903,79904,79905}
TRAIN_RANKS={1,2,4,5,6,7,9,10}
VAL_SEEDS={79906}
HOLD_SEEDS={79907,79908}
MARKET_SLOTS=10
SEED=20260923

def jkey(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def split_of(ep):
    seed=int(ep["seed"]);rank=int(ep["source_rank"])
    if seed in TRAIN_SEEDS and rank in TRAIN_RANKS:return "train"
    if seed in VAL_SEEDS:return "validation"
    if seed in HOLD_SEEDS:return "holdout"
    return "unused"

def load_shards(root):
    out=[]
    for mp in sorted(Path(root).rglob("META.json")):
        try:m=json.loads(mp.read_text())
        except Exception:continue
        if m.get("schema")!="kculture-v27c2-structural-dataset-shard-v1":continue
        d=np.load(mp.parent/"DATA.npz",allow_pickle=False)
        out.append({"meta":m,"data":d,"path":mp.parent})
    return out

def decode_local(vocab,ids):
    vv=np.asarray(vocab,dtype=object)
    return vv[np.asarray(ids,dtype=np.int64)]

def ep_arrays(sh,ep):
    d=sh["data"]
    ts,te=int(ep["turn_start"]),int(ep["turn_end"])
    us,ue=int(ep["unit_start"]),int(ep["unit_end"])
    g=np.asarray(d["turn_global"][ts:te,:114],dtype=np.float32)
    steps=np.asarray(d["steps"][ts:te],dtype=np.int16)
    local=np.asarray(d["unit_local"][us:ue],dtype=np.float32)
    uturn=np.asarray(d["unit_turn_index"][us:ue],dtype=np.int64)-ts
    actor=np.asarray(d["unit_actor_index"][us:ue],dtype=np.int64)
    uid=np.asarray(d["unit_label_id"][us:ue],dtype=np.int64)
    msid=np.asarray(d["market_slot_label_id"][ts:te],dtype=np.int64)
    return g,steps,local,uturn,actor,uid,msid

def build_global_vocabs(shards):
    unit=set();market=set()
    for sh in shards:
        m=sh["meta"];d=sh["data"]
        uv=m["vocabs"]["unit"];mv=m["vocabs"]["market_slot"]
        for ep in m["episodes"]:
            if split_of(ep)!="train":continue
            _,_,_,_,_,uid,msid=ep_arrays(sh,ep)
            unit.update(str(x) for x in decode_local(uv,uid))
            market.update(str(x) for x in decode_local(mv,msid.reshape(-1)))
    unit_vocab=sorted(unit);market_vocab=sorted(market)
    return unit_vocab,market_vocab

def attach_maps(shards,unit_vocab,market_vocab):
    um={x:i for i,x in enumerate(unit_vocab)}
    mm={x:i for i,x in enumerate(market_vocab)}
    for sh in shards:
        sh["unit_map"]=np.asarray([um.get(str(x),-1) for x in sh["meta"]["vocabs"]["unit"]],dtype=np.int64)
        sh["market_map"]=np.asarray([mm.get(str(x),-1) for x in sh["meta"]["vocabs"]["market_slot"]],dtype=np.int64)

def streaming_stats(shards):
    g_sum=np.zeros(114,dtype=np.float64);g_sq=np.zeros(114,dtype=np.float64);g_n=0
    l_sum=np.zeros(104,dtype=np.float64);l_sq=np.zeros(104,dtype=np.float64);l_n=0
    for sh in shards:
        for ep in sh["meta"]["episodes"]:
            if split_of(ep)!="train":continue
            g,_,local,_,_,_,_=ep_arrays(sh,ep)
            g64=g.astype(np.float64,copy=False);l64=local.astype(np.float64,copy=False)
            g_sum+=g64.sum(0);g_sq+=(g64*g64).sum(0);g_n+=len(g64)
            l_sum+=l64.sum(0);l_sq+=(l64*l64).sum(0);l_n+=len(l64)
    gm=g_sum/g_n;lm=l_sum/l_n
    gs=np.sqrt(np.maximum(g_sq/g_n-gm*gm,1e-8))
    ls=np.sqrt(np.maximum(l_sq/l_n-lm*lm,1e-8))
    gs[gs<1e-4]=1.0;ls[ls<1e-4]=1.0
    return gm.astype(np.float32),gs.astype(np.float32),lm.astype(np.float32),ls.astype(np.float32)

class Model(nn.Module):
    def __init__(self,n_unit,n_market):
        super().__init__()
        self.gru=nn.GRU(input_size=114,hidden_size=64,num_layers=1,batch_first=True)
        self.unit=nn.Sequential(nn.Linear(64+104,64),nn.ReLU(),nn.Linear(64,n_unit))
        self.market=nn.Sequential(nn.Linear(64+10,64),nn.ReLU(),nn.Linear(64,n_market))
    def encode(self,g):
        h,_=self.gru(g)
        return h
    def unit_logits(self,h,local,turn_idx):
        return self.unit(torch.cat([h[0,turn_idx],local],dim=1))
    def market_logits(self,h):
        T=h.shape[1]
        hh=h[0].repeat_interleave(MARKET_SLOTS,dim=0)
        slots=torch.eye(MARKET_SLOTS,device=h.device,dtype=h.dtype).repeat(T,1)
        return self.market(torch.cat([hh,slots],dim=1))

class EvalStats:
    def __init__(self):
        self.turns=0;self.farmer=0;self.hands=0;self.market=0;self.complete=0
        self.unit_samples=0;self.unit_correct=0;self.market_slots=0;self.market_slot_correct=0
        self.unseen_unit=0;self.unseen_market=0
        self.by_source=defaultdict(lambda:[0,0]);self.by_stage=defaultdict(lambda:[0,0]);self.episodes=0
    def add(self,sha,steps,farmer_ok,hands_ok,market_ok,unit_correct,unit_total,slot_correct,slot_total,unseen_u,unseen_m):
        complete=farmer_ok & hands_ok & market_ok
        n=len(complete);self.turns+=n;self.episodes+=1
        self.farmer+=int(farmer_ok.sum());self.hands+=int(hands_ok.sum());self.market+=int(market_ok.sum());self.complete+=int(complete.sum())
        self.unit_correct+=int(unit_correct);self.unit_samples+=int(unit_total)
        self.market_slot_correct+=int(slot_correct);self.market_slots+=int(slot_total)
        self.unseen_unit+=int(unseen_u);self.unseen_market+=int(unseen_m)
        self.by_source[sha][0]+=int(complete.sum());self.by_source[sha][1]+=n
        for st,ok in zip(steps,complete):
            b=int(st)//120
            self.by_stage[b][0]+=int(bool(ok));self.by_stage[b][1]+=1
    def result(self):
        src={k:v[0]/v[1] for k,v in sorted(self.by_source.items()) if v[1]}
        stage={str(k):v[0]/v[1] for k,v in sorted(self.by_stage.items()) if v[1]}
        return {
          "episodes":self.episodes,"turns":self.turns,
          "unit_sample_accuracy":self.unit_correct/self.unit_samples if self.unit_samples else None,
          "market_slot_accuracy":self.market_slot_correct/self.market_slots if self.market_slots else None,
          "farmer_parity":self.farmer/self.turns if self.turns else None,
          "hands_parity":self.hands/self.turns if self.turns else None,
          "market_parity":self.market/self.turns if self.turns else None,
          "complete_action_parity":self.complete/self.turns if self.turns else None,
          "by_source_complete_action_parity":src,
          "minimum_source_complete_action_parity":min(src.values()) if src else None,
          "by_120_turn_stage_complete_action_parity":stage,
          "minimum_stage_complete_action_parity":min(stage.values()) if stage else None,
          "unseen_unit_truth_labels":self.unseen_unit,
          "unseen_market_slot_truth_labels":self.unseen_market,
        }

def tensor(x,device):
    return torch.as_tensor(x,device=device)

def evaluate(model,shards,split,gm,gs,lm,ls,unit_vocab,market_vocab,device):
    stats=EvalStats();model.eval()
    with torch.no_grad():
      for sh in shards:
        m=sh["meta"];d=sh["data"]
        for ep in m["episodes"]:
            if split_of(ep)!=split:continue
            g,steps,local,uturn,actor,uid_local,msid_local=ep_arrays(sh,ep)
            ug=sh["unit_map"][uid_local]
            mg=sh["market_map"][msid_local]
            gn=(g-gm)/gs;ln=(local-lm)/ls
            gt=tensor(gn[None,...],device).float();lt=tensor(ln,device).float();tt=tensor(uturn,device).long()
            h=model.encode(gt)
            up=model.unit_logits(h,lt,tt).argmax(1).cpu().numpy()
            mp=model.market_logits(h).argmax(1).cpu().numpy().reshape((len(g),MARKET_SLOTS))

            pred_unit=[unit_vocab[int(x)] for x in up]
            true_farmer=decode_local(m["vocabs"]["farmer"],d["farmer_id"][int(ep["turn_start"]):int(ep["turn_end"])])
            true_hands=decode_local(m["vocabs"]["hands"],d["hands_id"][int(ep["turn_start"]):int(ep["turn_end"])])
            true_market=decode_local(m["vocabs"]["market"],d["market_id"][int(ep["turn_start"]):int(ep["turn_end"])])

            pred_farmer=[None]*len(g);pred_hands=[None]*len(g)
            for t in range(len(g)):
                idx=np.flatnonzero(uturn==t)
                order=idx[np.argsort(actor[idx])]
                labs=[pred_unit[i] for i in order]
                pred_farmer[t]=labs[0]
                pred_hands[t]=jkey([json.loads(x) for x in labs[1:]])

            pred_market=[]
            for row in mp:
                orders=[]
                for cid in row:
                    lab=market_vocab[int(cid)]
                    if lab=="<NONE>":break
                    orders.append(json.loads(lab))
                pred_market.append(jkey(orders))

            farmer_ok=np.asarray(pred_farmer,dtype=object)==true_farmer
            hands_ok=np.asarray(pred_hands,dtype=object)==true_hands
            market_ok=np.asarray(pred_market,dtype=object)==true_market

            unit_seen=ug>=0
            unit_correct=int(np.sum(unit_seen & (up==np.maximum(ug,0))))
            mflat=mg.reshape(-1);pflat=mp.reshape(-1);mseen=mflat>=0
            slot_correct=int(np.sum(mseen & (pflat==np.maximum(mflat,0))))
            stats.add(
              str(ep["main_sha256"]),steps,farmer_ok,hands_ok,market_ok,
              unit_correct,len(ug),slot_correct,len(mflat),
              int(np.sum(~unit_seen)),int(np.sum(~mseen))
            )
    return stats.result()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()

    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
    try:torch.use_deterministic_algorithms(True)
    except Exception:pass
    device=torch.device("cpu")

    shards=load_shards(args.input_dir)
    shard_ids={int(s["meta"].get("shard_index",-1)) for s in shards}
    mechanics=(len(shards)==12 and shard_ids==set(range(12)) and all(s["meta"].get("mechanical_pass") for s in shards) and all(not s["meta"].get("failures") for s in shards))
    total_eps=sum(len(s["meta"]["episodes"]) for s in shards)
    mechanics=mechanics and total_eps==192

    unit_vocab,market_vocab=build_global_vocabs(shards)
    attach_maps(shards,unit_vocab,market_vocab)
    gm,gs,lm,ls=streaming_stats(shards)

    train_eps=[(sh,ep) for sh in shards for ep in sh["meta"]["episodes"] if split_of(ep)=="train"]
    val_eps=sum(split_of(ep)=="validation" for sh in shards for ep in sh["meta"]["episodes"])
    hold_eps=sum(split_of(ep)=="holdout" for sh in shards for ep in sh["meta"]["episodes"])
    mechanics=mechanics and len(train_eps)==80 and val_eps==24 and hold_eps==48

    model=Model(len(unit_vocab),len(market_vocab)).to(device)
    params=sum(p.numel() for p in model.parameters())
    opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4)

    history=[]
    t0=time.time()
    if mechanics:
      for epoch in range(8):
        model.train()
        order=list(range(len(train_eps)))
        random.Random(SEED+epoch).shuffle(order)
        losses=[];ulosses=[];mlosses=[]
        for oi in order:
            sh,ep=train_eps[oi]
            g,_,local,uturn,actor,uid_local,msid_local=ep_arrays(sh,ep)
            uy=sh["unit_map"][uid_local];my=sh["market_map"][msid_local].reshape(-1)
            if np.any(uy<0) or np.any(my<0):
                raise RuntimeError("training label absent from frozen training vocabulary")
            gn=(g-gm)/gs;ln=(local-lm)/ls
            gt=tensor(gn[None,...],device).float();lt=tensor(ln,device).float();tt=tensor(uturn,device).long()
            uyt=tensor(uy,device).long();myt=tensor(my,device).long()
            opt.zero_grad(set_to_none=True)
            h=model.encode(gt)
            ulog=model.unit_logits(h,lt,tt)
            mlog=model.market_logits(h)
            ul=F.cross_entropy(ulog,uyt,reduction="none")
            uw=torch.where(tensor(actor,device).long()==0,torch.tensor(3.0,device=device),torch.tensor(1.0,device=device))
            ul=(ul*uw).sum()/uw.sum()
            ml=F.cross_entropy(mlog,myt,reduction="none")
            none_id=market_vocab.index("<NONE>") if "<NONE>" in market_vocab else -1
            mw=torch.where(myt==none_id,torch.tensor(1.0,device=device),torch.tensor(2.0,device=device))
            ml=(ml*mw).sum()/mw.sum()
            loss=ul+ml
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            opt.step()
            losses.append(float(loss.detach()));ulosses.append(float(ul.detach()));mlosses.append(float(ml.detach()))
        row={"epoch":epoch+1,"loss":float(np.mean(losses)),"unit_loss":float(np.mean(ulosses)),"market_loss":float(np.mean(mlosses))}
        history.append(row)
        print("V29A_EPOCH",json.dumps(row,sort_keys=True),flush=True)

    train_seconds=time.time()-t0
    validation=evaluate(model,shards,"validation",gm,gs,lm,ls,unit_vocab,market_vocab,device) if mechanics else {}
    holdout=evaluate(model,shards,"holdout",gm,gs,lm,ls,unit_vocab,market_vocab,device) if mechanics else {}

    strong=False;eligible=False
    if mechanics:
        strong=(
          holdout["complete_action_parity"]>=.90 and holdout["market_parity"]>=.94 and
          holdout["farmer_parity"]>=.99 and holdout["hands_parity"]>=.98 and
          holdout["minimum_source_complete_action_parity"]>=.80 and
          holdout["minimum_stage_complete_action_parity"]>=.80
        )
        eligible=(
          holdout["complete_action_parity"]>=.80 and holdout["market_parity"]>=.88 and
          holdout["farmer_parity"]>=.97 and holdout["hands_parity"]>=.90 and
          holdout["minimum_source_complete_action_parity"]>=.70 and
          holdout["minimum_stage_complete_action_parity"]>=.70
        )

    if not mechanics:decision="V29A_MECHANICS_INVALID"
    elif strong:decision="V29A_RECURRENT_STRUCTURAL_OFFLINE_STRONG_PASS"
    elif eligible:decision="V29A_RECURRENT_STRUCTURAL_CAUSAL_ELIGIBLE"
    else:decision="V29A_RECURRENT_STRUCTURAL_DISTILLATION_FAIL"

    outdir=Path(args.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    torch.save({
      "schema":"kculture-v29a-recurrent-structural-model-v1",
      "state_dict":model.state_dict(),
      "global_mean":gm,"global_std":gs,"local_mean":lm,"local_std":ls,
      "unit_vocab":unit_vocab,"market_vocab":market_vocab,
      "hidden_size":64,"unit_local_dim":104,"market_slots":10,
      "runtime_identity_features":False,"teacher_call_at_inference":False,
    },outdir/"V29A_MODEL.pt")

    result={
      "schema":"kculture-v29a-recurrent-structural-distillation-v1",
      "mechanical_pass":bool(mechanics),"decision":decision,
      "strong_pass":bool(strong),"causal_eligible":bool(eligible or strong),
      "dataset_shards":len(shards),"episodes_total":total_eps,
      "split_episode_counts":{"train":len(train_eps),"validation":val_eps,"holdout":hold_eps},
      "unit_classes":len(unit_vocab),"market_slot_classes":len(market_vocab),
      "model_parameters":int(params),"epochs":8,"seed":SEED,
      "training_seconds":train_seconds,"training_history":history,
      "validation":validation,"holdout":holdout,
      "runtime_identity_features":False,"teacher_call_at_inference":False,
      "automatic_kaggle_submission":False,
    }
    (outdir/"V29A_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V29A_RESULT",json.dumps({
      "mechanical_pass":mechanics,"decision":decision,"strong_pass":strong,
      "causal_eligible":eligible or strong,"unit_classes":len(unit_vocab),
      "market_slot_classes":len(market_vocab),"model_parameters":params,
      "training_seconds":train_seconds,"validation":validation,"holdout":holdout
    },sort_keys=True),flush=True)
    if not mechanics:raise SystemExit(2)

if __name__=="__main__":
    main()
