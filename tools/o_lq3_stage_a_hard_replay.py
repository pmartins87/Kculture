#!/usr/bin/env python3
"""O-LQ3 Stage A hard-context replay: exact ALL3 vs ALL3+LQ3."""
from __future__ import annotations
import argparse,json,math,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_lq3_priority_sell_order import lq3_action

class Candidate:
    def __init__(self,main,treatment):
        self.agent=load_public_agent(main);self.state=OptionHostState()
        self.treatment=bool(treatment);self.trace=[];self.fire_meta=[]
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",len(self.trace)))
        base=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        out=all3
        if self.treatment:
            out,meta=lq3_action(all3)
            if meta["fired"]:
                self.fire_meta.append({"step":step,**meta})
        self.trace.append((step,action_key(out)))
        return out

def finish(env,seat,cand):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {
      "reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps,
      "trace":cand.trace,"fire_meta":cand.fire_meta,"fire_count":len(cand.fire_meta),
      "first_fire":min((x["step"] for x in cand.fire_meta),default=None),
    }

def run(base_main,opp_main,seed,seat,treatment):
    cand=Candidate(base_main,treatment);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat,cand)

def parity(base,treat):
    ff=treat["first_fire"]
    if ff is None:
        return base["trace"]==treat["trace"] and base["margin"]==treat["margin"]
    bt=[x for x in base["trace"] if x[0]<ff]
    tt=[x for x in treat["trace"] if x[0]<ff]
    return bt==tt

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());contexts=list(cfg.get("selected_hard_contexts") or [])
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix="lq3-stage-a-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        opp_cache={}
        paths=[base_main]
        for idx,ctx in enumerate(contexts):
            opp_key=str(ctx["opponent"]);spec=next(x for x in V2_OPPONENTS if x["key"]==opp_key)
            if opp_key not in opp_cache:
                if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
                    opp_cache[opp_key]=base_main
                else:
                    pp,rec=acquire(spec,tmp/f"opp_{opp_key}");opp_cache[opp_key]=pp;provenance[opp_key]=rec;paths.append(pp)
            opp_main=opp_cache[opp_key]
            try:
                purge(paths);b=run(base_main,opp_main,int(ctx["seed"]),int(ctx["seat"]),False)
                if float(b["score"])!=float(ctx["score"]) or float(b["margin"])!=float(ctx["margin"]):
                    raise RuntimeError(f"ALL3 replay mismatch idx={idx}: {(b['score'],b['margin'])} != {(ctx['score'],ctx['margin'])}")
                purge(paths);t=run(base_main,opp_main,int(ctx["seed"]),int(ctx["seat"]),True)
                p=parity(b,t)
                if not p:raise RuntimeError(f"pre-fire parity failure idx={idx}")
                row={
                  "index":idx,"opponent":opp_key,"family":ctx.get("family"),"seed":ctx["seed"],"seat":ctx["seat"],
                  "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                  "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                  "fire_count":t["fire_count"],"first_fire":t["first_fire"],
                  "fire_steps":[x["step"] for x in t["fire_meta"]],
                  "parity_pre_fire":p,
                }
                rows.append(row)
                print("O_LQ3_STAGE_A_CONTEXT",json.dumps(row,sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"index":idx,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==4
    flips=sum(r["base_score"]<1 and r["treatment_score"]==1 for r in rows)
    mean_md=statistics.fmean(r["margin_delta"] for r in rows) if rows else 0.0
    if not mech:decision="O_LQ3_STAGE_A_FAIL"
    elif flips>=1 and mean_md>0:decision="O_LQ3_STAGE_A_PASS"
    elif mean_md>0:decision="O_LQ3_STAGE_A_DIRECTIONAL_ONLY"
    else:decision="O_LQ3_STAGE_A_FAIL"
    result={
      "schema":"kculture-o-lq3-stage-a-v1","mechanical_pass":mech,"decision":decision,
      "loss_to_win_flips":flips,"mean_margin_delta":mean_md,"rows":rows,"failures":failures,
      "provenance":provenance,"seconds":time.perf_counter()-started,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ3_STAGE_A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"loss_to_win_flips":flips,
      "mean_margin_delta":mean_md,"rows":rows,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
