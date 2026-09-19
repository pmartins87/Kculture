#!/usr/bin/env python3
"""Fresh V47×V48 divergence census.

Purpose: determine whether the hard V48 gap is primarily market/queue behaviour or
physical programme divergence before spending compute on multi-turn search.

Offline only. No runtime identity feature and no Kaggle submission.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,
    load_public_agent,
    purge_package_modules,
    sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    action_key,
    call_agent,
    canonical_action,
    plain,
    score,
)

EXPECTED_ENGINE = "1.32.7"
BASE = {
    "key": "v47",
    "handle": "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256": "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48 = {
    "key": "v48",
    "handle": "ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS = list(range(73001, 73005))


def acquire(spec: dict, tmp: Path):
    main, receipt = acquire_public_main(spec["handle"], tmp)
    observed = sha256_bytes(main.read_bytes())
    if observed != spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch: {observed}")
    return main, {
        "key": spec["key"],
        "handle": spec["handle"],
        "expected_main_sha256": spec["expected_main_sha256"],
        "observed_main_sha256": observed,
        **receipt,
    }


class CensusWrapper:
    def __init__(self, base_main: Path, shadow_main: Path):
        self.base = load_public_agent(base_main)
        self.shadow = load_public_agent(shadow_main)
        self.rows = []

    def __call__(self, obs, config=None):
        step = int(plain(obs).get("step", len(self.rows)))
        base = canonical_action(call_agent(self.base, obs, config))
        shadow = canonical_action(call_agent(self.shadow, obs, config))
        same_physical = (
            base["farmer"] == shadow["farmer"]
            and base["hands"] == shadow["hands"]
        )
        market_diff = base["market"] != shadow["market"]
        if (not same_physical) or market_diff:
            self.rows.append({
                "step": step,
                "same_physical": same_physical,
                "market_diff": market_diff,
                "base_action_key": action_key(base),
                "shadow_action_key": action_key(shadow),
                "base_market": base["market"],
                "shadow_market": shadow["market"],
                "base_farmer": base["farmer"],
                "shadow_farmer": shadow["farmer"],
                "base_hands": base["hands"],
                "shadow_hands": shadow["hands"],
            })
        return base


def finish(env, seat: int):
    p = env.toJSON()
    statuses = [str(x) for x in p.get("statuses", [])]
    rewards = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"statuses={statuses}")
    if steps < 720 or len(rewards) != 2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode steps={steps} rewards={rewards}")
    mine, opp = (rewards[0], rewards[1]) if seat == 0 else (rewards[1], rewards[0])
    margin = mine - opp
    return {
        "rewards": rewards,
        "margin": margin,
        "score": score(margin),
        "steps": steps,
        "statuses": statuses,
    }


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:
            continue
        seen.add(k)
        purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/v47-v48-divergence-census-v1/V47_V48_DIVERGENCE_CENSUS_V1.json",
    )
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    out_path=Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    failures=[]
    provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="v47-v48-census-") as td:
            tmp=Path(td)
            base_main, provenance["base"]=acquire(BASE,tmp/"base")
            v48_main, provenance["v48"]=acquire(V48,tmp/"v48")
            all_paths=[base_main,v48_main]

            for seed in SEEDS:
                for seat in (0,1):
                    key={"seed":seed,"seat":seat}
                    try:
                        purge(all_paths)
                        cand=CensusWrapper(base_main,v48_main)
                        opp=load_public_agent(v48_main)
                        env=make(
                            "kaggriculture",
                            configuration={"episodeSteps":720,"seed":int(seed)},
                            debug=False,
                        )
                        if seat==0:
                            env.run([cand,opp])
                        else:
                            env.run([opp,cand])
                        result=finish(env,seat)
                        divs=cand.rows
                        same_market=[
                            r for r in divs
                            if r["same_physical"] and r["market_diff"]
                        ]
                        physical=[r for r in divs if not r["same_physical"]]
                        rows.append({
                            **key,
                            "result":result,
                            "divergence_rows":divs,
                            "market_only_count":len(same_market),
                            "physical_divergence_count":len(physical),
                            "first_market_only_step": (
                                min(r["step"] for r in same_market) if same_market else None
                            ),
                            "first_physical_divergence_step": (
                                min(r["step"] for r in physical) if physical else None
                            ),
                        })
                        print("V47_V48_CENSUS_PAIR",json.dumps({
                            **key,
                            "score":result["score"],
                            "margin":result["margin"],
                            "market_only_count":len(same_market),
                            "physical_divergence_count":len(physical),
                            "first_market_only_step": (
                                min(r["step"] for r in same_market) if same_market else None
                            ),
                            "first_physical_divergence_step": (
                                min(r["step"] for r in physical) if physical else None
                            ),
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(all_paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    market_counter=Counter()
    physical_counter=Counter()
    action_counter=Counter()
    for row in rows:
        for d in row["divergence_rows"]:
            if d["same_physical"] and d["market_diff"]:
                market_counter[d["step"]]+=1
                action_counter[(d["step"],d["base_action_key"],d["shadow_action_key"])]+=1
            if not d["same_physical"]:
                physical_counter[d["step"]]+=1

    scores=[float(r["result"]["score"]) for r in rows]
    margins=[float(r["result"]["margin"]) for r in rows]
    nonwins=sum(x<1.0 for x in scores)
    total_market=sum(r["market_only_count"] for r in rows)
    total_physical=sum(r["physical_divergence_count"] for r in rows)
    mechanical_pass=not failures and len(rows)==len(SEEDS)*2

    if mechanical_pass and nonwins>=4 and total_market>0:
        decision="V48_CENSUS_MARKET_SEARCHABLE"
    elif mechanical_pass and nonwins>=4 and total_physical>0:
        decision="V48_CENSUS_PHYSICAL_SEARCH_REQUIRED"
    elif mechanical_pass:
        decision="V48_CENSUS_INSUFFICIENT_HARD_CONTEXTS"
    else:
        decision="V48_CENSUS_MECHANICS_INVALID"

    top_market_steps=[
        {"step":int(step),"count":int(count)}
        for step,count in market_counter.most_common(20)
    ]
    top_action_pairs=[
        {
            "step":int(k[0]),
            "count":int(v),
            "base_action_key":k[1],
            "v48_action_key":k[2],
        }
        for k,v in action_counter.most_common(30)
    ]

    result={
        "schema":"kculture-v47-v48-divergence-census-v1",
        "engine":EXPECTED_ENGINE,
        "base":BASE,
        "shadow_and_opponent":V48,
        "seeds":SEEDS,
        "contexts":len(rows),
        "mechanical_pass":mechanical_pass,
        "score_rate":statistics.mean(scores) if scores else None,
        "mean_margin":statistics.mean(margins) if margins else None,
        "wins":sum(x==1.0 for x in scores),
        "ties":sum(x==0.5 for x in scores),
        "losses":sum(x==0.0 for x in scores),
        "nonwins":nonwins,
        "total_market_only_divergences":total_market,
        "total_physical_divergences":total_physical,
        "top_market_steps":top_market_steps,
        "top_action_pairs":top_action_pairs,
        "physical_divergence_step_counts":dict(sorted(physical_counter.items())),
        "rows":rows,
        "failures":failures,
        "provenance":provenance,
        "decision":decision,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V47_V48_CENSUS_RESULT",json.dumps({
        "decision":decision,
        "mechanical_pass":mechanical_pass,
        "score_rate":result["score_rate"],
        "mean_margin":result["mean_margin"],
        "wins":result["wins"],
        "ties":result["ties"],
        "losses":result["losses"],
        "total_market_only_divergences":total_market,
        "total_physical_divergences":total_physical,
        "top_market_steps":top_market_steps[:10],
        "failures":len(failures),
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
