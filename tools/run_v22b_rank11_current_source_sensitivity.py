#!/usr/bin/env python3
"""NON-BINDING sensitivity for V22B missing rank-11 contexts using current yummers source.

The frozen historical SHA is unavailable. This script may only support sensitivity
analysis. It requires exact frozen BASE replay for all target contexts.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.all3_v22b_domain_upper_bound_shard import MODES, HybridCandidate, load_independent
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE, acquire_public_main, sha256_bytes, purge_package_modules
from tools.o_pc1_dev_shard import BASE
from tools.bounded_transaction_oracle_v1 import score


def run_one(base_main, teacher_main, ctx, mode):
    cand=HybridCandidate(base_main,teacher_main,mode)
    opp=load_independent(teacher_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(ctx["seed"])},debug=False)
    if int(ctx["seat"])==0:
        env.run([cand,opp])
    else:
        env.run([opp,cand])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode mode={mode} statuses={statuses} rewards={rewards} steps={steps}")
    mine,other=(rewards[0],rewards[1]) if int(ctx["seat"])==0 else (rewards[1],rewards[0])
    margin=mine-other
    return {"score":float(score(margin)),"margin":float(margin),"diff_stats":cand.stats}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--context-ids",default="v22a_hard_059,v22a_hard_063,v22a_hard_067")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__","")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.hard_config).read_text())
    wanted=[x for x in args.context_ids.split(",") if x]
    by_id={str(c["context_id"]):c for c in cfg["hard_contexts"]}
    contexts=[by_id[x] for x in wanted]
    expected_frozen={str(c["main_sha256"]) for c in contexts}
    if len(expected_frozen)!=1:
        raise SystemExit("target contexts do not share frozen source")

    with tempfile.TemporaryDirectory(prefix="v22b-r11-current-sens-") as td:
        td=Path(td)
        base_main,_=acquire_public_main(BASE["handle"],td/"base")
        if sha256_bytes(base_main.read_bytes()) != BASE["expected_main_sha256"]:
            raise SystemExit("base SHA drift")
        current_main,current_receipt=acquire_public_main("romantamrazov/kaggriculture-yummers",td/"teacher")
        current_sha=sha256_bytes(current_main.read_bytes())

        for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
            os.environ.pop(key,None)

        rows=[]
        failures=[]
        base_replay_pass=True
        for ctx in contexts:
            base_result=None
            for mode in MODES:
                try:
                    purge_package_modules(base_main.parent)
                    purge_package_modules(current_main.parent)
                    rr=run_one(base_main,current_main,ctx,mode)
                    if mode=="BASE":
                        ok=(float(rr["score"])==float(ctx["base_score"]) and float(rr["margin"])==float(ctx["base_margin"]))
                        base_replay_pass=base_replay_pass and ok
                        if not ok:
                            raise RuntimeError(
                                f"BASE replay mismatch current source {(rr['score'],rr['margin'])} != "
                                f"{(ctx['base_score'],ctx['base_margin'])}"
                            )
                        base_result=rr
                    if base_result is None:
                        raise RuntimeError("BASE must run first")
                    row={
                        "context_id":ctx["context_id"],
                        "seed":int(ctx["seed"]),
                        "seat":int(ctx["seat"]),
                        "mode":mode,
                        "frozen_source_sha":ctx["main_sha256"],
                        "current_source_sha":current_sha,
                        "base_score":float(base_result["score"]),
                        "treatment_score":float(rr["score"]),
                        "score_delta":float(rr["score"])-float(base_result["score"]),
                        "base_margin":float(base_result["margin"]),
                        "treatment_margin":float(rr["margin"]),
                        "margin_delta":float(rr["margin"])-float(base_result["margin"]),
                    }
                    rows.append(row)
                    print("V22B_R11_SENS_MODE",json.dumps(row,sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({"context_id":ctx["context_id"],"mode":mode,"error":f"{type(exc).__name__}: {exc}"})

    result={
      "schema":"kculture-all3-v22b-rank11-current-source-sensitivity-v1",
      "non_binding":True,
      "historical_frozen_sha":next(iter(expected_frozen)),
      "current_source_sha":current_sha,
      "current_receipt":current_receipt,
      "base_replay_pass":base_replay_pass,
      "rows":rows,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V22B_R11_SENS_RESULT",json.dumps({
      "base_replay_pass":base_replay_pass,
      "rows":len(rows),
      "failures":len(failures),
      "historical_frozen_sha":result["historical_frozen_sha"],
      "current_source_sha":current_sha,
    },sort_keys=True),flush=True)
    if failures or not base_replay_pass or len(rows)!=len(contexts)*len(MODES):
        raise SystemExit(2)

if __name__=="__main__":
    main()
