#!/usr/bin/env python3
"""V4B dormant diagnostic: long-horizon V48 market-only upper bound.

Purpose
-------
If the bounded 1-3 turn V4A fails, determine whether V48's advantage is cumulative
market-state control rather than a short local transaction.

The candidate preserves exact V47 farmer/hands at every turn. V48 runs only as an
offline shadow proposal source. When V48 and V47 physical actions match, the candidate
may substitute V48's market action for the entire remaining episode. If physical actions
diverge on the altered trajectory, fall back to exact V47 for that turn.

This is an upper-bound diagnostic, not a deployable policy.
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
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    call_agent,canonical_action,plain,score,
)

EXPECTED_ENGINE="1.32.7"
BASE={
    "key":"v47",
    "handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
    "key":"v48",
    "handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS=list(range(74101,74107))


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


def same_physical(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]


class BaseWrap:
    def __init__(self,main):
        self.agent=load_public_agent(main)
    def __call__(self,obs,config=None):
        return canonical_action(call_agent(self.agent,obs,config))


class MarketUpperBound:
    def __init__(self,base_main,v48_main):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.applied=0
        self.fallback_physical=0
        self.identical_market=0
        self.first_applied_step=None

    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",0))
        b=canonical_action(call_agent(self.base,obs,config))
        s=canonical_action(call_agent(self.v48,obs,config))
        if not same_physical(b,s):
            self.fallback_physical+=1
            return b
        if b["market"]==s["market"]:
            self.identical_market+=1
            return b
        out={
            "farmer":copy.deepcopy(b["farmer"]),
            "hands":copy.deepcopy(b["hands"]),
            "market":copy.deepcopy(s["market"]),
        }
        out=canonical_action(out)
        if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
            raise RuntimeError("V4B changed physical action")
        self.applied+=1
        if self.first_applied_step is None:
            self.first_applied_step=step
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


def run_one(base_main,v48_main,seed,seat,treatment):
    cand=MarketUpperBound(base_main,v48_main) if treatment else BaseWrap(base_main)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    if treatment:
        out.update({
            "applied_market_turns":cand.applied,
            "physical_fallback_turns":cand.fallback_physical,
            "identical_market_turns":cand.identical_market,
            "first_applied_step":cand.first_applied_step,
        })
    return out


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/v48-market-upper-bound-v4b/V48_MARKET_UPPER_BOUND_V4B.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    rows=[]; failures=[]; provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="v48-upper-v4b-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]
            for seed in SEEDS:
                for seat in (0,1):
                    key={"seed":seed,"seat":seat}
                    try:
                        purge(paths)
                        b=run_one(base_main,v48_main,seed,seat,False)
                        purge(paths)
                        t=run_one(base_main,v48_main,seed,seat,True)
                        row={
                            **key,
                            "base":b,
                            "upper":t,
                            "score_delta":t["score"]-b["score"],
                            "margin_delta":t["margin"]-b["margin"],
                        }
                        rows.append(row)
                        print("V48_V4B_PAIR",json.dumps({
                            **key,
                            "base_score":b["score"],
                            "upper_score":t["score"],
                            "score_delta":row["score_delta"],
                            "margin_delta":row["margin_delta"],
                            "applied_market_turns":t["applied_market_turns"],
                            "physical_fallback_turns":t["physical_fallback_turns"],
                            "first_applied_step":t["first_applied_step"],
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    bs=[float(r["base"]["score"]) for r in rows]
    us=[float(r["upper"]["score"]) for r in rows]
    md=[float(r["margin_delta"]) for r in rows]
    mechanical_pass=not failures and len(rows)==len(SEEDS)*2
    score_delta=(statistics.mean(us)-statistics.mean(bs)) if rows else 0.0
    flips=sum(r["base"]["score"]<1.0 and r["upper"]["score"]==1.0 for r in rows)

    if mechanical_pass and score_delta>0 and flips>=2:
        decision="V48_V4B_LONG_HORIZON_WL_HEADROOM"
    elif mechanical_pass and statistics.mean(md)>0:
        decision="V48_V4B_LONG_HORIZON_MARGIN_ONLY"
    elif mechanical_pass:
        decision="V48_V4B_MARKET_ONLY_NO_HEADROOM"
    else:
        decision="V48_V4B_MECHANICS_INVALID"

    result={
        "schema":"kculture-v48-market-upper-bound-v4b",
        "engine":EXPECTED_ENGINE,
        "seeds":SEEDS,
        "contexts":len(rows),
        "base_score_rate":statistics.mean(bs) if rows else None,
        "upper_score_rate":statistics.mean(us) if rows else None,
        "score_delta":score_delta,
        "nonwin_to_win_flips":flips,
        "mean_margin_delta":statistics.mean(md) if rows else None,
        "mean_applied_market_turns":statistics.mean(r["upper"]["applied_market_turns"] for r in rows) if rows else None,
        "mean_physical_fallback_turns":statistics.mean(r["upper"]["physical_fallback_turns"] for r in rows) if rows else None,
        "mechanical_pass":mechanical_pass,
        "decision":decision,
        "rows":rows,
        "failures":failures,
        "provenance":provenance,
        "seconds":time.perf_counter()-started,
        "offline_upper_bound_only":True,
        "automatic_kaggle_submission":False,
    }
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V48_V4B_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mechanical_pass,
        "base_score_rate":result["base_score_rate"],
        "upper_score_rate":result["upper_score_rate"],
        "score_delta":score_delta,
        "nonwin_to_win_flips":flips,
        "mean_margin_delta":result["mean_margin_delta"],
        "mean_applied_market_turns":result["mean_applied_market_turns"],
        "mean_physical_fallback_turns":result["mean_physical_fallback_turns"],
        "failures":len(failures),"seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
