#!/usr/bin/env python3
"""V18B2 transition-event market-controller distillation from binding V18B dataset."""
from __future__ import annotations
import argparse,copy,json,math
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from tools.all3_v18b_train_market_controller import (
    actionable_families, family_y, tree_json, json_predict, metric,
    compile_market, structurally_valid,
)

REQUIRED_KINDS={"QTY","PRESENCE"}

def market_key(row):
    return json.dumps(((row.get("base_action") or {}).get("market") or []),sort_keys=True,separators=(",",":"))

def transform_rows(rows):
    out=[]
    by_ctx={}
    for r in sorted(rows,key=lambda x:(str(x["context_id"]),int(x["turn"]))):
        cid=str(r["context_id"])
        cur={k:float(v) for k,v in (r.get("features") or {}).items()}
        prev=by_ctx.get(cid)
        if prev is None:
            prev=cur
            market_changed=False
        else:
            market_changed=market_key(r)!=by_ctx[cid+"_market"]
        feat={}
        any_change=False
        for k in sorted(cur):
            cv=float(cur[k]);pv=float(prev.get(k,cv));dv=cv-pv
            feat[f"cur__{k}"]=cv
            feat[f"prev__{k}"]=pv
            feat[f"delta__{k}"]=dv
            feat[f"absdelta__{k}"]=abs(dv)
            if abs(dv)>1e-12:any_change=True
        feat["edge__any_numeric_change"]=1.0 if any_change else 0.0
        feat["edge__all3_market_changed"]=1.0 if market_changed else 0.0

        nr=copy.deepcopy(r)
        nr["predictor_features"]=feat
        nr["current_features"]=cur
        out.append(nr)
        by_ctx[cid]=cur
        by_ctx[cid+"_market"]=market_key(r)
    return out

