#!/usr/bin/env python3
"""V18B P2 cumulative market-controller distillation with leave-one-source-out validation."""
from __future__ import annotations
import argparse,collections,copy,json,math
from pathlib import Path
import numpy as np
from sklearn.tree import DecisionTreeClassifier

REAL_PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
ACTIONABLE_KINDS={"QTY","PRESENCE","DUPLICATE"}
BUCKET_MIN={"1":1,"2":2,"3-4":3,"5+":5}
PROHIBITED_TOKENS=("source","sha","ref","rank","context","seed","seat","result","margin","reward","outcome")

def tree_json(clf,names):
    t=clf.tree_
    def node(i):
        vals=t.value[i][0].tolist()
        pred=int(clf.classes_[int(np.argmax(vals))])
        if t.children_left[i]==t.children_right[i]:
            return {"leaf":True,"prediction":pred,"n":int(t.n_node_samples[i])}
        return {
          "leaf":False,"feature":names[int(t.feature[i])],"threshold":float(t.threshold[i]),
          "n":int(t.n_node_samples[i]),
          "left":node(int(t.children_left[i])),"right":node(int(t.children_right[i]))
        }
    return node(0)

def json_predict(tree,row):
    n=tree
    while not n.get("leaf"):
        n=n["left"] if float(row.get(n["feature"],0.0))<=float(n["threshold"]) else n["right"]
    return int(n["prediction"])

def metric(y,pred):
    y=np.asarray(y,dtype=np.int8);pred=np.asarray(pred,dtype=np.int8)
    tp=int(np.sum((y==1)&(pred==1)));fp=int(np.sum((y==0)&(pred==1)))
    fn=int(np.sum((y==1)&(pred==0)));tn=int(np.sum((y==0)&(pred==0)))
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":precision,"recall":recall,"f1":f1}

def actionable_families(v14b,rows):
    labels_present=collections.Counter()
    for r in rows:
        for x in r.get("labels") or []:labels_present[str(x["family_id"])]+=1
    out=[]
    for f in v14b.get("recurrent_families") or []:
        e=f.get("representative_element") or {}
        kind=str(e.get("kind",""));side=str(e.get("side",""));product=str(e.get("product",""))
        direction=str(f.get("dominant_direction",""))
        fid=f"{f.get('group_key')}||{direction}"
        if labels_present[fid]<=0:continue
        if kind not in ACTIONABLE_KINDS or side!="SELL" or product not in REAL_PRODUCTS:continue
        if kind=="QTY" and str(e.get("magnitude_bucket","")) not in BUCKET_MIN:continue
        out.append({
          "family_id":fid,"group_key":str(f.get("group_key")),"kind":kind,"side":side,"product":product,
          "direction":direction,"magnitude_bucket":str(e.get("magnitude_bucket","")),
          "atlas_context_support":int(f.get("context_support",0)),
          "atlas_source_support":int(f.get("source_support",0)),
          "dataset_positive_rows":int(labels_present[fid]),
        })
    out.sort(key=lambda x:x["family_id"])
    return out

def family_y(rows,fid):
    return np.asarray([int(any(str(x.get("family_id"))==fid for x in (r.get("labels") or []))) for r in rows],dtype=np.int8)

def matrix(rows,names):
    return np.asarray([[float((r.get("features") or {}).get(n,0.0)) for n in names] for r in rows],dtype=np.float64)

def first_free(market):
    for i,o in enumerate(market):
        if not bool(list(o or [])):return i
    return len(market)

def order_parts(o):
    x=list(o or [])
    side=str(x[0]) if x else "EMPTY";product=str(x[1]) if len(x)>1 else "_"
    try:qty=int(x[2]) if len(x)>2 else 1
    except:qty=1
    return side,product,qty

def compact_product(market,product):
    idx=[];total=0
    for i,o in enumerate(market):
        s,p,q=order_parts(o)
        if s=="SELL" and p==product:idx.append(i);total+=max(0,q)
    if len(idx)<=1:return market
    market=copy.deepcopy(market)
    market[idx[0]]=["SELL",product,total]
    for i in idx[1:]:market[i]=[]
    return market

def split_product(market,product):
    idx=[]
    for i,o in enumerate(market):
        s,p,q=order_parts(o)
        if s=="SELL" and p==product:idx.append((i,q))
    if len(idx)!=1 or idx[0][1]<2:return market
    market=copy.deepcopy(market);i,q=idx[0];market[i]=["SELL",product,1]
    j=first_free(market)
    if j==len(market):market.append(["SELL",product,q-1])
    else:market[j]=["SELL",product,q-1]
    return market

