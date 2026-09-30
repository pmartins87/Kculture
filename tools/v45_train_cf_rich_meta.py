#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,statistics
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

LOOKS=(0,4,8,12)

def pts(r,l): return float(r["arms"][str(int(l))]["points"])
def margin(r,l): return float(r["arms"][str(int(l))]["margin"])

def best_label(r):
    scored=sorted([(pts(r,l),margin(r,l),-abs(l),l) for l in LOOKS],reverse=True)
    pvals=[pts(r,l) for l in LOOKS]; mvals=[margin(r,l) for l in LOOKS]
    # Default to no intervention when no W/L benefit and margin improvement is small.
    if max(pvals)==min(pvals) and max(mvals)-margin(r,0)<250:
        return 0
    return int(scored[0][3])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--features",required=True)
    ap.add_argument("--arms-dir",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--holdout-per-label",type=int,default=5)
    a=ap.parse_args()

    features_rows=json.loads(Path(a.features).read_text())
    fx={int(r["episode_id"]):r for r in features_rows}
    rows=[]
    for fn in glob.glob(str(Path(a.arms_dir)/"*.json")):
        rows += json.loads(Path(fn).read_text())
    if len(rows)!=75 or len(fx)!=75:
        raise SystemExit(f"expected 75/75 got arms={len(rows)} features={len(fx)}")
    pv=[r for r in rows if r["label"]=="v30b_final"]
    parity=sum(bool(r["parity"]) for r in pv)
    if parity!=25: raise SystemExit(f"V30B parity {parity}/25")

    for r in rows:
        ep=int(r["episode_id"])
        if ep not in fx: raise SystemExit(f"missing features {ep}")
        r["x"]={k:float(v) for k,v in fx[ep]["features"].items()}
        r["y"]=best_label(r)

    names=sorted(rows[0]["x"].keys())
    # Constant/non-finite filtering based only on training candidates happens below.
    tr=[];ho=[]
    for lab in sorted({r["label"] for r in rows}):
        rr=sorted([r for r in rows if r["label"]==lab],key=lambda r:int(r["episode_id"]),reverse=True)
        k=a.holdout_per_label
        ho += rr[:k]
        tr += rr[k:]

    # Remove constant features using training set only.
    keep=[]
    for name in names:
        vals=[r["x"][name] for r in tr]
        if max(vals)!=min(vals): keep.append(name)
    names=keep
    X=np.asarray([[r["x"][n] for n in names] for r in tr],dtype=float)
    y=np.asarray([r["y"] for r in tr],dtype=int)

    # Weight only the importance of contexts; labels still come solely from the
    # counterfactual arm tournament.
    weights=[]
    for r in tr:
        ps=[pts(r,l) for l in LOOKS]; ms=[margin(r,l) for l in LOOKS]
        pspread=max(ps)-min(ps); mspread=max(ms)-min(ms)
        weights.append(10.0 if pspread>=1 else 4.0 if pspread>=.5 else 1.5 if mspread>=1000 else 0.5)

    base_tr=sum(pts(r,0) for r in tr)
    base_ho=sum(pts(r,0) for r in ho)
    candidates=[]
    # Small model family only; depth <=3, meaningful leaves.
    for depth in (1,2,3):
      for leaf in (3,4,5,6,8,10):
        if 2*leaf>len(tr): continue
        clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=45)
        clf.fit(X,y,sample_weight=np.asarray(weights))
        pr=clf.predict(X)
        ptotal=sum(pts(r,int(q)) for r,q in zip(tr,pr))
        mm=statistics.mean(margin(r,int(q)) for r,q in zip(tr,pr))
        interventions=sum(int(q)!=0 for q in pr)
        candidates.append((ptotal-base_tr,mm,-clf.tree_.node_count,-interventions,depth,leaf,clf))
    candidates.sort(key=lambda x:x[:4],reverse=True)
    best=candidates[0]; clf=best[-1]

    Xh=np.asarray([[r["x"][n] for n in names] for r in ho],dtype=float)
    ph=clf.predict(Xh)
    hold_pts=sum(pts(r,int(q)) for r,q in zip(ho,ph))
    base_margin=statistics.mean(margin(r,0) for r in ho)
    cand_margin=statistics.mean(margin(r,int(q)) for r,q in zip(ho,ph))
    lw=wl=tw=wt=0; rows_out=[]
    per_label={}
    for r,q in zip(ho,ph):
        q=int(q);bp=pts(r,0);cp=pts(r,q)
        if bp==0 and cp==1:lw+=1
        if bp==1 and cp==0:wl+=1
        if bp==.5 and cp==1:tw+=1
        if bp==1 and cp==.5:wt+=1
        z=per_label.setdefault(r["label"],{"n":0,"base_points":0.0,"cand_points":0.0,"margin_delta":0.0})
        z["n"]+=1;z["base_points"]+=bp;z["cand_points"]+=cp;z["margin_delta"]+=margin(r,q)-margin(r,0)
        rows_out.append({"label":r["label"],"episode":int(r["episode_id"]),"opponent":r["opponent"],
                         "pred":q,"base_points":bp,"cand_points":cp,
                         "base_margin":margin(r,0),"cand_margin":margin(r,q)})

    train_delta=best[0]/len(tr)
    hold_delta=(hold_pts-base_ho)/len(ho)
    md=cand_margin-base_margin
    # Same binding gate as V43, but now feature construction is counterfactual-safe.
    passed=(hold_pts>=base_ho+1.0 and train_delta>=0.04
            and lw+tw>=wl+wt+1 and md>-1000)

    tree={
      "children_left":clf.tree_.children_left.tolist(),
      "children_right":clf.tree_.children_right.tolist(),
      "feature":clf.tree_.feature.tolist(),
      "threshold":clf.tree_.threshold.tolist(),
      "value":[v[0].tolist() for v in clf.tree_.value],
      "classes":[int(x) for x in clf.classes_.tolist()],
    }
    out={
      "decision":"V45_CF_RICH_TREE_GATE_PASS" if passed else "V45_CF_RICH_TREE_GATE_FAIL",
      "rows":len(rows),"v30b_parity":"25/25","feature_names":names,
      "model":{"depth":best[4],"min_samples_leaf":best[5],"tree":tree},
      "train_n":len(tr),"holdout_n":len(ho),
      "train_base_points":base_tr,"train_candidate_points":base_tr+best[0],
      "train_score_rate_delta":train_delta,
      "holdout_base_points":base_ho,"holdout_candidate_points":hold_pts,
      "holdout_score_rate_delta":hold_delta,
      "holdout_base_mean_margin":base_margin,
      "holdout_candidate_mean_margin":cand_margin,
      "holdout_mean_margin_delta":md,
      "loss_to_win_flips":lw,"win_to_loss_flips":wl,
      "tie_to_win_flips":tw,"win_to_tie_flips":wt,
      "per_label":per_label,"holdout_rows":rows_out,
      "tree_text":export_text(clf,feature_names=names),
      "top_models":[
        {"train_points_delta":x[0],"train_mean_margin":x[1],
         "nodes":-x[2],"interventions":-x[3],"depth":x[4],"leaf":x[5]}
        for x in candidates[:8]
      ],
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V45_MODEL",json.dumps({k:v for k,v in out.items()
          if k not in ("feature_names","model","holdout_rows","tree_text","top_models")},sort_keys=True))
    print(out["tree_text"])
    if not passed: raise SystemExit(7)

if __name__=="__main__": main()
