#!/usr/bin/env python3
"""V4E shard: exact semantic-category decomposition of V48 market headroom."""
from __future__ import annotations
import argparse,copy,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.v48_market_upper_bound_v4b import EXPECTED_ENGINE,BASE,V48

MIN_STEP=336
VARIANTS=[
 "FULL",
 "ONLY_SANITATION",
 "ONLY_REPLACE",
 "ONLY_QTY_UP",
 "ONLY_STRUCTURAL",
 "FULL_MINUS_SANITATION",
 "FULL_MINUS_REPLACE",
 "FULL_MINUS_QTY_UP",
 "FULL_MINUS_STRUCTURAL",
]
SANITATION={"CLEAR","QTY_DOWN"}
STRUCTURAL={"REPLACE","QTY_UP","OTHER"}

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

def is_sell(o):
    return isinstance(o,list) and len(o)>=3 and str(o[0])=="SELL"

def qty(o):
    try: return float(o[2])
    except Exception: return None

def category(b,v):
    if b==v: return "UNCHANGED"
    if is_sell(b) and not v: return "CLEAR"
    if is_sell(b) and is_sell(v):
        bp=str(b[1]); vp=str(v[1])
        if bp!=vp: return "REPLACE"
        bq=qty(b); vq=qty(v)
        if bq is not None and vq is not None:
            if vq<bq: return "QTY_DOWN"
            if vq>bq: return "QTY_UP"
    return "OTHER"

def same_physical(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]

def use_v48(variant,cat):
    if cat=="UNCHANGED": return False
    if variant=="FULL": return True
    if variant=="ONLY_SANITATION": return cat in SANITATION
    if variant=="ONLY_REPLACE": return cat=="REPLACE"
    if variant=="ONLY_QTY_UP": return cat=="QTY_UP"
    if variant=="ONLY_STRUCTURAL": return cat in STRUCTURAL
    if variant=="FULL_MINUS_SANITATION": return cat not in SANITATION
    if variant=="FULL_MINUS_REPLACE": return cat!="REPLACE"
    if variant=="FULL_MINUS_QTY_UP": return cat!="QTY_UP"
    if variant=="FULL_MINUS_STRUCTURAL": return cat not in STRUCTURAL
    raise ValueError(variant)

class BaseWrap:
    def __init__(self,main): self.agent=load_public_agent(main)
    def __call__(self,obs,config=None):
        return canonical_action(call_agent(self.agent,obs,config))

class HybridWrap:
    def __init__(self,base_main,v48_main,variant):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.variant=variant
        self.applied=0
        self.fallback=0
        self.cat_counts={k:0 for k in ["CLEAR","QTY_DOWN","QTY_UP","REPLACE","OTHER"]}
        self.first=None; self.last=None
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",0))
        b=canonical_action(call_agent(self.base,obs,config))
        s=canonical_action(call_agent(self.v48,obs,config))
        if step<MIN_STEP:
            return b
        if not same_physical(b,s):
            self.fallback+=1
            return b
        if self.variant=="FULL":
            if b["market"]!=s["market"]:
                self.applied+=1
                if self.first is None: self.first=step
                self.last=step
                bm=b["market"]; vm=s["market"]; n=max(len(bm),len(vm))
                for i in range(n):
                    bo=bm[i] if i<len(bm) else []
                    vo=vm[i] if i<len(vm) else []
                    cat=category(bo,vo)
                    if cat in self.cat_counts: self.cat_counts[cat]+=1
            return canonical_action({"farmer":copy.deepcopy(b["farmer"]),"hands":copy.deepcopy(b["hands"]),"market":copy.deepcopy(s["market"])})
        bm=b["market"]; vm=s["market"]; n=max(len(bm),len(vm))
        out=[]; changed=False
        for i in range(n):
            bo=copy.deepcopy(bm[i] if i<len(bm) else [])
            vo=copy.deepcopy(vm[i] if i<len(vm) else [])
            cat=category(bo,vo)
            if use_v48(self.variant,cat):
                out.append(vo); changed=changed or (vo!=bo)
                if cat in self.cat_counts and vo!=bo: self.cat_counts[cat]+=1
            else:
                out.append(bo)
        while out and out[-1]==[]:
            # Remove only padding/trailing empties; internal slot positions remain intact.
            out.pop()
        if changed:
            self.applied+=1
            if self.first is None: self.first=step
            self.last=step
        result=canonical_action({"farmer":copy.deepcopy(b["farmer"]),"hands":copy.deepcopy(b["hands"]),"market":out})
        if result["farmer"]!=b["farmer"] or result["hands"]!=b["hands"]:
            raise RuntimeError("V4E changed physical action")
        return result

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

def run(base_main,v48_main,seed,seat,variant):
    cand=BaseWrap(base_main) if variant=="BASE" else HybridWrap(base_main,v48_main,variant)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    if variant!="BASE":
        out.update({
            "variant":variant,"applied_turns":cand.applied,
            "physical_fallback_turns":cand.fallback,
            "category_application_counts":cand.cat_counts,
            "first_applied_step":cand.first,"last_applied_step":cand.last,
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
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")
    rows=[]; failures=[]; provenance={}; started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v4e-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
        paths=[base_main,v48_main]
        for seat in (0,1):
          try:
            purge(paths); base=run(base_main,v48_main,args.seed,seat,"BASE")
            variants={}
            for variant in VARIANTS:
                purge(paths)
                r=run(base_main,v48_main,args.seed,seat,variant)
                r["score_delta"]=r["score"]-base["score"]
                r["margin_delta"]=r["margin"]-base["margin"]
                r["reproduces_loss_to_tie"]=base["score"]==0.0 and r["score"]>=0.5
                variants[variant]=r
            rows.append({"seed":args.seed,"seat":seat,"base":base,"variants":variants})
            print("V4E_CONTEXT",json.dumps({
                "seed":args.seed,"seat":seat,"base_score":base["score"],
                "scores":{k:v["score"] for k,v in variants.items()},
                "margins":{k:v["margin_delta"] for k,v in variants.items()},
            },sort_keys=True),flush=True)
          except Exception as exc:
            failures.append({"seed":args.seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
          finally:
            purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==2
    outp=Path(args.out);outp.parent.mkdir(parents=True,exist_ok=True)
    result={"schema":"kculture-v4e-semantic-decomposition-shard-v1","seed":args.seed,"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started}
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V4E_SHARD_RESULT",json.dumps({"seed":args.seed,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),"seconds":result["seconds"]},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
