#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from collections import defaultdict
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,score

PRIMARY_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
V47_SHA="f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"
SEEDS={80511,80512,80513,80514,80515,80516}
SEATS={0,1}

def episode(agent_main,opp_main,seed,seat):
    purge_package_modules(agent_main.parent);purge_package_modules(opp_main.parent)
    ag=load_public_agent(agent_main);opp=load_public_agent(opp_main)
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

def load_primary_rows(root):
    rows=[]
    for p in sorted(Path(root).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")!="kculture-v30b-binding-validation-shard-v1":continue
        rows.extend(r for r in d.get("rows",[]) if r.get("candidate")=="PUBLIC")
    if len(rows)!=144: raise RuntimeError(f"binding primary row count {len(rows)} != 144")
    keys={(str(r["opponent_sha"]),int(r["seed"]),int(r["seat"])) for r in rows}
    if len(keys)!=144: raise RuntimeError("duplicate binding primary contexts")
    if {int(r["seed"]) for r in rows}!=SEEDS or {int(r["seat"]) for r in rows}!=SEATS:
        raise RuntimeError("binding context seed/seat drift")
    total=sum(float(r["score"]) for r in rows)
    if abs(total-131.0)>1e-9: raise RuntimeError(f"binding primary score total drift {total}")
    residual=[r for r in rows if float(r["score"])<1.0]
    if len(residual)!=20: raise RuntimeError(f"binding primary residual count {len(residual)} != 20")
    return rows,residual

def load_pool(v30a_root,v47_main):
    man=json.loads((Path(v30a_root)/"MANIFEST.json").read_text())
    pool=[]
    found_primary=False
    for s in man["sources"]:
        p=Path(v30a_root)/s["path"];sha=str(s["sha"])
        if sha256_bytes(p.read_bytes())!=sha: raise RuntimeError(f"V30A source SHA mismatch {sha}")
        if sha==PRIMARY_SHA:
            found_primary=True;continue
        pool.append({"key":sha,"sha":sha,"ref":str(s["representative_ref"]),"rank":int(s["representative_rank"]),"main":p})
    if not found_primary: raise RuntimeError("primary SHA absent from V30A snapshot")
    if sha256_bytes(Path(v47_main).read_bytes())!=V47_SHA: raise RuntimeError("V47 main SHA mismatch")
    pool.append({"key":"V47","sha":V47_SHA,"ref":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination","rank":999999,"main":Path(v47_main)})
    if len(pool)!=12: raise RuntimeError(f"hedge pool size {len(pool)} != 12")
    return pool

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v30a-snapshot",required=True)
    ap.add_argument("--frontier",required=True)
    ap.add_argument("--binding-shards",required=True)
    ap.add_argument("--v47-main",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")

    primary_rows,residual=load_primary_rows(a.binding_shards)
    fman=json.loads((Path(a.frontier)/"MANIFEST.json").read_text())
    fs={str(s["sha"]):s for s in fman["sources"]}
    if len(fs)!=12: raise RuntimeError(f"frontier source count {len(fs)} != 12")
    for sha,s in fs.items():
        p=Path(a.frontier)/s["path"]
        if sha256_bytes(p.read_bytes())!=sha: raise RuntimeError(f"frontier SHA mismatch {sha}")

    pool=load_pool(a.v30a_snapshot,a.v47_main)
    selected=[h for i,h in enumerate(pool) if i%a.num_shards==a.shard_index]
    rows=[];fails=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"): os.environ.pop(k,None)

    for h in selected:
      for pr in residual:
        sha=str(pr["opponent_sha"]);seed=int(pr["seed"]);seat=int(pr["seat"])
        opp=Path(a.frontier)/fs[sha]["path"]
        try:
            sc,mg=episode(h["main"],opp,seed,seat)
            rows.append({
              "hedge_key":h["key"],"hedge_sha":h["sha"],"hedge_ref":h["ref"],"hedge_rank":h["rank"],
              "opponent_sha":sha,"opponent_ref":pr.get("opponent_ref"),"seed":seed,"seat":seat,
              "primary_score":float(pr["score"]),"primary_margin":float(pr["margin"]),
              "hedge_score":sc,"hedge_margin":mg
            })
        except Exception as e:
            fails.append({"hedge_key":h["key"],"opponent_sha":sha,"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
        finally:
            purge_package_modules(h["main"].parent);purge_package_modules(opp.parent)

    expected=len(selected)*len(residual)
    mech=(not fails and len(rows)==expected)
    out={"schema":"kculture-v31a-second-slot-complementarity-shard-v1","mechanical_pass":mech,
         "shard_index":a.shard_index,"num_shards":a.num_shards,"hedges":[{k:v for k,v in h.items() if k!="main"} for h in selected],
         "primary_full_contexts":len(primary_rows),"primary_residual_contexts":len(residual),"rows":rows,"failures":fails}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V31A_SHARD_RESULT",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"hedges":len(selected),"rows":len(rows),"failures":len(fails)},sort_keys=True))
    if not mech: raise SystemExit(2)

if __name__=="__main__":main()
