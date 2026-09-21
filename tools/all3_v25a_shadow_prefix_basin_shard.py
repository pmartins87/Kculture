#!/usr/bin/env python3
"""V25A shadow-prefix state-basin horizon shard."""
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

HORIZONS=(0,4,8,16,32,64,128,256,720)

class PrefixCandidate:
    def __init__(self,base_main,teacher_main,horizon):
        purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
        self.base=load_public_agent(base_main)
        purge_package_modules(teacher_main.parent)
        self.teacher=load_public_agent(teacher_main)
        self.host=OptionHostState()
        self.horizon=int(horizon)
        self.turn=0
        self.shadow_turns=0
    def __call__(self,obs,config=None):
        t=self.turn;self.turn+=1
        exact=canonical_action(call_agent(self.base,obs,config))
        all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
        shadow=canonical_action(call_agent(self.teacher,obs,config))
        if t<self.horizon:
            self.shadow_turns+=1
            return shadow
        return all3

def run_one(base_main,teacher_main,ctx,horizon):
    cand=PrefixCandidate(base_main,teacher_main,horizon)
    purge_package_modules(teacher_main.parent)
    opp=load_public_agent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:env.run([cand,opp])
    else:env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode H={horizon} statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(ctx["seat"])==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {
      "score":float(score(margin)),"margin":float(margin),"rewards":rewards,"steps":steps,
      "shadow_turns":cand.shadow_turns,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--v23b-aggregate",required=True)
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.hard_config).read_text())
    agg=json.loads(Path(args.v23b_aggregate).read_text())
    if agg.get("decision")!="V23B_CROSS_DOMAIN_INTERACTION_HEADROOM" or not agg.get("mechanical_pass"):
        raise SystemExit("binding V23B mismatch")
    base_rows={str(r["context_id"]):r for r in agg["rows"] if r["mode"]=="BASE"}
    full_rows={str(r["context_id"]):r for r in agg["rows"] if r["mode"]=="FULL_SHADOW"}

    root=Path(args.snapshot_dir)
    manifest=json.loads((root/"MANIFEST.json").read_text())
    base_main=root/manifest["base"]["path"]
    if sha256_bytes(base_main.read_bytes())!=BASE["expected_main_sha256"]:raise SystemExit("base snapshot SHA mismatch")
    paths={}
    for src in manifest["sources"]:
        p=root/src["path"]
        if sha256_bytes(p.read_bytes())!=src["sha"]:raise SystemExit(f"snapshot SHA mismatch {src['sha']}")
        paths[src["sha"]]=p

    contexts=list(cfg["hard_contexts"])
    selected=[c for i,c in enumerate(contexts) if i%args.num_shards==args.shard_index]
    rows=[];failures=[]
    for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(key,None)

    for ctx in selected:
        cid=str(ctx["context_id"]);sha=str(ctx["main_sha256"])
        teacher=paths.get(sha)
        if teacher is None:
            failures.append({"context_id":cid,"phase":"snapshot_lookup","sha":sha,"error":"missing source"})
            continue
        for h in HORIZONS:
            try:
                purge_package_modules(base_main.parent);purge_package_modules(teacher.parent)
                rr=run_one(base_main,teacher,ctx,h)
                if h==0:
                    br=base_rows[cid]
                    if float(rr["score"])!=float(br["treatment_score"]) or float(rr["margin"])!=float(br["treatment_margin"]):
                        raise RuntimeError(f"H0 BASE mismatch {(rr['score'],rr['margin'])} != {(br['treatment_score'],br['treatment_margin'])}")
                if h==720:
                    fr=full_rows[cid]
                    if float(rr["score"])!=float(fr["treatment_score"]) or float(rr["margin"])!=float(fr["treatment_margin"]):
                        raise RuntimeError(f"H720 FULL mismatch {(rr['score'],rr['margin'])} != {(fr['treatment_score'],fr['treatment_margin'])}")
                row={
                  "context_id":cid,"source_rank":ctx["rank"],"ref":ctx["ref"],"main_sha256":sha,
                  "seed":int(ctx["seed"]),"seat":int(ctx["seat"]),"horizon":int(h),
                  "score":rr["score"],"margin":rr["margin"],"shadow_turns":rr["shadow_turns"],
                }
                rows.append(row)
                print("V25A_HORIZON",json.dumps({k:row[k] for k in ("context_id","source_rank","seed","seat","horizon","score","margin","shadow_turns")},sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"context_id":cid,"sha":sha,"seed":ctx["seed"],"seat":ctx["seat"],"horizon":h,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge_package_modules(base_main.parent);purge_package_modules(teacher.parent)

    expected=len(selected)*len(HORIZONS)
    mech=not failures and len(rows)==expected
    result={
      "schema":"kculture-all3-v25a-shadow-prefix-basin-shard-v1","mechanical_pass":mech,
      "shard_index":args.shard_index,"num_shards":args.num_shards,
      "contexts_assigned":len(selected),"horizons":list(HORIZONS),"expected_rows":expected,
      "rows":rows,"failures":failures,"immutable_snapshot_used":True,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V25A_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"contexts":len(selected),"rows":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
