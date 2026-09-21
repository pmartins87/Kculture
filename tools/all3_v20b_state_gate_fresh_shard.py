#!/usr/bin/env python3
"""V20B untouched fresh validation shard for O-TM2 state-gated P2 consensus."""
from __future__ import annotations
import argparse,hashlib,json,math,os,sys,tempfile,time
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

DROP_FEATURES={"turn","p2_progress"}
GATE_TURN=464

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

def load_gate(path):
    raw=Path(path).read_bytes();d=json.loads(raw)
    if d.get("decision")!="V20A_STATE_GATE_READY":raise RuntimeError("V20A gate not READY")
    if not d.get("mechanical_pass"):raise RuntimeError("V20A mechanical gate failed")
    if not d.get("tree") or not d.get("feature_names"):raise RuntimeError("V20A gate missing model")
    return d,hashlib.sha256(raw).hexdigest()

def transform(prev,cur):
    p={k:float(v) for k,v in prev.items() if k not in DROP_FEATURES}
    c={k:float(v) for k,v in cur.items() if k not in DROP_FEATURES}
    if set(p)!=set(c):raise RuntimeError("463/464 feature schema mismatch")
    out={}
    for k in sorted(c):
        dv=c[k]-p[k]
        out[f"cur__{k}"]=c[k];out[f"prev__{k}"]=p[k]
        out[f"delta__{k}"]=dv;out[f"absdelta__{k}"]=abs(dv)
    return out

def json_prob(tree,feat):
    n=tree
    while not n.get("leaf"):
        name=str(n["feature"])
        if name not in feat:raise RuntimeError(f"gate feature missing {name}")
        n=n["left"] if float(feat[name])<=float(n["threshold"]) else n["right"]
    return float(n["p_benefit"])

class Candidate:
    def __init__(self,base_main,treatment,schedule,seat,gate):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main);self.host=OptionHostState()
        self.treatment=bool(treatment);self.schedule=schedule;self.seat=int(seat);self.gate=gate
        self.turn=0;self.trace=[];self.fire_meta=[];self.snapshots={}
        self.gate_on=False;self.gate_prob=None;self.gate_decisions=0
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        if t in (463,464):self.snapshots[str(t)]=numeric_features(obs,self.seat,t,all3)
        out=all3;meta={"fired":False,"turn":t,"reason":"gate_off"}
        if self.treatment and t==GATE_TURN:
            if set(self.snapshots)!={"463","464"}:raise RuntimeError("missing gate snapshots")
            feat=transform(self.snapshots["463"],self.snapshots["464"])
            names=list(self.gate["feature_names"])
            if sorted(feat)!=sorted(names):raise RuntimeError("gate feature schema drift")
            prob=json_prob(self.gate["tree"],feat)
            self.gate_prob=float(prob);self.gate_on=bool(prob>=float(self.gate["threshold"]));self.gate_decisions+=1
        if self.treatment and self.gate_on and t>=GATE_TURN:
            out,meta=schedule_action(obs,all3,t,self.schedule)
            if meta.get("fired"):self.fire_meta.append(meta)
        self.trace.append((t,action_key(out)))
        return out

def run_episode(base_main,opp_main,seed,seat,treatment,schedule,gate):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,treatment,schedule,seat,gate)
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    if set(cand.snapshots)!={"463","464"}:raise RuntimeError("missing gate snapshots")
    if treatment and cand.gate_decisions!=1:raise RuntimeError(f"gate decision count {cand.gate_decisions}")
    mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"rewards":rw,"trace":cand.trace,
            "fire_count":len(cand.fire_meta),"fire_meta":cand.fire_meta,
            "gate_on":bool(cand.gate_on),"gate_prob":cand.gate_prob,"gate_decisions":cand.gate_decisions}

def prescope_parity(base,treat):
    return [x for x in base["trace"] if int(x[0])<=463]==[x for x in treat["trace"] if int(x[0])<=463]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True);ap.add_argument("--schedule",required=True);ap.add_argument("--gate",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=5);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());all_sources=list(cfg["sources"]);seeds=[int(x) for x in cfg["validation_seeds"]];seats=[int(x) for x in cfg["seats"]]
    if len(all_sources)!=10 or seeds!=[78801,78802,78803,78804] or seats!=[0,1]:raise SystemExit("frozen V20B population mismatch")
    selected=[s for i,s in enumerate(all_sources) if i%args.num_shards==args.shard_index]
    schedule,schedule_sha=load_schedule(args.schedule)
    if schedule_sha!=str(cfg["schedule_sha256"]):raise SystemExit("schedule SHA mismatch")
    gate,gate_sha=load_gate(args.gate)

    rows=[];failures=[];prov={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v20b-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base");prov["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            for i,s in enumerate(selected):
                try:
                    main,rec=acquire_exact(str(s["ref"]),str(s["main_sha256"]),root/f"teacher_{i}")
                    teachers[str(s["main_sha256"])]=main;prov[str(s["main_sha256"])]={"ref":s["ref"],"sha":s["main_sha256"],"receipt":rec};time.sleep(1.0)
                except Exception as exc:failures.append({"phase":"teacher_acquire","ref":s["ref"],"sha":s["main_sha256"],"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
        if base_main is not None:
            for s in selected:
                opp=teachers.get(str(s["main_sha256"]))
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        key={"rank":s["rank"],"ref":s["ref"],"main_sha256":s["main_sha256"],"seed":seed,"seat":seat}
                        try:
                            b=run_episode(base_main,opp,seed,seat,False,schedule,gate);t=run_episode(base_main,opp,seed,seat,True,schedule,gate)
                            if not prescope_parity(b,t):raise RuntimeError("pre-turn-464 action parity failure")
                            row={**key,"base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                                 "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                                 "gate_on":t["gate_on"],"gate_prob":t["gate_prob"],"gate_decisions":t["gate_decisions"],
                                 "fire_count":t["fire_count"],"fire_turns":[int(x["turn"]) for x in t["fire_meta"]]}
                            rows.append(row)
                        except Exception as exc:failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                        finally:purge_package_modules(base_main.parent);purge_package_modules(opp.parent)
    expected=len(selected)*len(seeds)*len(seats);mech=(not failures and len(rows)==expected and all(int(r["gate_decisions"])==1 for r in rows))
    out={"schema":"kculture-all3-v20b-state-gate-fresh-shard-v1","engine":EXPECTED_ENGINE,"schedule_sha256":schedule_sha,"gate_sha256":gate_sha,
         "gate_threshold":float(gate["threshold"]),"shard_index":args.shard_index,"num_shards":args.num_shards,"selected_sources":[s["main_sha256"] for s in selected],
         "expected_pairs":expected,"mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,"seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V20B_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"pairs":len(rows),"gate_on":sum(bool(r["gate_on"]) for r in rows),"fires":sum(int(r["fire_count"])>0 for r in rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
