#!/usr/bin/env python3
"""V4C dormant diagnostic: market->physical state-basin coupling.

Run only if V4B has no W/L headroom but records material physical fallback.
It replays the long-horizon V48-market intervention while logging when and how the
V48 shadow physical action diverges from exact V47 after prior market substitutions.

Offline diagnostic only.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.v48_market_upper_bound_v4b import EXPECTED_ENGINE,BASE,V48

SEEDS=list(range(74201,74205))


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


def same_physical(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]


def physical_kind(a,b):
    farmer=a["farmer"]!=b["farmer"]
    hands=a["hands"]!=b["hands"]
    if farmer and hands:
        return "farmer+hands"
    if farmer:
        return "farmer"
    if hands:
        return "hands"
    return "same"


class CouplingTrace:
    def __init__(self,base_main,v48_main):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.rows=[]
        self.applied_steps=[]
        self.physical_div_steps=[]

    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",0))
        b=canonical_action(call_agent(self.base,obs,config))
        s=canonical_action(call_agent(self.v48,obs,config))
        phys_same=same_physical(b,s)
        market_same=b["market"]==s["market"]
        last_applied=self.applied_steps[-1] if self.applied_steps else None
        lag=None if last_applied is None else step-last_applied

        row={
            "step":step,
            "physical_same":phys_same,
            "physical_kind":physical_kind(b,s),
            "market_same":market_same,
            "last_applied_market_step":last_applied,
            "lag_from_last_applied_market":lag,
            "v47_farmer":copy.deepcopy(b["farmer"]),
            "v48_farmer":copy.deepcopy(s["farmer"]),
            "v47_hands":copy.deepcopy(b["hands"]),
            "v48_hands":copy.deepcopy(s["hands"]),
        }

        if not phys_same:
            self.physical_div_steps.append(step)
            row["action"]="FALLBACK_BASE"
            self.rows.append(row)
            return b

        if market_same:
            row["action"]="BASE_IDENTICAL_MARKET"
            self.rows.append(row)
            return b

        out=canonical_action({
            "farmer":copy.deepcopy(b["farmer"]),
            "hands":copy.deepcopy(b["hands"]),
            "market":copy.deepcopy(s["market"]),
        })
        self.applied_steps.append(step)
        row["action"]="APPLY_V48_MARKET"
        row["applied_market"]=copy.deepcopy(s["market"])
        row["base_market"]=copy.deepcopy(b["market"])
        self.rows.append(row)
        return out


def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards) or steps<720:
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,opp=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-opp
    return {"rewards":rewards,"margin":margin,"score":score(margin),"steps":steps}


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/v48-state-basin-v4c/V48_STATE_BASIN_V4C.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    rows=[]; failures=[]; provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="v48-basin-v4c-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]
            for seed in SEEDS:
                for seat in (0,1):
                    try:
                        purge(paths)
                        cand=CouplingTrace(base_main,v48_main)
                        opp=load_public_agent(v48_main)
                        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
                        if seat==0: env.run([cand,opp])
                        else: env.run([opp,cand])
                        res=finish(env,seat)
                        divrows=[r for r in cand.rows if not r["physical_same"]]
                        lags=[
                            int(r["lag_from_last_applied_market"])
                            for r in divrows
                            if r["lag_from_last_applied_market"] is not None
                        ]
                        rows.append({
                            "seed":seed,"seat":seat,
                            "result":res,
                            "applied_market_turns":len(cand.applied_steps),
                            "physical_divergence_turns":len(divrows),
                            "first_applied_market_step":cand.applied_steps[0] if cand.applied_steps else None,
                            "first_physical_divergence_step":cand.physical_div_steps[0] if cand.physical_div_steps else None,
                            "min_lag_market_to_physical":min(lags) if lags else None,
                            "median_lag_market_to_physical":statistics.median(lags) if lags else None,
                            "physical_kind_counts":dict(Counter(r["physical_kind"] for r in divrows)),
                            "divergence_rows":divrows[:120],
                        })
                    except Exception as exc:
                        failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==len(SEEDS)*2
    total_applied=sum(r["applied_market_turns"] for r in rows)
    total_phys=sum(r["physical_divergence_turns"] for r in rows)
    immediate=sum(
        1
        for r in rows
        for d in r["divergence_rows"]
        if d["lag_from_last_applied_market"] is not None and d["lag_from_last_applied_market"]<=3
    )
    if mech and total_phys>0:
        decision="V4C_MARKET_INDUCES_PHYSICAL_STATE_DIVERGENCE"
    elif mech:
        decision="V4C_NO_PHYSICAL_COUPLING_OBSERVED"
    else:
        decision="V4C_MECHANICS_INVALID"

    result={
        "schema":"kculture-v48-state-basin-coupling-v4c",
        "engine":EXPECTED_ENGINE,
        "seeds":SEEDS,
        "contexts":len(rows),
        "mechanical_pass":mech,
        "total_applied_market_turns":total_applied,
        "total_physical_divergence_turns":total_phys,
        "physical_divergences_within_3_turns_of_market_substitution":immediate,
        "mean_applied_market_turns":statistics.mean(r["applied_market_turns"] for r in rows) if rows else None,
        "mean_physical_divergence_turns":statistics.mean(r["physical_divergence_turns"] for r in rows) if rows else None,
        "decision":decision,
        "rows":rows,
        "failures":failures,
        "provenance":provenance,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V48_V4C_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mech,
        "total_applied_market_turns":total_applied,
        "total_physical_divergence_turns":total_phys,
        "physical_divergences_within_3_turns_of_market_substitution":immediate,
        "mean_applied_market_turns":result["mean_applied_market_turns"],
        "mean_physical_divergence_turns":result["mean_physical_divergence_turns"],
        "failures":len(failures),"seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)


if __name__=="__main__":
    main()
