#!/usr/bin/env python3
"""Dormant V18A: localize V14A MARKET_W2PLUS headroom in fixed W2 windows."""
from __future__ import annotations
import argparse,copy,json,math,os,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

MODES=("BASE","MARKET_W2A_ONLY","MARKET_W2B_ONLY","MARKET_W2C_ONLY","MARKET_W2AB","MARKET_W2BC","MARKET_W2ABC")
WINDOWS={
 "MARKET_W2A_ONLY":((336,392),),
 "MARKET_W2B_ONLY":((392,448),),
 "MARKET_W2C_ONLY":((448,504),),
 "MARKET_W2AB":((336,392),(392,448)),
 "MARKET_W2BC":((392,448),(448,504)),
 "MARKET_W2ABC":((336,392),(392,448),(448,504)),
}

def acquire_exact(ref,expected,tmp,attempts=10):
    last=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,tmp/f"try{i}")
            h=sha256_bytes(main.read_bytes())
            if h!=expected:raise RuntimeError(f"source SHA drift {h} != {expected}")
            return main,receipt
        except Exception as exc:
            last=exc
            if i+1<attempts:time.sleep(min(24.0,2.0*(i+1)))
    raise last

def active(mode,turn):
    if mode=="BASE":return False
    return any(a<=int(turn)<b for a,b in WINDOWS[mode])

class Candidate:
    def __init__(self,base_main,teacher_main,mode):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.shadow=load_public_agent(teacher_main)
        self.host=OptionHostState();self.turn=0;self.mode=mode
        self.market_sub_turns=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        shadow=canonical_action(call_agent(self.shadow,obs,config))
        if not active(self.mode,t):return all3
        out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow.get("market") or [])
        out=canonical_action(out)
        if out["farmer"]!=all3["farmer"] or out["hands"]!=all3["hands"]:
            raise RuntimeError("V18A market mode changed physical action")
        if out["market"]!=all3["market"]:self.market_sub_turns.append(t)
        return out

def run(base_main,teacher_main,ctx,mode):
    purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
    cand=Candidate(base_main,teacher_main,mode)
    purge_package_modules(teacher_main.parent);opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(ctx["seat"])==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"rewards":rw,"market_sub_turns":cand.market_sub_turns}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True);ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.hard_config).read_text());all_ctx=list(cfg.get("hard_contexts") or [])
    selected=[(i,c) for i,c in enumerate(all_ctx) if i%args.num_shards==args.shard_index]
    rows=[];failures=[];provenance={}
    with tempfile.TemporaryDirectory(prefix=f"v18a-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            uniq={}
            for _i,c in selected:uniq.setdefault(str(c["main_sha256"]),str(c["ref"]))
            for i,(sha,ref) in enumerate(uniq.items()):
                try:
                    main,rec=acquire_exact(ref,sha,root/f"teacher_{i}")
                    teachers[sha]=main;provenance[sha]={"ref":ref,"sha":sha,"receipt":rec}
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":ref,"sha":sha,"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
        if base_main is not None:
            for idx,c in selected:
                teacher=teachers.get(str(c["main_sha256"]))
                if teacher is None:continue
                base=None
                for mode in MODES:
                    try:
                        rr=run(base_main,teacher,c,mode)
                        if mode=="BASE":
                            if float(rr["score"])!=float(c["base_score"]) or float(rr["margin"])!=float(c["base_margin"]):
                                raise RuntimeError(f"BASE replay mismatch {(rr['score'],rr['margin'])} != {(c['base_score'],c['base_margin'])}")
                            base=rr
                        if base is None:raise RuntimeError("BASE must run first")
                        row={
                          "context_id":c["context_id"],"rank":c.get("rank"),"ref":c["ref"],"main_sha256":c["main_sha256"],
                          "seed":c["seed"],"seat":c["seat"],"mode":mode,
                          "base_score":base["score"],"treatment_score":rr["score"],"score_delta":float(rr["score"])-float(base["score"]),
                          "base_margin":base["margin"],"treatment_margin":rr["margin"],"margin_delta":float(rr["margin"])-float(base["margin"]),
                          "market_sub_turns":rr["market_sub_turns"],
                        }
                        rows.append(row)
                    except Exception as exc:
                        failures.append({"phase":"episode","context_id":c["context_id"],"mode":mode,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge_package_modules(base_main.parent);purge_package_modules(teacher.parent)
    mech=(not failures and len(rows)==len(selected)*len(MODES))
    result={"schema":"kculture-all3-v18a-w2-temporal-shard-v1","mechanical_pass":mech,
      "shard_index":args.shard_index,"num_shards":args.num_shards,"rows":rows,"failures":failures,"provenance":provenance,
      "automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V18A_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"rows":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
