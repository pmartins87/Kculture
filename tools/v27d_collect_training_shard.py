#!/usr/bin/env python3
"""Collect V27D full bounded-history training matrices from immutable snapshot."""
from __future__ import annotations
import argparse,copy,json,math,os,sys
from collections import deque
from pathlib import Path
import numpy as np
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from solver.programme_features import features as programme_features
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79901,79902,79903,79904)
SEATS=(0,1)
LAGS=(1,4,16,64,128,256)
WINDOW=256

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def split_name(seed):
    return "train" if seed in (79901,79902) else ("validation" if seed==79903 else "test")

def build_rep(cur,hist):
    cur=np.asarray(cur,dtype=np.float32)
    blocks=[cur]
    earliest=hist[0] if hist else cur
    n=len(hist)
    for lag in LAGS:
        blocks.append(hist[-lag] if n>=lag else earliest)
    if hist:
        arr=np.stack(hist,axis=0)
        blocks.extend([
            np.min(arr,axis=0),
            np.max(arr,axis=0),
            np.mean(arr,axis=0,dtype=np.float32),
            cur-arr[0],
        ])
    else:
        blocks.extend([cur,cur,cur,np.zeros_like(cur)])
    return np.concatenate(blocks).astype(np.float32,copy=False)

class Collector:
    def __init__(self,teacher_main,source_sha,seed,seat):
        purge_package_modules(teacher_main.parent)
        self.fn=load_public_agent(teacher_main)
        self.hist=deque(maxlen=WINDOW)
        self.X=[]
        self.rows=[]
        self.source_sha=str(source_sha)
        self.seed=int(seed)
        self.seat=int(seat)
    def __call__(self,obs,config=None):
        feat=np.asarray(programme_features(copy.deepcopy(obs)),dtype=np.float32)
        self.X.append(build_rep(feat,list(self.hist)))
        action=canonical_action(call_agent(self.fn,obs,config))
        self.rows.append({
          "source_sha":self.source_sha,
          "seed":self.seed,
          "seat":self.seat,
          "step":int((obs or {}).get("step",len(self.rows))),
          "split":split_name(self.seed),
          "complete":canon(action),
          "market":canon(action.get("market")),
          "farmer":canon(action.get("farmer")),
          "hands":canon(action.get("hands")),
        })
        self.hist.append(feat)
        return action

def run_one(teacher,opp,source_sha,seed,seat):
    purge_package_modules(teacher.parent);purge_package_modules(opp.parent)
    c=Collector(teacher,source_sha,seed,seat)
    purge_package_modules(opp.parent);o=load_public_agent(opp)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([c,o])
    else:env.run([o,c])
    p=env.toJSON()
    sts=[str(x) for x in p.get("statuses",[])]
    rw=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if sts!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {sts} steps={steps}")
    if len(c.rows)<700 or len(c.X)!=len(c.rows):
        raise RuntimeError(f"bad row count X={len(c.X)} rows={len(c.rows)}")
    return np.stack(c.X).astype(np.float32),c.rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=12)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    root=Path(args.snapshot_dir);man=json.loads((root/"MANIFEST.json").read_text());sources=list(man["sources"])
    tm=next((s for s in sources if int(s["representative_rank"])==1),None)
    if tm is None or str(tm["sha"])!=TEACHER_SHA:raise SystemExit("teacher mismatch")
    teacher=root/tm["path"]
    if sha256_bytes(teacher.read_bytes())!=TEACHER_SHA:raise SystemExit("teacher SHA mismatch")
    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]

    xs=[];rows=[];failures=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
    for s in selected:
        opp=root/s["path"]
        if sha256_bytes(opp.read_bytes())!=str(s["sha"]):
            failures.append({"phase":"sha","sha":s["sha"]});continue
        for seed in SEEDS:
            for seat in SEATS:
                try:
                    X,rr=run_one(teacher,opp,str(s["sha"]),seed,seat)
                    xs.append(X);rows.extend(rr)
                except Exception as exc:
                    failures.append({"sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(teacher.parent);purge_package_modules(opp.parent)

    X=np.concatenate(xs,axis=0) if xs else np.zeros((0,1254),dtype=np.float32)
    if X.shape[0]!=len(rows):raise SystemExit("X/rows mismatch")
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    np.save(out/"X.npy",X,allow_pickle=False)
    with (out/"rows.jsonl").open("w") as fh:
        for r in rows:fh.write(json.dumps(r,separators=(",",":"))+"\n")
    meta={
      "schema":"kculture-v27d-training-shard-v1",
      "shard_index":args.shard_index,"num_shards":args.num_shards,
      "rows":len(rows),"feature_dim":int(X.shape[1]),"failures":failures,
      "mechanical_pass":not failures and len(rows)>=5600,
      "history_window":256,"automatic_kaggle_submission":False,
    }
    (out/"meta.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("V27D_COLLECT_RESULT",json.dumps(meta,sort_keys=True))
    if not meta["mechanical_pass"]:raise SystemExit(2)

if __name__=="__main__":main()
