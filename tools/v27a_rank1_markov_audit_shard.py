#!/usr/bin/env python3
"""V27A rank-1 teacher Markov reconstructibility audit shard."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE, load_public_agent, purge_package_modules, sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action, score

TEACHER_SHA="a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c"
SEEDS=(79701,79702,79703)
SEATS=(0,1)
CHECKPOINTS=(0,1,2,3,4,8,16,32,64,128,256,384,512,640,718)

def same_component(a,b,key):
    return a.get(key)==b.get(key)

class AuditCandidate:
    def __init__(self,teacher_main,fresh_main):
        purge_package_modules(teacher_main.parent)
        self.ongoing=load_public_agent(teacher_main)
        self.fresh_main=fresh_main
        self.samples=[]
        self.calls=0

    def __call__(self,obs,config=None):
        step=int((obs or {}).get("step",self.calls))
        self.calls+=1
        ongoing=canonical_action(call_agent(self.ongoing,obs,config))
        if step in CHECKPOINTS:
            purge_package_modules(self.fresh_main.parent)
            fresh_fn=load_public_agent(self.fresh_main)
            fresh=canonical_action(call_agent(fresh_fn,copy.deepcopy(obs),copy.deepcopy(config) if config is not None else None))
            self.samples.append({
              "step":step,
              "full_equal":ongoing==fresh,
              "market_equal":same_component(ongoing,fresh,"market"),
              "farmer_equal":same_component(ongoing,fresh,"farmer"),
              "hands_equal":same_component(ongoing,fresh,"hands"),
              "ongoing":ongoing,
              "fresh":fresh,
            })
            purge_package_modules(self.fresh_main.parent)
        return ongoing

def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {
      "score":float(score(margin)),
      "margin":float(margin),
      "rewards":rewards,
      "steps":steps,
    }

def run_one(teacher_main,fresh_main,opp_main,seed,seat):
    purge_package_modules(teacher_main.parent)
    purge_package_modules(fresh_main.parent)
    purge_package_modules(opp_main.parent)
    cand=AuditCandidate(teacher_main,fresh_main)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])
    result=finish(env,seat)
    steps={int(x["step"]) for x in cand.samples}
    if steps!=set(CHECKPOINTS):
        raise RuntimeError(f"checkpoint coverage mismatch got={sorted(steps)} expected={list(CHECKPOINTS)}")
    result["samples"]=cand.samples
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
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
    rows=[];failures=[]

    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(key,None)

    with tempfile.TemporaryDirectory(prefix="v27a-fresh-teacher-") as td:
        fresh_root=Path(td)/"teacher"
        fresh_root.mkdir(parents=True,exist_ok=True)
        fresh_main=fresh_root/"main.py"
        fresh_main.write_bytes(teacher_main.read_bytes())
        if sha256_bytes(fresh_main.read_bytes())!=TEACHER_SHA:
            raise SystemExit("fresh teacher copy SHA mismatch")

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
                        rr=run_one(teacher_main,fresh_main,opp_main,seed,seat)
                        row={**key,
                          "teacher_score":rr["score"],
                          "teacher_margin":rr["margin"],
                          "samples":rr["samples"],
                        }
                        rows.append(row)
                        full=sum(bool(x["full_equal"]) for x in rr["samples"])
                        print("V27A_EPISODE",json.dumps({
                          **key,"samples":len(rr["samples"]),"full_equal":full
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"phase":"episode","error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge_package_modules(teacher_main.parent)
                        purge_package_modules(fresh_main.parent)
                        purge_package_modules(opp_main.parent)

    expected_episodes=len(selected)*len(SEEDS)*len(SEATS)
    expected_samples=expected_episodes*len(CHECKPOINTS)
    actual_samples=sum(len(r["samples"]) for r in rows)
    mech=not failures and len(rows)==expected_episodes and actual_samples==expected_samples
    result={
      "schema":"kculture-v27a-rank1-markov-audit-shard-v1",
      "mechanical_pass":mech,
      "shard_index":args.shard_index,
      "num_shards":args.num_shards,
      "teacher_sha":TEACHER_SHA,
      "teacher_ref":teacher_meta["representative_ref"],
      "checkpoints":list(CHECKPOINTS),
      "seeds":list(SEEDS),
      "seats":list(SEATS),
      "expected_episodes":expected_episodes,
      "expected_samples":expected_samples,
      "rows":rows,
      "failures":failures,
      "immutable_snapshot_used":True,
      "live_kaggle_reacquisition_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V27A_SHARD_RESULT",json.dumps({
      "shard":args.shard_index,"mechanical_pass":mech,
      "episodes":len(rows),"samples":actual_samples,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
