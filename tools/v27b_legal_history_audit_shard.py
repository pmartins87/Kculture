#!/usr/bin/env python3
"""V27B legal-history reconstructibility audit shard.

Mechanical correction: the expensive history replays are performed only after the
binding episode completes. During the episode the ongoing teacher runs normally and
we only record its legal observations/actions. This avoids contaminating Kaggle's
per-turn runtime budget while preserving the frozen V27B semantics.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79801,79802,79803)
SEATS=(0,1)
CHECKPOINTS=(0,1,2,3,4,8,16,32,64,128,256,384,512,640,718)
HORIZONS=(0,1,2,4,8,16,32,64,128,256,512,"FULL")

def comp(a,b,k):
    return a.get(k)==b.get(k)

def replay_action(main_py,history,current,config,horizon):
    purge_package_modules(main_py.parent)
    fn=load_public_agent(main_py)
    if horizon=="FULL":
        prior=history
    else:
        prior=history[max(0,len(history)-int(horizon)):]
    for ob,cfg in prior:
        canonical_action(call_agent(fn,copy.deepcopy(ob),copy.deepcopy(cfg)))
    out=canonical_action(call_agent(fn,copy.deepcopy(current[0]),copy.deepcopy(current[1])))
    purge_package_modules(main_py.parent)
    return out

class RecorderCandidate:
    def __init__(self,teacher_main):
        purge_package_modules(teacher_main.parent)
        self.fn=load_public_agent(teacher_main)
        self.history=[]   # observations/configs before the current call
        self.records=[]   # all candidate calls; checkpoint action retained
        self.calls=0

    def __call__(self,obs,config=None):
        step=int((obs or {}).get("step",self.calls))
        self.calls+=1
        cfg=copy.deepcopy(config or {})
        ongoing=canonical_action(call_agent(self.fn,obs,config))
        rec={
            "step":step,
            "obs":copy.deepcopy(obs),
            "config":cfg,
            "ongoing":ongoing if step in CHECKPOINTS else None,
            "history_len":len(self.history),
        }
        self.records.append(rec)
        self.history.append((copy.deepcopy(obs),cfg))
        return ongoing

def run_episode(teacher_main,opp_main,seed,seat):
    purge_package_modules(teacher_main.parent)
    purge_package_modules(opp_main.parent)
    cand=RecorderCandidate(teacher_main)
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

    by_step={int(r["step"]):r for r in cand.records if int(r["step"]) in CHECKPOINTS}
    if set(by_step)!=set(CHECKPOINTS):
        raise RuntimeError(f"checkpoint capture mismatch got={sorted(by_step)} expected={list(CHECKPOINTS)}")

    samples=[]
    # Perform all counterfactual reconstruction only after the live episode has ended.
    for step in CHECKPOINTS:
        rec=by_step[step]
        hlen=int(rec["history_len"])
        prior=cand.history[:hlen]
        current=(rec["obs"],rec["config"])
        ongoing=rec["ongoing"]
        hs={}
        for h in HORIZONS:
            a=replay_action(teacher_main,prior,current,rec["config"],h)
            hs[str(h)]={
                "full_equal":a==ongoing,
                "market_equal":comp(a,ongoing,"market"),
                "farmer_equal":comp(a,ongoing,"farmer"),
                "hands_equal":comp(a,ongoing,"hands"),
            }
        samples.append({"step":step,"horizons":hs})

    return samples

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(a.snapshot_dir)
    man=json.loads((root/"MANIFEST.json").read_text())
    src=list(man["sources"])
    tm=next(x for x in src if int(x["representative_rank"])==1)
    teacher=root/tm["path"]
    if sha256_bytes(teacher.read_bytes())!=TEACHER_SHA:
        raise SystemExit("teacher SHA mismatch")

    selected=[x for i,x in enumerate(src) if i%a.num_shards==a.shard_index]
    rows=[]
    failures=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    for s in selected:
        opp=root/s["path"]
        if sha256_bytes(opp.read_bytes())!=str(s["sha"]):
            failures.append({
                "source_rank":int(s["representative_rank"]),
                "ref":s["representative_ref"],
                "main_sha256":s["sha"],
                "phase":"opponent_sha",
                "error":"snapshot SHA mismatch",
            })
            continue
        for seed in SEEDS:
            for seat in SEATS:
                key={
                    "source_rank":int(s["representative_rank"]),
                    "ref":s["representative_ref"],
                    "main_sha256":s["sha"],
                    "seed":int(seed),
                    "seat":int(seat),
                }
                try:
                    samples=run_episode(teacher,opp,seed,seat)
                    rows.append({**key,"samples":samples})
                    print("V27B_EPISODE",json.dumps({
                        **key,"samples":len(samples)
                    },sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({**key,"phase":"episode","error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(teacher.parent)
                    purge_package_modules(opp.parent)

    expected=len(selected)*len(SEEDS)*len(SEATS)
    expected_samples=expected*len(CHECKPOINTS)
    actual_samples=sum(len(r["samples"]) for r in rows)
    mech=not failures and len(rows)==expected and actual_samples==expected_samples

    out={
        "schema":"kculture-v27b-legal-history-audit-shard-v1",
        "mechanical_pass":mech,
        "shard_index":a.shard_index,
        "num_shards":a.num_shards,
        "rows":rows,
        "failures":failures,
        "horizons":[str(x) for x in HORIZONS],
        "checkpoints":list(CHECKPOINTS),
        "expected_episodes":expected,
        "expected_samples":expected_samples,
        "immutable_snapshot_used":True,
        "live_kaggle_reacquisition_used":False,
        "replay_execution":"offline_after_episode",
        "automatic_kaggle_submission":False,
    }
    p=Path(a.out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V27B_SHARD_RESULT",json.dumps({
        "shard":a.shard_index,
        "mechanical_pass":mech,
        "episodes":len(rows),
        "samples":actual_samples,
        "failures":len(failures),
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
