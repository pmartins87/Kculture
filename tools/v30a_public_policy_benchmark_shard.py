#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,statistics,sys
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

SEEDS=(80501,80502,80503,80504)
SEATS=(0,1)
BASE_MAIN=None
SOURCES={}

class All3:
    def __init__(self):
        purge_package_modules(BASE_MAIN.parent)
        self.base=load_public_agent(BASE_MAIN)
        self.host=OptionHostState()
    def __call__(self,obs,config=None):
        a=canonical_action(call_agent(self.base,obs,config))
        return apply_option_host(obs,config,a,self.host,use_rw=True,use_tw=True,use_lq2=True)

class Direct:
    def __init__(self,main):
        self.main=main
        purge_package_modules(main.parent)
        self.agent=load_public_agent(main)
    def __call__(self,obs,config=None):
        return call_agent(self.agent,obs,config)

def make_candidate(key):
    if key=="ALL3": return All3()
    return Direct(SOURCES[key])

def run_one(candidate_key,opp_main,seed,seat):
    purge_package_modules(BASE_MAIN.parent)
    for p in SOURCES.values(): purge_package_modules(p.parent)
    cand=make_candidate(candidate_key)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([cand,opp] if int(seat)==0 else [opp,cand])
    rep=env.toJSON()
    statuses=[str(x) for x in rep.get("statuses",[])]
    rewards=[float(x) for x in rep.get("rewards",[])]
    steps=len(rep.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode candidate={candidate_key} statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps}

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

    global BASE_MAIN,SOURCES
    root=Path(a.snapshot_dir)
    man=json.loads((root/"MANIFEST.json").read_text())
    BASE_MAIN=root/man["base"]["path"]
    if sha256_bytes(BASE_MAIN.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 base snapshot SHA mismatch")

    srcs=list(man["sources"])
    if not (8<=len(srcs)<=12):raise SystemExit(f"unexpected source count {len(srcs)}")
    SOURCES={}
    meta={}
    for s in srcs:
        sha=str(s["sha"]);p=root/s["path"]
        if sha256_bytes(p.read_bytes())!=sha:raise SystemExit(f"source SHA mismatch {sha}")
        SOURCES[sha]=p;meta[sha]=s

    candidates=["ALL3"]+[str(s["sha"]) for s in srcs]
    selected=[s for i,s in enumerate(srcs) if i%a.num_shards==a.shard_index]

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

    rows=[];fail=[]
    for src in selected:
        opp_sha=str(src["sha"]);opp=SOURCES[opp_sha]
        for seed in SEEDS:
            for seat in SEATS:
                context={"opponent_sha":opp_sha,"opponent_ref":src["representative_ref"],
                         "opponent_rank":int(src["representative_rank"]),
                         "seed":int(seed),"seat":int(seat)}
                for key in candidates:
                    try:
                        rr=run_one(key,opp,seed,seat)
                        cm=None if key=="ALL3" else meta[key]
                        rows.append({**context,"candidate_key":key,
                          "candidate_sha":None if key=="ALL3" else key,
                          "candidate_ref":None if key=="ALL3" else cm["representative_ref"],
                          "candidate_rank":None if key=="ALL3" else int(cm["representative_rank"]),
                          **rr})
                    except Exception as e:
                        fail.append({**context,"candidate_key":key,"error":f"{type(e).__name__}: {e}"})
                    finally:
                        purge_package_modules(BASE_MAIN.parent)
                        for p in SOURCES.values():purge_package_modules(p.parent)

    expected=len(selected)*len(SEEDS)*len(SEATS)*len(candidates)
    keys={(r["opponent_sha"],r["seed"],r["seat"],r["candidate_key"]) for r in rows}
    mech=not fail and len(rows)==expected and len(keys)==expected
    out={"schema":"kculture-v30a-public-persistent-policy-shard-v1",
         "mechanical_pass":mech,"shard_index":a.shard_index,"num_shards":a.num_shards,
         "candidate_count":len(candidates),"opponent_count":len(srcs),
         "candidates":candidates,"seeds":list(SEEDS),"seats":list(SEATS),
         "rows":rows,"failures":fail,"immutable_snapshot_used":True,
         "live_kaggle_reacquisition_used":False,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V30A_SHARD_RESULT",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"rows":len(rows),"failures":len(fail)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
