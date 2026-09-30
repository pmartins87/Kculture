#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,math,statistics,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

PAULO="Paulo Martins"
HORIZONS=(12,24,36,44)
ITEMS=("MILK","WOOL","STRAWBERRY","EGG","MELON","CARROT","TOMATO","WHEAT")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")

def load_agent(pkg,root):
    with tarfile.open(pkg,"r:*") as tf: tf.extractall(root)
    p=Path(root)/"main.py"
    return get_last_callable(p.read_text(encoding="utf-8"),path=str(p.resolve()))

def tile_features(farm):
    crop={k:0 for k in CROPS}; animal={k:0 for k in ANIMALS}; structures=0
    tiles=farm.get("tiles") or []
    for row in tiles:
        for t in row:
            if not isinstance(t,dict): continue
            c=t.get("crop"); a=t.get("animal")
            if c in crop: crop[c]+=1
            if a in animal: animal[a]+=1
            if t.get("kind") in ("PLANT","PASTURE","COOP"): structures+=1
    return crop,animal,structures

def struct_similarity(a,b):
    same=0; seen=0
    ta=a.get("tiles") or []; tb=b.get("tiles") or []
    for y in range(min(len(ta),len(tb))):
        for x in range(min(len(ta[y]),len(tb[y]))):
            aa,bb=ta[y][x],tb[y][x]
            if not isinstance(aa,dict) and not isinstance(bb,dict): continue
            seen+=1
            def key(t):
                if not isinstance(t,dict): return None
                return (t.get("kind"),t.get("crop"),t.get("animal"))
            same+= key(aa)==key(bb)
    return same/seen if seen else 0.0

def snapshot_features(obs,g):
    p=int(obs["player"]); q=1-p
    farms=obs.get("farms") or [{},{}]
    own,opp=farms[p],farms[q]
    rc=(g.get("_V9_RACE") or {}).get(p) or {}
    rr=g.get("_V9_RACE_REPORT") or {}
    try: sim=float(g["_r37_similarity"](obs))
    except Exception: sim=0.0
    oc,oa,os=tile_features(own); qc,qa,qs=tile_features(opp)
    f={
      "similarity":sim,
      "lead":float(rc.get("lead",-12) or -12),
      "rival_sales":float(rr.get("rival_sales",0) or 0),
      "lead_events":float(rr.get("leads",0) or 0),
      "money_diff":float(own.get("money",0) or 0)-float(opp.get("money",0) or 0),
      "opp_money":float(opp.get("money",0) or 0),
      "struct_similarity":struct_similarity(own,opp),
      "structure_diff":float(os-qs),
      "quadrant_diff":float(len(own.get("unlocked_quadrants") or [])-len(opp.get("unlocked_quadrants") or [])),
    }
    for k in CROPS: f["opp_crop_"+k]=float(qc[k])
    for k in ANIMALS: f["opp_animal_"+k]=float(qa[k])
    inv=(obs.get("market") or {}).get("inventory") or {}
    for k in ITEMS: f["market_"+k]=float(inv.get(k,10000) or 0)-10000.0
    return f

def tape_agent(actions):
    def agent(obs,config=None):
        s=max(0,min(len(actions)-1,int(obs.get("step",0) or 0)))
        return actions[s]
    return agent

def run_one(pkg,replay,seat,horizon):
    steps=replay["steps"]; opp=1-seat
    opp_actions=[steps[t+1][opp].get("action") for t in range(len(steps)-1)]
    with tempfile.TemporaryDirectory() as td:
        base=load_agent(pkg,td); g=base.__globals__; rec={"features":None}
        def me(obs,conf=None):
            step=int(obs.get("step",0) or 0)
            if step==0:
                g["V9_RACE_DEFAULT"]=44
            if step==216:
                rec["features"]=snapshot_features(obs,g)
            if step>=216:
                g["V9_RACE_DEFAULT"]=int(horizon)
            return base(obs,conf)
        cfg=dict(replay.get("configuration") or {})
        cfg["seed"]=int((replay.get("info") or {})["seed"])
        env=make("kaggriculture",configuration=cfg,debug=False)
        env.run([me,tape_agent(opp_actions)] if seat==0 else [tape_agent(opp_actions),me])
        rep=env.toJSON(); st=[str(x) for x in rep.get("statuses",[])]
        rw=[float(x) for x in rep.get("rewards",[])]
        if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw):
            raise RuntimeError((st,rw))
        mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
        return mine,other,rec["features"] or {}

