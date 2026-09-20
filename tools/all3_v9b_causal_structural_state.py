#!/usr/bin/env python3
"""V9B one-turn causal structural category isolation on frozen representative states."""
from __future__ import annotations
import argparse,copy,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.all3_v9a_residual_structural_census import classify_market

def nonempty(x):
    return isinstance(x,list) and bool(x)

def sig(x):
    if not nonempty(x): return ("EMPTY",)
    return (str(x[0]), str(x[1]) if len(x)>=2 else None)

def qty_up_transform(base,shadow):
    out=copy.deepcopy(base)
    bslots=[i for i,x in enumerate(base["market"]) if nonempty(x)]
    sorders=[copy.deepcopy(x) for x in shadow["market"] if nonempty(x)]
    if len(bslots)!=len(sorders):
        raise RuntimeError("QTY_UP structure count mismatch")
    changes=[]
    for pos,(bi,so) in enumerate(zip(bslots,sorders)):
        bo=out["market"][bi]
        if sig(bo)!=sig(so):
            raise RuntimeError(f"QTY_UP signature mismatch pos={pos}: {sig(bo)} != {sig(so)}")
        if str(bo[0])=="SELL":
            if len(bo)<3 or len(so)<3:
                raise RuntimeError("QTY_UP SELL missing quantity")
            bq=int(bo[2]);sq=int(so[2])
            if sq<bq:
                raise RuntimeError(f"QTY_UP shadow decreased quantity {bq}->{sq}")
            if sq>bq:
                bo[2]=sq
                changes.append({"slot":bi,"product":str(bo[1]),"before":bq,"after":sq})
        elif bo!=so:
            raise RuntimeError(f"QTY_UP non-SELL payload differs: {bo} != {so}")
    if not changes:
        raise RuntimeError("QTY_UP target produced no quantity increase")
    return out,{"changes":changes}

def isolate(base,shadow,category):
    if base["farmer"]!=shadow["farmer"] or base["hands"]!=shadow["hands"]:
        raise RuntimeError("V9B target has physical divergence")
    live,detail=classify_market(base["market"],shadow["market"])
    if live!=category:
        raise RuntimeError(f"live category mismatch {live} != {category}")
    if category=="QTY_UP":
        out,meta=qty_up_transform(base,shadow)
    elif category=="INSERT_DROP":
        out=copy.deepcopy(base)
        out["market"]=copy.deepcopy(shadow["market"])
        meta={"base_market":copy.deepcopy(base["market"]),"shadow_market":copy.deepcopy(shadow["market"])}
    else:
        raise RuntimeError(f"unsupported V9B category {category}")
    if out["farmer"]!=base["farmer"] or out["hands"]!=base["hands"]:
        raise RuntimeError("V9B isolation changed physical action")
    if action_key(out)==action_key(base):
        raise RuntimeError("V9B isolation did not change action")
    return out,{"live_category":live,"classifier_detail":detail,**meta}

class Candidate:
    def __init__(self,base_main,shadow_main,treatment,target_turn,category):
        self.base=load_public_agent(base_main)
        self.shadow=load_public_agent(shadow_main) if treatment else None
        self.state=OptionHostState()
        self.treatment=bool(treatment)
        self.target_turn=int(target_turn)
        self.category=str(category)
        self.turn=0
        self.trace=[]
        self.target_meta=[]
    def __call__(self,obs,config=None):
        turn=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.state,use_rw=True,use_tw=True,use_lq2=True)
        before_key=action_key(all3)
        out=all3
        if self.treatment:
            shadow=canonical_action(call_agent(self.shadow,obs,config))
            if turn==self.target_turn:
                out,meta=isolate(all3,shadow,self.category)
                self.target_meta.append({"turn":turn,"category":self.category,**meta})
        self.trace.append({"turn":turn,"before":before_key,"after":action_key(out)})
        return out

def finish(env,seat):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);margin=mine-opp
    return {"reward":mine,"opponent_reward":opp,"margin":margin,"score":score(margin),"rewards":rw,"steps":steps}

def run(base_main,shadow_main,opp_main,ctx,state,treatment):
    cand=Candidate(base_main,shadow_main,treatment,state["turn"],state["category"])
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    res=finish(env,int(ctx["seat"]))
    res["trace"]=cand.trace;res["target_meta"]=cand.target_meta
    return res

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contexts",required=True)
    ap.add_argument("--states",required=True)
    ap.add_argument("--state-id",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    contexts=list(json.loads(Path(args.contexts).read_text()).get("selected_hard_contexts") or [])
    states=list(json.loads(Path(args.states).read_text()).get("states") or [])
    state=next((x for x in states if x["id"]==args.state_id),None)
    if state is None:raise SystemExit("unknown state id")
    ctx=contexts[int(state["index"])]
    v48_spec=next(x for x in V2_OPPONENTS if x["key"]=="v48")
    opp_spec=next(x for x in V2_OPPONENTS if x["key"]==ctx["opponent"])
    failure=None;row=None;prov={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v9b-{args.state_id}-") as td:
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

        purge(paths);b=run(base_main,v48_main,opp_main,ctx,state,False)
        purge(paths);t=run(base_main,v48_main,opp_main,ctx,state,True)

        if float(b["score"])!=float(ctx["score"]) or float(b["margin"])!=float(ctx["margin"]):
            raise RuntimeError(f"base replay mismatch {(b['score'],b['margin'])} != {(ctx['score'],ctx['margin'])}")
        target=int(state["turn"])
        bpre=[x for x in b["trace"] if x["turn"]<=target]
        tpre=[x for x in t["trace"] if x["turn"]<=target]
        if len(bpre)!=len(tpre):
            raise RuntimeError("pre-target trace length mismatch")
        for xb,xt in zip(bpre,tpre):
            if xb["before"]!=xt["before"]:
                raise RuntimeError(f"pre-target ALL3 parity mismatch at turn {xb['turn']}")
            if xb["turn"]<target and xb["after"]!=xt["after"]:
                raise RuntimeError(f"pre-target returned-action mismatch at turn {xb['turn']}")
        if len(t["target_meta"])!=1:
            raise RuntimeError(f"expected exactly one target fire, got {len(t['target_meta'])}")
        row={
          "state_id":state["id"],"index":int(state["index"]),"turn":target,
          "category":state["category"],"selection_role":state["selection_role"],
          "opponent":ctx["opponent"],"family":ctx.get("family"),"seed":ctx["seed"],"seat":ctx["seat"],
          "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
          "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
          "loss_to_win":float(b["score"])<1.0 and float(t["score"])==1.0,
          "target_meta":t["target_meta"][0],
        }
    except Exception as exc:
      failure=f"{type(exc).__name__}: {exc}"

    mech=failure is None and row is not None
    result={"schema":"kculture-v9b-causal-state-v1","mechanical_pass":mech,"state":state,
            "context":ctx,"row":row,"failure":failure,"provenance":prov,
            "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V9B_STATE_RESULT",json.dumps({"state_id":state["id"],"mechanical_pass":mech,
      "category":state["category"],"index":state["index"],"turn":state["turn"],
      "score_delta":row["score_delta"] if row else None,"margin_delta":row["margin_delta"] if row else None,
      "loss_to_win":row["loss_to_win"] if row else None,"failure":failure},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
