#!/usr/bin/env python3
"""V16C fresh paired validation for frozen O-LQ5F."""
from __future__ import annotations
import argparse,json,math,os,statistics,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,action_key,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.first_party_lq5f_w2_fertilizer_queue import LQ5FState,lq5f_action

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
    def __init__(self,base_main,treatment):
        purge_package_modules(base_main.parent)
        self.agent=load_public_agent(base_main)
        self.host=OptionHostState();self.lq5=LQ5FState()
        self.treatment=bool(treatment);self.turn=0;self.trace=[];self.fire_meta=[]
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        self.trace.append((t,action_key(all3)))
        if not self.treatment:return all3
        out,meta=lq5f_action(all3,t,self.lq5)
        if meta.get("fired"):self.fire_meta.append(meta)
        return out

def run_episode(base_main,opp_main,seed,seat,treatment):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=Candidate(base_main,treatment)
    purge_package_modules(opp_main.parent);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"result":"W" if m>0 else ("L" if m<0 else "T"),
      "rewards":rw,"trace":cand.trace,"fire_meta":cand.fire_meta,"fire_count":len(cand.fire_meta)}

def prefire_parity(base,treat):
    fires=treat.get("fire_meta") or []
    if not fires:return base["trace"]==treat["trace"] and base["rewards"]==treat["rewards"]
    first=min(int(x["turn"]) for x in fires)
    return [x for x in base["trace"] if x[0]<=first]==[x for x in treat["trace"] if x[0]<=first]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());sources=list(cfg.get("sources") or []);seeds=[int(x) for x in cfg.get("seeds") or []];seats=[int(x) for x in cfg.get("seats") or []]
    if len(sources)!=10 or seeds!=[78301,78302,78303,78304] or seats!=[0,1]:raise SystemExit("frozen V16C population mismatch")

    rows=[];failures=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v16c-lq5f-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            for i,s in enumerate(sources):
                try:
                    main,rec=acquire_exact(str(s["ref"]),str(s["main_sha256"]),root/f"teacher_{i}")
                    teachers[str(s["main_sha256"])]=main
                    provenance[str(s["main_sha256"])]={"ref":s["ref"],"sha":s["main_sha256"],"receipt":rec}
                    print("V16C_ACQUIRE",json.dumps({"rank":s["rank"],"ref":s["ref"],"sha":s["main_sha256"]},sort_keys=True),flush=True)
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","rank":s["rank"],"ref":s["ref"],"sha":s["main_sha256"],"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

        if base_main is not None:
            for s in sources:
                opp=teachers.get(str(s["main_sha256"]))
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        key={"rank":s["rank"],"ref":s["ref"],"main_sha256":s["main_sha256"],"seed":seed,"seat":seat}
                        try:
                            b=run_episode(base_main,opp,seed,seat,False)
                            t=run_episode(base_main,opp,seed,seat,True)
                            if not prefire_parity(b,t):raise RuntimeError("pre-fire parity failure")
                            if int(t["fire_count"])>1:raise RuntimeError("O-LQ5F fired more than once")
                            if any(int(x["turn"])<336 or int(x["turn"])>=504 for x in t["fire_meta"]):raise RuntimeError("O-LQ5F fired outside W2")
                            row={**key,
                              "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                              "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                              "fire_count":t["fire_count"],"fire_meta":t["fire_meta"]}
                            rows.append(row);print("V16C_PAIR",json.dumps(row,sort_keys=True),flush=True)
                        except Exception as exc:
                            failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    mech=(not failures and len(rows)==80)
    fire=[r for r in rows if int(r["fire_count"])>0]
    pos=[r for r in rows if float(r["score_delta"])>0]
    neg=[r for r in rows if float(r["score_delta"])<0]
    win_to_nonwin=[r for r in rows if float(r["base_score"])==1.0 and float(r["treatment_score"])<1.0]
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else 0.0
    mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    coverage=(mech and len(fire)>=8)
    pass_gate=(coverage and len(pos)>=2 and mean_score>0 and not neg and not win_to_nonwin and mean_margin>=0)
    if not mech:decision="V16C_MECHANICS_INVALID"
    elif not coverage:decision="V16C_LQ5F_UNDERPOWERED"
    elif pass_gate:decision="V16C_LQ5F_FRESH_PASS"
    else:decision="V16C_LQ5F_FRESH_FAIL_CLOSE"
    result={
      "schema":"kculture-all3-v16c-lq5f-fresh-validation-v1","engine":EXPECTED_ENGINE,
      "mechanical_pass":mech,"coverage_pass":coverage,"decision":decision,
      "pairs":len(rows),"fire_contexts":len(fire),"positive_score_contexts":len(pos),"negative_score_contexts":len(neg),
      "win_to_nonwin":len(win_to_nonwin),"mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
      "rows":rows,"failures":failures,"provenance":provenance,
      "automatic_kaggle_submission":False,"runtime_identity_feature_allowed":False,
      "seconds":time.perf_counter()-started}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V16C_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"coverage_pass":coverage,"pairs":len(rows),
      "fire_contexts":len(fire),"positive_score_contexts":len(pos),"negative_score_contexts":len(neg),
      "win_to_nonwin":len(win_to_nonwin),"mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
      "failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