def points(margin): return 1.0 if margin>0 else 0.5 if margin==0 else 0.0

def select_files(root,max_per_label):
    selected=[]
    for label in ("v30b_final","v47_final","v37c"):
        fs=glob.glob(str(Path(root)/label/"replays"/"*-replay.json"))
        def ep(fn):
            try:return int(Path(fn).name.split("-")[1])
            except Exception:return 0
        fs=sorted(fs,key=ep,reverse=True)[:max_per_label]
        selected += [(label,f) for f in fs]
    return selected

def eval_shard(args):
    rows=[]
    files=select_files(args.corpus_root,args.max_per_label)
    files=[x for i,x in enumerate(files) if i%args.num_shards==args.shard]
    for label,fn in files:
        d=json.loads(Path(fn).read_text())
        names=list((d.get("info") or {}).get("TeamNames") or [])
        if names.count(PAULO)!=1: continue
        seat=names.index(PAULO); opponent=names[1-seat]
        hosted=d.get("rewards")
        if hosted is None and d.get("steps"): hosted=[x.get("reward") for x in d["steps"][-1]]
        hosted=[float(x) for x in hosted]; hm,ho=(hosted[seat],hosted[1-seat])
        arm={}; feats=None
        for h in HORIZONS:
            m,o,f=run_one(args.base_package,d,seat,h)
            arm[str(h)]={"mine":m,"other":o,"margin":m-o,"points":points(m-o)}
            if feats is None: feats=f
        parity=True
        if label=="v30b_final":
            parity=(arm["44"]["mine"]==hm and arm["44"]["other"]==ho)
        row={
          "label":label,"file":Path(fn).name,"episode_id":int((d.get("info") or {}).get("EpisodeId") or 0),
          "seed":int((d.get("info") or {}).get("seed") or 0),"seat":seat,"opponent":opponent,
          "hosted_margin":hm-ho,"parity44":parity,"features":feats,"arms":arm
        }
        rows.append(row); print("V41_ARM",json.dumps({"label":label,"episode":row["episode_id"],"opponent":opponent,"parity":parity,"margins":{h:arm[h]["margin"] for h in arm}},sort_keys=True),flush=True)
    Path(args.output).write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")

def rule_choice(row,rule):
    f=row["features"]; low=rule["low"]; s=rule["sim"]; l=rule["lead"]
    return 44 if float(f.get("similarity",0))>=s or float(f.get("lead",-12))>=l else low

def metrics(rows,rule=None):
    pts=0.; margins=[]; choices=[]
    for r in rows:
        h=44 if rule is None else rule_choice(r,rule)
        a=r["arms"][str(h)];pts+=a["points"];margins.append(a["margin"]);choices.append(h)
    return {"n":len(rows),"points":pts,"rate":pts/len(rows) if rows else 0,
            "mean_margin":statistics.mean(margins) if margins else 0,
            "median_margin":statistics.median(margins) if margins else 0,"choices":choices}

