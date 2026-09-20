#!/usr/bin/env python3
"""V8B pairwise SELL-order transposition oracle on frozen post-LQ2 states."""
from __future__ import annotations
import argparse,copy,itertools,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

class All3Base:
    def __init__(self,main):
        self.agent=load_public_agent(main);self.state=OptionHostState()
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        return apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)

class SwapBranch:
    def __init__(self,main,state_cfg,i,j):
        self.agent=load_public_agent(main);self.state=OptionHostState()
        self.cfg=state_cfg;self.i=int(i);self.j=int(j)
        self.target_seen=False
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",-1))
        base=canonical_action(call_agent(self.agent,obs,config))
        out=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        if step!=int(self.cfg["step"]):
            return out
        self.target_seen=True
        frozen=self.cfg["post_lq2_market"]
        if out["market"]!=frozen:
            raise RuntimeError(f"target market mismatch at step {step}")
        a=int(self.cfg["start"])+self.i
        b=int(self.cfg["start"])+self.j
        if a<0 or b<0 or a>=len(out["market"]) or b>=len(out["market"]) or a==b:
            raise RuntimeError("bad swap positions")
        oa=out["market"][a];ob=out["market"][b]
        if not (isinstance(oa,list) and oa and oa[0]=="SELL" and isinstance(ob,list) and ob and ob[0]=="SELL"):
            raise RuntimeError("swap positions are not SELL orders")
        m=copy.deepcopy(out["market"])
        before=sorted(json.dumps(x,sort_keys=True) for x in m)
        m[a],m[b]=m[b],m[a]
        after=sorted(json.dumps(x,sort_keys=True) for x in m)
        if before!=after:
            raise RuntimeError("market order multiset changed")
        result=canonical_action({"farmer":copy.deepcopy(out["farmer"]),"hands":copy.deepcopy(out["hands"]),"market":m})
        if result["farmer"]!=out["farmer"] or result["hands"]!=out["hands"]:
            raise RuntimeError("physical action changed")
        return result

def finish(env,seat,wrapper=None):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    if wrapper is not None and not wrapper.target_seen:
        raise RuntimeError("target step not seen")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps}

def run_base(base_main,opp_main,seed,seat):
    cand=All3Base(base_main);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat)

def run_swap(base_main,opp_main,seed,seat,state_cfg,i,j):
    cand=SwapBranch(base_main,state_cfg,i,j);opp=load_public_agent(opp_main)
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
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--state-config",required=True)
    ap.add_argument("--index",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    hard=json.loads(Path(args.hard_config).read_text())
    states=json.loads(Path(args.state_config).read_text())
    contexts=list(hard.get("selected_hard_contexts") or [])
    ctx=contexts[args.index];opp_key=str(ctx["opponent"]);seed=int(ctx["seed"]);seat=int(ctx["seat"])
    targets=[s for s in states.get("selected_states",[]) if int(s["index"])==args.index]
    spec=next(x for x in V2_OPPONENTS if x["key"]==opp_key)
    branches=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v8b-{args.index}-{opp_key}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":opp_key,"family":spec.get("family"),"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");provenance["opponent"]={**rec,"family":spec.get("family")}
        paths=[base_main,opp_main]

        purge(paths);base=run_base(base_main,opp_main,seed,seat)
        if float(base["score"])!=float(ctx["score"]) or float(base["margin"])!=float(ctx["margin"]):
            raise RuntimeError(f"ALL3 base mismatch {(base['score'],base['margin'])} != {(ctx['score'],ctx['margin'])}")

        for t in targets:
            n=int(t["nonempty_sell_orders"]) if "nonempty_sell_orders" in t else int(t["end"])-int(t["start"])+1
            for i,j in itertools.combinations(range(n),2):
                try:
                    purge(paths)
                    r=run_swap(base_main,opp_main,seed,seat,t,i,j)
                    a=int(t["start"])+i;b=int(t["start"])+j
                    oi=t["post_lq2_market"][a];oj=t["post_lq2_market"][b]
                    row={
                      "index":args.index,"opponent":opp_key,"family":ctx.get("family"),"seed":seed,"seat":seat,
                      "step":int(t["step"]),"run_start":int(t["start"]),"run_end":int(t["end"]),
                      "i":i,"j":j,"slot_i":a,"slot_j":b,
                      "order_i":oi,"order_j":oj,
                      "product_i":str(oi[1]),"product_j":str(oj[1]),
                      "base_score":base["score"],"base_margin":base["margin"],
                      "score":r["score"],"margin":r["margin"],
                      "score_delta":float(r["score"])-float(base["score"]),
                      "margin_delta":float(r["margin"])-float(base["margin"]),
                    }
                    branches.append(row)
                    print("V8B_BRANCH",json.dumps(row,sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"step":t["step"],"i":i,"j":j,"error":f"{type(exc).__name__}: {exc}"})
        best=max(
          [{"label":"BASE","score":base["score"],"margin":base["margin"],"margin_delta":0.0}]+
          [{"label":"SWAP",**x} for x in branches],
          key=lambda x:(float(x["score"]),float(x["margin"]),str(x.get("product_i","")),str(x.get("product_j","")),-int(x.get("step",0)))
        )
        mech=not failures and len(targets)==2
        result={
          "schema":"kculture-v8b-lq2-order-context-v1","mechanical_pass":mech,
          "index":args.index,"context":ctx,"base":base,"targets":targets,
          "branches":branches,"best":best,"failures":failures,"provenance":provenance,
          "seconds":time.perf_counter()-started,
        }
    except Exception as exc:
      failures.append({"phase":"setup_or_base","error":f"{type(exc).__name__}: {exc}"})
      result={
        "schema":"kculture-v8b-lq2-order-context-v1","mechanical_pass":False,
        "index":args.index,"context":ctx,"branches":branches,"failures":failures,
        "seconds":time.perf_counter()-started,
      }
    finally:
      try:purge(paths)
      except Exception:pass

    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8B_CONTEXT_RESULT",json.dumps({
      "index":args.index,"opponent":opp_key,"seed":seed,"seat":seat,
      "mechanical_pass":result.get("mechanical_pass"),"branch_count":len(branches),
      "base":result.get("base"),"best":result.get("best"),
      "winning_branches":sum(float(x["score"])==1.0 for x in branches),
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not result.get("mechanical_pass"):raise SystemExit(2)

if __name__=="__main__":main()
