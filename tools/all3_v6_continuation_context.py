#!/usr/bin/env python3
"""V6 bounded 2-3 turn one-locus physical continuation oracle for one frozen hard context."""
from __future__ import annotations
import argparse,copy,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.adaptive_wrapper_proposal_oracle_v3 import PROPOSERS
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,obs_step,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

MIN_STEP=120
MAX_STEP=600
MIN_SEPARATION=120
MAX_EVENTS=2
MAX_SOURCE_LOCUS=4
HORIZONS=(2,3)

def all3_from(base_agent,host_state,obs,config):
    raw=canonical_action(call_agent(base_agent,obs,config))
    return apply_option_host(obs,config,raw,host_state)

def _unit_at(a,locus):
    a=canonical_action(a)
    if locus=="farmer": return copy.deepcopy(a["farmer"])
    if locus.startswith("hand:"):
        i=int(locus.split(":",1)[1])
        if 0<=i<len(a["hands"]): return copy.deepcopy(a["hands"][i])
    return None

def _hybrid(base,locus,new_unit):
    a=canonical_action(base)
    farmer=copy.deepcopy(a["farmer"]);hands=copy.deepcopy(a["hands"])
    if locus=="farmer":
        farmer=copy.deepcopy(new_unit)
    elif locus.startswith("hand:"):
        i=int(locus.split(":",1)[1])
        if not (0<=i<len(hands)): return None
        hands[i]=copy.deepcopy(new_unit)
    else:
        return None
    out=canonical_action({"farmer":farmer,"hands":hands,"market":copy.deepcopy(a["market"])})
    return out

def grouped_localized(base,shadow_actions):
    base=canonical_action(base);bkey=action_key(base);grouped={}
    for source,raw in sorted(shadow_actions.items()):
        a=canonical_action(raw)
        pairs=[]
        if a["farmer"]!=base["farmer"]:
            pairs.append(("farmer",a["farmer"]))
        n=min(len(a["hands"]),len(base["hands"]))
        for i in range(n):
            if a["hands"][i]!=base["hands"][i]:
                pairs.append((f"hand:{i}",a["hands"][i]))
        for locus,new_unit in pairs:
            h=_hybrid(base,locus,new_unit)
            if h is None or action_key(h)==bkey: continue
            k=action_key(h)
            rec=grouped.get(k)
            if rec is None:
                grouped[k]={
                  "action_key":k,"locus":locus,
                  "old_unit":_unit_at(base,locus),"new_unit":copy.deepcopy(new_unit),
                  "sources":[source],
                }
            else:
                rec["sources"].append(source)
    out=list(grouped.values())
    for p in out:
        p["sources"]=sorted(set(p["sources"]));p["support"]=len(p["sources"])
    out.sort(key=lambda p:(-p["support"],p["locus"],p["action_key"]))
    return out

def select_events(trace):
    eligible=[r for r in trace if MIN_STEP<=int(r["step"])<=MAX_STEP and r["proposals"]]
    ranked=sorted(
      eligible,
      key=lambda r:(-max(int(p["support"]) for p in r["proposals"]),-len(r["proposals"]),int(r["step"]))
    )
    chosen=[]
    for row in ranked:
        st=int(row["step"])
        if any(abs(st-int(x["step"]))<MIN_SEPARATION for x in chosen): continue
        chosen.append(row)
        if len(chosen)>=MAX_EVENTS: break
    return sorted(chosen,key=lambda r:int(r["step"]))

def source_locus_candidates(event):
    flat=[]
    for p in event["proposals"]:
        for src in p["sources"]:
            flat.append({
              "source":src,"locus":p["locus"],"support":p["support"],
              "first_action_key":p["action_key"],
              "old_unit":copy.deepcopy(p["old_unit"]),"new_unit":copy.deepcopy(p["new_unit"]),
            })
    flat.sort(key=lambda x:(-int(x["support"]),x["locus"],x["source"],x["first_action_key"]))
    return flat[:MAX_SOURCE_LOCUS]

class Discovery:
    def __init__(self,base_main,proposer_paths):
        self.base=load_public_agent(base_main);self.host=OptionHostState()
        self.shadows={k:load_public_agent(p) for k,p in sorted(proposer_paths.items())}
        self.trace=[]
    def __call__(self,obs,config=None):
        step=obs_step(obs)
        base=all3_from(self.base,self.host,obs,config)
        shadows={k:canonical_action(call_agent(a,obs,config)) for k,a in self.shadows.items()}
        self.trace.append({
          "step":step,"base_action_key":action_key(base),
          "proposals":copy.deepcopy(grouped_localized(base,shadows)),
        })
        return base

