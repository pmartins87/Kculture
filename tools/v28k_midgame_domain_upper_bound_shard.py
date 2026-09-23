#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,os,statistics,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

MODES=("BASE","MARKET_WINDOW","PHYSICAL_WINDOW","FULL_WINDOW")
START=384
END=479

class Hybrid:
    def __init__(self,base_main,teacher_main,mode):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.teacher=None if mode=="BASE" else load_public_agent(teacher_main)
        self.host=OptionHostState();self.mode=mode
        self.stats={"turns":0,"teacher_evaluations":0,"window_turns":0,"changed_window_turns":0,
                    "market_diff_window_turns":0,"physical_diff_window_turns":0}
    def __call__(self,obs,config=None):
        self.stats["turns"]+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        if self.mode=="BASE":
            return all3
        shadow=canonical_action(call_agent(self.teacher,obs,config))
        self.stats["teacher_evaluations"]+=1
        step=int((obs or {}).get("step",-1))
        if not (START<=step<=END):
            return all3
        self.stats["window_turns"]+=1
        md=all3["market"]!=shadow["market"]
        pd=(all3["farmer"]!=shadow["farmer"] or all3["hands"]!=shadow["hands"])
        self.stats["market_diff_window_turns"]+=int(md)
        self.stats["physical_diff_window_turns"]+=int(pd)
        if self.mode=="MARKET_WINDOW":
            out=copy.deepcopy(all3);out["market"]=copy.deepcopy(shadow["market"])
        elif self.mode=="PHYSICAL_WINDOW":
            out=copy.deepcopy(all3);out["farmer"]=copy.deepcopy(shadow["farmer"]);out["hands"]=copy.deepcopy(shadow["hands"])
        elif self.mode=="FULL_WINDOW":
            out=copy.deepcopy(shadow)
        else:
            raise RuntimeError(self.mode)
        self.stats["changed_window_turns"]+=int(out!=all3)
        return out

def run_one(base_main,teacher_main,seed,seat,mode):
    purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
    cand=Hybrid(base_main,teacher_main,mode)
    purge_package_modules(teacher_main.parent)
    opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([cand,opp] if int(seat)==0 else [opp,cand])
    rep=env.toJSON()
    statuses=[str(x) for x in rep.get("statuses",[])]
    rewards=[float(x) for x in rep.get("rewards",[])]
    steps=len(rep.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode {mode} {statuses} {rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps,"stats":cand.stats}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--v28f",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    root=Path(a.snapshot_dir)
    man=json.loads((root/"MANIFEST.json").read_text())
    f=json.loads(Path(a.v28f).read_text())
    if not f.get("mechanical_pass") or f.get("decision")!="V28F_NO_MATERIAL_HEDGE_REPLACEMENT":
        raise SystemExit("V28F binding mismatch")

    base=root/man["base"]["path"]
    if sha256_bytes(base.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("base SHA mismatch")
    paths={}
    meta={}
    for src in man["sources"]:
        p=root/src["path"];sha=str(src["sha"])
        if sha256_bytes(p.read_bytes())!=sha:
            raise SystemExit(f"source SHA mismatch {sha}")
        paths[sha]=p;meta[sha]=src

    all3=[r for r in f["rows"] if r["candidate"]=="ALL3"]
    hard=[r for r in all3 if float(r["score"])==0.0]
    if len(hard)!=66:
        raise SystemExit(f"expected 66 residual losses got {len(hard)}")
    hard=sorted(hard,key=lambda r:(int(r["source_rank"]),str(r["main_sha256"]),int(r["seed"]),int(r["seat"])))
    selected=[r for i,r in enumerate(hard) if i%a.num_shards==a.shard_index]

    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    rows=[];fail=[]
    for ctx in selected:
        sha=str(ctx["main_sha256"])
        base_result=None
        for mode in MODES:
            try:
                rr=run_one(base,paths[sha],int(ctx["seed"]),int(ctx["seat"]),mode)
                if mode=="BASE":
                    if float(rr["score"])!=float(ctx["score"]) or float(rr["margin"])!=float(ctx["margin"]):
                        raise RuntimeError(f"BASE replay mismatch observed={(rr['score'],rr['margin'])} expected={(ctx['score'],ctx['margin'])}")
                    base_result=rr
                if base_result is None:
                    raise RuntimeError("BASE must run first")
                rows.append({
                  "main_sha256":sha,"representative_ref":meta[sha]["representative_ref"],
                  "source_rank":int(meta[sha]["representative_rank"]),
                  "seed":int(ctx["seed"]),"seat":int(ctx["seat"]),"mode":mode,
                  "base_score":float(base_result["score"]),"treatment_score":float(rr["score"]),
                  "score_delta":float(rr["score"])-float(base_result["score"]),
                  "base_margin":float(base_result["margin"]),"treatment_margin":float(rr["margin"]),
                  "margin_delta":float(rr["margin"])-float(base_result["margin"]),
                  "stats":rr["stats"],
                })
            except Exception as e:
                fail.append({"sha":sha,"seed":int(ctx["seed"]),"seat":int(ctx["seat"]),"mode":mode,
                             "error":f"{type(e).__name__}: {e}"})
            finally:
                purge_package_modules(base.parent);purge_package_modules(paths[sha].parent)

    expected=len(selected)*len(MODES)
    mech=not fail and len(rows)==expected
    out={"schema":"kculture-v28k-midgame-domain-upper-bound-shard-v1",
         "mechanical_pass":mech,"shard_index":a.shard_index,"num_shards":a.num_shards,
         "window":[START,END],"contexts_assigned":len(selected),"expected_rows":expected,
         "rows":rows,"failures":fail,"immutable_snapshot_used":True,
         "live_kaggle_reacquisition_used":False,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28K_SHARD_RESULT",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"contexts":len(selected),"rows":len(rows),"failures":len(fail)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
