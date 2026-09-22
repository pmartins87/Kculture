#!/usr/bin/env python3
"""Fit/evaluate the pre-registered V27D bounded-history behavioral clone."""
from __future__ import annotations
import argparse,json,os,sys
from collections import defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.bounded_transaction_oracle_v1 import canonical_action

COMPONENTS=("market","farmer","hands")

def load_data(root):
    Xs=[];rows=[];metas=[]
    for meta_path in sorted(Path(root).rglob("meta.json")):
        d=meta_path.parent
        meta=json.loads(meta_path.read_text());metas.append(meta)
        X=np.load(d/"X.npy",allow_pickle=False)
        rr=[json.loads(line) for line in (d/"rows.jsonl").read_text().splitlines() if line.strip()]
        if X.shape[0]!=len(rr):raise RuntimeError(f"X/row mismatch {d}")
        Xs.append(X);rows.extend(rr)
    if len(metas)!=12 or {int(m["shard_index"]) for m in metas}!=set(range(12)):
        raise RuntimeError(f"expected 12 shards, got {len(metas)}")
    if not all(m.get("mechanical_pass") for m in metas):
        raise RuntimeError("collector shard mechanical failure")
    return np.concatenate(Xs,axis=0),rows,metas

def make_model(n_classes):
    if n_classes<=64:
        return "HistGradientBoostingClassifier",HistGradientBoostingClassifier(
          learning_rate=0.08,
          max_iter=150,
          max_leaf_nodes=31,
          min_samples_leaf=20,
          l2_regularization=1.0,
          early_stopping=False,
          random_state=20260922,
        )
    return "RandomForestClassifier",RandomForestClassifier(
      n_estimators=160,
      max_depth=24,
      min_samples_leaf=2,
      max_features="sqrt",
      class_weight="balanced_subsample",
      n_jobs=-1,
      random_state=20260922,
    )

def decode_action(market,farmer,hands):
    return {
      "market":json.loads(market),
      "farmer":json.loads(farmer),
      "hands":json.loads(hands),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--model-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    X,rows,metas=load_data(args.input_dir)
    if X.shape[1]!=1254:raise SystemExit(f"feature dim mismatch {X.shape}")

    split=np.array([r["split"] for r in rows],dtype=object)
    idx_train=np.flatnonzero(split=="train")
    idx_val=np.flatnonzero(split=="validation")
    idx_test=np.flatnonzero(split=="test")
    if not len(idx_train) or not len(idx_val) or not len(idx_test):raise SystemExit("missing split")

    model_dir=Path(args.model_dir);model_dir.mkdir(parents=True,exist_ok=True)
    predictions={}
    component_metrics={}
    failures=[]

    for comp in COMPONENTS:
        y=np.array([r[comp] for r in rows],dtype=object)
        enc=LabelEncoder()
        enc.fit(y[idx_train])
        unseen_val=sorted(set(y[idx_val])-set(enc.classes_))
        unseen_test=sorted(set(y[idx_test])-set(enc.classes_))
        if unseen_val or unseen_test:
            failures.append({
              "component":comp,
              "phase":"unseen_labels",
              "unseen_validation":len(unseen_val),
              "unseen_test":len(unseen_test),
            })
            continue

        ytr=enc.transform(y[idx_train])
        model_name,model=make_model(len(enc.classes_))
        fallback_reason=None
        try:
            model.fit(X[idx_train],ytr)
        except (MemoryError,ValueError) as exc:
            if model_name=="HistGradientBoostingClassifier":
                fallback_reason=f"{type(exc).__name__}: {exc}"
                model_name="RandomForestClassifier"
                model=RandomForestClassifier(
                  n_estimators=160,max_depth=24,min_samples_leaf=2,max_features="sqrt",
                  class_weight="balanced_subsample",n_jobs=-1,random_state=20260922,
                )
                model.fit(X[idx_train],ytr)
            else:
                raise

        pv=enc.inverse_transform(model.predict(X[idx_val]))
        pt=enc.inverse_transform(model.predict(X[idx_test]))
        predictions[comp]={"validation":pv,"test":pt}
        av=float(np.mean(pv==y[idx_val]))
        at=float(np.mean(pt==y[idx_test]))
        component_metrics[comp]={
          "model":model_name,
          "training_classes":int(len(enc.classes_)),
          "validation_accuracy":av,
          "test_accuracy":at,
          "fallback_reason":fallback_reason,
        }
        joblib.dump({"model":model,"classes":enc.classes_},model_dir/f"{comp}_model.joblib",compress=3)

    if failures:
        decision="V27D_MECHANICS_INVALID"
        mechanical=False
        complete_val=None;complete_test=None;min_source=None;invalid=0
    else:
        mechanical=True
        true_complete=np.array([r["complete"] for r in rows],dtype=object)

        def reconstructed(split_name,indices):
            pm=predictions["market"][split_name]
            pf=predictions["farmer"][split_name]
            ph=predictions["hands"][split_name]
            out=[]
            invalid=0
            for a,b,c in zip(pm,pf,ph):
                try:
                    act=canonical_action(decode_action(a,b,c))
                    out.append(json.dumps(act,sort_keys=True,separators=(",",":")))
                except Exception:
                    invalid+=1;out.append("__INVALID__")
            return np.array(out,dtype=object),invalid

        rv,inv_v=reconstructed("validation",idx_val)
        rt,inv_t=reconstructed("test",idx_test)
        invalid=inv_v+inv_t
        complete_val=float(np.mean(rv==true_complete[idx_val]))
        complete_test=float(np.mean(rt==true_complete[idx_test]))

        by_source=defaultdict(list)
        for local_i,global_i in enumerate(idx_test):
            by_source[rows[global_i]["source_sha"]].append(bool(rt[local_i]==true_complete[global_i]))
        source_acc={sha:sum(v)/len(v) for sha,v in by_source.items()}
        min_source=min(source_acc.values()) if source_acc else None

        gate=(
          component_metrics["market"]["test_accuracy"]>=0.97
          and component_metrics["farmer"]["test_accuracy"]>=0.995
          and component_metrics["hands"]["test_accuracy"]>=0.98
          and complete_test>=0.95
          and min_source>=0.90
          and invalid==0
        )
        decision="V27D_BEHAVIORAL_CLONE_OFFLINE_PASS" if gate else "V27D_BEHAVIORAL_CLONE_OFFLINE_FAIL"

    summary={
      "schema":"kculture-v27d-bounded-history-behavioral-clone-v1",
      "mechanical_pass":mechanical,
      "decision":decision,
      "rows":len(rows),
      "feature_dim":int(X.shape[1]),
      "split_rows":{"train":int(len(idx_train)),"validation":int(len(idx_val)),"test":int(len(idx_test))},
      "component_metrics":component_metrics,
      "validation_complete_action_accuracy":complete_val,
      "test_complete_action_accuracy":complete_test,
      "minimum_test_source_complete_action_accuracy":min_source,
      "invalid_reconstructed_actions":invalid,
      "failures":failures,
      "history_window":256,
      "source_identity_feature_used":False,
      "automatic_kaggle_submission":False,
    }
    outp=Path(args.out);outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("V27D_RESULT",json.dumps({
      "decision":decision,
      "mechanical_pass":mechanical,
      "rows":len(rows),
      "component_metrics":component_metrics,
      "validation_complete_action_accuracy":complete_val,
      "test_complete_action_accuracy":complete_test,
      "minimum_test_source_complete_action_accuracy":min_source,
      "invalid_reconstructed_actions":invalid,
      "failures":len(failures),
    },sort_keys=True))
    if not mechanical:raise SystemExit(2)

if __name__=="__main__":main()