class BaseAll3:
    def __init__(self,base_main):
        self.base=load_public_agent(base_main);self.host=OptionHostState()
    def __call__(self,obs,config=None):
        return all3_from(self.base,self.host,obs,config)

class Continuation:
    def __init__(self,base_main,source_main,*,target_step,locus,horizon,expected_base_key):
        self.base=load_public_agent(base_main);self.host=OptionHostState()
        self.source=load_public_agent(source_main)
        self.target_step=int(target_step);self.locus=str(locus);self.horizon=int(horizon)
        self.expected_base_key=str(expected_base_key)
        self.target_seen=False;self.branch_steps=[];self.market_parity=True;self.other_locus_parity=True
    def __call__(self,obs,config=None):
        step=obs_step(obs)
        base=all3_from(self.base,self.host,obs,config)
        shadow=canonical_action(call_agent(self.source,obs,config))
        if step<self.target_step or step>=self.target_step+self.horizon:
            return base
        if step==self.target_step:
            self.target_seen=True
            if action_key(base)!=self.expected_base_key:
                raise RuntimeError(f"ALL3 base mismatch at target {step}")
        unit=_unit_at(shadow,self.locus)
        if unit is None:
            raise RuntimeError(f"source locus missing at step {step}: {self.locus}")
        out=_hybrid(base,self.locus,unit)
        if out is None: raise RuntimeError("hybrid construction failed")
        if out["market"]!=base["market"]:
            self.market_parity=False;raise RuntimeError("market changed in continuation")
        # Verify every nonselected physical locus.
        if self.locus!="farmer" and out["farmer"]!=base["farmer"]:
            self.other_locus_parity=False;raise RuntimeError("farmer changed outside selected locus")
        for i,(x,y) in enumerate(zip(out["hands"],base["hands"])):
            if self.locus==f"hand:{i}": continue
            if x!=y:
                self.other_locus_parity=False;raise RuntimeError(f"hand:{i} changed outside selected locus")
        self.branch_steps.append({
          "step":step,"base_unit":_unit_at(base,self.locus),"source_unit":copy.deepcopy(unit),
          "changed":_unit_at(base,self.locus)!=unit,
        })
        return out

def finish(env,seat,wrapper=None):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    if wrapper is not None:
        if not wrapper.target_seen: raise RuntimeError("continuation target not seen")
        if len(wrapper.branch_steps)!=wrapper.horizon:
            raise RuntimeError(f"continuation length mismatch {len(wrapper.branch_steps)} != {wrapper.horizon}")
        if not wrapper.market_parity or not wrapper.other_locus_parity:
            raise RuntimeError("continuation parity failure")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"rewards":rw,"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps}

def run_base(base_main,opp_main,seed,seat):
    cand=BaseAll3(base_main);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat)

def run_discovery(base_main,proposer_paths,opp_main,seed,seat):
    cand=Discovery(base_main,proposer_paths);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    r=finish(env,seat);r["trace"]=cand.trace;return r

