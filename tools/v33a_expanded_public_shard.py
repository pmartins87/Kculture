#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,score
SEEDS=(80901,80902,80903);SEATS=(0,1)
PRIMARY_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"

def run(main,opp,seed,seat):
    purge_package_modules(main.parent);purge_package_modules(opp.parent)
    a=load_public_agent(main);b=load_public_agent(opp)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    env.run([a,b] if seat==0 else [b,a]);rep=env.toJSON()
    st=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):raise RuntimeError(f"bad terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-other
    return float(score(m)),float(m)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidates",required=True);ap.add_argument("--opponents",required=True);ap.add_argument("--primary-main",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=8);ap.add_argument("--out",required=True);a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cr=Path(a.candidates);cm=json.loads((cr/"MANIFEST.json").read_text());cands=list(cm["sources"])
    oroot=Path(a.opponents);om=json.loads((oroot/"MANIFEST.json").read_text());opps=list(om["sources"])
    primary=Path(a.primary_main)
    if sha256_bytes(primary.read_bytes())!=PRIMARY_SHA:raise RuntimeError("primary SHA mismatch")
    selected=[x for i,x in enumerate(cands) if i%a.num_shards==a.shard_index]
    rows=[];fails=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
    for cand in selected:
      cp=cr/cand["path"]
      if sha256_bytes(cp.read_bytes())!=cand["sha"]:raise RuntimeError("candidate SHA mismatch")
      for oppm in opps:
        op=oroot/oppm["path"]
        if sha256_bytes(op.read_bytes())!=oppm["sha"]:raise RuntimeError("opponent SHA mismatch")
        for seed in SEEDS:
          for seat in SEATS:
            for key,mainp,sha,ref,rank in [
              ("PRIMARY",primary,PRIMARY_SHA,"arsgorynich/herd-safe-v3-experimental-risk-aware-feed",999999),
              ("CANDIDATE",cp,cand["sha"],cand["representative_ref"],cand["representative_rank"])]:
              try:
                sc,mg=run(mainp,op,seed,seat)
                rows.append({"candidate_key":key,"candidate_sha":sha,"candidate_ref":ref,"candidate_rank":rank,
                             "opponent_sha":oppm["sha"],"seed":seed,"seat":seat,"score":sc,"margin":mg})
              except Exception as e:
                fails.append({"candidate_sha":cand["sha"],"candidate_key":key,"opponent_sha":oppm["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
    out={"schema":"kculture-v33a-expanded-public-shard-v1","mechanical_pass":not fails,"shard_index":a.shard_index,
         "candidate_count":len(selected),"rows":rows,"failures":fails}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V33A_SHARD",json.dumps({"shard":a.shard_index,"candidates":len(selected),"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if fails:raise SystemExit(2)
if __name__=="__main__":main()
