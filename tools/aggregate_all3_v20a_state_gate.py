#!/usr/bin/env python3
"""Aggregate V20A discovery pairs and fit frozen turn-464 state gate."""
from __future__ import annotations
import argparse,json,math,statistics
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier

THRESHOLD=0.80
TRAIN_SEEDS={78711,78712,78713,78714}
HOLDOUT_SEEDS={78715,78716}
DROP_FEATURES={"turn","p2_progress"}

def transform(row):
    p={k:float(v) for k,v in row["snapshots"]["463"].items() if k not in DROP_FEATURES}
    c={k:float(v) for k,v in row["snapshots"]["464"].items() if k not in DROP_FEATURES}
    if set(p)!=set(c):raise RuntimeError("463/464 feature schema mismatch")
    out={}
    for k in sorted(c):
        dv=c[k]-p[k]
        out[f"cur__{k}"]=c[k];out[f"prev__{k}"]=p[k];out[f"delta__{k}"]=dv;out[f"absdelta__{k}"]=abs(dv)
    return out

def tree_json(clf,names):
    t=clf.tree_;classes=[int(x) for x in clf.classes_]
    one_idx=classes.index(1)
    def node(i):
        vals=t.value[i][0].tolist();total=sum(vals);p1=float(vals[one_idx]/total) if total else 0.0
        if t.children_left[i]==t.children_right[i]:
            return {"leaf":True,"p_benefit":p1,"n":int(t.n_node_samples[i])}
        return {"leaf":False,"feature":names[int(t.feature[i])],"threshold":float(t.threshold[i]),
                "n":int(t.n_node_samples[i]),"p_benefit":p1,
                "left":node(int(t.children_left[i])),"right":node(int(t.children_right[i]))}
    return node(0)

def json_prob(tree,feat):
    n=tree
    while not n.get("leaf"):
        n=n["left"] if float(feat[n["feature"]])<=float(n["threshold"]) else n["right"]
    return float(n["p_benefit"])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    cfg=json.loads(Path(args.config).read_text())
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    keys={(r["main_sha256"],int(r["seed"]),int(r["seat"])) for r in rows}
    shas={d.get("schedule_sha256") for d in docs}
    mech=(len(docs)==5 and len(rows)==120 and len(keys)==120 and not failures
          and all(d.get("mechanical_pass") for d in docs)
          and shas=={cfg["schedule_sha256"]})
    if not mech:
        result={"schema":"kculture-all3-v20a-state-gate-v1","decision":"V20A_MECHANICS_INVALID","mechanical_pass":False,
                "pairs":len(rows),"failures":failures,"automatic_kaggle_submission":False}
        Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print("V20A_RESULT",json.dumps(result,sort_keys=True));raise SystemExit(2)

    feats=[transform(r) for r in rows]
    names=sorted(feats[0])
    if any(sorted(x)!=names for x in feats):raise RuntimeError("transformed feature schema drift")
    # The transformed schema originates only from the pre-approved legal V18B features.
    forbidden=("source","ref","rank","context","scenario_seed","seed_meta","seat","margin","reward","result","outcome")
    bad=[n for n in names if any(tok in n.lower() for tok in forbidden)]
    # legitimate in-game seed inventory names include seed_<product>; do not reject substring 'seed'.
    bad=[n for n in bad if "seed_" not in n.lower() or "scenario_seed" in n.lower()]
    if bad:raise RuntimeError(f"prohibited gate features {bad}")

    X=np.asarray([[f[n] for n in names] for f in feats],dtype=np.float64)
    y=np.asarray([int(float(r["score_delta"])>0) for r in rows],dtype=np.int8)
    seeds=np.asarray([int(r["seed"]) for r in rows])
    train=np.flatnonzero(np.isin(seeds,list(TRAIN_SEEDS)));hold=np.flatnonzero(np.isin(seeds,list(HOLDOUT_SEEDS)))
    train_pos=int(np.sum(y[train]));train_non=int(len(train)-train_pos)
    pos_seed_support=len({int(rows[i]["seed"]) for i in train if y[i]==1})
    non_seed_support=len({int(rows[i]["seed"]) for i in train if y[i]==0})
    trainable=(train_pos>=8 and train_non>=8 and pos_seed_support>=2 and non_seed_support>=2)

    if not trainable:
        decision="V20A_GATE_NOT_TRAINABLE";tree=None;metrics={}
    else:
        clf=DecisionTreeClassifier(max_depth=3,min_samples_leaf=8,class_weight="balanced",random_state=20260921)
        clf.fit(X[train],y[train])
        tree=tree_json(clf,names)
        sk=clf.predict_proba(X)[:,list(clf.classes_).index(1)]
        js=np.asarray([json_prob(tree,f) for f in feats])
        parity=bool(np.allclose(sk,js,rtol=0,atol=1e-12))
        active=[i for i in hold if js[i]>=THRESHOLD]
        pos=[i for i in active if float(rows[i]["score_delta"])>0]
        neg=[i for i in active if float(rows[i]["score_delta"])<0]
        pos_sources={rows[i]["main_sha256"] for i in pos}
        win_to_non=[i for i in active if float(rows[i]["base_score"])==1.0 and float(rows[i]["treatment_score"])<1.0]
        gated_score=[float(rows[i]["score_delta"]) if i in active else 0.0 for i in hold]
        gated_margin=[float(rows[i]["margin_delta"]) if i in active else 0.0 for i in hold]
        metrics={"holdout_contexts":len(hold),"activated":len(active),"positive_score_activated":len(pos),
                 "negative_score_activated":len(neg),"positive_score_sources":len(pos_sources),
                 "win_to_nonwin":len(win_to_non),"mean_gated_score_delta":statistics.fmean(gated_score),
                 "mean_gated_margin_delta":statistics.fmean(gated_margin),"json_parity":parity,
                 "active_keys":[[rows[i]["main_sha256"],rows[i]["seed"],rows[i]["seat"],float(js[i])] for i in active]}
        ready=(parity and len(active)>=4 and len(pos)>=2 and len(pos_sources)>=2 and len(neg)==0 and len(win_to_non)==0
               and metrics["mean_gated_score_delta"]>0 and metrics["mean_gated_margin_delta"]>=0)
        decision="V20A_STATE_GATE_READY" if ready else "V20A_STATE_GATE_NOT_READY"

    result={"schema":"kculture-all3-v20a-state-gate-v1","decision":decision,"mechanical_pass":True,
      "schedule_sha256":cfg["schedule_sha256"],"pairs":len(rows),"feature_names":names,"threshold":THRESHOLD,
      "train_seeds":sorted(TRAIN_SEEDS),"holdout_seeds":sorted(HOLDOUT_SEEDS),
      "train_positive":train_pos,"train_nonpositive":train_non,"positive_seed_support":pos_seed_support,
      "nonpositive_seed_support":non_seed_support,"tree":tree,"holdout_metrics":metrics,
      "rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V20A_RESULT",json.dumps({"decision":decision,"train_positive":train_pos,"train_nonpositive":train_non,
      "positive_seed_support":pos_seed_support,"nonpositive_seed_support":non_seed_support,
      "holdout_metrics":metrics},sort_keys=True),flush=True)
    if decision!="V20A_STATE_GATE_READY":raise SystemExit(2)

if __name__=="__main__":main()