def train(args):
    rows=[]
    for fn in glob.glob(str(Path(args.shards_dir)/"*.json")):
        rows.extend(json.loads(Path(fn).read_text()))
    if not rows: raise SystemExit("no rows")
    p=[r for r in rows if r["label"]=="v30b_final"]
    parity=sum(bool(r["parity44"]) for r in p)
    if parity!=len(p):
        raise SystemExit(f"V30B baseline replay parity failed {parity}/{len(p)}")
    # Per-label temporal holdout: newest N examples per label are untouched for rule selection.
    train=[];hold=[]
    for label in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==label],key=lambda r:r["episode_id"],reverse=True)
        k=min(args.holdout_per_label,max(1,len(rr)//4))
        hold+=rr[:k];train+=rr[k:]
    rules=[]
    for low in (12,24,36):
      for sim in (0.90,0.95,0.98,1.01):
        for lead in (0,4,8,12,16,24,999):
          rules.append({"low":low,"sim":sim,"lead":lead})
    base_tr=metrics(train);base_ho=metrics(hold)
    scored=[]
    for rule in rules:
        mt=metrics(train,rule)
        scored.append((mt["points"]-base_tr["points"],mt["mean_margin"]-base_tr["mean_margin"],rule,mt))
    scored.sort(key=lambda x:(x[0],x[1]),reverse=True)
    best=scored[0][2];tr=scored[0][3];ho=metrics(hold,best)
    # Count held-out W/L flips vs baseline.
    lw=wl=tw=wt=0
    pos_labels={}
    for r in hold:
        b=r["arms"]["44"]; h=rule_choice(r,best); a=r["arms"][str(h)]
        bp,ap=b["points"],a["points"]
        if bp==0 and ap==1:lw+=1
        if bp==1 and ap==0:wl+=1
        if bp==.5 and ap==1:tw+=1
        if bp==1 and ap==.5:wt+=1
        lab=r["label"]; pos_labels.setdefault(lab,[0.,0.,0])
        pos_labels[lab][0]+=ap-bp;pos_labels[lab][1]+=a["margin"]-b["margin"];pos_labels[lab][2]+=1
    delta=ho["rate"]-base_ho["rate"]
    md=ho["mean_margin"]-base_ho["mean_margin"]
    train_delta=tr["rate"]-base_tr["rate"]
    pass_gate=(delta>=0.04 and train_delta>=0.02 and lw>=wl+1 and md>-750)
    out={
      "decision":"V41_ADAPTIVE_GATE_PASS" if pass_gate else "V41_ADAPTIVE_GATE_FAIL",
      "rows":len(rows),"v30b_parity":f"{parity}/{len(p)}","train_n":len(train),"holdout_n":len(hold),
      "best_rule":best,"train_baseline":{k:v for k,v in base_tr.items() if k!="choices"},
      "train_adaptive":{k:v for k,v in tr.items() if k!="choices"},
      "holdout_baseline":{k:v for k,v in base_ho.items() if k!="choices"},
      "holdout_adaptive":{k:v for k,v in ho.items() if k!="choices"},
      "holdout_score_rate_delta":delta,"holdout_mean_margin_delta":md,
      "loss_to_win_flips":lw,"win_to_loss_flips":wl,"tie_to_win_flips":tw,"win_to_tie_flips":wt,
      "holdout_by_label":pos_labels,
      "top_rules":[{"train_points_delta":x[0],"train_mean_margin_delta":x[1],"rule":x[2]} for x in scored[:10]]
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V41_MODEL",json.dumps(out,sort_keys=True))
    if not pass_gate: raise SystemExit(7)

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    e=sp.add_parser("eval");e.add_argument("--corpus-root",required=True);e.add_argument("--base-package",required=True);e.add_argument("--shard",type=int,required=True);e.add_argument("--num-shards",type=int,required=True);e.add_argument("--max-per-label",type=int,default=40);e.add_argument("--output",required=True)
    t=sp.add_parser("train");t.add_argument("--shards-dir",required=True);t.add_argument("--holdout-per-label",type=int,default=10);t.add_argument("--output",required=True)
    a=ap.parse_args()
    if a.cmd=="eval":eval_shard(a)
    else:train(a)
if __name__=="__main__":main()
