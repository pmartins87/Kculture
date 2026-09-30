#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

PAULO="Paulo Martins"
ITEMS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")

def load(pkg,root):
    with tarfile.open(pkg,"r:*") as tf:tf.extractall(root)
    p=Path(root)/"main.py";return get_last_callable(p.read_text(),path=str(p.resolve()))

def tape_agent(actions):
    def f(obs,c=None):
        s=max(0,min(len(actions)-1,int(obs.get("step",0) or 0)));return actions[s]
    return f

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
    p=int(obs["player"]);q=1-p;farms=obs.get("farms") or [{},{}];own=farms[p];opp=farms[q]
    oc,oa,ok=counts(own);qc,qa,qk=counts(opp)
    race=(g.get("_V9_RACE") or {}).get(p) or {}
    try:sim=float(g["_r37_similarity"](obs))
    except Exception:sim=0.0
    vals={"similarity":sim,"lead":float(race.get("lead",-12) or -12),"seat":float(p),
          "own_money":float(own.get("money",0) or 0),"opp_money":float(opp.get("money",0) or 0),
          "money_diff":float(own.get("money",0) or 0)-float(opp.get("money",0) or 0),
          "own_hands":float(len(own.get("hands") or [])),"opp_hands":float(len(opp.get("hands") or [])),
          "hands_diff":float(len(own.get("hands") or []))-float(len(opp.get("hands") or [])),
          "own_quads":float(len(own.get("unlocked_quadrants") or [])),"opp_quads":float(len(opp.get("unlocked_quadrants") or []))}
    for k in CROPS:
        vals["own_crop_"+k]=float(oc[k]);vals["opp_crop_"+k]=float(qc[k]);vals["crop_diff_"+k]=float(oc[k]-qc[k])
    for k in ANIMALS:
        vals["own_animal_"+k]=float(oa[k]);vals["opp_animal_"+k]=float(qa[k]);vals["animal_diff_"+k]=float(oa[k]-qa[k])
    for kind in ("PLANT","PASTURE","COOP"):
        vals["own_kind_"+kind]=float(ok.get(kind,0));vals["opp_kind_"+kind]=float(qk.get(kind,0))
    now=hist[216]
    for lag in (0,24,48):
        s=now if lag==0 else hist[216-lag]
        for it in ITEMS:
            vals[f"inv_{it}_lag{lag}"]=s["inv"][it];vals[f"price_{it}_lag{lag}"]=s["price"][it]
    for it in ITEMS:
        vals[f"inv_delta24_{it}"]=vals[f"inv_{it}_lag0"]-vals[f"inv_{it}_lag24"]
        vals[f"inv_delta48_{it}"]=vals[f"inv_{it}_lag0"]-vals[f"inv_{it}_lag48"]
        vals[f"price_delta24_{it}"]=vals[f"price_{it}_lag0"]-vals[f"price_{it}_lag24"]
    return vals

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--corpus-root",required=True);ap.add_argument("--base-package",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--num-shards",type=int,required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    files=[]
    for label in ("v30b_final","v47_final","v37c"):
        fs=glob.glob(str(Path(a.corpus_root)/label/"replays"/"*-replay.json"))
        def ep(fn):
            try:return int(Path(fn).name.split("-")[1])
            except:return 0
        files += [(label,f) for f in sorted(fs,key=ep,reverse=True)[:25]]
    files=[x for i,x in enumerate(files) if i%a.num_shards==a.shard]
    rows=[]
    for label,fn in files:
        d=json.loads(Path(fn).read_text());names=list((d.get("info") or {}).get("TeamNames") or [])
        if names.count(PAULO)!=1:continue
        seat=names.index(PAULO);opp=1-seat;acts=[d["steps"][t+1][opp].get("action") for t in range(min(217,len(d["steps"])-1))]
        with tempfile.TemporaryDirectory() as td:
            base=load(a.base_package,td);g=base.__globals__;hist={};capt={}
            def me(obs,c=None):
                action=base(obs,c);step=int(obs.get("step",0) or 0);hist[step]=snap(obs)
                if step==216:capt["x"]=features(obs,g,hist)
                return action
            cfg=dict(d.get("configuration") or {});cfg["seed"]=int((d.get("info") or {})["seed"]);cfg["episodeSteps"]=218
            env=make("kaggriculture",configuration=cfg,debug=False);env.run([me,tape_agent(acts)] if seat==0 else [tape_agent(acts),me])
            if "x" not in capt:raise RuntimeError(f"no step216 {fn}")
            # For exact V30B hosted episodes, public/own step216 state should agree on invariant scalar probes.
            parity=None
            if label=="v30b_final":
                ro=d["steps"][216][seat]["observation"];rf=ro["farms"];x=capt["x"]
                parity=(x["own_money"]==float(rf[seat].get("money",0) or 0) and x["opp_money"]==float(rf[opp].get("money",0) or 0)
                        and x["inv_WHEAT_lag0"]==float(ro["market"]["inventory"].get("WHEAT",10000) or 0))
            row={"label":label,"episode_id":int((d.get("info") or {}).get("EpisodeId") or 0),"seat":seat,"opponent":names[opp],"features":capt["x"],"step216_parity":parity}
            rows.append(row);print("V45_FEATURE",json.dumps({"label":label,"episode":row["episode_id"],"parity":parity,"similarity":capt["x"]["similarity"],"lead":capt["x"]["lead"]},sort_keys=True),flush=True)
    Path(a.output).write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