def compile_market(row,predicted,meta_by_id):
    base=copy.deepcopy((row.get("base_action") or {}).get("market") or [])
    features=row.get("features") or {}
    by_product=collections.defaultdict(list)
    for fid in predicted:by_product[meta_by_id[fid]["product"]].append(meta_by_id[fid])

    for product in sorted(by_product):
        fs=by_product[product]
        remove=[f for f in fs if f["kind"]=="PRESENCE" and f["direction"]=="REMOVE"]
        if remove:
            for i,o in enumerate(base):
                s,p,_q=order_parts(o)
                if s=="SELL" and p==product:base[i]=[]
            continue

        qty=[f for f in fs if f["kind"]=="QTY"]
        qty.sort(key=lambda f:(-int(f["positive_support"]),f["family_id"]))
        qf=qty[0] if qty else None
        delta=0
        if qf:
            d=BUCKET_MIN[qf["magnitude_bucket"]]
            delta=d if qf["direction"]=="INC" else -d

        add=any(f["kind"]=="PRESENCE" and f["direction"]=="ADD" for f in fs)
        sell_idx=[];aggregate=0
        for i,o in enumerate(base):
            s,p,q=order_parts(o)
            if s=="SELL" and p==product:sell_idx.append(i);aggregate+=max(0,q)

        available=max(0,int(float(features.get(f"available_{product}",0.0))))
        if aggregate<=0 and add:
            q=max(1,delta if delta>0 else 1)
            q=min(q,available)
            if q>0:
                j=first_free(base)
                if j==len(base):base.append(["SELL",product,q])
                else:base[j]=["SELL",product,q]
        elif aggregate>0 and qf:
            target=max(0,min(available,aggregate+delta))
            if sell_idx:
                first=sell_idx[0]
                others=sum(max(0,order_parts(base[i])[2]) for i in sell_idx[1:])
                first_q=max(0,target-others)
                base[first]=["SELL",product,first_q] if first_q>0 else []
        dups=[f for f in fs if f["kind"]=="DUPLICATE"]
        dups.sort(key=lambda f:(-int(f["positive_support"]),f["family_id"]))
        if dups:
            if dups[0]["direction"]=="COMPACT":base=compact_product(base,product)
            elif dups[0]["direction"]=="SPLIT":base=split_product(base,product)
    return base

