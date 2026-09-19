#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,math,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,plain,score
from tools.first_party_ready_wool_causal_gate import eligible as rw_eligible,treated_action as rw_treated_action
from tools.first_party_town_wheat_deferral_causal_gate import eligible as tw_eligible,treated_action as tw_treated_action
from tools.first_party_lq2_canonical_sell_queue import lq2_action
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS

EXPECTED_ENGINE="1.32.7"
BASE={"key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination","expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"}
SEEDS=[74601,74602,74603,74604]
VARIANTS=("base","old","lq2","all3")

def obs_hash(obs): return hashlib.sha256(json.dumps(plain(obs),sort_keys=True,separators=(",",":")).encode()).hexdigest()

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

class Host:
    def __init__(self,main,variant):
        self.agent=load_public_agent(main); self.variant=variant
        self.rw_used=False; self.tw_used=False
        self.trace=[]; self.first_trigger_step=None
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((obs_hash(obs),action_key(base)))
        step=int(plain(obs).get("step",len(self.trace)-1))
        out=base
        if self.variant in ("old","all3"):
            if not self.tw_used and tw_eligible(obs,config,base):
                out,removed=tw_treated_action(base)
                if removed<=0: raise RuntimeError("TW1 eligible but removed none")
                self.tw_used=True
            elif not self.rw_used and rw_eligible(obs,base):
                out=rw_treated_action(base); self.rw_used=True
        if self.variant in ("lq2","all3"):
            out=lq2_action(obs,config,out)
        if out["farmer"]!=base["farmer"] or out["hands"]!=base["hands"]:
            raise RuntimeError("triple host changed physical action")
        if action_key(out)!=action_key(base) and self.first_trigger_step is None:
            self.first_trigger_step=step
        return out

def finish(env,seat):
    p=env.toJSON(); st=[str(x) for x in p.get("statuses",[])]; rw=[float(x) for x in p.get("rewards",[])]; steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720: raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]); m=mine-opp
    return {"rewards":rw,"margin":m,"score":score(m),"steps":steps}

def run(base_main,opp_main,seed,seat,variant):
    cand=Host(base_main,variant); opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat); out.update({"trace":cand.trace,"first_trigger_step":cand.first_trigger_step,"rw_used":cand.rw_used,"tw_used":cand.tw_used}); return out

def parity(base,t):
    trig=t["first_trigger_step"]
    if trig is None: return {"ok":base["trace"]==t["trace"] and base["rewards"]==t["rewards"],"triggered":False}
    lim=min(trig,len(base["trace"])-1,len(t["trace"])-1)
    return {"ok":all(base["trace"][i]==t["trace"][i] for i in range(lim+1)),"triggered":True,"trigger_step":trig}

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--opponent",required=True); ap.add_argument("--out",required=True); args=ap.parse_args()
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];prov={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"triple-{args.opponent}-") as td:
        tmp=Path(td); base_main,prov["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main; prov["opponent"]={**prov["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else: opp_main,prov["opponent"]=acquire(spec,tmp/"opp")
        paths=[base_main,opp_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                res={}
                for v in VARIANTS:
                    purge(paths); res[v]=run(base_main,opp_main,seed,seat,v)
                pars={v:parity(res["base"],res[v]) for v in ("old","lq2","all3")}
                if not all(x["ok"] for x in pars.values()): raise RuntimeError(f"parity failure {pars}")
                rows.append({"opponent":args.opponent,"family":spec["family"],"seed":seed,"seat":seat,**res,"parity":pars})
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally: purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==8
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    result={"schema":"kculture-triple-combo-shard-v1","opponent":args.opponent,"family":spec["family"],"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,"seconds":time.perf_counter()-started}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("TRIPLE_COMBO_SHARD_RESULT",json.dumps({"opponent":args.opponent,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures),"score_rates":{v:(statistics.mean(r[v]["score"] for r in rows) if rows else None) for v in VARIANTS}},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
