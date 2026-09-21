#!/usr/bin/env python3
"""V26B persistent source-agnostic modal-teacher consensus benchmark shard."""
from __future__ import annotations
import argparse,json,math,os,sys
from collections import Counter
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import action_key,call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host

SEEDS=(79601,79602,79603,79604,79605,79606)
SEATS=(0,1)
BASE_MAIN=None

class All3:
    def __init__(self):
        purge_package_modules(BASE_MAIN.parent)
        self.base=load_public_agent(BASE_MAIN)
        self.host=OptionHostState()
    def __call__(self,obs,config=None):
        exact=canonical_action(call_agent(self.base,obs,config))
        return apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)

class ConsensusPolicy:
    def __init__(self,teacher_paths):
        self.teacher_paths=list(teacher_paths)
        self.teachers=[]
        for p in self.teacher_paths:
            purge_package_modules(p.parent)
            self.teachers.append(load_public_agent(p))
        self.turns=0
        self.modal_support_sum=0
        self.modal_support_min=None
        self.unanimous_turns=0
        self.tie_turns=0

    def __call__(self,obs,config=None):
        self.turns+=1
        emitted=[]
        by_key={}
        for fn in self.teachers:
            a=canonical_action(call_agent(fn,obs,config))
            k=json.dumps(a,sort_keys=True,separators=(",",":"))
            emitted.append(k)
            by_key[k]=a
        counts=Counter(emitted)
        max_n=max(counts.values())
        winners=sorted(k for k,n in counts.items() if n==max_n)
        chosen=winners[0]
        self.modal_support_sum+=max_n
        self.modal_support_min=max_n if self.modal_support_min is None else min(self.modal_support_min,max_n)
        if max_n==len(self.teachers):
            self.unanimous_turns+=1
        if len(winners)>1:
            self.tie_turns+=1
        return by_key[chosen]

    def stats(self):
        n=max(1,self.turns)
        return {
          "turns":self.turns,
          "teacher_count":len(self.teachers),
          "mean_modal_support":self.modal_support_sum/n,
          "min_modal_support":self.modal_support_min,
          "unanimous_turns":self.unanimous_turns,
          "tie_turns":self.tie_turns,
        }

def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(seat)==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps}

def run_control(opp_main,seed,seat):
    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
    cand=All3()
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    return finish(env,seat)

def run_consensus(teacher_paths,opp_main,seed,seat):
    for p in teacher_paths:
        purge_package_modules(p.parent)
    purge_package_modules(opp_main.parent)
    cand=ConsensusPolicy(teacher_paths)
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:env.run([cand,opp])
    else:env.run([opp,cand])
    out=finish(env,seat)
    out["consensus_stats"]=cand.stats()
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    global BASE_MAIN
    root=Path(args.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    BASE_MAIN=root/manifest["base"]["path"]
    if sha256_bytes(BASE_MAIN.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 base snapshot SHA mismatch")

    sources=list(manifest["sources"])
    teacher_paths=[]
    for s in sources:
        p=root/s["path"]
        if sha256_bytes(p.read_bytes())!=s["sha"]:
            raise SystemExit(f"teacher snapshot SHA mismatch {s['sha']}")
        teacher_paths.append(p)

    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]
    rows=[];failures=[]
    for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(k,None)

    for src in selected:
        opp_main=root/src["path"]
        for seed in SEEDS:
            for seat in SEATS:
                key={
                  "source_rank":int(src["representative_rank"]),
                  "ref":src["representative_ref"],
                  "main_sha256":src["sha"],
                  "seed":int(seed),"seat":int(seat),
                }
                try:
                    b=run_control(opp_main,seed,seat)
                    for p in teacher_paths:
                        purge_package_modules(p.parent)
                    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
                    t=run_consensus(teacher_paths,opp_main,seed,seat)
                    row={**key,
                      "control_score":b["score"],"treatment_score":t["score"],
                      "score_delta":float(t["score"])-float(b["score"]),
                      "control_margin":b["margin"],"treatment_margin":t["margin"],
                      "margin_delta":float(t["margin"])-float(b["margin"]),
                      "control_win":float(b["score"])==1.0,
                      "treatment_nonwin":float(t["score"])<1.0,
                      "consensus_stats":t["consensus_stats"],
                    }
                    rows.append(row)
                    print("V26B_PAIR",json.dumps({
                      k:row[k] for k in (
                        "source_rank","main_sha256","seed","seat",
                        "control_score","treatment_score","score_delta",
                        "control_margin","treatment_margin","margin_delta"
                      )
                    },sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                finally:
                    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
                    for p in teacher_paths:
                        purge_package_modules(p.parent)

    expected=len(selected)*len(SEEDS)*len(SEATS)
    mech=not failures and len(rows)==expected
    result={
      "schema":"kculture-v26b-persistent-consensus-benchmark-shard-v1",
      "mechanical_pass":mech,
      "shard_index":args.shard_index,"num_shards":args.num_shards,
      "teacher_count":len(teacher_paths),
      "selected_sources":[s["sha"] for s in selected],
      "expected_pairs":expected,"rows":rows,"failures":failures,
      "seeds":list(SEEDS),"seats":list(SEATS),
      "immutable_snapshot_used":True,
      "live_kaggle_reacquisition_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V26B_SHARD_RESULT",json.dumps({
      "shard":args.shard_index,"mechanical_pass":mech,
      "pairs":len(rows),"failures":len(failures),"teacher_count":len(teacher_paths)
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