def matrix(rows,names):
    return np.asarray([[float((r.get("predictor_features") or {}).get(n,0.0)) for n in names] for r in rows],dtype=np.float64)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--v14b",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    raw=[r for d in docs for r in d.get("rows",[])]
    if len(docs)!=4 or len(raw)!=3072 or failures or not all(d.get("mechanical_pass") for d in docs):
        raise RuntimeError(f"binding dataset invalid docs={len(docs)} rows={len(raw)} failures={len(failures)}")
    rows=transform_rows(raw)
    if len(rows)!=3072:raise RuntimeError("transformed row count mismatch")
    contexts={str(r["context_id"]) for r in rows}
    sources=sorted({str(r["main_sha256"]) for r in rows})
    if len(contexts)!=24 or len(sources)!=10:raise RuntimeError("support mismatch")

    names=sorted(rows[0]["predictor_features"].keys())
    for r in rows:
        if sorted(r["predictor_features"].keys())!=names:raise RuntimeError("predictor schema drift")
    # Predictor schema is generated solely from the already-approved V18B legal features.
    forbidden_literal={"source","source_sha","sha","ref","rank","context","context_id","scenario_seed","seed","seat","result","margin","reward","outcome"}
    bad=[n for n in names if n.lower() in forbidden_literal]
    if bad:raise RuntimeError(f"prohibited transformed features {bad}")

    X=matrix(rows,names)
    v14b=json.loads(Path(args.v14b).read_text())
    # helper expects current rows with labels only, so predictor transform does not alter eligibility/targets
    fams=actionable_families(v14b,raw)
    source_arr=np.asarray([str(r["main_sha256"]) for r in rows],dtype=object)
    retained=[];results=[]

    for fam in fams:
        fid=fam["family_id"]
        y=family_y(raw,fid)
        pos_sources=sorted({str(rows[i]["main_sha256"]) for i in np.flatnonzero(y==1)})
        oof=np.zeros(len(rows),dtype=np.int8)
        folds=[]
        for hold in sources:
            tr=np.flatnonzero(source_arr!=hold);te=np.flatnonzero(source_arr==hold)
            clf=DecisionTreeClassifier(
                max_depth=4,min_samples_leaf=8,class_weight="balanced",random_state=20260921
            )
            clf.fit(X[tr],y[tr])
            oof[te]=clf.predict(X[te]).astype(np.int8)
            folds.append({"holdout_source":hold,"train_rows":len(tr),"test_rows":len(te),"min_leaf":8})
        m=metric(y,oof)
        tp_sources=sorted({str(rows[i]["main_sha256"]) for i in np.flatnonzero((y==1)&(oof==1))})
        eligible=(len(pos_sources)>=4 and m["precision"]>=0.80 and m["recall"]>=0.70 and m["f1"]>=0.75)
        rec={**fam,
             "positive_source_support":len(pos_sources),"positive_sources":pos_sources,
             "oof_tp_source_support":len(tp_sources),"oof_metrics":m,"folds":folds,
             "retained":eligible}
        if eligible:
            clf=DecisionTreeClassifier(
                max_depth=4,min_samples_leaf=8,class_weight="balanced",random_state=20260921
            )
            clf.fit(X,y)
            tree=tree_json(clf,names)
            sk=clf.predict(X).astype(np.int8)
            js=np.asarray([json_predict(tree,r["predictor_features"]) for r in rows],dtype=np.int8)
            parity=bool(np.array_equal(sk,js))
            if not parity:raise RuntimeError(f"JSON parity failure {fid}")
            rec["tree"]=tree;rec["json_parity"]=True;rec["positive_support"]=int(np.sum(y))
            retained.append(rec)
        results.append(rec)

    meta={r["family_id"]:r for r in retained}
    compiler_ok=True;changed=0
    if retained:
        for r in rows:
            pred=[fam["family_id"] for fam in retained if json_predict(fam["tree"],r["predictor_features"])==1]
            compile_row=copy.deepcopy(r)
            compile_row["features"]=r["current_features"]
            out=compile_market(compile_row,pred,meta)
            if not structurally_valid(compile_row,out):
                compiler_ok=False;break
            if out!=((r.get("base_action") or {}).get("market") or []):changed+=1

    kinds=sorted({r["kind"] for r in retained})
    pos_source_union=sorted({s for r in retained for s in r["positive_sources"]})
    ready=(
        len(retained)>=3 and REQUIRED_KINDS.issubset(set(kinds))
        and len(pos_source_union)>=4
        and all(r.get("json_parity") for r in retained)
        and compiler_ok
    )
    decision="V18B2_EVENT_CONTROLLER_READY_FOR_CAUSAL" if ready else "V18B2_EVENT_CONTROLLER_NOT_DISTILLABLE"
    result={
      "schema":"kculture-all3-v18b2-p2-event-controller-v1",
      "source_dataset_workflow":35552335995,
      "scope":[464,591],
      "decision":decision,
      "dataset_rows":len(rows),"contexts":len(contexts),"sources":len(sources),
      "predictor_feature_count":len(names),"predictor_feature_names":names,
      "eligible_family_count":len(fams),"family_results":results,
      "retained_families":retained,"retained_count":len(retained),"retained_kinds":kinds,
      "retained_positive_sources":len(pos_source_union),
      "json_parity_pass":all(r.get("json_parity") for r in retained),
      "compiler_structural_pass":compiler_ok,"compiled_changed_rows":changed,
      "runtime_state":"previous legal V18B feature vector and previous exact ALL3 market only",
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18B2_RESULT",json.dumps({
      "decision":decision,"dataset_rows":len(rows),"predictor_feature_count":len(names),
      "eligible_family_count":len(fams),"retained_count":len(retained),"retained_kinds":kinds,
      "retained_families":[{"family_id":r["family_id"],"kind":r["kind"],"product":r["product"],
        "direction":r["direction"],"positive_support":r["positive_support"],
        "positive_source_support":r["positive_source_support"],"oof_metrics":r["oof_metrics"]} for r in retained],
      "json_parity_pass":result["json_parity_pass"],
      "compiler_structural_pass":compiler_ok,"compiled_changed_rows":changed
    },sort_keys=True),flush=True)
    if not ready:raise SystemExit(2)

if __name__=="__main__":main()
