#!/usr/bin/env python3
"""V28B fresh final-slot benchmark: V47 vs ORW1 vs ALL3."""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

SEEDS=(80301,80302,80303,80304,80305,80306)
SEATS=(0,1)
CANDIDATES=("V47","ORW1","ALL3")
BASE_MAIN=None

class Candidate:
    def __init__(self,key):
        purge_package_modules(BASE_MAIN.parent)
        self.base=load_public_agent(BASE_MAIN)
        self.key=key
        self.host=OptionHostState()
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.base,obs,config))
        if self.key=="V47":
            return base
        if self.key=="ORW1":
            return apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=False,use_lq2=False)
        if self.key=="ALL3":
            return apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=True,use_lq2=True)
        raise RuntimeError(f"unknown candidate {self.key}")

def run_one(key,opp_main,seed,seat):
    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(key)
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
        raise RuntimeError(f"invalid episode candidate={key} statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps}

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

    global BASE_MAIN
    root=Path(args.snapshot_dir)
    man=json.loads((root/"MANIFEST.json").read_text())
    BASE_MAIN=root/man["base"]["path"]
    if sha256_bytes(BASE_MAIN.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 base snapshot SHA mismatch")

    sources=list(man["sources"])
    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    rows=[];failures=[]
    for src in selected:
        opp=root/src["path"]
        if sha256_bytes(opp.read_bytes())!=str(src["sha"]):
            failures.append({"phase":"snapshot_sha","sha":src["sha"],"error":"SHA mismatch"})
            continue
        for seed in SEEDS:
            for seat in SEATS:
                context={
                    "source_rank":int(src["representative_rank"]),
                    "ref":src["representative_ref"],
                    "main_sha256":src["sha"],
                    "seed":int(seed),"seat":int(seat),
                }
                for key in CANDIDATES:
                    try:
                        rr=run_one(key,opp,seed,seat)
                        row={**context,"candidate":key,**rr}
                        rows.append(row)
                        print("V28B_CELL",json.dumps({
                            "candidate":key,"source_rank":context["source_rank"],
                            "seed":seed,"seat":seat,"score":rr["score"],"margin":rr["margin"]
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**context,"candidate":key,"phase":"episode","error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp.parent)

    expected=len(selected)*len(SEEDS)*len(SEATS)*len(CANDIDATES)
    keys={(r["main_sha256"],r["seed"],r["seat"],r["candidate"]) for r in rows}
    mech=not failures and len(rows)==expected and len(keys)==expected
    result={
        "schema":"kculture-v28b-final-slot-benchmark-shard-v1",
        "mechanical_pass":mech,
        "shard_index":args.shard_index,"num_shards":args.num_shards,
        "selected_sources":[s["sha"] for s in selected],
        "candidates":list(CANDIDATES),
        "seeds":list(SEEDS),"seats":list(SEATS),
        "expected_rows":expected,"rows":rows,"failures":failures,
        "immutable_snapshot_used":True,"live_kaggle_reacquisition_used":False,
        "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V28B_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"rows":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
