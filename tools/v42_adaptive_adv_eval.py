#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,math,statistics,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

PAULO="Paulo Martins"
LOOKS=(0,4,8,12)
ADV_ITEMS=("STRAWBERRY","WOOL","EGG","MILK","MELON","CARROT","TOMATO")

def load_agent(pkg,root):
    with tarfile.open(pkg,"r:*") as tf:tf.extractall(root)
    p=Path(root)/"main.py"
    return get_last_callable(p.read_text(encoding="utf-8"),path=str(p.resolve()))

def tape_agent(actions):
    def agent(obs,config=None):
        s=max(0,min(len(actions)-1,int(obs.get("step",0) or 0)))
        return actions[s]
    return agent

def points(m): return 1.0 if m>0 else 0.5 if m==0 else 0.0

def gate_features(obs,g):
    p=int(obs["player"])
    race=(g.get("_V9_RACE") or {}).get(p) or {}
    try: sim=float(g["_r37_similarity"](obs))
    except Exception: sim=0.0
    lead=float(race.get("lead",-12) or -12)
    return {"similarity":sim,"lead":lead}

def future_orders(g,player,step,look):
    native=g["_IMPL"].chassis.players.get(player)
    if not native or native.get("route") not in g["_IMPL"].chassis.routes:return []
    route=native["route"];out=[];first=None
    for off in range(1,look+1):
        t=step+off
        if t>718:break
        tape=g["_IMPL"].chassis.routes[2 if t>=648 else route]
        for o in (tape[t].get("market") or []):
            if not o or len(o)<3:continue
            if first is None:first=o
            if o[0]=="SELL" and o[1] in ADV_ITEMS:
                try:q=max(0,int(o[2]))
                except Exception:q=0
                if q>0:out.append((t,o[1],q))
    protected=first[1] if first is not None and first[0]=="SELL" else None
    return [(t,i,q) for t,i,q in out if i!=protected]

def apply_adv(obs,action,g,look,stats):
    step=int(obs["step"]);player=int(obs["player"])
    if look<=0 or step<216 or step>=718 or step%24==23:return action
    plan=future_orders(g,player,step,look)
    if not plan:return action
    market=[list(o) for o in (action.get("market") or [])]
    if any(len(o)>1 and o[0]=="BUY_PRODUCT" for o in market):return action
    stock=g["projected_shed"](action,g["FarmView"](obs))
    selling={}
    for o in market:
        if len(o)>=3 and o[0]=="SELL":
            selling[o[1]]=selling.get(o[1],0)+max(0,int(o[2]))
    commands=[action.get("farmer") or ["PASS"],*(action.get("hands") or [])]
    picked={c[1] for c in commands if len(c)>1 and c[0]=="PICKUP"}
    prices=obs["market"]["prices"];extra=[];added=0
    for item in sorted({it for _,it,_ in plan},key=lambda it:-int(prices.get(it,0))):
        if item in picked or int(prices.get(item,0))<2:continue
        avail=int(stock.get(item,0))-selling.get(item,0)
        if avail<1:continue
        hit=next((o for o in market if len(o)>=3 and o[0]=="SELL" and o[1]==item),None)
        if hit is None and len(market)+len(extra)>=10:continue
        n=0
        for t,it,q in plan:
            if it!=item or avail<=0:continue
            take=min(q,avail);n+=take;avail-=take
        if n<1:continue
        if hit is not None:hit[2]=int(hit[2])+n
        else:extra.append(["SELL",item,n])
        added+=n
    if not added:return action
    stats["fires"]+=1;stats["units"]+=added
    return dict(action,market=(extra+market)[:10])

def run_one(pkg,replay,seat,look):
    steps=replay["steps"];opp=1-seat
    opp_actions=[steps[t+1][opp].get("action") for t in range(len(steps)-1)]
    with tempfile.TemporaryDirectory() as td:
        base=load_agent(pkg,td);g=base.__globals__
        st={"active":False,"decided":False,"features":{},"fires":0,"units":0,"errors":0}
        def me(obs,conf=None):
            action=base(obs,conf)
            step=int(obs.get("step",0) or 0)
            if step==216 and not st["decided"]:
                f=gate_features(obs,g);st["features"]=f;st["decided"]=True
                st["active"]=bool(f["similarity"]>=0.95 or f["lead"]>=4.0)
            if look and st["active"]:
                try:action=apply_adv(obs,action,g,look,st)
                except Exception:st["errors"]+=1
            return action
        cfg=dict(replay.get("configuration") or {});cfg["seed"]=int((replay.get("info") or {})["seed"])
        env=make("kaggriculture",configuration=cfg,debug=False)
        env.run([me,tape_agent(opp_actions)] if seat==0 else [tape_agent(opp_actions),me])
        rep=env.toJSON();statuses=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])]
        if statuses!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw):raise RuntimeError((statuses,rw))
        mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
        return mine,other,st

def select_files(root,max_per_label):
    out=[]
    for label in ("v30b_final","v47_final","v37c"):
        fs=glob.glob(str(Path(root)/label/"replays"/"*-replay.json"))
        def ep(fn):
            try:return int(Path(fn).name.split("-")[1])
            except:return 0
        for f in sorted(fs,key=ep,reverse=True)[:max_per_label]:out.append((label,f))
    return out

