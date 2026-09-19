#!/usr/bin/env python3
"""Execution-equivalent V5 physical oracle shard for one opponent x one seed."""
from __future__ import annotations
import argparse,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.all3_physical_proposal_oracle_v5_shard import (
    EXPECTED_ENGINE,BASE,PROPOSERS,V2_OPPONENTS,
    acquire,run_discovery,run_base,run_branch,select_events,purge,summarize,
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--opponent",required=True)
    ap.add_argument("--seed",type=int,required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    opp_spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    failures=[];rows=[];matchups=[];provenance={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v5-{args.opponent}-{args.seed}-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        paths_by_sha={BASE["expected_main_sha256"]:base_main}
        proposer_paths={}
        for spec in PROPOSERS:
            sha=spec["expected_main_sha256"]
            if sha in paths_by_sha:
                p=paths_by_sha[sha];rec={"reused_exact_bytes":True,"observed_main_sha256":sha}
            else:
                p,rec=acquire(spec,tmp/f"prop_{spec['key']}");paths_by_sha[sha]=p
            proposer_paths[spec["key"]]=p
            provenance[spec["key"]]={"key":spec["key"],"handle":spec["handle"],**rec}
        sha=opp_spec["expected_main_sha256"]
        if sha in paths_by_sha:
            opp_main=paths_by_sha[sha]
            provenance["opponent"]={"key":opp_spec["key"],"family":opp_spec.get("family"),"reused_exact_bytes":True,"observed_main_sha256":sha}
        else:
            opp_main,rec=acquire(opp_spec,tmp/"opponent");paths_by_sha[sha]=opp_main
            provenance["opponent"]={**rec,"family":opp_spec.get("family")}
        all_paths=list({str(p.resolve()):p for p in [base_main,*proposer_paths.values(),opp_main]}.values())

        for seat in (0,1):
            key={"opponent":args.opponent,"family":opp_spec.get("family"),"seed":args.seed,"seat":seat}
            try:
                purge(all_paths);disc=run_discovery(base_main,proposer_paths,opp_main,args.seed,seat)
                purge(all_paths);base=run_base(base_main,opp_main,args.seed,seat)
                if disc["rewards"]!=base["rewards"]:
                    raise RuntimeError(f"shadow discovery changed ALL3 rewards {disc['rewards']} != {base['rewards']}")
                events=select_events(disc["trace"])
                matchups.append({
                  **key,"replay_parity":True,"base_rewards":base["rewards"],"base_margin":base["margin"],
                  "physical_disagreement_states":sum(1 for r in disc["trace"] if r["proposals"]),
                  "selected_steps":[int(e["step"]) for e in events],
                  "selected_counts":[len(e["proposals"]) for e in events],
                })
                for event in events:
                    candidates=[{
                      "label":"BASE","sources":["ALL3"],"action_key":event["base_action_key"],
                      "locus":None,"old_unit":None,"new_unit":None,
                      "reward":base["reward"],"opponent_reward":base["opponent_reward"],
                      "margin":base["margin"],"score":base["score"],
                    }]
                    for prop in event["proposals"]:
                        purge(all_paths)
                        res=run_branch(base_main,proposer_paths,opp_main,args.seed,seat,event,prop)
                        candidates.append({
                          "label":"PHYSICAL_LOCAL","sources":prop["sources"],"support":prop["support"],
                          "action_key":prop["action_key"],"locus":prop["locus"],
                          "old_unit":prop["old_unit"],"new_unit":prop["new_unit"],
                          "reward":res["reward"],"opponent_reward":res["opponent_reward"],
                          "margin":res["margin"],"score":res["score"],
                        })
                    oracle=max(candidates,key=lambda x:(float(x["score"]),float(x["margin"]),str(x.get("locus")),",".join(x.get("sources",[]))))
                    rows.append({
                      **key,"step":int(event["step"]),"proposal_count":len(candidates),
                      "base":candidates[0],"oracle":oracle,"candidates":candidates,
                    })
            except Exception as exc:
                failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(all_paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    summary=summarize(rows)
    mech=not failures and len(matchups)==2 and all(m.get("replay_parity") for m in matchups)
    result={
      "schema":"kculture-all3-physical-proposal-v5-seed-shard",
      "opponent":args.opponent,"family":opp_spec.get("family"),"seed":args.seed,
      "mechanical_pass":mech,"summary":summary,"matchups":matchups,"rows":rows,
      "failures":failures,"provenance":provenance,"seconds":time.perf_counter()-started,
      "offline_oracle_only":True,"third_party_code_persisted":False,"automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V5_PHYSICAL_SEED_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"seed":args.seed,"mechanical_pass":mech,
      "summary":summary,"branch_states":len(rows),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__":main()
