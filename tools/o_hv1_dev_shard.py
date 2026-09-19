#!/usr/bin/env python3
"""O-HV1 development shard over one public opponent family."""
from __future__ import annotations
import argparse,json,math,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_hv1_high_value_stock_flush import hv1_transform
from tools.option_value_dataset_ryzen_v2 import V2_OPPONENTS

EXPECTED_ENGINE="1.32.7"
BASE={
 "key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
 "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
SEEDS=[74801,74802,74803,74804]
CONFIGS={
 "D1":{"min_step":240,"min_price":175},
 "D2":{"min_step":240,"min_price":200},
 "D3":{"min_step":336,"min_price":175},
 "D4":{"min_step":336,"min_price":200},
}
VARIANTS=("BASE",*CONFIGS.keys())

def acquire(spec,tmp):
    last=None
    for attempt in range(1,4):
        try:
            main,receipt=acquire_public_main(spec["handle"],tmp/f"attempt-{attempt}")
            observed=sha256_bytes(main.read_bytes())
            if observed!=spec["expected_main_sha256"]:
                raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
            return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,"acquisition_attempt":attempt,**receipt}
        except Exception as exc:
            last=exc
            if attempt<3: time.sleep(2*attempt)
    raise RuntimeError(f"{spec['key']} acquisition failed: {type(last).__name__}: {last}")

class Candidate:
    def __init__(self,main,variant):
        self.agent=load_public_agent(main)
        self.variant=variant
        self.host_state=OptionHostState()
        self.trace=[]
        self.fire_meta=[]
    def __call__(self,obs,config=None):
        base=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,base,self.host_state)
        step=int(plain(obs).get("step",len(self.trace)))
        self.trace.append((step,action_key(all3)))
        if self.variant=="BASE":
            return all3
        cfg=CONFIGS[self.variant]
        out,meta=hv1_transform(obs,config,all3,**cfg)
        if meta["fired"]:
            self.fire_meta.append(meta)
        if out["farmer"]!=all3["farmer"] or out["hands"]!=all3["hands"]:
            raise RuntimeError("HV1 changed physical action")
        return out

def finish(env,seat):
    p=env.toJSON()
    st=[str(x) for x in p.get("statuses",[])]
    rw=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    mine,opp=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
    margin=mine-opp
    return {"rewards":rw,"margin":margin,"score":score(margin),"steps":steps}

def run(base_main,opp_main,seed,seat,variant):
    cand=Candidate(base_main,variant)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    out["trace"]=cand.trace
    out["fire_meta"]=cand.fire_meta
    out["fire_count"]=len(cand.fire_meta)
    return out

def parity(base,treat):
    fires=treat.get("fire_meta",[])
    if not fires:
        return {"ok":base["trace"]==treat["trace"] and base["rewards"]==treat["rewards"],"first_fire":None}
    first=min(int(x["step"]) for x in fires)
    bt=[x for x in base["trace"] if x[0]<=first]
    tt=[x for x in treat["trace"] if x[0]<=first]
    return {"ok":bt==tt,"first_fire":first}

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k);purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--opponent",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"hv1-dev-{args.opponent}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            provenance["opponent"]={**provenance["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,provenance["opponent"]=acquire(spec,tmp/"opp")
        paths=[base_main,opp_main]

        for seed in SEEDS:
          for seat in (0,1):
            try:
                res={}
                for variant in VARIANTS:
                    purge(paths)
                    res[variant]=run(base_main,opp_main,seed,seat,variant)
                pars={v:parity(res["BASE"],res[v]) for v in CONFIGS}
                if not all(x["ok"] for x in pars.values()):
                    raise RuntimeError(f"pre-HV parity failure {pars}")
                row={
                  "opponent":args.opponent,"family":spec["family"],"seed":seed,"seat":seat,
                  "base":{"score":res["BASE"]["score"],"margin":res["BASE"]["margin"],"rewards":res["BASE"]["rewards"]},
                  "variants":{},
                  "parity":pars,
                }
                for v,cfg in CONFIGS.items():
                    rr=res[v]
                    row["variants"][v]={
                      "config":cfg,
                      "score":rr["score"],"margin":rr["margin"],"rewards":rr["rewards"],
                      "score_delta":rr["score"]-res["BASE"]["score"],
                      "margin_delta":rr["margin"]-res["BASE"]["margin"],
                      "fire_count":rr["fire_count"],
                      "first_fire":min((x["step"] for x in rr["fire_meta"]),default=None),
                      "products":dict(__import__("collections").Counter(x["product"] for x in rr["fire_meta"])),
                      "gross_added":sum(int(x["gross_value"]) for x in rr["fire_meta"]),
                    }
                rows.append(row)
                print("O_HV1_DEV_CONTEXT",json.dumps({
                  "opponent":args.opponent,"seed":seed,"seat":seat,
                  "base_score":res["BASE"]["score"],
                  "score_deltas":{v:row["variants"][v]["score_delta"] for v in CONFIGS},
                  "margin_deltas":{v:row["variants"][v]["margin_delta"] for v in CONFIGS},
                  "fires":{v:row["variants"][v]["fire_count"] for v in CONFIGS},
                },sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==8
    result={
      "schema":"kculture-o-hv1-dev-shard-v1",
      "opponent":args.opponent,"family":spec["family"],
      "configs":CONFIGS,"seeds":SEEDS,
      "mechanical_pass":mech,"rows":rows,"failures":failures,
      "provenance":provenance,"seconds":time.perf_counter()-started,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_HV1_DEV_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
