#!/usr/bin/env python3
"""Run only frozen V22B contexts missing after attempts 1+2 using recovered exact source bytes."""
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
    return {
        "score":float(score(margin)),
        "margin":float(margin),
        "rewards":rewards,
        "steps":steps,
        "diff_stats":cand.stats,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--teacher-main",required=True)
    ap.add_argument("--context-ids",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__","")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.hard_config).read_text())
    wanted=[x.strip() for x in args.context_ids.split(",") if x.strip()]
    by_id={str(c["context_id"]):c for c in cfg.get("hard_contexts",[])}
    contexts=[by_id[x] for x in wanted]
    if len(contexts)!=len(wanted):
        raise SystemExit("missing context id")

    teacher=Path(args.teacher_main)
    got=sha256_bytes(teacher.read_bytes())
    expected={str(c["main_sha256"]) for c in contexts}
    if len(expected)!=1 or got not in expected:
        raise SystemExit(f"recovered teacher SHA mismatch {got} expected={sorted(expected)}")

    with tempfile.TemporaryDirectory(prefix="v22b-missing-") as td:
        base_main,base_receipt=acquire_public_main(BASE["handle"],Path(td)/"base")
        base_sha=sha256_bytes(base_main.read_bytes())
        if base_sha != BASE["expected_main_sha256"]:
            raise SystemExit(f"base SHA drift {base_sha}")

        for key in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):
            os.environ.pop(key,None)

        rows=[]
        failures=[]
        for ctx in contexts:
            base_result=None
            for mode in MODES:
                try:
                    purge_package_modules(base_main.parent)
                    purge_package_modules(teacher.parent)
                    rr=run_one(base_main,teacher,ctx,mode)
                    if mode=="BASE":
                        if float(rr["score"])!=float(ctx["base_score"]) or float(rr["margin"])!=float(ctx["base_margin"]):
                            raise RuntimeError(
                                f"BASE replay mismatch {(rr['score'],rr['margin'])} != "
                                f"{(ctx['base_score'],ctx['base_margin'])}"
                            )
                        base_result=rr
                    if base_result is None:
                        raise RuntimeError("BASE must run first")
                    row={
                        "context_id":ctx["context_id"],
                        "source_rank":ctx.get("rank"),
                        "ref":ctx["ref"],
                        "main_sha256":ctx["main_sha256"],
                        "seed":int(ctx["seed"]),
                        "seat":int(ctx["seat"]),
                        "mode":mode,
                        "base_score":float(base_result["score"]),
                        "treatment_score":float(rr["score"]),
                        "score_delta":float(rr["score"])-float(base_result["score"]),
                        "base_margin":float(base_result["margin"]),
                        "treatment_margin":float(rr["margin"]),
                        "margin_delta":float(rr["margin"])-float(base_result["margin"]),
                        "diff_stats":rr["diff_stats"],
                    }
                    rows.append(row)
                    print("V22B_MISSING_MODE",json.dumps({
                        k:row[k] for k in ("context_id","source_rank","seed","seat","mode","score_delta","margin_delta")
                    },sort_keys=True),flush=True)
                except Exception as exc:
                    failures.append({
                        "phase":"episode",
                        "context_id":ctx["context_id"],
                        "mode":mode,
                        "error":f"{type(exc).__name__}: {exc}",
                    })

    expected_rows=len(contexts)*len(MODES)
    mechanical_pass=not failures and len(rows)==expected_rows
    result={
        "schema":"kculture-all3-v22b-domain-upper-bound-shard-v1",
        "mechanical_pass":mechanical_pass,
        "shard_index":3,
        "num_shards":4,
        "contexts_assigned":len(contexts),
        "expected_rows":expected_rows,
        "rows":rows,
        "failures":failures,
        "provenance":{
            "historical_recovery":True,
            "teacher_sha":got,
            "teacher_ref":contexts[0]["ref"],
            "base_sha":base_sha,
            "base_receipt":base_receipt,
        },
        "credentials_removed_before_third_party_execution":True,
        "third_party_code_persisted":False,
        "automatic_kaggle_submission":False,
    }
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V22B_MISSING_RESULT",json.dumps({
        "mechanical_pass":mechanical_pass,
        "contexts":len(contexts),
        "rows":len(rows),
        "failures":len(failures),
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)

if __name__=="__main__":
    main()
