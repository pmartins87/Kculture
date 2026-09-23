#!/usr/bin/env python3
"""V28F fresh ALL3-centered hedge complementarity benchmark shard."""
from __future__ import annotations
import argparse,json,math,os,statistics,sys
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

SEEDS=(80401,80402,80403,80404,80405,80406)
SEATS=(0,1)
CANDIDATES=("ALL3","V47","ORW1","CR053","CR029")
BASE_MAIN=None
LEGACY={}

class OptionCandidate:
    def __init__(self,key):
        purge_package_modules(BASE_MAIN.parent)
        self.base=load_public_agent(BASE_MAIN)
        self.key=key
        self.host=OptionHostState()
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.base,obs,config))
        if self.key=="V47": return base
        if self.key=="ORW1":
            return apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=False,use_lq2=False)
        if self.key=="ALL3":
            return apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=True,use_lq2=True)
        raise RuntimeError(self.key)

class DirectCandidate:
    def __init__(self,key):
        self.key=key
        self.main=LEGACY[key]
        purge_package_modules(self.main.parent)
        self.agent=load_public_agent(self.main)
    def __call__(self,obs,config=None):
        return call_agent(self.agent,obs,config)

def build_candidate(key):
    if key in ("ALL3","V47","ORW1"): return OptionCandidate(key)
    if key in LEGACY: return DirectCandidate(key)
    raise RuntimeError(f"unknown candidate {key}")

def run_one(key,opp_main,seed,seat):
    purge_package_modules(BASE_MAIN.parent); purge_package_modules(opp_main.parent)
    for p in LEGACY.values(): purge_package_modules(p.parent)
    cand=build_candidate(key)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0: env.run([cand,opp])
    else: env.run([opp,cand])
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
    a=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    global BASE_MAIN,LEGACY
    root=Path(a.snapshot_dir)
    front=json.loads((root/"MANIFEST.json").read_text())
    hedge=json.loads((root/"HEDGE_MANIFEST.json").read_text())
    if not hedge.get("mechanical_pass"): raise SystemExit("hedge candidate prep not mechanical PASS")

    BASE_MAIN=root/front["base"]["path"]
    if sha256_bytes(BASE_MAIN.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 base snapshot SHA mismatch")

    LEGACY={}
    for key in ("CR053","CR029"):
        meta=hedge["candidates"][key]
        p=root/meta["path"]
        if sha256_bytes(p.read_bytes())!=meta["main_sha256"]:
            raise SystemExit(f"{key} main SHA mismatch")
        LEGACY[key]=p

    sources=list(front["sources"])
    selected=[s for i,s in enumerate(sources) if i%a.num_shards==a.shard_index]

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    rows=[]; failures=[]
    for src in selected:
        opp=root/src["path"]
        if sha256_bytes(opp.read_bytes())!=str(src["sha"]):
            failures.append({"phase":"snapshot_sha","sha":src["sha"],"error":"SHA mismatch"}); continue
        for seed in SEEDS:
            for seat in SEATS:
                ctx={"source_rank":int(src["representative_rank"]),"ref":src["representative_ref"],"main_sha256":src["sha"],"seed":int(seed),"seat":int(seat)}
                for key in CANDIDATES:
                    try:
                        rr=run_one(key,opp,seed,seat)
                        rows.append({**ctx,"candidate":key,**rr})
                        print("V28F_CELL",json.dumps({"candidate":key,"source_rank":ctx["source_rank"],"seed":seed,"seat":seat,"score":rr["score"],"margin":rr["margin"]},sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**ctx,"candidate":key,"phase":"episode","error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge_package_modules(BASE_MAIN.parent); purge_package_modules(opp.parent)
                        for p in LEGACY.values(): purge_package_modules(p.parent)

    expected=len(selected)*len(SEEDS)*len(SEATS)*len(CANDIDATES)
    keys={(r["main_sha256"],r["seed"],r["seat"],r["candidate"]) for r in rows}
    mech=not failures and len(rows)==expected and len(keys)==expected
    result={
      "schema":"kculture-v28f-hedge-benchmark-shard-v1",
      "mechanical_pass":mech,
      "shard_index":a.shard_index,"num_shards":a.num_shards,
      "selected_sources":[s["sha"] for s in selected],
      "candidates":list(CANDIDATES),"seeds":list(SEEDS),"seats":list(SEATS),
      "expected_rows":expected,"rows":rows,"failures":failures,
      "immutable_snapshot_used":True,"live_kaggle_reacquisition_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V28F_SHARD_RESULT",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"rows":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
