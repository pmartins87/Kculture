#!/usr/bin/env python3
"""V27C collect rank-1 teacher behavioral data from immutable V26A snapshot."""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from solver.programme_features import features as programme_features
from tools.kaggle_exact_runtime import plain
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79901,79902,79903,79904,79905,79906,79907,79908)
SEATS=(0,1)

def jkey(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))

class Recorder:
    def __init__(self,teacher_main):
        purge_package_modules(teacher_main.parent)
        self.fn=load_public_agent(teacher_main)
        self.features=[]
        self.steps=[]
        self.market=[]
        self.farmer=[]
        self.hands=[]
        self.complete=[]

    def __call__(self,obs,config=None):
        action=canonical_action(call_agent(self.fn,obs,config))
        feat=np.asarray(programme_features(plain(obs)),dtype=np.float32)
        if feat.shape!=(114,):
            raise RuntimeError(f"unexpected programme feature shape {feat.shape}")
        self.features.append(feat)
        self.steps.append(int((obs or {}).get("step",len(self.steps))))
        self.market.append(jkey(action.get("market")))
        self.farmer.append(jkey(action.get("farmer")))
        self.hands.append(jkey(action.get("hands")))
        self.complete.append(jkey(action))
        return action

def run_episode(teacher_main,opp_main,seed,seat):
    purge_package_modules(teacher_main.parent)
    purge_package_modules(opp_main.parent)
    cand=Recorder(teacher_main)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)

    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])

    payload=env.toJSON()
    statuses=[str(x) for x in payload.get("statuses",[])]
    rewards=[float(x) for x in payload.get("rewards",[])]
    steps=len(payload.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    if len(cand.steps)<719 or 0 not in cand.steps or 718 not in cand.steps:
        raise RuntimeError(f"incomplete candidate calls n={len(cand.steps)} first={cand.steps[:3]} last={cand.steps[-3:]}")
    return cand

def encode_labels(values):
    vocab=sorted(set(values))
    enc={v:i for i,v in enumerate(vocab)}
    ids=np.asarray([enc[v] for v in values],dtype=np.uint16)
    return vocab,ids

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=12)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(args.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    sources=list(manifest["sources"])
    teacher_meta=next(s for s in sources if int(s["representative_rank"])==1)
    teacher_main=root/teacher_meta["path"]
    if sha256_bytes(teacher_main.read_bytes())!=TEACHER_SHA:
        raise SystemExit("teacher snapshot SHA mismatch")

    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]
    if len(selected)!=1:
        raise SystemExit(f"expected exactly one source for 12-way collection, got {len(selected)}")
    src=selected[0]
    opp_main=root/src["path"]
    if sha256_bytes(opp_main.read_bytes())!=str(src["sha"]):
        raise SystemExit("opponent snapshot SHA mismatch")

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    all_features=[]
    all_steps=[]
    all_episode_idx=[]
    market=[]
    farmer=[]
    hands=[]
    complete=[]
    episodes=[]
    failures=[]
    cursor=0

    for seed in SEEDS:
        for seat in SEATS:
            ep_idx=len(episodes)
            try:
                rec=run_episode(teacher_main,opp_main,seed,seat)
                n=len(rec.steps)
                all_features.extend(rec.features)
                all_steps.extend(rec.steps)
                all_episode_idx.extend([ep_idx]*n)
                market.extend(rec.market)
                farmer.extend(rec.farmer)
                hands.extend(rec.hands)
                complete.extend(rec.complete)
                episodes.append({
                    "episode_index":ep_idx,
                    "source_rank":int(src["representative_rank"]),
                    "ref":src["representative_ref"],
                    "main_sha256":src["sha"],
                    "seed":int(seed),
                    "seat":int(seat),
                    "start":cursor,
                    "end":cursor+n,
                    "calls":n,
                })
                cursor+=n
                print("V27C_DATA_EPISODE",json.dumps({
                    "source_rank":int(src["representative_rank"]),
                    "seed":seed,"seat":seat,"calls":n
                },sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({
                    "source_rank":int(src["representative_rank"]),
                    "ref":src["representative_ref"],
                    "main_sha256":src["sha"],
                    "seed":int(seed),"seat":int(seat),
                    "error":f"{type(exc).__name__}: {exc}",
                })
            finally:
                purge_package_modules(teacher_main.parent)
                purge_package_modules(opp_main.parent)

    expected=len(SEEDS)*len(SEATS)
    mech=not failures and len(episodes)==expected

    outdir=Path(args.out_dir)
    outdir.mkdir(parents=True,exist_ok=True)

    if all_features:
        X=np.stack(all_features).astype(np.float32,copy=False)
    else:
        X=np.zeros((0,114),dtype=np.float32)

    mv,mi=encode_labels(market)
    fv,fi=encode_labels(farmer)
    hv,hi=encode_labels(hands)
    cv,ci=encode_labels(complete)

    np.savez_compressed(
        outdir/"DATA.npz",
        current_features=X,
        steps=np.asarray(all_steps,dtype=np.int16),
        episode_index=np.asarray(all_episode_idx,dtype=np.int16),
        market_id=mi,
        farmer_id=fi,
        hands_id=hi,
        complete_id=ci,
    )

    meta={
        "schema":"kculture-v27c-teacher-dataset-shard-v1",
        "mechanical_pass":mech,
        "shard_index":args.shard_index,
        "num_shards":args.num_shards,
        "teacher_sha":TEACHER_SHA,
        "source_rank":int(src["representative_rank"]),
        "source_ref":src["representative_ref"],
        "source_sha":src["sha"],
        "seeds":list(SEEDS),
        "seats":list(SEATS),
        "episodes":episodes,
        "rows":int(X.shape[0]),
        "feature_dim":int(X.shape[1]) if X.ndim==2 else 0,
        "vocabs":{
            "market":mv,
            "farmer":fv,
            "hands":hv,
            "complete":cv,
        },
        "failures":failures,
        "immutable_snapshot_used":True,
        "live_kaggle_reacquisition_used":False,
        "automatic_kaggle_submission":False,
    }
    (outdir/"META.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")

    print("V27C_DATA_SHARD_RESULT",json.dumps({
        "shard":args.shard_index,
        "rank":int(src["representative_rank"]),
        "mechanical_pass":mech,
        "episodes":len(episodes),
        "rows":int(X.shape[0]),
        "failures":len(failures),
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
