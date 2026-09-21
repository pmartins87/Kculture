#!/usr/bin/env python3
"""V26A paired ALL3 vs PrizeSolverV4 architecture benchmark shard."""
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from solver.prize_solver_v4 import PrizeSolverV4

SEEDS=(79501,79502,79503,79504,79505,79506)
SEATS=(0,1)
BASE_MAIN=None

class All3:
    def __init__(self):
        self.base=load_public_agent(BASE_MAIN)
        self.host=OptionHostState()
    def __call__(self,obs,config=None):
        exact=canonical_action(call_agent(self.base,obs,config))
        return apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)

class PS4:
    def __init__(self):
        self.solver=PrizeSolverV4()
    def __call__(self,obs,config=None):
        return self.solver.act(obs,config or {})

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

def run_agent(factory,opp_main,seed,seat):
    purge_package_modules(opp_main.parent)
    cand=factory()
    purge_package_modules(opp_main.parent)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if int(seat)==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])
    return finish(env,seat)

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
    sources=list(manifest["sources"])
    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]

    base_meta=manifest.get("base") or {}
    BASE_MAIN=root/str(base_meta.get("path","base/main.py"))
    if not BASE_MAIN.exists():
        raise SystemExit("V47 base missing from immutable snapshot")
    if sha256_bytes(BASE_MAIN.read_bytes())!=BASE["expected_main_sha256"]:
        raise SystemExit("V47 snapshot SHA drift")

    rows=[];failures=[]
    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
        os.environ.pop(key,None)

    for src in selected:
        opp_main=root/src["path"]
        if not opp_main.exists():
            failures.append({"phase":"snapshot_lookup","sha":src["sha"],"error":"main.py missing"})
            continue
        if sha256_bytes(opp_main.read_bytes())!=src["sha"]:
            failures.append({"phase":"snapshot_sha","sha":src["sha"],"error":"SHA mismatch"})
            continue
        for seed in SEEDS:
            for seat in SEATS:
                key={
                    "source_rank":int(src["representative_rank"]),
                    "ref":src["representative_ref"],
                    "main_sha256":src["sha"],
                    "seed":int(seed),
                    "seat":int(seat),
                }
                try:
                    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
                    b=run_agent(All3,opp_main,seed,seat)
                    purge_package_modules(BASE_MAIN.parent);purge_package_modules(opp_main.parent)
                    t=run_agent(PS4,opp_main,seed,seat)
                    row={**key,
                      "control_score":b["score"],"treatment_score":t["score"],
                      "score_delta":float(t["score"])-float(b["score"]),
                      "control_margin":b["margin"],"treatment_margin":t["margin"],
                      "margin_delta":float(t["margin"])-float(b["margin"]),
                      "control_win":float(b["score"])==1.0,
                      "treatment_nonwin":float(t["score"])<1.0,
                    }
                    rows.append(row)
                    print("V26A_PAIR",json.dumps({
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

    expected=len(selected)*len(SEEDS)*len(SEATS)
    mech=not failures and len(rows)==expected
    result={
      "schema":"kculture-v26a-base-architecture-benchmark-shard-v1",
      "mechanical_pass":mech,
      "shard_index":args.shard_index,
      "num_shards":args.num_shards,
      "selected_sources":[s["sha"] for s in selected],
      "expected_pairs":expected,
      "rows":rows,
      "failures":failures,
      "seeds":list(SEEDS),
      "seats":list(SEATS),
      "immutable_snapshot_used":True,
      "live_kaggle_reacquisition_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V26A_SHARD_RESULT",json.dumps({
        "shard":args.shard_index,"mechanical_pass":mech,
        "pairs":len(rows),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
