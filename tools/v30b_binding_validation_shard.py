#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

SEEDS=(80511,80512,80513,80514,80515,80516);SEATS=(0,1)
FROZEN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"

class All3:
    def __init__(self,base):
        purge_package_modules(base.parent);self.agent=load_public_agent(base);self.host=OptionHostState()
    def __call__(self,obs,config=None):
        a=canonical_action(call_agent(self.agent,obs,config))
        return apply_option_host(obs,config,a,self.host,use_rw=True,use_tw=True,use_lq2=True)
class Direct:
    def __init__(self,main): purge_package_modules(main.parent);self.agent=load_public_agent(main)
    def __call__(self,obs,config=None): return call_agent(self.agent,obs,config)

def episode(candidate,opp_main,seed,seat):
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([candidate,opp] if seat==0 else [opp,candidate]);rep=env.toJSON()
    st=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);mg=mine-other
    return float(score(mg)),float(mg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--package-dir",required=True);ap.add_argument("--fresh-snapshot",required=True);ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")
    cand=Path(a.package_dir)/"main.py"
    if sha256_bytes(cand.read_bytes())!=FROZEN_SHA: raise SystemExit("packaged candidate SHA mismatch")
    root=Path(a.fresh_snapshot);man=json.loads((root/"MANIFEST.json").read_text());srcs=list(man["sources"])
    if not 8<=len(srcs)<=12: raise SystemExit(f"source count {len(srcs)}")
    base=root/man["base"]["path"]
    if sha256_bytes(base.read_bytes())!=BASE["expected_main_sha256"]: raise SystemExit("ALL3 base SHA mismatch")
    selected=[s for i,s in enumerate(srcs) if i%a.num_shards==a.shard_index]
    rows=[];fails=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
    for s in selected:
      opp=root/s["path"]
      if sha256_bytes(opp.read_bytes())!=str(s["sha"]): raise SystemExit("opponent SHA mismatch")
      for seed in SEEDS:
       for seat in SEATS:
        for key in ("ALL3","PUBLIC"):
         try:
          purge_package_modules(base.parent);purge_package_modules(cand.parent);purge_package_modules(opp.parent)
          ag=All3(base) if key=="ALL3" else Direct(cand)
          sc,mg=episode(ag,opp,seed,seat)
          rows.append({"candidate":key,"opponent_sha":s["sha"],"opponent_ref":s["representative_ref"],"seed":seed,"seat":seat,"score":sc,"margin":mg})
         except Exception as e:
          fails.append({"candidate":key,"opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
    expected=len(selected)*len(SEEDS)*len(SEATS)*2
    mech=(not fails and len(rows)==expected)
    out={"schema":"kculture-v30b-binding-validation-shard-v1","mechanical_pass":mech,"shard_index":a.shard_index,
         "num_shards":a.num_shards,"sources":len(selected),"rows":rows,"failures":fails}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V30B_BINDING_SHARD",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"sources":len(selected),"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