def run_branch(base_main,source_main,opp_main,seed,seat,event,candidate,horizon):
    cand=Continuation(
      base_main,source_main,target_step=event["step"],locus=candidate["locus"],
      horizon=horizon,expected_base_key=event["base_action_key"]
    )
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    r=finish(env,seat,cand);r["branch_steps"]=cand.branch_steps;return r

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    ap.add_argument("--index",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text())
    contexts=list(cfg.get("selected_hard_contexts") or [])
    if args.index>=len(contexts):
        result={"schema":"kculture-v6-continuation-context-v1","active":False,"index":args.index,"mechanical_pass":True,"rows":[],"failures":[]}
        p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V6_CONTEXT_RESULT",json.dumps({"index":args.index,"active":False,"mechanical_pass":True},sort_keys=True));return

    ctx=contexts[args.index]
    opp_key=str(ctx["opponent"]);seed=int(ctx["seed"]);seat=int(ctx["seat"])
    spec=next(x for x in V2_OPPONENTS if x["key"]==opp_key)
    failures=[];branches=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v6-{args.index}-{opp_key}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        paths_by_sha={BASE["expected_main_sha256"]:base_main}
        proposer_paths={}
        for ps in PROPOSERS:
            sha=ps["expected_main_sha256"]
            if sha in paths_by_sha:
                pp=paths_by_sha[sha];rec={"observed_main_sha256":sha,"reused_exact_bytes":True}
            else:
                pp,rec=acquire(ps,tmp/f"prop_{ps['key']}");paths_by_sha[sha]=pp
            proposer_paths[ps["key"]]=pp;provenance[ps["key"]]={"key":ps["key"],**rec}
        sha=spec["expected_main_sha256"]
        if sha in paths_by_sha:
            opp_main=paths_by_sha[sha];provenance["opponent"]={"key":opp_key,"observed_main_sha256":sha,"reused_exact_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");paths_by_sha[sha]=opp_main;provenance["opponent"]={**rec,"key":opp_key}
        all_paths=list({str(p.resolve()):p for p in [base_main,*proposer_paths.values(),opp_main]}.values())

        purge(all_paths);base=run_base(base_main,opp_main,seed,seat)
        exp_score=float(ctx["score"]);exp_margin=float(ctx["margin"])
        if float(base["score"])!=exp_score or float(base["margin"])!=exp_margin:
            raise RuntimeError(f"frozen base mismatch score/margin {(base['score'],base['margin'])} != {(exp_score,exp_margin)}")
        purge(all_paths);disc=run_discovery(base_main,proposer_paths,opp_main,seed,seat)
        if disc["rewards"]!=base["rewards"]:
            raise RuntimeError("shadow discovery changed base final rewards")
        events=select_events(disc["trace"])
        for event in events:
            candidates=source_locus_candidates(event)
            for cand in candidates:
                for horizon in HORIZONS:
                    try:
                        purge(all_paths)
                        r=run_branch(base_main,proposer_paths[cand["source"]],opp_main,seed,seat,event,cand,horizon)
                        branches.append({
                          "step":int(event["step"]),"source":cand["source"],"locus":cand["locus"],
                          "support":int(cand["support"]),"old_unit":cand["old_unit"],"new_unit":cand["new_unit"],
                          "horizon":horizon,"score":r["score"],"margin":r["margin"],
                          "score_delta":float(r["score"])-float(base["score"]),
                          "margin_delta":float(r["margin"])-float(base["margin"]),
                          "branch_steps":r["branch_steps"],
                        })
                    except Exception as exc:
                        failures.append({"step":event["step"],"source":cand["source"],"locus":cand["locus"],"horizon":horizon,"error":f"{type(exc).__name__}: {exc}"})
        best=max(
          [{"label":"BASE","score":base["score"],"margin":base["margin"]}]+[
            {"label":"CONTINUATION",**b} for b in branches
          ],
          key=lambda x:(float(x["score"]),float(x["margin"]),str(x.get("source","")),str(x.get("locus","")),-int(x.get("horizon",0)))
        )
        mech=not failures
        result={
          "schema":"kculture-v6-continuation-context-v1","active":True,"index":args.index,
          "context":ctx,"base":base,"discovery_parity":disc["rewards"]==base["rewards"],
          "selected_events":[{"step":e["step"],"candidates":source_locus_candidates(e)} for e in events],
          "branches":branches,"oracle":best,"mechanical_pass":mech,"failures":failures,
          "provenance":provenance,"seconds":time.perf_counter()-started,
        }
    except Exception as exc:
      failures.append({"phase":"setup_or_base","error":f"{type(exc).__name__}: {exc}"})
      result={
        "schema":"kculture-v6-continuation-context-v1","active":True,"index":args.index,
        "context":ctx,"mechanical_pass":False,"branches":branches,"failures":failures,
        "seconds":time.perf_counter()-started,
      }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V6_CONTEXT_RESULT",json.dumps({
      "index":args.index,"active":True,"opponent":opp_key,"seed":seed,"seat":seat,
      "mechanical_pass":result.get("mechanical_pass"),"branch_count":len(branches),
      "base_score":result.get("base",{}).get("score"),"base_margin":result.get("base",{}).get("margin"),
      "oracle":result.get("oracle"),"failures":len(failures),
    },sort_keys=True),flush=True)
    if not result.get("mechanical_pass"):raise SystemExit(2)
if __name__=="__main__":main()
