#!/usr/bin/env python3
"""Frozen O-CQ2 validation on untouched seeds.

The candidate config selects exactly one mode + min_step and pins the SHA-256 of
the implementation source used during development. This script refuses to validate
if that implementation moved after selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    call_agent,canonical_action,plain,
)
from tools.cq2_projected_queue_dev_matrix import (
    EXPECTED_ENGINE,BASE,V48,cq2_action,metrics,
)

SEEDS=list(range(73401,73405))
IMPLEMENTATION_PATH=ROOT/"tools/cq2_projected_queue_dev_matrix.py"


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch: {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


class Capture:
    def __init__(self,base_main,v48_main):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.rows=[]
    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.base,obs,config))
        v=canonical_action(call_agent(self.v48,obs,config))
        self.rows.append({
            "obs":json.loads(json.dumps(plain(obs))),
            "config":json.loads(json.dumps(plain(config or {}))),
            "base":b,"v48":v,
        })
        return b


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    ap.add_argument("--out",default="artifacts/cq2-validation/CQ2_VALIDATION.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg=json.loads(Path(args.config).read_text(encoding="utf-8"))
    mode=str(cfg["mode"]); min_step=int(cfg["min_step"])
    expected_impl=str(cfg["implementation_sha256"])
    observed_impl=hashlib.sha256(IMPLEMENTATION_PATH.read_bytes()).hexdigest()
    if observed_impl!=expected_impl:
        raise SystemExit(f"implementation SHA mismatch {observed_impl} != {expected_impl}")

    rows=[]; failures=[]; provenance={}
    started=time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="cq2-validation-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]
            for seed in SEEDS:
                for seat in (0,1):
                    try:
                        purge(paths)
                        cand=Capture(base_main,v48_main)
                        opp=load_public_agent(v48_main)
                        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
                        if seat==0: env.run([cand,opp])
                        else: env.run([opp,cand])
                        payload=env.toJSON()
                        statuses=[str(x) for x in payload.get("statuses",[])]
                        if statuses!=["DONE","DONE"]:
                            raise RuntimeError(f"statuses={statuses}")
                        rows.extend(cand.rows)
                    except Exception as exc:
                        failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    expected_rows=len(SEEDS)*2*719
    mechanical_pass=not failures and len(rows)==expected_rows
    m=metrics(rows,mode,min_step) if mechanical_pass else {}

    if mechanical_pass and m["precision"]>=0.75 and m["recall"]>=0.70 and m["f1"]>=0.72:
        decision="CQ2_VALIDATION_PASS_OPEN_CAUSAL"
    elif mechanical_pass and m["precision"]>=0.60 and m["recall"]>=0.60:
        decision="CQ2_VALIDATION_PARTIAL_DO_NOT_CAUSALIZE_YET"
    elif mechanical_pass:
        decision="CQ2_VALIDATION_FAIL_USE_V4A"
    else:
        decision="CQ2_VALIDATION_MECHANICS_INVALID"

    result={
        "schema":"kculture-cq2-projected-queue-validation-v1",
        "engine":EXPECTED_ENGINE,
        "frozen_config":cfg,
        "observed_implementation_sha256":observed_impl,
        "validation_seeds":SEEDS,
        "expected_action_rows":expected_rows,
        "row_count":len(rows),
        "mechanical_pass":mechanical_pass,
        "metrics":m,
        "gate":{
            "min_precision":0.75,
            "min_recall":0.70,
            "min_f1":0.72,
        },
        "decision":decision,
        "failures":failures,
        "provenance":provenance,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CQ2_VALIDATION_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mechanical_pass,
        "metrics":m,"failures":len(failures),"seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
