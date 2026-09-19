#!/usr/bin/env python3
"""V6A hard-context census shard for one V2 opponent family."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire,purge
from tools.all3_physical_proposal_oracle_v5_shard import BaseAll3,finish
from tools.programme_adaptive_expert_gate import load_public_agent

SEEDS=list(range(75101,75109))

def run(base_main,opp_main,seed,seat):
    cand=BaseAll3(base_main)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    return finish(env,seat)

def purge_paths(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k);purge(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v6a-{args.opponent}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec.get("family"),"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp")
            provenance["opponent"]={**rec,"family":spec.get("family")}
        paths=[base_main,opp_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                purge_paths(paths)
                r=run(base_main,opp_main,seed,seat)
                rows.append({
                  "opponent":args.opponent,"family":spec.get("family"),"seed":seed,"seat":seat,
                  "reward":r["reward"],"opponent_reward":r["opponent_reward"],
                  "margin":r["margin"],"score":r["score"],"steps":r["steps"],
                })
                print("V6A_CONTEXT",json.dumps(rows[-1],sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge_paths(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==16
    out={
      "schema":"kculture-all3-v6a-hard-context-shard-v1",
      "opponent":args.opponent,"family":spec.get("family"),"seeds":SEEDS,
      "mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":provenance,
      "seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V6A_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),
      "wins":sum(r["score"]==1 for r in rows),"ties":sum(r["score"]==0.5 for r in rows),
      "losses":sum(r["score"]==0 for r in rows),
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__":main()
