#!/usr/bin/env python3
"""V19B paired causal discovery for frozen O-TM1 consensus schedule."""
from __future__ import annotations
import argparse,hashlib,json,math,os,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_tm1_p2_consensus_schedule import schedule_action

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
    def __init__(self,base_main,treatment,schedule):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main)
        self.host=OptionHostState()
        self.treatment=bool(treatment)
        self.schedule=schedule
        self.turn=0;self.trace=[];self.fire_meta=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        self.trace.append((t,action_key(all3)))
        if not self.treatment:return all3
        out,meta=schedule_action(obs,all3,t,self.schedule)
        if meta.get("fired"):self.fire_meta.append(meta)
        return out

def run_episode(base_main,opp_main,ctx,treatment,schedule):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,treatment,schedule)
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(ctx["seat"])==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"result":"W" if m>0 else ("L" if m<0 else "T"),
      "rewards":rw,"trace":cand.trace,"fire_meta":cand.fire_meta,"fire_count":len(cand.fire_meta)}

def prefire_parity(base,treat):
    fires=treat.get("fire_meta") or []
    if not fires:return base["trace"]==treat["trace"] and base["rewards"]==treat["rewards"]
    first=min(int(x["turn"]) for x in fires)
    return [x for x in base["trace"] if int(x[0])<=first]==[x for x in treat["trace"] if int(x[0])<=first]

def load_schedule(path):
    raw=Path(path).read_bytes();d=json.loads(raw)
    if d.get("decision")!="V19A_CONSENSUS_SCHEDULE_READY":raise RuntimeError("schedule artifact not READY")
    if int(d.get("scheduled_turns",0))<20:raise RuntimeError("schedule too small")
    return d["schedule"],hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hard-config",required=True);ap.add_argument("--schedule",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    hard=json.loads(Path(args.hard_config).read_text());contexts=list(hard.get("hard_contexts") or [])
    schedule,schedule_sha=load_schedule(args.schedule)
    if len(contexts)!=24:raise SystemExit("expected 24 hard contexts")

    rows=[];failures=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v19b-tm1-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={};source_ref={}
        if base_main is not None:
            for c in contexts:source_ref.setdefault(str(c["main_sha256"]),str(c["ref"]))
            for i,(sha,ref) in enumerate(source_ref.items()):
                try:
                    main,rec=acquire_exact(ref,sha,root/f"teacher_{i}")
                    teachers[sha]=main;provenance[sha]={"ref":ref,"sha":sha,"receipt":rec}
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":ref,"sha":sha,"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

        if base_main is not None:
            for c in contexts:
                opp=teachers.get(str(c["main_sha256"]))
                if opp is None:continue
                try:
                    b=run_episode(base_main,opp,c,False,schedule)
                    if float(b["score"])!=float(c["base_score"]) or float(b["margin"])!=float(c["base_margin"]):
                        raise RuntimeError(f"BASE replay mismatch {(b['score'],b['margin'])} != {(c['base_score'],c['base_margin'])}")
                    t=run_episode(base_main,opp,c,True,schedule)
                    if not prefire_parity(b,t):raise RuntimeError("pre-fire parity failure")
                    if any(int(x["turn"])<464 or int(x["turn"])>591 for x in t["fire_meta"]):raise RuntimeError("O-TM1 fired outside P2")
                    row={
                      "context_id":c["context_id"],"rank":c.get("rank"),"ref":c["ref"],"main_sha256":c["main_sha256"],
                      "seed":c["seed"],"seat":c["seat"],
                      "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                      "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                      "fire_count":t["fire_count"],"fire_turns":[int(x["turn"]) for x in t["fire_meta"]],
                    }
                    rows.append(row);print("V19B_PAIR",json.dumps(row,sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"phase":"pair","context_id":c["context_id"],"error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    mech=(not failures and len(rows)==24)
    fire=[r for r in rows if int(r["fire_count"])>0]
    fire_sources={r["main_sha256"] for r in fire}
    pos=[r for r in rows if float(r["score_delta"])>0]
    neg=[r for r in rows if float(r["score_delta"])<0]
    pos_sources={r["main_sha256"] for r in pos}
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else 0.0
    mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    coverage=(mech and len(fire)>=8 and len(fire_sources)>=4)
    if not mech:decision="V19B_MECHANICS_INVALID"
    elif not coverage:decision="V19B_CONSENSUS_UNDERPOWERED"
    elif len(pos)>=4 and len(pos_sources)>=2 and len(neg)==0 and mean_score>0 and mean_margin>0:
        decision="V19B_CONSENSUS_WL_HEADROOM"
    elif len(neg)==0 and mean_margin>0:
        decision="V19B_CONSENSUS_MARGIN_ONLY_CLOSE"
    else:
        decision="V19B_CONSENSUS_NO_HEADROOM_CLOSE"

    result={
      "schema":"kculture-all3-v19b-consensus-causal-v1","engine":EXPECTED_ENGINE,
      "schedule_sha256":schedule_sha,"mechanical_pass":mech,"coverage_pass":coverage,"decision":decision,
      "contexts":len(rows),"fire_contexts":len(fire),"fire_sources":len(fire_sources),
      "positive_score_contexts":len(pos),"positive_score_sources":len(pos_sources),"negative_score_contexts":len(neg),
      "mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
      "rows":rows,"failures":failures,"provenance":provenance,
      "automatic_kaggle_submission":False,"runtime_identity_feature_allowed":False,
      "seconds":time.perf_counter()-started,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V19B_RESULT",json.dumps({
      "decision":decision,"schedule_sha256":schedule_sha,"mechanical_pass":mech,"coverage_pass":coverage,
      "fire_contexts":len(fire),"fire_sources":len(fire_sources),
      "positive_score_contexts":len(pos),"positive_score_sources":len(pos_sources),"negative_score_contexts":len(neg),
      "mean_score_delta":mean_score,"mean_margin_delta":mean_margin,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
