#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,plain,score
from tools.first_party_lq2_canonical_sell_queue import lq2_action
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS

EXPECTED_ENGINE="1.32.7"
BASE={"key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination","expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"}
SEEDS=[74501,74502,74503,74504]

def acquire(spec,tmp):
    last=None
    for attempt in range(1,4):
        try:
            main,receipt=acquire_public_main(spec["handle"],tmp/f"attempt-{attempt}")
            observed=sha256_bytes(main.read_bytes())
            if observed!=spec["expected_main_sha256"]: raise RuntimeError(f"identity mismatch {observed}")
            return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,"acquisition_attempt":attempt,**receipt}
        except Exception as exc:
            last=exc
            if attempt<3: time.sleep(2*attempt)
    raise RuntimeError(f"{spec['key']} acquisition failed: {type(last).__name__}: {last}")

class BaseWrap:
    def __init__(self,main): self.agent=load_public_agent(main); self.trace=[]
    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.agent,obs,config)); self.trace.append((int(plain(obs).get("step",len(self.trace))),action_key(b))); return b
class TreatWrap:
    def __init__(self,main): self.agent=load_public_agent(main); self.trace=[]; self.fire_steps=[]
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",len(self.trace))); b=canonical_action(call_agent(self.agent,obs,config)); self.trace.append((step,action_key(b))); o=lq2_action(obs,config,b)
        if action_key(o)!=action_key(b): self.fire_steps.append(step)
        return o

def finish(env,seat):
    p=env.toJSON(); st=[str(x) for x in p.get("statuses",[])]; rw=[float(x) for x in p.get("rewards",[])]; steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720: raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]); margin=mine-opp
    return {"rewards":rw,"margin":margin,"score":score(margin),"steps":steps}

def run(base_main,opp_main,seed,seat,treat):
    cand=TreatWrap(base_main) if treat else BaseWrap(base_main); opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat); out["trace"]=cand.trace
    if treat: out["fire_steps"]=cand.fire_steps
    return out

def parity(b,t):
    fs=t.get("fire_steps",[])
    if not fs: return {"ok":b["trace"]==t["trace"] and b["rewards"]==t["rewards"],"first_fire":None}
    f=min(fs); return {"ok":[x for x in b["trace"] if x[0]<=f]==[x for x in t["trace"] if x[0]<=f],"first_fire":f}

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--opponent",required=True); ap.add_argument("--out",required=True); args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[]; failures=[]; prov={}; started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"lq2-broad-{args.opponent}-") as td:
        tmp=Path(td); base_main,prov["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main; prov["opponent"]={**prov["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,prov["opponent"]=acquire(spec,tmp/"opp")
        paths=[base_main,opp_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                purge(paths); b=run(base_main,opp_main,seed,seat,False); purge(paths); t=run(base_main,opp_main,seed,seat,True)
                p=parity(b,t)
                if not p["ok"]: raise RuntimeError(f"parity failure {p}")
                rows.append({"opponent":args.opponent,"family":spec["family"],"seed":seed,"seat":seat,"base_score":b["score"],"treatment_score":t["score"],"score_delta":t["score"]-b["score"],"base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":t["margin"]-b["margin"],"first_fire":p["first_fire"],"parity":p})
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally: purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==8 and all(r["parity"]["ok"] for r in rows)
    result={"schema":"kculture-o-lq2-broad-shard-v1","opponent":args.opponent,"family":spec["family"],"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,"seconds":time.perf_counter()-started}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ2_BROAD_SHARD_RESULT",json.dumps({"opponent":args.opponent,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),"mean_score_delta":(sum(r["score_delta"] for r in rows)/len(rows) if rows else None)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
