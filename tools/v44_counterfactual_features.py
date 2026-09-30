#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,math,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

PAULO="Paulo Martins"
ITEMS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")

def load(pkg,root):
    with tarfile.open(pkg,"r:*") as tf:tf.extractall(root)
    p=Path(root)/"main.py"
    return get_last_callable(p.read_text(encoding="utf-8"),path=str(p.resolve()))

def tape_agent(actions):
    def agent(obs,config=None):
        s=max(0,min(len(actions)-1,int(obs.get("step",0) or 0)))
        return actions[s]
    return agent

def counts(farm):
    c={k:0 for k in CROPS};a={k:0 for k in ANIMALS};kinds={}
    for row in (farm.get("tiles") or []):
        for t in row:
            if not isinstance(t,dict):continue
            x=t.get("crop");y=t.get("animal");z=t.get("kind")
            if x in c:c[x]+=1
            if y in a:a[y]+=1
            if z:kinds[z]=kinds.get(z,0)+1
    return c,a,kinds

def snap(obs):
    market=obs.get("market") or {};inv=market.get("inventory") or {};pr=market.get("prices") or {}
    return {"inv":{i:float(inv.get(i,10000) or 0) for i in ITEMS},"price":{i:float(pr.get(i,0) or 0) for i in ITEMS}}

def features(obs,g,hist):
    p=int(obs["player"]);q=1-p;farms=obs.get("farms") or [{},{}]
    own=farms[p];other=farms[q];oc,oa,ok=counts(own);qc,qa,qk=counts(other)
    race=(g.get("_V9_RACE") or {}).get(p) or {}
    try:sim=float(g["_r37_similarity"](obs))
    except Exception:sim=0.0
    v={
      "similarity":sim,"lead":float(race.get("lead",-12) or -12),"seat":float(p),
      "own_money":float(own.get("money",0) or 0),"opp_money":float(other.get("money",0) or 0),
      "money_diff":float(own.get("money",0) or 0)-float(other.get("money",0) or 0),
      "own_hands":float(len(own.get("hands") or [])),"opp_hands":float(len(other.get("hands") or [])),
      "hands_diff":float(len(own.get("hands") or []))-float(len(other.get("hands") or [])),
      "own_quads":float(len(own.get("unlocked_quadrants") or [])),"opp_quads":float(len(other.get("unlocked_quadrants") or [])),
    }
    for k in CROPS:
        v["own_crop_"+k]=float(oc[k]);v["opp_crop_"+k]=float(qc[k]);v["crop_diff_"+k]=float(oc[k]-qc[k])
    for k in ANIMALS:
        v["own_animal_"+k]=float(oa[k]);v["opp_animal_"+k]=float(qa[k]);v["animal_diff_"+k]=float(oa[k]-qa[k])
    for kind in ("PLANT","PASTURE","COOP"):
        v["own_kind_"+kind]=float(ok.get(kind,0));v["opp_kind_"+kind]=float(qk.get(kind,0))
    now=hist[216]
    for lag in (0,24,48):
        ss=hist[216-lag]
        for it in ITEMS:
            v[f"inv_{it}_lag{lag}"]=ss["inv"][it];v[f"price_{it}_lag{lag}"]=ss["price"][it]
    for it in ITEMS:
        v[f"inv_delta24_{it}"]=v[f"inv_{it}_lag0"]-v[f"inv_{it}_lag24"]
        v[f"inv_delta48_{it}"]=v[f"inv_{it}_lag0"]-v[f"inv_{it}_lag48"]
        v[f"price_delta24_{it}"]=v[f"price_{it}_lag0"]-v[f"price_{it}_lag24"]
    return v

def select(root,cap):
    out=[]
    for label in ("v30b_final","v47_final","v37c"):
        fs=glob.glob(str(Path(root)/label/"replays"/"*-replay.json"))
        def ep(fn):
            try:return int(Path(fn).name.split("-")[1])
            except:return 0
        out += [(label,x) for x in sorted(fs,key=ep,reverse=True)[:cap]]
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--corpus-root",required=True);ap.add_argument("--base-package",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--num-shards",type=int,required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    todo=[x for i,x in enumerate(select(a.corpus_root,25)) if i%a.num_shards==a.shard];rows=[]
    for label,fn in todo:
        d=json.loads(Path(fn).read_text());names=(d.get("info") or {}).get("TeamNames") or []
        if names.count(PAULO)!=1:continue
        seat=names.index(PAULO);opp=1-seat;acts=[d["steps"][t+1][opp].get("action") for t in range(len(d["steps"])-1)]
        hist={};rec={"x":None}
        with tempfile.TemporaryDirectory() as td:
            me0=load(a.base_package,td);g=me0.__globals__
            def me(obs,conf=None):
                action=me0(obs,conf);step=int(obs.get("step",0) or 0)
                if step in (168,192,216):hist[step]=snap(obs)
                if step==216:
                    rec["x"]=features(obs,g,hist)
                return action
            cfg=dict(d.get("configuration") or {});cfg["seed"]=int((d.get("info") or {})["seed"])
            env=make("kaggriculture",configuration=cfg,debug=False);env.run([me,tape_agent(acts)] if seat==0 else [tape_agent(acts),me])
            rw=[float(x) for x in env.toJSON().get("rewards",[])];mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
        row={"label":label,"episode_id":int((d.get("info") or {}).get("EpisodeId") or 0),"seat":seat,"opponent":names[opp],"margin":mine-other,"x":rec["x"]}
        if rec["x"] is None:raise SystemExit(f"missing features {row['episode_id']}")
        rows.append(row);print("V44_CF_FEATURE",json.dumps({"episode":row["episode_id"],"label":label,"margin":row["margin"],"root":{k:rec["x"][k] for k in ("inv_delta48_WHEAT","opp_money","similarity","price_WOOL_lag48")}},sort_keys=True),flush=True)
    Path(a.output).write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
