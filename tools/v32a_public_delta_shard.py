#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,score
SEEDS=(80801,80802,80803,80804);SEATS=(0,1)
PRIMARY_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"

def episode(main,opp,seed,seat):
    purge_package_modules(main.parent);purge_package_modules(opp.parent)
    a=load_public_agent(main);b=load_public_agent(opp)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([a,b] if seat==0 else [b,a]);rep=env.toJSON()
    st=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):raise RuntimeError(f"invalid terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=float(mine-other)
    return float(score(m)),m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True);ap.add_argument("--delta",required=True);ap.add_argument("--primary-main",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True);a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    root=Path(a.snapshot);man=json.loads((root/"MANIFEST.json").read_text());delta=json.loads(Path(a.delta).read_text())
    primary=Path(a.primary_main)
    if sha256_bytes(primary.read_bytes())!=PRIMARY_SHA:raise RuntimeError("primary SHA mismatch")
    newc=delta["new_candidates"]
    srcs=list(man["sources"]);selected=[s for i,s in enumerate(srcs) if i%a.num_shards==a.shard_index]
    cand=[]
    for c in newc:
        p=root/c["path"]
        if sha256_bytes(p.read_bytes())!=c["sha"]:raise RuntimeError("candidate SHA mismatch")
        cand.append((c,p))
    rows=[];fails=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
    for s in selected:
      opp=root/s["path"]
      if sha256_bytes(opp.read_bytes())!=str(s["sha"]):raise RuntimeError("opponent SHA mismatch")
      for seed in SEEDS:
       for seat in SEATS:
        try:
          sc,mg=episode(primary,opp,seed,seat)
          rows.append({"candidate":"PRIMARY","candidate_sha":PRIMARY_SHA,"candidate_ref":"arsgorynich/herd-safe-v3-experimental-risk-aware-feed",
                       "candidate_rank":999999,"opponent_sha":s["sha"],"opponent_ref":s["representative_ref"],"seed":seed,"seat":seat,"score":sc,"margin":mg})
        except Exception as e:
          fails.append({"candidate":"PRIMARY","opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
        for c,p in cand:
         try:
          sc,mg=episode(p,opp,seed,seat)
          rows.append({"candidate":c["sha"],"candidate_sha":c["sha"],"candidate_ref":c["ref"],"candidate_rank":c["rank"],
                       "opponent_sha":s["sha"],"opponent_ref":s["representative_ref"],"seed":seed,"seat":seat,"score":sc,"margin":mg})
         except Exception as e:
          fails.append({"candidate":c["sha"],"opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
    expected=len(selected)*len(SEEDS)*len(SEATS)*(1+len(cand))
    mech=(not fails and len(rows)==expected)
    out={"schema":"kculture-v32a-public-delta-shard-v1","mechanical_pass":mech,"shard_index":a.shard_index,"sources":len(selected),
         "new_candidates":len(cand),"rows":rows,"failures":fails}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V32A_SHARD",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"sources":len(selected),"new_candidates":len(cand),"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
