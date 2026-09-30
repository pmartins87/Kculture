#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,statistics
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

PAULO="Paulo Martins"
LOOKS=(0,4,8,12)
ITEMS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")

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

def obs_at(d,step,seat):
    steps=d.get("steps") or []
    if step>=len(steps):step=len(steps)-1
    return steps[step][seat].get("observation") or {}

def feature_vector(d,row):
    seat=int(row["seat"]);opp=1-seat
    o=obs_at(d,216,seat);farms=o.get("farms") or [{},{}]
    own=farms[seat] if seat<len(farms) else {};other=farms[opp] if opp<len(farms) else {}
    oc,oa,ok=counts(own);qc,qa,qk=counts(other)
    f0=row["arms"]["0"].get("features") or {}
    vals={
      "similarity":float(f0.get("similarity",0) or 0),
      "lead":float(f0.get("lead",-12) or -12),
      "seat":float(seat),
      "own_money":float(own.get("money",0) or 0),"opp_money":float(other.get("money",0) or 0),
      "money_diff":float(own.get("money",0) or 0)-float(other.get("money",0) or 0),
      "own_hands":float(len(own.get("hands") or [])),"opp_hands":float(len(other.get("hands") or [])),
      "hands_diff":float(len(own.get("hands") or []))-float(len(other.get("hands") or [])),
      "own_quads":float(len(own.get("unlocked_quadrants") or [])),"opp_quads":float(len(other.get("unlocked_quadrants") or [])),
    }
    for k in CROPS:
        vals["own_crop_"+k]=float(oc[k]);vals["opp_crop_"+k]=float(qc[k]);vals["crop_diff_"+k]=float(oc[k]-qc[k])
    for k in ANIMALS:
        vals["own_animal_"+k]=float(oa[k]);vals["opp_animal_"+k]=float(qa[k]);vals["animal_diff_"+k]=float(oa[k]-qa[k])
    for kind in ("PLANT","PASTURE","COOP"):
        vals["own_kind_"+kind]=float(ok.get(kind,0));vals["opp_kind_"+kind]=float(qk.get(kind,0))
    for lag in (0,24,48):
        oo=obs_at(d,max(0,216-lag),seat)
        market=oo.get("market") or {};inv=market.get("inventory") or {};pr=market.get("prices") or {}
        for it in ITEMS:
            vals[f"inv_{it}_lag{lag}"]=float(inv.get(it,10000) or 0)
            vals[f"price_{it}_lag{lag}"]=float(pr.get(it,0) or 0)
    for it in ITEMS:
        vals[f"inv_delta24_{it}"]=vals[f"inv_{it}_lag0"]-vals[f"inv_{it}_lag24"]
        vals[f"inv_delta48_{it}"]=vals[f"inv_{it}_lag0"]-vals[f"inv_{it}_lag48"]
        vals[f"price_delta24_{it}"]=vals[f"price_{it}_lag0"]-vals[f"price_{it}_lag24"]
    return vals

def best_label(row):
    # Win/tie/loss first. Margin breaks ties. Prefer no intervention when practically tied.
    base=row["arms"]["0"]
    scored=[]
    for look in LOOKS:
        a=row["arms"][str(look)]
        scored.append((float(a["points"]),float(a["margin"]),-abs(look),look))
    scored.sort(reverse=True)
    top=scored[0]
    # If all arms have same W/L and best margin gain is tiny, default to baseline.
    maxp=max(float(row["arms"][str(x)]["points"]) for x in LOOKS)
    minp=min(float(row["arms"][str(x)]["points"]) for x in LOOKS)
    maxm=max(float(row["arms"][str(x)]["margin"]) for x in LOOKS)
    basem=float(base["margin"])
    if maxp==minp and maxm-basem<250:return 0
    return int(top[3])

