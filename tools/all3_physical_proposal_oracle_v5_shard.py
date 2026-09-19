#!/usr/bin/env python3
"""ALL3 Physical Proposal Oracle V5 shard.

Runs one opponent family. Third-party public agents are shadow proposers only.
Every evaluated branch substitutes exactly one farmer/hand physical action once,
preserving the exact ALL3 market action.
"""
from __future__ import annotations
import argparse,copy,json,math,statistics,sys,tempfile,time
from collections import Counter
from pathlib import Path
from typing import Any
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.adaptive_wrapper_proposal_oracle_v2 import EXPECTED_ENGINE,BASE,acquire
from tools.adaptive_wrapper_proposal_oracle_v3 import PROPOSERS
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,obs_step,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

SEEDS=(75001,75002)
MIN_STEP=120
MAX_STEP=647
MIN_SEPARATION=96
MAX_EVENTS=2
MAX_PROPOSALS=6

def all3_from(base_agent,host_state,obs,config):
    raw=canonical_action(call_agent(base_agent,obs,config))
    return apply_option_host(obs,config,raw,host_state)

def _hybrid(base,locus,new_unit):
    a=canonical_action(base)
    if locus=="farmer":
        farmer=copy.deepcopy(new_unit);hands=copy.deepcopy(a["hands"])
    else:
        farmer=copy.deepcopy(a["farmer"]);hands=copy.deepcopy(a["hands"])
        idx=int(locus.split(":",1)[1])
        if idx<0 or idx>=len(hands):
            return None
        hands[idx]=copy.deepcopy(new_unit)
    return canonical_action({"farmer":farmer,"hands":hands,"market":copy.deepcopy(a["market"])})

def localized_proposals(base,shadow_actions):
    base=canonical_action(base)
    bkey=action_key(base)
    grouped={}
    for source,raw in sorted(shadow_actions.items()):
        a=canonical_action(raw)
        candidates=[]
        if a["farmer"]!=base["farmer"]:
            candidates.append(("farmer",a["farmer"]))
        n=min(len(a["hands"]),len(base["hands"]))
        for i in range(n):
            if a["hands"][i]!=base["hands"][i]:
                candidates.append((f"hand:{i}",a["hands"][i]))
        for locus,new_unit in candidates:
            h=_hybrid(base,locus,new_unit)
            if h is None or len(h["market"])>10:
                continue
            k=action_key(h)
            if k==bkey:
                continue
            rec=grouped.get(k)
            if rec is None:
                grouped[k]={
                    "action_key":k,
                    "action":h,
                    "locus":locus,
                    "new_unit":copy.deepcopy(new_unit),
                    "old_unit":copy.deepcopy(base["farmer"] if locus=="farmer" else base["hands"][int(locus.split(":")[1])]),
                    "sources":[source],
                }
            else:
                rec["sources"].append(source)
    proposals=list(grouped.values())
    for p in proposals:
        p["sources"]=sorted(set(p["sources"]))
        p["support"]=len(p["sources"])
    proposals.sort(key=lambda p:(-p["support"],p["locus"],p["action_key"]))
    return proposals[:MAX_PROPOSALS]

def select_events(trace):
    eligible=[r for r in trace if MIN_STEP<=int(r["step"])<=MAX_STEP and r["proposals"]]
    ranked=sorted(
        eligible,
        key=lambda r:(
            -max(int(p["support"]) for p in r["proposals"]),
            -len(r["proposals"]),
            int(r["step"]),
        ),
    )
    selected=[]
    for row in ranked:
        step=int(row["step"])
        if any(abs(step-int(x["step"]))<MIN_SEPARATION for x in selected):
            continue
        selected.append(row)
        if len(selected)>=MAX_EVENTS:
            break
    return sorted(selected,key=lambda r:int(r["step"]))

