#!/usr/bin/env python3
"""V7 first-party option-composition attribution on one frozen ALL3 hard context."""
from __future__ import annotations
import argparse,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

COMPOSITIONS=[
  ("V47",False,False,False),
  ("RW",True,False,False),
  ("TW",False,True,False),
  ("LQ2",False,False,True),
  ("RW_TW",True,True,False),
  ("RW_LQ2",True,False,True),
  ("TW_LQ2",False,True,True),
  ("ALL3",True,True,True),
]

class Candidate:
    def __init__(self,main,use_rw,use_tw,use_lq2):
        self.agent=load_public_agent(main)
        self.state=OptionHostState()
        self.flags=(bool(use_rw),bool(use_tw),bool(use_lq2))
        self.changed_steps=0
        self.steps=0
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        out=apply_option_host(
          obs,config,base,self.state,
          use_rw=self.flags[0],use_tw=self.flags[1],use_lq2=self.flags[2]
        )
        if out!=base:self.changed_steps+=1
        self.steps+=1
        return out

def finish(env,seat,cand):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);margin=mine-opp
    return {
      "reward":mine,"opponent_reward":opp,"rewards":rw,"margin":margin,"score":score(margin),"steps":steps,
      "changed_steps":cand.changed_steps,"rw_used":cand.state.rw_used,"tw_used":cand.state.tw_used,
    }

def run(base_main,opp_main,seed,seat,flags):
    cand=Candidate(base_main,*flags);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat,cand)

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True);ap.add_argument("--index",type=int,required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.config).read_text());contexts=list(cfg.get("selected_hard_contexts") or [])
    if args.index>=len(contexts):raise SystemExit(f"index {args.index} out of range")
    ctx=contexts[args.index];opp_key=str(ctx["opponent"]);seed=int(ctx["seed"]);seat=int(ctx["seat"])
    spec=next(x for x in V2_OPPONENTS if x["key"]==opp_key)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v7-{args.index}-{opp_key}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":opp_key,"family":spec.get("family"),"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");provenance["opponent"]={**rec,"family":spec.get("family")}
        paths=[base_main,opp_main]
        for name,rw,tw,lq2 in COMPOSITIONS:
            try:
                purge(paths)
                r=run(base_main,opp_main,seed,seat,(rw,tw,lq2))
                rows.append({
                  "composition":name,"use_rw":rw,"use_tw":tw,"use_lq2":lq2,
                  "opponent":opp_key,"family":spec.get("family"),"seed":seed,"seat":seat,
                  **r,
                })
                print("V7_COMPOSITION",json.dumps(rows[-1],sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"composition":name,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==len(COMPOSITIONS)
    all3=next((r for r in rows if r["composition"]=="ALL3"),None)
    if mech:
        if float(all3["score"])!=float(ctx["score"]) or float(all3["margin"])!=float(ctx["margin"]):
            failures.append({"phase":"all3_replay","error":f"frozen mismatch {(all3['score'],all3['margin'])} != {(ctx['score'],ctx['margin'])}"})
            mech=False
    ranked=sorted(rows,key=lambda r:(float(r["score"]),float(r["margin"]),r["composition"]),reverse=True)
    result={
      "schema":"kculture-v7-option-composition-context-v1",
      "mechanical_pass":mech,"index":args.index,"context":ctx,"rows":rows,
      "best":ranked[0] if ranked else None,"failures":failures,"provenance":provenance,
      "seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V7_CONTEXT_RESULT",json.dumps({
      "index":args.index,"opponent":opp_key,"seed":seed,"seat":seat,"mechanical_pass":mech,
      "all3":all3,"best":result["best"],"wins":[r["composition"] for r in rows if float(r["score"])==1.0],
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
