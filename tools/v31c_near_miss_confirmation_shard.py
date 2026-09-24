#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,score

SEEDS=(80701,80702,80703,80704,80705,80706)
SEATS=(0,1)
PRIMARY_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
V47_SHA="f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"
A_SHA="178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a"
B_SHA="20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e"

def episode(main,opp_main,seed,seat):
    purge_package_modules(main.parent);purge_package_modules(opp_main.parent)
    ag=load_public_agent(main);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([ag,opp] if seat==0 else [opp,ag])
    rep=env.toJSON()
    st=[str(x) for x in rep.get("statuses",[])]
    rw=[float(x) for x in rep.get("rewards",[])]
    steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
    margin=float(mine-other)
    return float(score(margin)),margin

def find_v30a(root,sha):
    man=json.loads((Path(root)/"MANIFEST.json").read_text())
    for s in man["sources"]:
        if str(s["sha"])==sha:
            p=Path(root)/s["path"]
            if sha256_bytes(p.read_bytes())!=sha: raise RuntimeError("V30A source SHA mismatch")
            return p,str(s["representative_ref"])
    raise RuntimeError(f"missing source {sha}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v30a-snapshot",required=True)
    ap.add_argument("--frontier",required=True)
    ap.add_argument("--primary-main",required=True)
    ap.add_argument("--v47-main",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")

    primary=Path(a.primary_main);v47=Path(a.v47_main)
    if sha256_bytes(primary.read_bytes())!=PRIMARY_SHA: raise RuntimeError("primary SHA mismatch")
    if sha256_bytes(v47.read_bytes())!=V47_SHA: raise RuntimeError("V47 SHA mismatch")
    aa,aref=find_v30a(a.v30a_snapshot,A_SHA)
    bb,bref=find_v30a(a.v30a_snapshot,B_SHA)

    froot=Path(a.frontier);man=json.loads((froot/"MANIFEST.json").read_text());srcs=list(man["sources"])
    if not 8<=len(srcs)<=12: raise RuntimeError(f"frontier source count {len(srcs)}")
    selected=[s for i,s in enumerate(srcs) if i%a.num_shards==a.shard_index]
    policies=[
      ("PRIMARY",PRIMARY_SHA,"arsgorynich/herd-safe-v3-experimental-risk-aware-feed",primary),
      ("V47",V47_SHA,"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",v47),
      ("A",A_SHA,aref,aa),("B",B_SHA,bref,bb)
    ]
    rows=[];fails=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
    for s in selected:
      opp=froot/s["path"]
      if sha256_bytes(opp.read_bytes())!=str(s["sha"]): raise RuntimeError("frontier SHA mismatch")
      for seed in SEEDS:
       for seat in SEATS:
        for key,sha,ref,mainp in policies:
         try:
          sc,mg=episode(mainp,opp,seed,seat)
          rows.append({"policy":key,"policy_sha":sha,"policy_ref":ref,"opponent_sha":s["sha"],"opponent_ref":s["representative_ref"],
                       "seed":seed,"seat":seat,"score":sc,"margin":mg})
         except Exception as e:
          fails.append({"policy":key,"opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
    expected=len(selected)*len(SEEDS)*len(SEATS)*4
    mech=(not fails and len(rows)==expected)
    out={"schema":"kculture-v31c-near-miss-confirmation-shard-v1","mechanical_pass":mech,"shard_index":a.shard_index,
         "sources":len(selected),"rows":rows,"failures":fails}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V31C_SHARD",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"sources":len(selected),"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