def structurally_valid(row,market):
    if not isinstance(market,list):return False
    features=row.get("features") or {}
    agg=collections.Counter()
    for o in market:
        if not bool(list(o or [])):continue
        if not isinstance(o,list) or len(o)<1:return False
        s,p,q=order_parts(o)
        if s=="SELL":
            if p not in REAL_PRODUCTS or q<=0:return False
            agg[p]+=q
    for p,q in agg.items():
        if q>int(float(features.get(f"available_{p}",0.0))):return False
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True);ap.add_argument("--v14b",required=True);ap.add_argument("--out",required=True)
    args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    if len(docs)!=4 or len(rows)!=3072 or failures or not all(d.get("mechanical_pass") for d in docs):
        raise RuntimeError(f"V18B dataset mechanical failure docs={len(docs)} rows={len(rows)} failures={len(failures)}")
    contexts={str(r["context_id"]) for r in rows}
    sources=sorted({str(r["main_sha256"]) for r in rows})
    if len(contexts)!=24 or len(sources)!=10:raise RuntimeError(f"dataset support mismatch contexts={len(contexts)} sources={len(sources)}")

    feature_names=sorted((rows[0].get("features") or {}).keys())
    if not feature_names:raise RuntimeError("empty feature schema")
    for r in rows:
        if sorted((r.get("features") or {}).keys())!=feature_names:raise RuntimeError("feature schema drift")
    bad=[n for n in feature_names if any(tok in n.lower() for tok in PROHIBITED_TOKENS)]
    if bad:raise RuntimeError(f"prohibited predictive features: {bad}")

    X=matrix(rows,feature_names)
    v14b=json.loads(Path(args.v14b).read_text())
    families=actionable_families(v14b,rows)
    retained=[];all_results=[]
    source_arr=np.asarray([str(r["main_sha256"]) for r in rows],dtype=object)

    for fam in families:
        fid=fam["family_id"];y=family_y(rows,fid)
        pos_sources=sorted({str(rows[i]["main_sha256"]) for i in np.flatnonzero(y==1)})
        oof=np.zeros(len(rows),dtype=np.int8)
        fold_rows=[]
        for hold in sources:
            train_idx=np.flatnonzero(source_arr!=hold);test_idx=np.flatnonzero(source_arr==hold)
            min_leaf=max(8,int(math.ceil(0.01*len(train_idx))))
            clf=DecisionTreeClassifier(max_depth=4,min_samples_leaf=min_leaf,class_weight="balanced",random_state=20260920)
            clf.fit(X[train_idx],y[train_idx])
            oof[test_idx]=clf.predict(X[test_idx]).astype(np.int8)
            fold_rows.append({"holdout_source":hold,"train_rows":len(train_idx),"test_rows":len(test_idx),"min_leaf":min_leaf})
        m=metric(y,oof)
        tp_sources=sorted({str(rows[i]["main_sha256"]) for i in np.flatnonzero((y==1)&(oof==1))})
        eligible=(len(pos_sources)>=4 and m["precision"]>=0.80 and m["recall"]>=0.70 and m["f1"]>=0.75)
        rec={**fam,"positive_source_support":len(pos_sources),"positive_sources":pos_sources,
             "oof_tp_source_support":len(tp_sources),"oof_metrics":m,"folds":fold_rows,"retained":eligible}
        if eligible:
            min_leaf=max(8,int(math.ceil(0.01*len(rows))))
            clf=DecisionTreeClassifier(max_depth=4,min_samples_leaf=min_leaf,class_weight="balanced",random_state=20260920)
            clf.fit(X,y)
            tree=tree_json(clf,feature_names)
            sk=clf.predict(X).astype(np.int8)
            js=np.asarray([json_predict(tree,r["features"]) for r in rows],dtype=np.int8)
            parity=bool(np.array_equal(sk,js))
            if not parity:raise RuntimeError(f"JSON parity failure {fid}")
            rec["final_min_leaf"]=min_leaf;rec["tree"]=tree;rec["json_parity"]=parity
            rec["positive_support"]=int(np.sum(y))
            retained.append(rec)
        all_results.append(rec)

    meta={r["family_id"]:r for r in retained}
    compiled_valid=True;compiled_changed=0
    if retained:
        for i,row in enumerate(rows):
            pred=[]
            for fam in retained:
                if json_predict(fam["tree"],row["features"])==1:pred.append(fam["family_id"])
            out=compile_market(row,pred,meta)
            if not structurally_valid(row,out):
                compiled_valid=False;break
            if out!=((row.get("base_action") or {}).get("market") or []):compiled_changed+=1

    kinds=sorted({r["kind"] for r in retained})
    retained_positive_sources=sorted({s for r in retained for s in r["positive_sources"]})
    pass_gate=(
      len(retained)>=3 and len(kinds)>=3 and len(retained_positive_sources)>=4
      and all(r.get("json_parity") for r in retained) and compiled_valid
    )
    decision="V18B_CONTROLLER_READY_FOR_CAUSAL" if pass_gate else "V18B_CONTROLLER_NOT_DISTILLABLE"
    result={
      "schema":"kculture-all3-v18b-p2-market-controller-v1",
      "scope":[464,591],"mechanical_pass":True,"decision":decision,
      "dataset_rows":len(rows),"contexts":len(contexts),"sources":len(sources),
      "feature_names":feature_names,"prohibited_feature_hits":bad,
      "eligible_family_count":len(families),"family_results":all_results,
      "retained_families":retained,"retained_count":len(retained),
      "retained_kinds":kinds,"retained_positive_sources":len(retained_positive_sources),
      "json_parity_pass":all(r.get("json_parity") for r in retained),
      "compiler_structural_pass":compiled_valid,"compiled_changed_rows":compiled_changed,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18B_RESULT",json.dumps({
      "decision":decision,"dataset_rows":len(rows),"eligible_family_count":len(families),
      "retained_count":len(retained),"retained_kinds":kinds,
      "retained_families":[{"family_id":r["family_id"],"kind":r["kind"],"product":r["product"],
        "direction":r["direction"],"positive_support":r["positive_support"],
        "positive_source_support":r["positive_source_support"],"oof_metrics":r["oof_metrics"]} for r in retained],
      "json_parity_pass":result["json_parity_pass"],"compiler_structural_pass":compiled_valid,
      "compiled_changed_rows":compiled_changed
    },sort_keys=True),flush=True)
    if not pass_gate:raise SystemExit(2)

if __name__=="__main__":main()
