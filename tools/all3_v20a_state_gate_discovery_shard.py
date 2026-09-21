#!/usr/bin/env python3
"""V20A paired discovery shard for state-conditioned O-TM1 gate."""
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
from tools.all3_v18b_p2_dataset_shard import numeric_features
from tools.all3_v19c_consensus_fresh_validation import load_schedule

SNAP_TURNS=(463,464)

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

class Candidate:
    def __init__(self,base_main,treatment,schedule,seat):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main);self.host=OptionHostState()
        self.treatment=bool(treatment);self.schedule=schedule;self.seat=int(seat)
        self.turn=0;self.trace=[];self.fire_meta=[];self.snapshots={}
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        self.trace.append((t,action_key(all3)))
        if t in SNAP_TURNS:
            self.snapshots[str(t)]=numeric_features(obs,self.seat,t,all3)
        if not self.treatment:return all3
        out,meta=schedule_action(obs,all3,t,self.schedule)
        if meta.get("fired"):self.fire_meta.append(meta)
        return out

def run_episode(base_main,opp_main,seed,seat,treatment,schedule):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,treatment,schedule,seat)
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    if set(cand.snapshots)!={"463","464"}:raise RuntimeError(f"missing gate snapshots {cand.snapshots.keys()}")
    mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"rewards":rw,"trace":cand.trace,
            "fire_count":len(cand.fire_meta),"snapshots":cand.snapshots}

def prefire_parity(base,treat):
    # O-TM1 scope begins at 464; compare through turn 463.
    return [x for x in base["trace"] if int(x[0])<=463]==[x for x in treat["trace"] if int(x[0])<=463]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True);ap.add_argument("--schedule",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=5)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());all_sources=list(cfg["sources"])
    seeds=[int(x) for x in cfg["discovery_seeds"]];seats=[int(x) for x in cfg["seats"]]
    if seeds!=[78711,78712,78713,78714,78715,78716] or seats!=[0,1] or len(all_sources)!=10:
        raise SystemExit("frozen V20A population mismatch")
    selected=[s for i,s in enumerate(all_sources) if i%args.num_shards==args.shard_index]
    schedule,schedule_sha=load_schedule(args.schedule)
    if schedule_sha!=str(cfg["schedule_sha256"]):raise SystemExit("schedule SHA mismatch")

    rows=[];failures=[];prov={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v20a-s{args.shard_index}-") as td:
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
                            b=run_episode(base_main,opp,seed,seat,False,schedule)
                            t=run_episode(base_main,opp,seed,seat,True,schedule)
                            if not prefire_parity(b,t):raise RuntimeError("pre-scope trace parity failure")
                            if b["snapshots"]!=t["snapshots"]:raise RuntimeError("BASE/treatment gate snapshot mismatch")
                            row={**key,
                              "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                              "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                              "fire_count":t["fire_count"],"snapshots":b["snapshots"]}
                            rows.append(row)
                        except Exception as exc:
                            failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    expected=len(selected)*len(seeds)*len(seats)
    mech=(not failures and len(rows)==expected)
    result={"schema":"kculture-all3-v20a-state-gate-discovery-shard-v1","engine":EXPECTED_ENGINE,
      "schedule_sha256":schedule_sha,"shard_index":args.shard_index,"num_shards":args.num_shards,
      "selected_sources":[s["main_sha256"] for s in selected],"expected_pairs":expected,
      "mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,
      "automatic_kaggle_submission":False,"seconds":time.perf_counter()-started}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V20A_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"pairs":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
