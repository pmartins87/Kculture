#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,os,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score

POLICIES={
 "P0":{"ref":"arsgorynich/herd-safe-v3-experimental-risk-aware-feed","sha":"4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"},
 "P1":{"ref":"prvsiyan/kaggriculture-frontier-the-moon-counts-melons","sha":"178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a"},
 "P2":{"ref":"abhinav0370/kaggriculture-cha22-agent","sha":"127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"},
 "P3":{"ref":"dmitriigluzdov/kaggriculture-herd-safe-sale-window-lb-2700","sha":"4889137f1adf1f9266b2ad5a6ac6700c40e9be6dfe3654e39db375fb55b71341"},
}
SEEDS=(80911,80912,80913,80914);SEATS=(0,1)

class Full:
    def __init__(self,p):
        purge_package_modules(p.parent);self.a=load_public_agent(p)
    def __call__(self,obs,config=None):return call_agent(self.a,obs,config)

class Hybrid:
    def __init__(self,market_p,physical_p):
        purge_package_modules(market_p.parent);self.m=load_public_agent(market_p)
        purge_package_modules(physical_p.parent);self.p=load_public_agent(physical_p)
    def __call__(self,obs,config=None):
        ma=canonical_action(call_agent(self.m,obs,config))
        pa=canonical_action(call_agent(self.p,obs,config))
        out=copy.deepcopy(pa)
        out["market"]=copy.deepcopy(ma.get("market") or [])
        return out

def run(cand,opp,seed,seat):
    purge_package_modules(opp.parent);op=load_public_agent(opp)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([cand,op] if seat==0 else [op,cand]);rep=env.toJSON()
    st=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"bad terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-other
    return float(score(m)),float(m)

def load_policy_paths(v30b,v30a,v32a):
    out={"P0":Path(v30b)}
    for root,key in [(Path(v30a),"P1"),(Path(v30a),"P3"),(Path(v32a),"P2")]:
        man=json.loads((root/"MANIFEST.json").read_text())
        want=POLICIES[key]["sha"]
        src=next((s for s in man["sources"] if str(s["sha"])==want),None)
        if src is None:raise RuntimeError(f"{key} missing")
        out[key]=root/src["path"]
    for k,p in out.items():
        if sha256_bytes(p.read_bytes())!=POLICIES[k]["sha"]:raise RuntimeError(f"{k} SHA mismatch")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v30b-main",required=True);ap.add_argument("--v30a",required=True);ap.add_argument("--v32a",required=True)
    ap.add_argument("--opponents",required=True);ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    paths=load_policy_paths(a.v30b_main,a.v30a,a.v32a)
    oroot=Path(a.opponents);om=json.loads((oroot/"MANIFEST.json").read_text());opps=list(om["sources"])
    selected=[x for i,x in enumerate(opps) if i%a.num_shards==a.shard_index]
    modes=[f"FULL_{k}" for k in POLICIES]
    for m in POLICIES:
      for p in POLICIES:
        if m!=p:modes.append(f"M_{m}__P_{p}")
    rows=[];fails=[]
    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(key,None)
    for ometa in selected:
      opp=oroot/ometa["path"]
      if sha256_bytes(opp.read_bytes())!=str(ometa["sha"]):raise RuntimeError("opponent SHA mismatch")
      for seed in SEEDS:
       for seat in SEATS:
        for mode in modes:
         try:
          for p in paths.values():purge_package_modules(p.parent)
          if mode.startswith("FULL_"):
            k=mode[5:];cand=Full(paths[k])
          else:
            x,y=mode.split("__");mk=x[2:];pk=y[2:];cand=Hybrid(paths[mk],paths[pk])
          sc,mg=run(cand,opp,seed,seat)
          rows.append({"mode":mode,"opponent_sha":ometa["sha"],"seed":seed,"seat":seat,"score":sc,"margin":mg})
         except Exception as e:
          fails.append({"mode":mode,"opponent_sha":ometa["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
    expected=len(selected)*len(SEEDS)*len(SEATS)*len(modes)
    mech=not fails and len(rows)==expected
    out={"schema":"kculture-v34a-cross-domain-shard-v1","mechanical_pass":mech,"shard_index":a.shard_index,"rows":rows,"failures":fails}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V34A_SHARD",json.dumps({"shard":a.shard_index,"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
