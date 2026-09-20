#!/usr/bin/env python3
"""V13C exact ALL3 census against refreshed current public frontier reps."""
from __future__ import annotations
import argparse,json,math,os,sys,tempfile,time,collections
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    EXPECTED_ENGINE, acquire_public_main, load_public_agent, purge_package_modules, sha256_bytes
)
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.cr087_top_macro_profile import public_counts

CHECKPOINTS=(336,408,456,504,552,600,648,696)
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")

def acquire_retry(ref,tmp,expected,attempts=5):
    err=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,tmp/f"a{i}")
            h=sha256_bytes(main.read_bytes())
            if h!=expected:
                raise RuntimeError(f"source SHA drift {h} != {expected}")
            return main,receipt
        except Exception as exc:
            err=exc
            if i+1<attempts: time.sleep(1.5*(i+1))
    raise err

def snap(obs,seat):
    p=plain(obs);farms=p.get("farms") or []
    if len(farms)!=2:return {}
    own,opp=farms[seat],farms[1-seat]
    oc,pc=public_counts(own),public_counts(opp)
    q={"own_money":float(own.get("money",0) or 0),"opp_money":float(opp.get("money",0) or 0)}
    for x in CROPS:
        q[f"own_{x}"]=int(oc.get(f"crop_{x}",0));q[f"opp_{x}"]=int(pc.get(f"crop_{x}",0))
    return q

class All3:
    def __init__(self,base_main,seat):
        self.agent=load_public_agent(base_main);self.state=OptionHostState();self.turn=0;self.seat=seat;self.snaps={}
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        base=canonical_action(call_agent(self.agent,obs,config))
        out=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        if t in CHECKPOINTS:self.snaps[str(t)]=snap(obs,self.seat)
        return out

def run_one(base_main,opp_main,seed,seat):
    purge_package_modules(base_main.parent);purge_package_modules(opp_main.parent)
    cand=All3(base_main,seat)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON();st=[str(x) for x in p.get("statuses",[])];rw=[float(x) for x in p.get("rewards",[])];steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid episode {st} {rw} steps={steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);m=mine-other
    return {"score":score(m),"margin":m,"result":"W" if m>0 else ("L" if m<0 else "T"),"rewards":rw,"snapshots":cand.snaps}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());reps=cfg["representatives"];seeds=cfg["seeds"];seats=cfg["seats"]
    rows=[];failures=[];acq=[];started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v13c-") as td:
        tmp=Path(td);paths={}
        for i,r in enumerate(reps):
            try:
                main,receipt=acquire_retry(r["ref"],tmp/f"r{i:02d}",r["main_sha256"])
                paths[r["main_sha256"]]=main
                acq.append({"rank":r["rank"],"ref":r["ref"],"sha":r["main_sha256"],"status":"PASS","receipt":receipt})
            except Exception as exc:
                failures.append({"phase":"acquire","rank":r["rank"],"ref":r["ref"],"error":f"{type(exc).__name__}: {exc}"})
        base_main=paths.get(BASE["expected_main_sha256"])
        if base_main is None:
            try:
                base_main,receipt=acquire_retry(BASE["handle"],tmp/"base",BASE["expected_main_sha256"])
            except Exception as exc:
                failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
                base_main=None

        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

        if base_main is not None:
            for r in reps:
                opp=paths.get(r["main_sha256"])
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        try:
                            rr=run_one(base_main,opp,int(seed),int(seat))
                            row={**r,"seed":int(seed),"seat":int(seat),**rr};rows.append(row)
                            print("V13C_EPISODE",json.dumps({k:row[k] for k in ("rank","ref","main_sha256","seed","seat","result","score","margin")},sort_keys=True),flush=True)
                        except Exception as exc:
                            failures.append({"phase":"episode","rank":r["rank"],"ref":r["ref"],"sha":r["main_sha256"],"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})

    expected=len(reps)*len(seeds)*len(seats)
    mech=(not failures and len(rows)==expected)
    hard=[r for r in rows if float(r["score"])<1.0]
    hard_shas=sorted({r["main_sha256"] for r in hard})
    if not mech:decision="V13C_MECHANICS_INVALID"
    elif len(hard)>=4 and len(hard_shas)>=2:decision="V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY"
    elif hard:decision="V13C_CURRENT_FRONTIER_HARD_CONTEXTS_NARROW"
    else:decision="V13C_LOCAL_FRONTIER_TOO_EASY"
    by_source=[]
    for r in reps:
        rr=[x for x in rows if x["main_sha256"]==r["main_sha256"]]
        if not rr:continue
        by_source.append({"rank":r["rank"],"ref":r["ref"],"sha":r["main_sha256"],"games":len(rr),
          "wins":sum(x["result"]=="W" for x in rr),"losses":sum(x["result"]=="L" for x in rr),"ties":sum(x["result"]=="T" for x in rr),
          "score_rate":sum(float(x["score"]) for x in rr)/len(rr),
          "mean_margin":sum(float(x["margin"]) for x in rr)/len(rr)})
    result={"schema":"kculture-all3-v13c-current-frontier-hard-context-v1","engine":EXPECTED_ENGINE,"mechanical_pass":mech,
      "decision":decision,"expected_games":expected,"completed_games":len(rows),"hard_contexts":len(hard),"hard_source_shas":hard_shas,
      "by_source":by_source,"hard_rows":hard,"rows":rows,"acquisitions":acq,"failures":failures,
      "local_h2h_is_not_hosted_rating_estimator":True,"automatic_kaggle_submission":False,"seconds":time.perf_counter()-started}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V13C_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"completed_games":len(rows),"expected_games":expected,
      "hard_contexts":len(hard),"hard_sources":len(hard_shas),"hard_source_shas":hard_shas,"failures":len(failures),"by_source":by_source},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
