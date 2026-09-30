#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,statistics
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

LOOKS=(0,4,8,12)

def points_for(r,l): return float(r["arms"][str(int(l))]["points"])
def margin_for(r,l): return float(r["arms"][str(int(l))]["margin"])

def best_label(r):
    scored=[]
    for l in LOOKS:
        a=r["arms"][str(l)]
        scored.append((float(a["points"]),float(a["margin"]),-abs(l),l))
    scored.sort(reverse=True)
    maxp=max(points_for(r,l) for l in LOOKS);minp=min(points_for(r,l) for l in LOOKS)
    maxm=max(margin_for(r,l) for l in LOOKS);basem=margin_for(r,0)
    if maxp==minp and maxm-basem<250:return 0
    return int(scored[0][3])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--arms-dir",required=True);ap.add_argument("--features-dir",required=True);ap.add_argument("--output",required=True);ap.add_argument("--holdout-per-label",type=int,default=5);a=ap.parse_args()
    arms=[]
    for fn in glob.glob(str(Path(a.arms_dir)/"*.json")):arms+=json.loads(Path(fn).read_text())
    feats=[]
    for fn in glob.glob(str(Path(a.features_dir)/"*.json")):feats+=json.loads(Path(fn).read_text())
    if len(arms)!=75 or len(feats)!=75:raise SystemExit({"arms":len(arms),"features":len(feats)})
    fm={int(x["episode_id"]):x for x in feats}
    rows=[]
    for r in arms:
        ep=int(r["episode_id"]);f=fm.get(ep)
        if f is None:raise SystemExit(f"missing cf feature {ep}")
        # Baseline counterfactual replay must match arm-0 result exactly.
        if float(f["margin"])!=float(r["arms"]["0"]["margin"]):
            raise SystemExit(f"counterfactual baseline mismatch {ep}: {f['margin']} != {r['arms']['0']['margin']}")
        q=dict(r);q["x"]=f["x"];q["y"]=best_label(r);rows.append(q)
    p=[r for r in rows if r["label"]=="v30b_final"]
    parity=sum(bool(r["parity"]) for r in p)
    if parity!=len(p):raise SystemExit(f"hosted V30B parity failed {parity}/{len(p)}")
    features=sorted(rows[0]["x"])
    train=[];hold=[]
    for label in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==label],key=lambda r:r["episode_id"],reverse=True)
        k=a.holdout_per_label;hold+=rr[:k];train+=rr[k:]
    X=np.array([[r["x"][f] for f in features] for r in train],float);y=np.array([r["y"] for r in train],int)
    weights=[]
    for r in train:
        ps=[points_for(r,l) for l in LOOKS];ms=[margin_for(r,l) for l in LOOKS]
        spread=max(ps)-min(ps);mspread=max(ms)-min(ms)
        weights.append(8.0 if spread>=1 else 3.0 if spread>=.5 else 1.5 if mspread>=1000 else .5)
    base_tr=sum(points_for(r,0) for r in train);base_ho=sum(points_for(r,0) for r in hold)
    cands=[]
    for depth in (1,2,3):
      for leaf in (3,5,7,9):
        if leaf*2>len(train):continue
        clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=44)
        clf.fit(X,y,sample_weight=np.array(weights))
        pred=clf.predict(X)
        pts=sum(points_for(r,int(p)) for r,p in zip(train,pred))
        mean=statistics.mean(margin_for(r,int(p)) for r,p in zip(train,pred))
        interventions=sum(int(p)!=0 for p in pred)
        cands.append((pts-base_tr,mean,-clf.tree_.node_count,-interventions,depth,leaf,clf))
    cands.sort(key=lambda z:z[:4],reverse=True);best=cands[0];clf=best[-1]
    Xh=np.array([[r["x"][f] for f in features] for r in hold],float);ph=clf.predict(Xh)
    hold_pts=sum(points_for(r,int(p)) for r,p in zip(hold,ph))
    base_margin=statistics.mean(margin_for(r,0) for r in hold)
    cand_margin=statistics.mean(margin_for(r,int(p)) for r,p in zip(hold,ph))
    lw=wl=tw=wt=0;per={};rows_out=[]
    for r,pred in zip(hold,ph):
        pred=int(pred);bp=points_for(r,0);cp=points_for(r,pred)
        if bp==0 and cp==1:lw+=1
        if bp==1 and cp==0:wl+=1
        if bp==.5 and cp==1:tw+=1
        if bp==1 and cp==.5:wt+=1
        q=per.setdefault(r["label"],{"n":0,"base_points":0.0,"cand_points":0.0,"margin_delta":0.0})
        q["n"]+=1;q["base_points"]+=bp;q["cand_points"]+=cp;q["margin_delta"]+=margin_for(r,pred)-margin_for(r,0)
        rows_out.append({"label":r["label"],"episode":r["episode_id"],"opponent":r["opponent"],"seat":r["seat"],"pred":pred,"y":r["y"],"base_points":bp,"cand_points":cp,"base_margin":margin_for(r,0),"cand_margin":margin_for(r,pred)})
    train_delta=best[0]/len(train);hold_delta=(hold_pts-base_ho)/len(hold);md=cand_margin-base_margin
    passed=(hold_pts>=base_ho+1.0 and train_delta>=0.04 and lw+tw>=wl+wt+1 and md>-1000)
    tree={"children_left":clf.tree_.children_left.tolist(),"children_right":clf.tree_.children_right.tolist(),"feature":clf.tree_.feature.tolist(),"threshold":clf.tree_.threshold.tolist(),"value":[v[0].tolist() for v in clf.tree_.value],"classes":[int(x) for x in clf.classes_.tolist()]}
    out={"decision":"V44_CF_TREE_GATE_PASS" if passed else "V44_CF_TREE_GATE_FAIL","rows":len(rows),"v30b_parity":f"{parity}/{len(p)}","feature_names":features,"model":{"max_depth":best[4],"min_samples_leaf":best[5],"tree":tree},"train_n":len(train),"holdout_n":len(hold),"train_base_points":base_tr,"train_candidate_points":base_tr+best[0],"train_score_rate_delta":train_delta,"holdout_base_points":base_ho,"holdout_candidate_points":hold_pts,"holdout_score_rate_delta":hold_delta,"holdout_base_mean_margin":base_margin,"holdout_candidate_mean_margin":cand_margin,"holdout_mean_margin_delta":md,"loss_to_win_flips":lw,"win_to_loss_flips":wl,"tie_to_win_flips":tw,"win_to_tie_flips":wt,"per_label":per,"holdout_rows":rows_out,"tree_text":export_text(clf,feature_names=features)}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V44_MODEL",json.dumps({k:v for k,v in out.items() if k not in ("model","feature_names","holdout_rows","tree_text")},sort_keys=True))
    print(out["tree_text"])
    if not passed:raise SystemExit(7)
if __name__=="__main__":main()
