#!/usr/bin/env python3
"""V8D fresh paired validation shard for frozen O-LQ3C."""
from __future__ import annotations
import argparse,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_lq3c_conditional_sell_order import lq3c_action

SEED_BLOCKS={
 "A":[76001,76002,76003,76004],
 "B":[76005,76006,76007,76008],
 "C":[76009,76010,76011,76012],
}
ALLOWED={"v48","v47_mirror","ready_stock"}

class Candidate:
    def __init__(self,main,treatment):
        self.agent=load_public_agent(main)
        self.state=OptionHostState()
        self.treatment=bool(treatment)
        self.turn=0
        self.trace=[]
        self.fire_meta=[]
    def __call__(self,obs,config=None):
        turn=self.turn;self.turn+=1
        base=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        self.trace.append((turn,action_key(all3)))
        if not self.treatment:return all3
        out,meta=lq3c_action(all3)
        if meta.get("fired"):
            self.fire_meta.append({"turn":turn,**meta})
        return out

def finish(env,seat,cand):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"rewards":rw,"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps,
            "trace":cand.trace,"fire_meta":cand.fire_meta,"fire_count":len(cand.fire_meta)}

def run(base_main,opp_main,seed,seat,treatment):
    cand=Candidate(base_main,treatment);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat,cand)

def parity(base,treat):
    fires=treat.get("fire_meta",[])
    if not fires:
        return base["trace"]==treat["trace"] and base["rewards"]==treat["rewards"]
    first=min(int(x["turn"]) for x in fires)
    bt=[x for x in base["trace"] if x[0]<=first]
    tt=[x for x in treat["trace"] if x[0]<=first]
    return bt==tt

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--block",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    if args.opponent not in ALLOWED:raise SystemExit("bad opponent")
    if args.block not in SEED_BLOCKS:raise SystemExit("bad block")
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};paths=[];started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v8d-{args.opponent}-{args.block}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main;provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");provenance["opponent"]={**rec,"family":spec["family"]}
        paths=[base_main,opp_main]
        for seed in SEED_BLOCKS[args.block]:
          for seat in (0,1):
            key={"opponent":args.opponent,"family":spec["family"],"block":args.block,"seed":seed,"seat":seat}
            try:
                purge(paths);b=run(base_main,opp_main,seed,seat,False)
                purge(paths);t=run(base_main,opp_main,seed,seat,True)
                if not parity(b,t):raise RuntimeError("pre-fire parity failure")
                row={**key,
                     "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                     "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                     "fire_count":t["fire_count"],"fire_turns":[int(x["turn"]) for x in t["fire_meta"]]}
                rows.append(row)
                print("V8D_PAIR",json.dumps(row,sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})
    mech=not failures and len(rows)==8
    result={"schema":"kculture-v8d-lq3c-shard-v1","mechanical_pass":mech,
            "opponent":args.opponent,"block":args.block,"seeds":SEED_BLOCKS[args.block],
            "rows":rows,"failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started,
            "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8D_SHARD_RESULT",json.dumps({"opponent":args.opponent,"block":args.block,"mechanical_pass":mech,
      "rows":len(rows),"fire_contexts":sum(r["fire_count"]>0 for r in rows),
      "positive_score_contexts":sum(r["score_delta"]>0 for r in rows),
      "negative_score_contexts":sum(r["score_delta"]<0 for r in rows),
      "mean_score_delta":sum(r["score_delta"] for r in rows)/len(rows) if rows else 0,
      "mean_margin_delta":sum(r["margin_delta"] for r in rows)/len(rows) if rows else 0,
      "failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
