#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,statistics
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

LOOKS=(0,4,8,12)
FEATURES=("similarity","lead")

def p(r,l): return float(r["arms"][str(l)]["points"])
def m(r,l): return float(r["arms"][str(l)]["margin"])
def best_label(r):
    xs=sorted([(p(r,l),m(r,l),-abs(l),l) for l in LOOKS],reverse=True)
    maxp=max(p(r,l) for l in LOOKS);minp=min(p(r,l) for l in LOOKS)
    maxm=max(m(r,l) for l in LOOKS);bm=m(r,0)
    if maxp==minp and maxm-bm<250:return 0
    return int(xs[0][3])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--shards-dir",required=True);ap.add_argument("--output",required=True);ap.add_argument("--holdout-per-label",type=int,default=5);a=ap.parse_args()
    rows=[]
    for fn in glob.glob(str(Path(a.shards_dir)/"*.json")):rows+=json.loads(Path(fn).read_text())
    if len(rows)!=75:raise SystemExit(f"expected 75 rows got {len(rows)}")
    pv=[r for r in rows if r["label"]=="v30b_final"];par=sum(bool(r["parity"]) for r in pv)
    if par!=len(pv):raise SystemExit(f"parity {par}/{len(pv)}")
    for r in rows:
        f=r["arms"]["0"].get("features") or {}
        r["x"]={k:float(f.get(k,0.0) or 0.0) for k in FEATURES};r["y"]=best_label(r)
    tr=[];ho=[]
    for lab in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==lab],key=lambda r:r["episode_id"],reverse=True)
        ho+=rr[:a.holdout_per_label];tr+=rr[a.holdout_per_label:]
    X=np.array([[r["x"][k] for k in FEATURES] for r in tr]);y=np.array([r["y"] for r in tr],dtype=int)
    w=[]
    for r in tr:
        ps=[p(r,l) for l in LOOKS];ms=[m(r,l) for l in LOOKS]
        spread=max(ps)-min(ps);md=max(ms)-min(ms)
        w.append(10.0 if spread>=1 else 4.0 if spread>=.5 else 1.5 if md>=1000 else .5)
    base_tr=sum(p(r,0) for r in tr);base_ho=sum(p(r,0) for r in ho)
    cand=[]
    for depth in (1,2,3):
      for leaf in (2,3,4,5,7,9):
        clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=44)
        clf.fit(X,y,sample_weight=np.array(w))
        pr=clf.predict(X)
        pts=sum(p(r,int(q)) for r,q in zip(tr,pr))
        mar=statistics.mean(m(r,int(q)) for r,q in zip(tr,pr))
        cand.append((pts-base_tr,mar,-clf.tree_.node_count,-sum(int(q)!=0 for q in pr),depth,leaf,clf))
    cand.sort(key=lambda z:z[:4],reverse=True);best=cand[0];clf=best[-1]
    Xh=np.array([[r["x"][k] for k in FEATURES] for r in ho]);ph=clf.predict(Xh)
    hpts=sum(p(r,int(q)) for r,q in zip(ho,ph));bm=statistics.mean(m(r,0) for r in ho);cm=statistics.mean(m(r,int(q)) for r,q in zip(ho,ph))
    lw=wl=tw=wt=0;hr=[]
    for r,q in zip(ho,ph):
        q=int(q);bp=p(r,0);cp=p(r,q)
        if bp==0 and cp==1:lw+=1
        if bp==1 and cp==0:wl+=1
        if bp==.5 and cp==1:tw+=1
        if bp==1 and cp==.5:wt+=1
        hr.append({"label":r["label"],"episode":r["episode_id"],"opponent":r["opponent"],"pred":q,"base_points":bp,"cand_points":cp,"base_margin":m(r,0),"cand_margin":m(r,q),"similarity":r["x"]["similarity"],"lead":r["x"]["lead"]})
    trd=best[0]/len(tr);hod=(hpts-base_ho)/len(ho);md=cm-bm
    passed=(hpts>=base_ho+1.0 and trd>=0.04 and lw+tw>=wl+wt+1 and md>-1000)
    t={"children_left":clf.tree_.children_left.tolist(),"children_right":clf.tree_.children_right.tolist(),"feature":clf.tree_.feature.tolist(),"threshold":clf.tree_.threshold.tolist(),"value":[v[0].tolist() for v in clf.tree_.value],"classes":[int(x) for x in clf.classes_.tolist()]}
    out={"decision":"V44_CF_TREE_GATE_PASS" if passed else "V44_CF_TREE_GATE_FAIL","rows":len(rows),"v30b_parity":f"{par}/{len(pv)}","feature_names":list(FEATURES),"model":{"depth":best[4],"leaf":best[5],"tree":t},"train_n":len(tr),"holdout_n":len(ho),"train_base_points":base_tr,"train_candidate_points":base_tr+best[0],"train_score_delta":trd,"holdout_base_points":base_ho,"holdout_candidate_points":hpts,"holdout_score_delta":hod,"holdout_margin_delta":md,"loss_to_win":lw,"win_to_loss":wl,"tie_to_win":tw,"win_to_tie":wt,"holdout_rows":hr,"tree_text":export_text(clf,feature_names=list(FEATURES))}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("V44_MODEL",json.dumps({k:v for k,v in out.items() if k not in ("model","holdout_rows","tree_text","feature_names")},sort_keys=True));print(out["tree_text"])
    if not passed:raise SystemExit(7)
if __name__=="__main__":main()