def eval_shard(a):
    rows=[]
    files=[x for i,x in enumerate(select_files(a.corpus_root,a.max_per_label)) if i%a.num_shards==a.shard]
    for label,fn in files:
        d=json.loads(Path(fn).read_text());names=list((d.get("info") or {}).get("TeamNames") or [])
        if names.count(PAULO)!=1:continue
        seat=names.index(PAULO);opp=names[1-seat];hosted=d.get("rewards") or [x.get("reward") for x in d["steps"][-1]]
        hm,ho=(float(hosted[seat]),float(hosted[1-seat]))
        arms={}
        for look in LOOKS:
            m,o,st=run_one(a.base_package,d,seat,look)
            arms[str(look)]={"mine":m,"other":o,"margin":m-o,"points":points(m-o),"active":st["active"],"fires":st["fires"],"units":st["units"],"errors":st["errors"],"features":st["features"]}
        parity=True
        if label=="v30b_final":parity=(arms["0"]["mine"]==hm and arms["0"]["other"]==ho)
        row={"label":label,"episode_id":int((d.get("info") or {}).get("EpisodeId") or 0),"opponent":opp,"seat":seat,"parity":parity,"arms":arms}
        rows.append(row)
        print("V42_ADV",json.dumps({"label":label,"episode":row["episode_id"],"opponent":opp,"parity":parity,"arms":{k:{"m":v["margin"],"a":v["active"],"f":v["fires"]} for k,v in arms.items()}},sort_keys=True),flush=True)
    Path(a.output).write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")

def met(rows,look):
    a=[r["arms"][str(look)] for r in rows]
    return {"n":len(a),"points":sum(x["points"] for x in a),"rate":sum(x["points"] for x in a)/len(a) if a else 0,
            "mean_margin":statistics.mean(x["margin"] for x in a) if a else 0,
            "fires":sum(x["fires"] for x in a),"fire_games":sum(x["fires"]>0 for x in a),"errors":sum(x["errors"] for x in a)}

def train(a):
    rows=[]
    for fn in glob.glob(str(Path(a.shards_dir)/"*.json")):rows+=json.loads(Path(fn).read_text())
    p=[r for r in rows if r["label"]=="v30b_final"];parity=sum(r["parity"] for r in p)
    if parity!=len(p):raise SystemExit(f"baseline parity failed {parity}/{len(p)}")
    tr=[];ho=[]
    for label in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==label],key=lambda r:r["episode_id"],reverse=True)
        k=min(a.holdout_per_label,max(1,len(rr)//4));ho+=rr[:k];tr+=rr[k:]
    base_tr=met(tr,0);base_ho=met(ho,0)
    choices=[]
    for look in (4,8,12):
        m=met(tr,look);choices.append((m["points"]-base_tr["points"],m["mean_margin"]-base_tr["mean_margin"],look,m))
    choices.sort(reverse=True);look=choices[0][2];mtr=choices[0][3];mho=met(ho,look)
    lw=wl=0
    for r in ho:
        b=r["arms"]["0"];x=r["arms"][str(look)]
        if b["points"]==0 and x["points"]==1:lw+=1
        if b["points"]==1 and x["points"]==0:wl+=1
    train_delta=mtr["rate"]-base_tr["rate"];hold_delta=mho["rate"]-base_ho["rate"];md=mho["mean_margin"]-base_ho["mean_margin"]
    passed=(train_delta>=0.02 and hold_delta>=0.04 and lw>=wl+1 and mho["errors"]==0 and mho["fire_games"]>=2 and md>-750)
    out={"decision":"V42_ADAPTIVE_ADV_GATE_PASS" if passed else "V42_ADAPTIVE_ADV_GATE_FAIL","rows":len(rows),"v30b_parity":f"{parity}/{len(p)}","chosen_look":look,
         "gate":{"similarity":0.95,"lead":4.0},"train_base":base_tr,"train_candidate":mtr,"holdout_base":base_ho,"holdout_candidate":mho,
         "train_score_delta":train_delta,"holdout_score_delta":hold_delta,"holdout_mean_margin_delta":md,"loss_to_win_flips":lw,"win_to_loss_flips":wl,
         "all_look_train":[{"look":x[2],"points_delta":x[0],"mean_margin_delta":x[1]} for x in choices]}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("V42_MODEL",json.dumps(out,sort_keys=True))
    if not passed:raise SystemExit(7)

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    e=sp.add_parser("eval");e.add_argument("--corpus-root",required=True);e.add_argument("--base-package",required=True);e.add_argument("--shard",type=int,required=True);e.add_argument("--num-shards",type=int,required=True);e.add_argument("--max-per-label",type=int,default=25);e.add_argument("--output",required=True)
    t=sp.add_parser("train");t.add_argument("--shards-dir",required=True);t.add_argument("--holdout-per-label",type=int,default=5);t.add_argument("--output",required=True)
    a=ap.parse_args();eval_shard(a) if a.cmd=="eval" else train(a)
if __name__=="__main__":main()
