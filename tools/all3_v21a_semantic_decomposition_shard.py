#!/usr/bin/env python3
"""V21A semantic decomposition shard for frozen V19A P2 consensus schedule."""
from __future__ import annotations
import argparse,json,math,os,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_tm1_p2_consensus_schedule import schedule_action
from tools.all3_v19c_consensus_fresh_validation import load_schedule

CATEGORIES=("EMPTY","SELL_PRESENT","BUY_ONLY","HIRE_PRESENT")
MODE_CATS={
    "BASE":set(),
    "FULL":set(CATEGORIES),
    "EMPTY_ONLY":{"EMPTY"},
    "SELL_ONLY":{"SELL_PRESENT"},
    "BUY_ONLY":{"BUY_ONLY"},
    "HIRE_ONLY":{"HIRE_PRESENT"},
    "FULL_MINUS_EMPTY":set(CATEGORIES)-{"EMPTY"},
    "FULL_MINUS_SELL":set(CATEGORIES)-{"SELL_PRESENT"},
    "FULL_MINUS_BUY":set(CATEGORIES)-{"BUY_ONLY"},
    "FULL_MINUS_HIRE":set(CATEGORIES)-{"HIRE_PRESENT"},
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

def semantic_category(entry):
    market=(entry.get("market") if isinstance(entry,dict) else entry) or []
    nonempty=[list(o) for o in market if list(o or [])]
    if not nonempty:return "EMPTY"
    sides={str(o[0]) for o in nonempty if o}
    if "HIRE" in sides:return "HIRE_PRESENT"
    if "SELL" in sides:return "SELL_PRESENT"
    return "BUY_ONLY"

def build_category_map(schedule):
    cats={str(t):semantic_category(e) for t,e in schedule.items()}
    counts={c:sum(v==c for v in cats.values()) for c in CATEGORIES}
    return cats,counts

class Candidate:
    def __init__(self,base_main,mode,schedule,cats):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main);self.host=OptionHostState()
        self.mode=str(mode);self.schedule=schedule;self.cats=cats
        self.turn=0;self.trace=[];self.fire_meta=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        out=all3
        entry=self.schedule.get(str(t))
        if entry is not None and self.cats[str(t)] in MODE_CATS[self.mode]:
            out,meta=schedule_action(obs,all3,t,self.schedule)
            if meta.get("fired"):
                mm=dict(meta);mm["category"]=self.cats[str(t)];self.fire_meta.append(mm)
        self.trace.append((t,action_key(out)))
        return out

def run_episode(base_main,opp_main,seed,seat,mode,schedule,cats):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,mode,schedule,cats)
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"trace":cand.trace,
            "fire_count":len(cand.fire_meta),"fire_turns":[int(x["turn"]) for x in cand.fire_meta],
            "fire_categories":[str(x["category"]) for x in cand.fire_meta]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True);ap.add_argument("--schedule",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=10)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());all_sources=list(cfg["sources"])
    seeds=[int(x) for x in cfg["discovery_seeds"]];seats=[int(x) for x in cfg["seats"]];modes=list(cfg["modes"])
    if len(all_sources)!=10 or seeds!=[78711,78712,78713,78714,78715,78716] or seats!=[0,1]:
        raise SystemExit("frozen V21A population mismatch")
    if modes!=list(MODE_CATS):raise SystemExit(f"frozen mode mismatch {modes} != {list(MODE_CATS)}")
    selected=[s for i,s in enumerate(all_sources) if i%args.num_shards==args.shard_index]
    schedule,schedule_sha=load_schedule(args.schedule)
    if schedule_sha!=str(cfg["schedule_sha256"]):raise SystemExit("schedule SHA mismatch")
    cats,counts=build_category_map(schedule)
    if counts!={k:int(v) for k,v in cfg["expected_category_counts"].items()}:
        raise SystemExit(f"semantic category count mismatch {counts}")

    rows=[];failures=[];prov={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v21a-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            prov["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            for i,s in enumerate(selected):
                try:
                    main,rec=acquire_exact(str(s["ref"]),str(s["main_sha256"]),root/f"teacher_{i}")
                    teachers[str(s["main_sha256"])]=main;prov[str(s["main_sha256"])]={"ref":s["ref"],"sha":s["main_sha256"],"receipt":rec}
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":s["ref"],"sha":s["main_sha256"],"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

        if base_main is not None:
            for s in selected:
                opp=teachers.get(str(s["main_sha256"]))
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        key={"rank":s["rank"],"ref":s["ref"],"main_sha256":s["main_sha256"],"seed":seed,"seat":seat}
                        try:
                            results={}
                            for mode in modes:
                                results[mode]=run_episode(base_main,opp,seed,seat,mode,schedule,cats)
                            base_trace=results["BASE"]["trace"]
                            for mode in modes:
                                if mode=="BASE":continue
                                if [x for x in base_trace if int(x[0])<=463] != [x for x in results[mode]["trace"] if int(x[0])<=463]:
                                    raise RuntimeError(f"pre-scope trace mismatch mode={mode}")
                            rows.append({**key,"results":{m:{
                                "score":results[m]["score"],"margin":results[m]["margin"],
                                "fire_count":results[m]["fire_count"],"fire_turns":results[m]["fire_turns"],
                                "fire_categories":results[m]["fire_categories"]} for m in modes}})
                        except Exception as exc:
                            failures.append({**key,"phase":"context","error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    expected=len(selected)*len(seeds)*len(seats)
    mech=(not failures and len(rows)==expected and all(set(r["results"])==set(modes) for r in rows))
    out={"schema":"kculture-all3-v21a-semantic-decomposition-shard-v1","engine":EXPECTED_ENGINE,
         "schedule_sha256":schedule_sha,"category_counts":counts,"modes":modes,
         "shard_index":args.shard_index,"num_shards":args.num_shards,"selected_sources":[s["main_sha256"] for s in selected],
         "expected_contexts":expected,"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,
         "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V21A_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"contexts":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
