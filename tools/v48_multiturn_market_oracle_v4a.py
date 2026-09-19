#!/usr/bin/env python3
"""Targeted V4A: V48-guided bounded multi-turn market oracle.

Dormant until the fresh V47×V48 divergence census confirms market searchability.

The candidate keeps exact V47 farmer/hands. At a replay-verified market-divergence
state it may follow V48's market action for a bounded 1, 2, or 3-turn window, but
only on turns where V48 farmer/hands exactly match current V47 farmer/hands.
After the window exact V47 resumes autonomously.

Offline oracle only. V48 identity is proposal-generation metadata, never a runtime
feature for a promoted first-party option.
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
    acquire_public_main, load_public_agent, purge_package_modules, sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    action_key, call_agent, canonical_action, plain, score,
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
SEEDS=list(range(74001,74007))
HORIZONS=(1,2,3)
MAX_EVENTS=3
MIN_EVENT_SEPARATION=36


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch: {observed}")
    return main,{
        "key":spec["key"],"handle":spec["handle"],
        "expected_main_sha256":spec["expected_main_sha256"],
        "observed_main_sha256":observed,**receipt,
    }


def same_physical(a,b):
    return a["farmer"]==b["farmer"] and a["hands"]==b["hands"]


class Discovery:
    def __init__(self,base_main,shadow_main):
        self.base=load_public_agent(base_main)
        self.shadow=load_public_agent(shadow_main)
        self.trace=[]

    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",len(self.trace)))
        b=canonical_action(call_agent(self.base,obs,config))
        s=canonical_action(call_agent(self.shadow,obs,config))
        self.trace.append({
            "step":step,
            "base_key":action_key(b),
            "shadow_key":action_key(s),
            "same_physical":same_physical(b,s),
            "market_diff":b["market"]!=s["market"],
            "base_action":copy.deepcopy(b),
            "shadow_action":copy.deepcopy(s),
        })
        return b


class BaseOnly:
    def __init__(self,base_main):
        self.base=load_public_agent(base_main)
    def __call__(self,obs,config=None):
        return canonical_action(call_agent(self.base,obs,config))


class V48MarketWindow:
    def __init__(self,base_main,shadow_main,*,target_step,expected_base_key,horizon):
        self.base=load_public_agent(base_main)
        self.shadow=load_public_agent(shadow_main)
        self.target_step=int(target_step)
        self.expected_base_key=str(expected_base_key)
        self.horizon=int(horizon)
        self.target_seen=False
        self.applied_turns=0
        self.physical_fallback_turns=0
        self.cardinality_fallback_turns=0
        self.window_rows=[]

    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",0))
        b=canonical_action(call_agent(self.base,obs,config))
        # Keep shadow memory synchronized before/during the intervention.
        s=canonical_action(call_agent(self.shadow,obs,config))

        if step==self.target_step:
            self.target_seen=True
            if action_key(b)!=self.expected_base_key:
                raise RuntimeError(
                    f"base replay mismatch at target {step}: {action_key(b)} != {self.expected_base_key}"
                )

        if step<self.target_step or step>=self.target_step+self.horizon:
            return b

        row={
            "step":step,
            "same_physical":same_physical(b,s),
            "base_key":action_key(b),
            "shadow_key":action_key(s),
            "base_market":copy.deepcopy(b["market"]),
            "shadow_market":copy.deepcopy(s["market"]),
        }
        if not same_physical(b,s):
            self.physical_fallback_turns+=1
            row["applied"]=False
            row["fallback"]="physical"
            self.window_rows.append(row)
            return b
        if len(s["market"])>10:
            self.cardinality_fallback_turns+=1
            row["applied"]=False
            row["fallback"]="cardinality"
            self.window_rows.append(row)
            return b

        out=canonical_action({
            "farmer":copy.deepcopy(b["farmer"]),
            "hands":copy.deepcopy(b["hands"]),
            "market":copy.deepcopy(s["market"]),
        })
        if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
            raise RuntimeError("V4A changed V47 physical action")
        self.applied_turns+=1
        row["applied"]=True
        row["fallback"]=None
        self.window_rows.append(row)
        return out


def finish(env,seat,wrapper=None):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"]:
        raise RuntimeError(f"episode statuses={statuses}")
    if steps<720 or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode steps={steps} rewards={rewards}")
    if wrapper is not None and hasattr(wrapper,"target_seen") and not wrapper.target_seen:
        raise RuntimeError(f"target {wrapper.target_step} not seen")
    mine,opp=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-opp
    return {
        "rewards":rewards,"margin":margin,"score":score(margin),
        "statuses":statuses,"steps":steps,
    }


def run_discovery(base_main,v48_main,*,seed,seat):
    cand=Discovery(base_main,v48_main)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    out["trace"]=cand.trace
    return out


def run_base(base_main,v48_main,*,seed,seat):
    cand=BaseOnly(base_main)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    return finish(env,seat)


def run_branch(base_main,v48_main,*,seed,seat,event,horizon):
    cand=V48MarketWindow(
        base_main,v48_main,
        target_step=event["step"],
        expected_base_key=event["base_key"],
        horizon=horizon,
    )
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat,cand)
    out.update({
        "applied_turns":cand.applied_turns,
        "physical_fallback_turns":cand.physical_fallback_turns,
        "cardinality_fallback_turns":cand.cardinality_fallback_turns,
        "window_rows":cand.window_rows,
    })
    return out


def select_events(trace):
    eligible=[
        r for r in trace
        if r["same_physical"] and r["market_diff"] and int(r["step"])<=671
    ]
    selected=[]
    for row in eligible:
        if selected and int(row["step"])-int(selected[-1]["step"])<MIN_EVENT_SEPARATION:
            continue
        selected.append(row)
        if len(selected)>=MAX_EVENTS:
            break
    return selected


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k)
        purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/v48-multiturn-market-v4a/V48_MULTITURN_MARKET_V4A.json",
    )
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    out_path=Path(args.out)
    out_path.parent.mkdir(parents=True,exist_ok=True)
    contexts=[]
    failures=[]
    provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="v48-multiturn-v4a-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]

            for seed in SEEDS:
                for seat in (0,1):
                    key={"seed":seed,"seat":seat}
                    try:
                        purge(paths)
                        discovery=run_discovery(base_main,v48_main,seed=seed,seat=seat)
                        purge(paths)
                        base=run_base(base_main,v48_main,seed=seed,seat=seat)
                        if discovery["rewards"]!=base["rewards"]:
                            raise RuntimeError("discovery shadow changed BASE rewards")

                        events=select_events(discovery["trace"])
                        candidates=[{
                            "label":"BASE","event_step":None,"horizon":0,
                            "score":base["score"],"margin":base["margin"],
                            "rewards":base["rewards"],"applied_turns":0,
                        }]
                        # Discovery work is focused on hard contexts. Wins are retained
                        # as receipts but do not spend branch rollout compute.
                        if base["score"]<1.0:
                            for event in events:
                                for horizon in HORIZONS:
                                    purge(paths)
                                    res=run_branch(
                                        base_main,v48_main,seed=seed,seat=seat,
                                        event=event,horizon=horizon,
                                    )
                                    candidates.append({
                                        "label":"V48_MARKET_WINDOW",
                                        "event_step":int(event["step"]),
                                        "horizon":int(horizon),
                                        "score":res["score"],
                                        "margin":res["margin"],
                                        "rewards":res["rewards"],
                                        "applied_turns":res["applied_turns"],
                                        "physical_fallback_turns":res["physical_fallback_turns"],
                                        "cardinality_fallback_turns":res["cardinality_fallback_turns"],
                                        "window_rows":res["window_rows"],
                                    })

                        oracle=max(
                            candidates,
                            key=lambda x:(float(x["score"]),float(x["margin"]),-int(x["horizon"])),
                        )
                        contexts.append({
                            **key,
                            "base":candidates[0],
                            "oracle":oracle,
                            "events":[{
                                "step":int(e["step"]),
                                "base_key":e["base_key"],
                                "shadow_key":e["shadow_key"],
                            } for e in events],
                            "candidate_count":len(candidates),
                            "candidates":candidates,
                        })
                        print("V48_V4A_CONTEXT",json.dumps({
                            **key,
                            "base_score":base["score"],
                            "base_margin":base["margin"],
                            "events":[int(e["step"]) for e in events],
                            "candidates":len(candidates),
                            "oracle_score":oracle["score"],
                            "oracle_margin":oracle["margin"],
                            "oracle_step":oracle["event_step"],
                            "oracle_horizon":oracle["horizon"],
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    base_scores=[float(r["base"]["score"]) for r in contexts]
    oracle_scores=[float(r["oracle"]["score"]) for r in contexts]
    base_margins=[float(r["base"]["margin"]) for r in contexts]
    oracle_margins=[float(r["oracle"]["margin"]) for r in contexts]
    flips=sum(
        r["base"]["score"]<1.0 and r["oracle"]["score"]==1.0
        for r in contexts
    )
    positive=sum(r["oracle"]["score"]>r["base"]["score"] for r in contexts)
    negative=sum(r["oracle"]["score"]<r["base"]["score"] for r in contexts)
    nonwins=sum(r["base"]["score"]<1.0 for r in contexts)
    mechanical_pass=not failures and len(contexts)==len(SEEDS)*2
    score_delta=(
        statistics.mean(oracle_scores)-statistics.mean(base_scores)
        if contexts else 0.0
    )
    mean_margin_delta=(
        statistics.mean(o-b for o,b in zip(oracle_margins,base_margins))
        if contexts else 0.0
    )

    if mechanical_pass and nonwins>=4 and flips>=2 and score_delta>0:
        decision="V48_V4A_WL_HEADROOM_PASS"
    elif mechanical_pass and nonwins>=4 and score_delta>=0.125 and positive>0:
        decision="V48_V4A_WL_HEADROOM_WEAK"
    elif mechanical_pass and mean_margin_delta>0:
        decision="V48_V4A_MARGIN_ONLY"
    elif mechanical_pass:
        decision="V48_V4A_NO_HEADROOM"
    else:
        decision="V48_V4A_MECHANICS_INVALID"

    result={
        "schema":"kculture-v48-multiturn-market-oracle-v4a",
        "engine":EXPECTED_ENGINE,
        "base":BASE,
        "opponent_and_shadow":V48,
        "seeds":SEEDS,
        "horizons":HORIZONS,
        "max_events":MAX_EVENTS,
        "min_event_separation":MIN_EVENT_SEPARATION,
        "contexts":len(contexts),
        "hard_base_nonwins":nonwins,
        "base_score_rate":statistics.mean(base_scores) if contexts else None,
        "oracle_score_rate":statistics.mean(oracle_scores) if contexts else None,
        "score_delta":score_delta,
        "nonwin_to_win_flips":flips,
        "positive_score_contexts":positive,
        "negative_score_contexts":negative,
        "mean_oracle_margin_delta":mean_margin_delta,
        "mechanical_pass":mechanical_pass,
        "decision":decision,
        "failures":failures,
        "provenance":provenance,
        "rows":contexts,
        "seconds":time.perf_counter()-started,
        "offline_oracle_only":True,
        "automatic_kaggle_submission":False,
    }
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V48_V4A_RESULT",json.dumps({
        "decision":decision,
        "mechanical_pass":mechanical_pass,
        "contexts":len(contexts),
        "hard_base_nonwins":nonwins,
        "base_score_rate":result["base_score_rate"],
        "oracle_score_rate":result["oracle_score_rate"],
        "score_delta":score_delta,
        "nonwin_to_win_flips":flips,
        "positive_score_contexts":positive,
        "negative_score_contexts":negative,
        "mean_oracle_margin_delta":mean_margin_delta,
        "failures":len(failures),
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
