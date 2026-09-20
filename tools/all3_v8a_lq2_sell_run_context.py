#!/usr/bin/env python3
"""V8A census of residual multi-product SELL runs after exact ALL3/LQ2."""
from __future__ import annotations
import argparse,copy,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_lq2_canonical_sell_queue import lq2_action,is_sell
from tools.cq2_projected_queue_dev_matrix import projected_shed_after_physical

def sell_runs(market):
    out=[];i=0
    while i<len(market):
        if not is_sell(market[i]):
            i+=1;continue
        j=i;orders=[]
        while j<len(market) and is_sell(market[j]):
            orders.append(copy.deepcopy(market[j]));j+=1
        out.append({"start":i,"end":j-1,"orders":orders})
        i=j
    return out

def eligible_run(run):
    orders=run["orders"]
    products=[str(o[1]) for o in orders if len(o)>=3]
    return len(orders)>=2 and len(set(products))>=2

class CensusCandidate:
    def __init__(self,main,index,ctx):
        self.agent=load_public_agent(main);self.state=OptionHostState()
        self.index=index;self.ctx=ctx;self.rows=[];self.changed=0
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        pre=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=False)
        post=lq2_action(obs,config,pre)
        step=int(plain(obs).get("step",len(self.rows)))
        changed=(pre["market"]!=post["market"])
        if changed:self.changed+=1
        shed=projected_shed_after_physical(obs,config,pre)
        runs=sell_runs(post["market"])
        eligible=[]
        for r in runs:
            if not eligible_run(r):continue
            orders=r["orders"];products=[str(o[1]) for o in orders]
            qty=[int(o[2]) for o in orders]
            eligible.append({
              "start":r["start"],"end":r["end"],"orders":orders,
              "distinct_products":len(set(products)),
              "nonempty_sell_orders":len(orders),
              "total_sell_qty":sum(max(0,x) for x in qty),
              "products":products,"quantities":qty,
            })
        if changed or eligible:
            self.rows.append({
              "index":self.index,"opponent":self.ctx["opponent"],"family":self.ctx.get("family"),
              "seed":self.ctx["seed"],"seat":self.ctx["seat"],"step":step,
              "lq2_changed":changed,
              "pre_lq2_market":copy.deepcopy(pre["market"]),
              "post_lq2_market":copy.deepcopy(post["market"]),
              "projected_shed":copy.deepcopy(shed),
              "eligible_runs":eligible,
            })
        return post

def finish(env,seat):
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-opp
    return {"reward":mine,"opponent_reward":opp,"margin":m,"score":score(m),"steps":steps}

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
    ctx=contexts[args.index];opp_key=str(ctx["opponent"]);seed=int(ctx["seed"]);seat=int(ctx["seat"])
    spec=next(x for x in V2_OPPONENTS if x["key"]==opp_key)
    failures=[];provenance={};started=time.perf_counter();rows=[];result=None
    try:
      with tempfile.TemporaryDirectory(prefix=f"v8a-{args.index}-{opp_key}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":opp_key,"family":spec.get("family"),"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp");provenance["opponent"]={**rec,"family":spec.get("family")}
        paths=[base_main,opp_main];purge(paths)
        cand=CensusCandidate(base_main,args.index,ctx);opp=load_public_agent(opp_main)
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
        if seat==0:env.run([cand,opp])
        else:env.run([opp,cand])
        fin=finish(env,seat)
        if float(fin["score"])!=float(ctx["score"]) or float(fin["margin"])!=float(ctx["margin"]):
            raise RuntimeError(f"ALL3 replay mismatch {(fin['score'],fin['margin'])} != {(ctx['score'],ctx['margin'])}")
        rows=cand.rows
        eligible_states=[]
        for row in rows:
            for run in row["eligible_runs"]:
                eligible_states.append({
                  "index":args.index,"opponent":opp_key,"family":ctx.get("family"),"seed":seed,"seat":seat,
                  "step":row["step"],"pre_lq2_market":row["pre_lq2_market"],
                  "post_lq2_market":row["post_lq2_market"],"projected_shed":row["projected_shed"],
                  **run,
                })
        eligible_states.sort(key=lambda x:(-x["distinct_products"],-x["nonempty_sell_orders"],-x["total_sell_qty"],x["step"]))
        result={
          "schema":"kculture-v8a-lq2-sell-run-context-v1","mechanical_pass":True,
          "index":args.index,"context":ctx,"final":fin,
          "lq2_changed_turns":cand.changed,
          "eligible_state_count":len(eligible_states),
          "max_distinct_products":max((x["distinct_products"] for x in eligible_states),default=0),
          "eligible_states":eligible_states,"trace_rows":rows,
          "failures":[],"provenance":provenance,"seconds":time.perf_counter()-started,
        }
    except Exception as exc:
      failures.append({"error":f"{type(exc).__name__}: {exc}"})
      result={
        "schema":"kculture-v8a-lq2-sell-run-context-v1","mechanical_pass":False,
        "index":args.index,"context":ctx,"eligible_states":[],"trace_rows":rows,
        "failures":failures,"seconds":time.perf_counter()-started,
      }
    finally:
      try:purge(paths)
      except Exception:pass

    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V8A_CONTEXT_RESULT",json.dumps({
      "index":args.index,"opponent":opp_key,"seed":seed,"seat":seat,
      "mechanical_pass":result["mechanical_pass"],
      "lq2_changed_turns":result.get("lq2_changed_turns"),
      "eligible_state_count":len(result.get("eligible_states",[])),
      "max_distinct_products":result.get("max_distinct_products"),
      "top_states":[{k:x[k] for k in ("step","start","end","distinct_products","nonempty_sell_orders","total_sell_qty","products","quantities")} for x in result.get("eligible_states",[])[:8]],
      "failures":len(result.get("failures",[])),
    },sort_keys=True),flush=True)
    if not result["mechanical_pass"]:raise SystemExit(2)

if __name__=="__main__":main()