class Discovery:
    def __init__(self,base_main,proposer_paths):
        self.base=load_public_agent(base_main)
        self.host=OptionHostState()
        self.shadows={k:load_public_agent(p) for k,p in sorted(proposer_paths.items())}
        self.trace=[]
    def __call__(self,obs,config=None):
        step=obs_step(obs)
        base=all3_from(self.base,self.host,obs,config)
        shadows={k:canonical_action(call_agent(a,obs,config)) for k,a in self.shadows.items()}
        props=localized_proposals(base,shadows)
        self.trace.append({
            "step":step,"base_action":copy.deepcopy(base),
            "base_action_key":action_key(base),"proposals":copy.deepcopy(props),
        })
        return base

class BaseAll3:
    def __init__(self,base_main):
        self.base=load_public_agent(base_main);self.host=OptionHostState()
    def __call__(self,obs,config=None):
        return all3_from(self.base,self.host,obs,config)

class Branch:
    def __init__(self,base_main,proposer_paths,target_step,expected_base_key,expected_proposal_key):
        self.base=load_public_agent(base_main);self.host=OptionHostState()
        self.shadows={k:load_public_agent(p) for k,p in sorted(proposer_paths.items())}
        self.target_step=int(target_step)
        self.expected_base_key=str(expected_base_key)
        self.expected_proposal_key=str(expected_proposal_key)
        self.target_seen=False
    def __call__(self,obs,config=None):
        step=obs_step(obs)
        base=all3_from(self.base,self.host,obs,config)
        shadows={k:canonical_action(call_agent(a,obs,config)) for k,a in self.shadows.items()}
        if step!=self.target_step:
            return base
        self.target_seen=True
        if action_key(base)!=self.expected_base_key:
            raise RuntimeError(f"ALL3 base mismatch at target step {step}")
        props=localized_proposals(base,shadows)
        hit=next((p for p in props if p["action_key"]==self.expected_proposal_key),None)
        if hit is None:
            raise RuntimeError(f"physical proposal not reproduced at step {step}")
        return hit["action"]

def finish(env,seat,wrapper=None):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    if wrapper is not None and hasattr(wrapper,"target_seen") and not wrapper.target_seen:
        raise RuntimeError(f"target step {wrapper.target_step} not reached")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"rewards":rw,"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps}

def run_discovery(base_main,proposer_paths,opp_main,seed,seat):
    cand=Discovery(base_main,proposer_paths);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat);out["trace"]=cand.trace;return out

def run_base(base_main,opp_main,seed,seat):
    cand=BaseAll3(base_main);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    return finish(env,seat)

