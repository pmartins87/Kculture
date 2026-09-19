#!/usr/bin/env python3
"""Parallel fresh causal shard for O-LQ2 vs exact V48."""
from __future__ import annotations
import argparse,json,math,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,plain,score
from tools.first_party_lq2_canonical_sell_queue import lq2_action,MIN_STEP

EXPECTED_ENGINE="1.32.7"
BASE={
 "key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
 "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
 "key":"v48","handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
 "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}

def acquire(spec,tmp):
    last=None
    for attempt in range(1,4):
        try:
            main,receipt=acquire_public_main(spec["handle"],tmp/f"attempt-{attempt}")
            observed=sha256_bytes(main.read_bytes())
            if observed!=spec["expected_main_sha256"]:
                raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
            return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,"acquisition_attempt":attempt,**receipt}
        except Exception as exc:
            last=exc
            if attempt<3: time.sleep(2*attempt)
    raise RuntimeError(f"{spec['key']} acquisition failed: {type(last).__name__}: {last}")

class BaseWrap:
    def __init__(self,main):
        self.agent=load_public_agent(main); self.trace=[]
    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((int(plain(obs).get("step",len(self.trace))),action_key(b)))
        return b

class LQ2Wrap:
    def __init__(self,main):
        self.agent=load_public_agent(main); self.trace=[]
        self.fire_steps=[]; self.changed_slots=0; self.merged_runs=0
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",len(self.trace)))
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((step,action_key(b)))
        out=lq2_action(obs,config,b)
        if action_key(out)!=action_key(b):
            self.fire_steps.append(step)
            n=max(len(b["market"]),len(out["market"]))
            self.changed_slots+=sum(
                (b["market"][i] if i<len(b["market"]) else []) != (out["market"][i] if i<len(out["market"]) else [])
                for i in range(n)
            )
            self.merged_runs+=1
        return out

def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards) or steps<720:
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,opp=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-opp
    return {"rewards":rewards,"margin":margin,"score":score(margin),"steps":steps}

def run(base_main,v48_main,seed,seat,treatment):
    cand=LQ2Wrap(base_main) if treatment else BaseWrap(base_main)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    out["trace"]=cand.trace
    if treatment:
        out.update({
            "fire_steps":cand.fire_steps,
            "fire_count":len(cand.fire_steps),
            "changed_slots":cand.changed_slots,
            "merged_runs":cand.merged_runs,
        })
    return out

def parity(base,treat):
    fires=treat.get("fire_steps",[])
    if not fires:
        return {"ok":base["trace"]==treat["trace"] and base["rewards"]==treat["rewards"],"first_fire":None}
    first=min(fires)
    bt=[x for x in base["trace"] if x[0]<=first]
    tt=[x for x in treat["trace"] if x[0]<=first]
    return {"ok":bt==tt,"first_fire":first,"base_prefix":len(bt),"treatment_prefix":len(tt)}

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--seed",type=int,required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"o-lq2-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
        paths=[base_main,v48_main]
        for seat in (0,1):
          try:
            purge(paths); b=run(base_main,v48_main,args.seed,seat,False)
            purge(paths); t=run(base_main,v48_main,args.seed,seat,True)
            p=parity(b,t)
            if not p["ok"]: raise RuntimeError(f"pretrigger parity failure {p}")
            row={
              "seed":args.seed,"seat":seat,
              "base_score":b["score"],"treatment_score":t["score"],"score_delta":t["score"]-b["score"],
              "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":t["margin"]-b["margin"],
              "base_rewards":b["rewards"],"treatment_rewards":t["rewards"],
              "fire_count":t["fire_count"],"first_fire":min(t["fire_steps"]) if t["fire_steps"] else None,
              "last_fire":max(t["fire_steps"]) if t["fire_steps"] else None,
              "changed_slots":t["changed_slots"],"merged_runs":t["merged_runs"],"parity":p
            }
            rows.append(row)
            print("O_LQ2_PAIR",json.dumps(row,sort_keys=True),flush=True)
          except Exception as exc:
            failures.append({"seed":args.seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
          finally:
            purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==2 and all(r["parity"]["ok"] for r in rows)
    result={"schema":"kculture-o-lq2-v48-causal-shard-v1","seed":args.seed,"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ2_SHARD_RESULT",json.dumps({"seed":args.seed,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),"seconds":result["seconds"]},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
