#!/usr/bin/env python3
"""V27C bounded-history behavioral distillation census shard."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
from collections import Counter, deque
from pathlib import Path

import numpy as np
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from solver.programme_features import features as programme_features
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE, load_public_agent, purge_package_modules, sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79901,79902,79903,79904)
SEATS=(0,1)
LAGS=(1,4,16,64,128,256)
WINDOW=256

def canon_label(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def split_name(seed):
    if seed in (79901,79902):
        return "train"
    if seed==79903:
        return "validation"
    if seed==79904:
        return "test"
    raise RuntimeError(seed)

def build_rep(current,hist):
    cur=np.asarray(current,dtype=np.float32)
    blocks=[cur]
    if hist:
        earliest=hist[0]
    else:
        earliest=cur
    n=len(hist)
    for lag in LAGS:
        if n>=lag:
            blocks.append(hist[-lag])
        else:
            blocks.append(earliest)
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
    out=np.concatenate(blocks).astype(np.float32,copy=False)
    return out

def feature_hash(vec):
    return hashlib.sha256(memoryview(np.ascontiguousarray(vec)).tobytes()).hexdigest()

class CensusCandidate:
    def __init__(self,teacher_main,source_sha,seed,seat):
        purge_package_modules(teacher_main.parent)
        self.fn=load_public_agent(teacher_main)
        self.hist=deque(maxlen=WINDOW)
        self.rows=[]
        self.source_sha=source_sha
        self.seed=int(seed)
        self.seat=int(seat)

    def __call__(self,obs,config=None):
        feat=np.asarray(programme_features(copy.deepcopy(obs)),dtype=np.float32)
        rep=build_rep(feat,list(self.hist))
        action=canonical_action(call_agent(self.fn,obs,config))
        row={
          "feature_hash":feature_hash(rep),
          "step":int((obs or {}).get("step",len(self.rows))),
          "seed":self.seed,
          "seat":self.seat,
          "split":split_name(self.seed),
          "source_sha":self.source_sha,
          "complete":canon_label(action),
          "market":canon_label(action.get("market")),
          "farmer":canon_label(action.get("farmer")),
          "hands":canon_label(action.get("hands")),
        }
        self.rows.append(row)
        self.hist.append(feat)
        return action

def run_one(teacher_main,opp_main,source_sha,seed,seat):
    purge_package_modules(teacher_main.parent)
    purge_package_modules(opp_main.parent)
    cand=CensusCandidate(teacher_main,source_sha,seed,seat)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    if len(cand.rows)<700:
        raise RuntimeError(f"too few candidate calls {len(cand.rows)}")
    return cand.rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=12)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(args.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    sources=list(manifest["sources"])
    teacher_meta=next((s for s in sources if int(s["representative_rank"])==1),None)
    if teacher_meta is None or str(teacher_meta["sha"])!=TEACHER_SHA:
        raise SystemExit(f"rank1 teacher mismatch {teacher_meta}")
    teacher_main=root/teacher_meta["path"]
    if sha256_bytes(teacher_main.read_bytes())!=TEACHER_SHA:
        raise SystemExit("teacher snapshot SHA mismatch")

    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]
    rows=[]
    failures=[]
    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(key,None)

    for src in selected:
        opp_main=root/src["path"]
        if sha256_bytes(opp_main.read_bytes())!=str(src["sha"]):
            failures.append({"phase":"opponent_sha","sha":src["sha"],"error":"snapshot SHA mismatch"})
            continue
        for seed in SEEDS:
            for seat in SEATS:
                key={
                  "source_rank":int(src["representative_rank"]),
                  "ref":src["representative_ref"],
                  "main_sha256":src["sha"],
                  "seed":int(seed),
                  "seat":int(seat),
                }
                try:
                    rr=run_one(teacher_main,opp_main,str(src["sha"]),seed,seat)
                    rows.extend(rr)
                    print("V27C_EPISODE",json.dumps({
                      **key,"rows":len(rr),"split":split_name(seed)
                    },sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({**key,"phase":"episode","error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(teacher_main.parent)
                    purge_package_modules(opp_main.parent)

    expected_episodes=len(selected)*len(SEEDS)*len(SEATS)
    actual_episodes=len({(r["source_sha"],r["seed"],r["seat"]) for r in rows})
    mech=not failures and actual_episodes==expected_episodes

    result={
      "schema":"kculture-v27c-bounded-history-census-shard-v1",
      "mechanical_pass":mech,
      "shard_index":args.shard_index,
      "num_shards":args.num_shards,
      "teacher_sha":TEACHER_SHA,
      "history_window":WINDOW,
      "lags":list(LAGS),
      "representation_blocks":11,
      "feature_dim":114*11,
      "expected_episodes":expected_episodes,
      "actual_episodes":actual_episodes,
      "row_count":len(rows),
      "rows":rows,
      "failures":failures,
      "immutable_snapshot_used":True,
      "live_kaggle_reacquisition_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,separators=(",",":"))+"\n")
    print("V27C_SHARD_RESULT",json.dumps({
      "shard":args.shard_index,"mechanical_pass":mech,
      "episodes":actual_episodes,"rows":len(rows),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