def run_branch(base_main,proposer_paths,opp_main,seed,seat,event,proposal):
    cand=Branch(base_main,proposer_paths,event["step"],event["base_action_key"],proposal["action_key"])
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    return finish(env,seat,cand)

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def summarize(rows):
    if not rows:return {}
    bs=[float(r["base"]["score"]) for r in rows];os=[float(r["oracle"]["score"]) for r in rows]
    md=[float(r["oracle"]["margin"]-r["base"]["margin"]) for r in rows]
    return {
      "branch_states":len(rows),
      "base_score_rate":statistics.fmean(bs),
      "oracle_score_rate":statistics.fmean(os),
      "score_delta":statistics.fmean(os)-statistics.fmean(bs),
      "mean_oracle_margin_delta":statistics.fmean(md),
      "median_oracle_margin_delta":statistics.median(md),
      "nonwin_to_win_flips":sum(r["base"]["score"]<1 and r["oracle"]["score"]==1 for r in rows),
      "loss_to_win_flips":sum(r["base"]["score"]==0 and r["oracle"]["score"]==1 for r in rows),
      "positive_margin_states":sum(x>0 for x in md),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    opp_spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    failures=[];rows=[];matchups=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v5-physical-{args.opponent}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        paths_by_sha={BASE["expected_main_sha256"]:base_main}
        proposer_paths={}
        for spec in PROPOSERS:
            sha=spec["expected_main_sha256"]
            if sha in paths_by_sha:
                p=paths_by_sha[sha];rec={"reused_exact_bytes":True,"observed_main_sha256":sha}
            else:
                p,rec=acquire(spec,tmp/f"prop_{spec['key']}");paths_by_sha[sha]=p
            proposer_paths[spec["key"]]=p
            provenance[spec["key"]]={"key":spec["key"],"handle":spec["handle"],**rec}
        sha=opp_spec["expected_main_sha256"]
        if sha in paths_by_sha:
            opp_main=paths_by_sha[sha]
            provenance["opponent"]={"key":opp_spec["key"],"family":opp_spec.get("family"),"reused_exact_bytes":True,"observed_main_sha256":sha}
        else:
            opp_main,rec=acquire(opp_spec,tmp/"opponent");paths_by_sha[sha]=opp_main
            provenance["opponent"]={**rec,"family":opp_spec.get("family")}
        all_paths=list({str(p.resolve()):p for p in [base_main,*proposer_paths.values(),opp_main]}.values())

        for seed in SEEDS:
          for seat in (0,1):
            key={"opponent":args.opponent,"family":opp_spec.get("family"),"seed":seed,"seat":seat}
            try:
                purge(all_paths);disc=run_discovery(base_main,proposer_paths,opp_main,seed,seat)
                purge(all_paths);base=run_base(base_main,opp_main,seed,seat)
                if disc["rewards"]!=base["rewards"]:
                    raise RuntimeError(f"shadow discovery changed ALL3 rewards {disc['rewards']} != {base['rewards']}")
                events=select_events(disc["trace"])
                matchups.append({
                  **key,"replay_parity":True,"base_rewards":base["rewards"],"base_margin":base["margin"],
                  "physical_disagreement_states":sum(1 for r in disc["trace"] if r["proposals"]),
                  "selected_steps":[int(e["step"]) for e in events],
                  "selected_counts":[len(e["proposals"]) for e in events],
                })
                for event in events:
                    candidates=[{
                      "label":"BASE","sources":["ALL3"],"action_key":event["base_action_key"],
                      "locus":None,"old_unit":None,"new_unit":None,
                      "reward":base["reward"],"opponent_reward":base["opponent_reward"],
                      "margin":base["margin"],"score":base["score"],
                    }]
                    for prop in event["proposals"]:
                        purge(all_paths);res=run_branch(base_main,proposer_paths,opp_main,seed,seat,event,prop)
                        candidates.append({
                          "label":"PHYSICAL_LOCAL","sources":prop["sources"],"support":prop["support"],
                          "action_key":prop["action_key"],"locus":prop["locus"],
                          "old_unit":prop["old_unit"],"new_unit":prop["new_unit"],
                          "reward":res["reward"],"opponent_reward":res["opponent_reward"],
                          "margin":res["margin"],"score":res["score"],
                        })
                    oracle=max(candidates,key=lambda x:(float(x["score"]),float(x["margin"]),str(x.get("locus")),",".join(x.get("sources",[]))))
                    rows.append({
                      **key,"step":int(event["step"]),"proposal_count":len(candidates),
                      "base":candidates[0],"oracle":oracle,"candidates":candidates,
                    })
                    print("V5_PHYSICAL_BRANCH",json.dumps({
                      **key,"step":event["step"],"proposal_count":len(candidates),
                      "base_score":base["score"],"oracle_score":oracle["score"],
                      "margin_delta":oracle["margin"]-base["margin"],
                      "locus":oracle.get("locus"),"old_unit":oracle.get("old_unit"),
                      "new_unit":oracle.get("new_unit"),"sources":oracle.get("sources"),
                    },sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
            finally:purge(all_paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    summary=summarize(rows)
    mech=not failures and len(matchups)==4 and all(m.get("replay_parity") for m in matchups)
    result={
      "schema":"kculture-all3-physical-proposal-v5-shard",
      "opponent":args.opponent,"family":opp_spec.get("family"),"seeds":SEEDS,
      "mechanical_pass":mech,"summary":summary,"matchups":matchups,"rows":rows,
      "failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started,
      "offline_oracle_only":True,"third_party_code_persisted":False,"automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V5_PHYSICAL_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"mechanical_pass":mech,"summary":summary,
      "branch_states":len(rows),"failures":len(failures),"seconds":result["seconds"]
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
