#!/usr/bin/env python3
"""V4D shard: temporal localization of V4B market headroom for one seed."""
from __future__ import annotations
import argparse, copy, json, math, statistics, sys, tempfile, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.v48_market_upper_bound_v4b import EXPECTED_ENGINE,BASE,V48

WINDOWS={
 "W0":(0,215),
 "W1":(216,335),
 "W2":(336,431),
 "W3":(432,527),
 "W4":(528,623),
 "W5":(624,718),
 "W4_PLUS":(528,718),
 "W3_PLUS":(432,718),
 "W2_PLUS":(336,718),
 "W1_PLUS":(216,718),
}

def acquire(spec,tmp):
    last=None
    for attempt in range(1,4):
        try:
            attempt_dir=tmp/f"attempt-{attempt}"
            main,receipt=acquire_public_main(spec["handle"],attempt_dir)
            observed=sha256_bytes(main.read_bytes())
            if observed!=spec["expected_main_sha256"]:
                raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
            return main,{
                "key":spec["key"],"handle":spec["handle"],
                "observed_main_sha256":observed,
                "acquisition_attempt":attempt,**receipt,
            }
        except Exception as exc:
            last=exc
            if attempt<3:
                time.sleep(2*attempt)
    raise RuntimeError(f"{spec['key']} acquisition failed after 3 attempts: {type(last).__name__}: {last}")

def same_physical(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]

class BaseWrap:
    def __init__(self,main): self.agent=load_public_agent(main)
    def __call__(self,obs,config=None):
        return canonical_action(call_agent(self.agent,obs,config))

class WindowWrap:
    def __init__(self,base_main,v48_main,start,end):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.start=int(start); self.end=int(end)
        self.applied=0; self.fallback=0; self.first=None; self.last=None
        self.applied_rows=[]
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",0))
        b=canonical_action(call_agent(self.base,obs,config))
        s=canonical_action(call_agent(self.v48,obs,config))
        if step<self.start or step>self.end:
            return b
        if not same_physical(b,s):
            self.fallback+=1
            return b
        if b["market"]==s["market"]:
            return b
        out=canonical_action({
            "farmer":copy.deepcopy(b["farmer"]),
            "hands":copy.deepcopy(b["hands"]),
            "market":copy.deepcopy(s["market"]),
        })
        self.applied+=1
        if self.first is None: self.first=step
        self.last=step
        self.applied_rows.append({
            "step":step,
            "base_market":copy.deepcopy(b["market"]),
            "v48_market":copy.deepcopy(s["market"]),
        })
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

def run(base_main,v48_main,seed,seat,label):
    if label=="BASE":
        cand=BaseWrap(base_main)
    else:
        start,end=WINDOWS[label]
        cand=WindowWrap(base_main,v48_main,start,end)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    if label!="BASE":
        out.update({
            "label":label,
            "start":WINDOWS[label][0],"end":WINDOWS[label][1],
            "planned_steps":WINDOWS[label][1]-WINDOWS[label][0]+1,
            "applied_market_turns":cand.applied,
            "physical_fallback_turns":cand.fallback,
            "first_applied_step":cand.first,
            "last_applied_step":cand.last,
            "applied_rows":cand.applied_rows,
        })
    return out

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    rows=[]; failures=[]; provenance={}; started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v4d-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
        paths=[base_main,v48_main]
        for seat in (0,1):
          try:
            purge(paths); base=run(base_main,v48_main,args.seed,seat,"BASE")
            candidates=[]
            for label in WINDOWS:
                purge(paths)
                r=run(base_main,v48_main,args.seed,seat,label)
                r["score_delta"]=r["score"]-base["score"]
                r["margin_delta"]=r["margin"]-base["margin"]
                r["reproduces_headroom"]=r["score"]>=0.5 and base["score"]<0.5
                candidates.append(r)
            winners=[x for x in candidates if x["reproduces_headroom"]]
            winners.sort(key=lambda x:(x["planned_steps"],x["applied_market_turns"],-x["start"]))
            rows.append({
                "seed":args.seed,"seat":seat,"base":base,
                "candidates":candidates,
                "minimal_reproducer":winners[0] if winners else None,
                "reproducer_count":len(winners),
            })
            print("V48_V4D_CONTEXT",json.dumps({
                "seed":args.seed,"seat":seat,"base_score":base["score"],"base_margin":base["margin"],
                "minimal_reproducer":None if not winners else {
                    "label":winners[0]["label"],"score":winners[0]["score"],
                    "margin":winners[0]["margin"],"applied_market_turns":winners[0]["applied_market_turns"]
                },
                "reproducer_count":len(winners),
            },sort_keys=True),flush=True)
          except Exception as exc:
            failures.append({"seed":args.seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
          finally:
            purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==2
    result={
      "schema":"kculture-v48-market-temporal-localization-v4d-shard",
      "engine":EXPECTED_ENGINE,"seed":args.seed,"windows":WINDOWS,
      "mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":provenance,
      "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False
    }
    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V48_V4D_SHARD_RESULT",json.dumps({
      "seed":args.seed,"mechanical_pass":mech,
      "contexts":len(rows),"failures":len(failures),"seconds":result["seconds"]
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__":
    main()