def points_for(row,look):return float(row["arms"][str(int(look))]["points"])
def margin_for(row,look):return float(row["arms"][str(int(look))]["margin"])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--shards-dir",required=True);ap.add_argument("--corpus-root",required=True);ap.add_argument("--output",required=True);ap.add_argument("--holdout-per-label",type=int,default=5);a=ap.parse_args()
    rows=[]
    for fn in glob.glob(str(Path(a.shards_dir)/"*.json")):rows+=json.loads(Path(fn).read_text())
    if len(rows)!=75:raise SystemExit(f"expected 75 rows got {len(rows)}")
    # Exact V30B hosted reconstruction remains mandatory.
    p=[r for r in rows if r["label"]=="v30b_final"]
    parity=sum(bool(r["parity"]) for r in p)
    if parity!=len(p):raise SystemExit(f"baseline parity failed {parity}/{len(p)}")
    replay_by_ep={}
    for fn in glob.glob(str(Path(a.corpus_root)/"*"/"replays"/"*-replay.json")):
        d=json.loads(Path(fn).read_text());ep=int((d.get("info") or {}).get("EpisodeId") or 0);replay_by_ep[ep]=d
    for r in rows:
        d=replay_by_ep.get(int(r["episode_id"]))
        if d is None:raise SystemExit(f"missing replay {r['episode_id']}")
        r["x"]=feature_vector(d,r);r["y"]=best_label(r)
    features=sorted(rows[0]["x"])
    train=[];hold=[]
    for label in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==label],key=lambda r:r["episode_id"],reverse=True)
        k=a.holdout_per_label;hold+=rr[:k];train+=rr[k:]
    X=np.array([[r["x"][f] for f in features] for r in train],dtype=float)
    y=np.array([r["y"] for r in train],dtype=int)
    # Weight contexts where the available actions actually change W/L more heavily.
    w=[]
    for r in train:
        ps=[points_for(r,l) for l in LOOKS]
        spread=max(ps)-min(ps)
        margins=[margin_for(r,l) for l in LOOKS]
        mspread=max(margins)-min(margins)
        w.append(8.0 if spread>=1 else 3.0 if spread>=0.5 else 1.5 if mspread>=1000 else 0.5)
    base_tr=sum(points_for(r,0) for r in train);base_ho=sum(points_for(r,0) for r in hold)
    candidates=[]
    for depth in (1,2,3):
      for leaf in (3,5,7,9):
        if leaf*2>len(train):continue
        clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=41,class_weight=None)
        clf.fit(X,y,sample_weight=np.array(w))
        pred=clf.predict(X)
        pts=sum(points_for(r,int(p)) for r,p in zip(train,pred))
        margin=sum(margin_for(r,int(p)) for r,p in zip(train,pred))/len(train)
        interventions=sum(int(p)!=0 for p in pred)
        candidates.append((pts-base_tr,margin, -clf.tree_.node_count,-interventions,depth,leaf,clf))
    candidates.sort(key=lambda z:z[:4],reverse=True)
    best=candidates[0];clf=best[-1]
    Xh=np.array([[r["x"][f] for f in features] for r in hold],dtype=float)
    ph=clf.predict(Xh)
    hold_pts=sum(points_for(r,int(p)) for r,p in zip(hold,ph))
    base_margin=statistics.mean(margin_for(r,0) for r in hold)
    cand_margin=statistics.mean(margin_for(r,int(p)) for r,p in zip(hold,ph))
    lw=wl=tw=wt=0
    per_label={}
    rows_out=[]
    for r,pred in zip(hold,ph):
        pred=int(pred);bp=points_for(r,0);cp=points_for(r,pred)
        if bp==0 and cp==1:lw+=1
        if bp==1 and cp==0:wl+=1
        if bp==.5 and cp==1:tw+=1
        if bp==1 and cp==.5:wt+=1
        q=per_label.setdefault(r["label"],{"n":0,"base_points":0.0,"cand_points":0.0,"margin_delta":0.0})
        q["n"]+=1;q["base_points"]+=bp;q["cand_points"]+=cp;q["margin_delta"]+=margin_for(r,pred)-margin_for(r,0)
        rows_out.append({"label":r["label"],"episode":r["episode_id"],"opponent":r["opponent"],"pred":pred,"y":r["y"],"base_points":bp,"cand_points":cp,"base_margin":margin_for(r,0),"cand_margin":margin_for(r,pred)})
    train_rate_delta=best[0]/len(train);hold_delta=(hold_pts-base_ho)/len(hold);md=cand_margin-base_margin
    # Strict: at least +1 full point on 15 untouched latest games, more positive than negative flips, no huge margin damage.
    passed=(hold_pts>=base_ho+1.0 and train_rate_delta>=0.04 and lw+tw>=wl+wt+1 and md>-1000)
    tree={
      "children_left":clf.tree_.children_left.tolist(),"children_right":clf.tree_.children_right.tolist(),
      "feature":clf.tree_.feature.tolist(),"threshold":clf.tree_.threshold.tolist(),
      "value":[v[0].tolist() for v in clf.tree_.value],"classes":[int(x) for x in clf.classes_.tolist()]
    }
    out={"decision":"V43_TREE_GATE_PASS" if passed else "V43_TREE_GATE_FAIL","rows":len(rows),"v30b_parity":f"{parity}/{len(p)}",
         "feature_names":features,"model":{"max_depth":best[4],"min_samples_leaf":best[5],"tree":tree},
         "train_n":len(train),"holdout_n":len(hold),"train_base_points":base_tr,"train_candidate_points":base_tr+best[0],"train_score_rate_delta":train_rate_delta,
         "holdout_base_points":base_ho,"holdout_candidate_points":hold_pts,"holdout_score_rate_delta":hold_delta,
         "holdout_base_mean_margin":base_margin,"holdout_candidate_mean_margin":cand_margin,"holdout_mean_margin_delta":md,
         "loss_to_win_flips":lw,"win_to_loss_flips":wl,"tie_to_win_flips":tw,"win_to_tie_flips":wt,
         "per_label":per_label,"holdout_rows":rows_out,"tree_text":export_text(clf,feature_names=features)}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V43_MODEL",json.dumps({k:v for k,v in out.items() if k not in ("model","feature_names","holdout_rows","tree_text")},sort_keys=True))
    print(out["tree_text"])
    if not passed:raise SystemExit(7)
if __name__=="__main__":main()
