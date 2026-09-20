#!/usr/bin/env python3
"""V10A cumulative residual market upper bound over exact ALL3 hard contexts."""
from __future__ import annotations
import argparse,copy,json,math,sys,tempfile,time
from collections import Counter
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.all3_v9a_residual_structural_census import classify_market
from tools.all3_v9b_causal_structural_state import qty_up_transform

MODES=("BASE","FULL_ALL","FULL_W2PLUS","STRUCT_W2PLUS","INSERT_W2PLUS","QTY_W2PLUS","REORDER_W2PLUS")

def physical_equal(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]

class Candidate:
    def __init__(self,base_main,shadow_main,mode):
        self.base=load_public_agent(base_main)
        self.shadow=load_public_agent(shadow_main) if mode!="BASE" else None
        self.state=OptionHostState()
        self.mode=str(mode)
        self.turn=0
        self.substitutions=0
        self.physical_fallbacks=0
        self.live_categories=Counter()
        self.applied_categories=Counter()
    def __call__(self,obs,config=None):
        turn=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.state,use_rw=True,use_tw=True,use_lq2=True)
        if self.mode=="BASE":
            return all3

        shadow=canonical_action(call_agent(self.shadow,obs,config))
        if not physical_equal(all3,shadow):
            self.physical_fallbacks+=1
            return all3

        cat,detail=classify_market(all3["market"],shadow["market"])
        if cat!="EXACT":
            self.live_categories[cat]+=1

        out=all3
        if self.mode=="FULL_ALL":
            if all3["market"]!=shadow["market"]:
                out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
                self.substitutions+=1;self.applied_categories[cat]+=1
        elif turn>=336:
            if self.mode=="FULL_W2PLUS":
                if all3["market"]!=shadow["market"]:
                    out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
                    self.substitutions+=1;self.applied_categories[cat]+=1
            elif self.mode=="STRUCT_W2PLUS":
                if cat=="INSERT_DROP":
                    out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
                    self.substitutions+=1;self.applied_categories[cat]+=1
                elif cat=="QTY_UP":
                    out,_=qty_up_transform(all3,shadow)
                    self.substitutions+=1;self.applied_categories[cat]+=1
            elif self.mode=="INSERT_W2PLUS" and cat=="INSERT_DROP":
                out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
                self.substitutions+=1;self.applied_categories[cat]+=1
            elif self.mode=="QTY_W2PLUS" and cat=="QTY_UP":
                out,_=qty_up_transform(all3,shadow)
                self.substitutions+=1;self.applied_categories[cat]+=1
            elif self.mode=="REORDER_W2PLUS" and cat=="REORDER_ONLY":
                out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
                self.substitutions+=1;self.applied_categories[cat]+=1

        if out["farmer"]!=all3["farmer"] or out["hands"]!=all3["hands"]:
            raise RuntimeError("V10A changed ALL3 physical action")
        return out

def finish(env,seat):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"rewards":rw,"steps":steps}

def run(base_main,shadow_main,opp_main,ctx,mode):
    cand=Candidate(base_main,shadow_main,mode)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    res=finish(env,int(ctx["seat"]))
    res.update({
      "mode":mode,
      "substitutions":cand.substitutions,
      "physical_fallbacks":cand.physical_fallbacks,
      "live_categories":dict(sorted(cand.live_categories.items())),
      "applied_categories":dict(sorted(cand.applied_categories.items())),
    })
    return res

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--contexts",required=True);ap.add_argument("--index",type=int,required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    contexts=list(json.loads(Path(args.contexts).read_text()).get("selected_hard_contexts") or [])
    if args.index<0 or args.index>=len(contexts):raise SystemExit("bad index")
    ctx=contexts[args.index]
    v48_spec=next(x for x in V2_OPPONENTS if x["key"]=="v48")
    opp_spec=next(x for x in V2_OPPONENTS if x["key"]==ctx["opponent"])
    rows=[];failures=[];prov={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v10a-{args.index}-") as td:
        tmp=Path(td)
        base_main,prov["base"]=acquire(BASE,tmp/"base")
        v48_main,prov["v48_shadow"]=acquire(v48_spec,tmp/"v48")
        paths=[base_main,v48_main]
        if opp_spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
        elif opp_spec["expected_main_sha256"]==v48_spec["expected_main_sha256"]:
            opp_main=v48_main
        else:
            opp_main,prov["opponent"]=acquire(opp_spec,tmp/"opp");paths.append(opp_main)

        base_res=None
        for mode in MODES:
            try:
                purge(paths)
                rr=run(base_main,v48_main,opp_main,ctx,mode)
                if mode=="BASE":
                    if float(rr["score"])!=float(ctx["score"]) or float(rr["margin"])!=float(ctx["margin"]):
                        raise RuntimeError(f"base replay mismatch {(rr['score'],rr['margin'])} != {(ctx['score'],ctx['margin'])}")
                    base_res=rr
                if base_res is None:
                    raise RuntimeError("BASE must run first")
                row={
                  "index":args.index,"opponent":ctx["opponent"],"family":ctx.get("family"),
                  "seed":ctx["seed"],"seat":ctx["seat"],"mode":mode,
                  "base_score":base_res["score"],"treatment_score":rr["score"],
                  "score_delta":float(rr["score"])-float(base_res["score"]),
                  "base_margin":base_res["margin"],"treatment_margin":rr["margin"],
                  "margin_delta":float(rr["margin"])-float(base_res["margin"]),
                  "substitutions":rr["substitutions"],
                  "physical_fallbacks":rr["physical_fallbacks"],
                  "live_categories":rr["live_categories"],
                  "applied_categories":rr["applied_categories"],
                }
                rows.append(row)
                print("V10A_MODE",json.dumps(row,sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"index":args.index,"mode":mode,"error":f"{type(exc).__name__}: {exc}"})
    except Exception as exc:
      failures.append({"index":args.index,"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==len(MODES)
    result={"schema":"kculture-v10a-context-v1","mechanical_pass":mech,"index":args.index,
      "context":ctx,"rows":rows,"failures":failures,"provenance":prov,
      "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V10A_CONTEXT_RESULT",json.dumps({"index":args.index,"mechanical_pass":mech,"failures":len(failures),
      "modes":{r["mode"]:{"score_delta":r["score_delta"],"margin_delta":r["margin_delta"],
      "substitutions":r["substitutions"],"physical_fallbacks":r["physical_fallbacks"]} for r in rows}},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
