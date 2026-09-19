#!/usr/bin/env python3
"""Fresh causal full-episode gate for first-party O-CQ1 Queue Clamp/Clear.

Treatment runtime uses only exact V47 current action + own private current shed.
No V48 shadow code is used inside the treatment.
"""
from __future__ import annotations

import argparse
import hashlib
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
    action_key,call_agent,canonical_action,plain,score,
)
from tools.cq1_queue_clamp_parity_audit import cq1_action

EXPECTED_ENGINE="1.32.7"
BASE={
    "key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
    "key":"v48","handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS=list(range(73201,73209))


def obs_hash(obs):
    b=json.dumps(plain(obs),sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    return hashlib.sha256(b).hexdigest()


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


class BaseTrace:
    def __init__(self,main):
        self.agent=load_public_agent(main)
        self.trace=[]
    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((obs_hash(obs),action_key(b)))
        return b


class CQ1Runtime:
    def __init__(self,main):
        self.agent=load_public_agent(main)
        self.trace=[]
        self.fire_steps=[]
        self.changed_slots=0
        self.cleared_slots=0
        self.clamped_slots=0

    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((obs_hash(obs),action_key(b)))
        c=cq1_action(obs,b)
        if action_key(c)!=action_key(b):
            step=int(plain(obs).get("step",len(self.trace)-1))
            self.fire_steps.append(step)
            for bo,co in zip(b["market"],c["market"]):
                if bo==co:
                    continue
                self.changed_slots+=1
                if co==[]:
                    self.cleared_slots+=1
                else:
                    self.clamped_slots+=1
        if c["farmer"]!=b["farmer"] or c["hands"]!=b["hands"]:
            raise RuntimeError("O-CQ1 changed farmer/hands")
        return c


def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"]:
        raise RuntimeError(f"statuses={statuses}")
    if steps<720 or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode steps={steps} rewards={rewards}")
    mine,opp=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-opp
    return {"rewards":rewards,"margin":margin,"score":score(margin),"steps":steps}


def run_episode(base_main,opp_main,*,seed,seat,treatment):
    cand=CQ1Runtime(base_main) if treatment else BaseTrace(base_main)
    opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    out["trace"]=cand.trace
    out["fire_steps"]=getattr(cand,"fire_steps",[])
    out["changed_slots"]=getattr(cand,"changed_slots",0)
    out["cleared_slots"]=getattr(cand,"cleared_slots",0)
    out["clamped_slots"]=getattr(cand,"clamped_slots",0)
    return out


def parity(base,tr):
    bt,tt=base["trace"],tr["trace"]
    if len(bt)!=len(tt):
        return {"ok":False,"reason":"trace length"}
    fires=tr["fire_steps"]
    if not fires:
        return {
            "ok":bt==tt and base["rewards"]==tr["rewards"],
            "triggered":False,
            "checked_through_step":len(bt)-1,
        }
    first=min(fires)
    for i in range(min(first,len(bt)-1)+1):
        if bt[i]!=tt[i]:
            return {"ok":False,"reason":f"pretrigger mismatch {i}","first_fire":first}
    return {"ok":True,"triggered":True,"checked_through_step":first,"first_fire":first}


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k)
        purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/cq1-v48-causal/CQ1_V48_CAUSAL.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    rows=[]; failures=[]; provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="cq1-v48-causal-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            opp_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,opp_main]
            for seed in SEEDS:
                for seat in (0,1):
                    key={"seed":seed,"seat":seat}
                    try:
                        purge(paths)
                        b=run_episode(base_main,opp_main,seed=seed,seat=seat,treatment=False)
                        purge(paths)
                        t=run_episode(base_main,opp_main,seed=seed,seat=seat,treatment=True)
                        p=parity(b,t)
                        if not p["ok"]:
                            raise RuntimeError(f"pretrigger parity failure {p}")
                        row={
                            **key,
                            "base_score":b["score"],"treatment_score":t["score"],
                            "score_delta":t["score"]-b["score"],
                            "base_margin":b["margin"],"treatment_margin":t["margin"],
                            "margin_delta":t["margin"]-b["margin"],
                            "base_rewards":b["rewards"],"treatment_rewards":t["rewards"],
                            "fire_count":len(t["fire_steps"]),"fire_steps":t["fire_steps"],
                            "changed_slots":t["changed_slots"],
                            "cleared_slots":t["cleared_slots"],
                            "clamped_slots":t["clamped_slots"],
                            "parity":p,
                        }
                        rows.append(row)
                        print("CQ1_V48_PAIR",json.dumps({
                            **key,"base_score":row["base_score"],
                            "treatment_score":row["treatment_score"],
                            "score_delta":row["score_delta"],
                            "margin_delta":row["margin_delta"],
                            "fire_count":row["fire_count"],
                        },sort_keys=True),flush=True)
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    bs=[float(r["base_score"]) for r in rows]
    ts=[float(r["treatment_score"]) for r in rows]
    md=[float(r["margin_delta"]) for r in rows]
    sd=[float(r["score_delta"]) for r in rows]
    mechanical_pass=not failures and len(rows)==len(SEEDS)*2 and all(r["parity"]["ok"] for r in rows)
    summary={
        "pairs":len(rows),
        "base_score_rate":statistics.mean(bs) if bs else None,
        "treatment_score_rate":statistics.mean(ts) if ts else None,
        "score_delta":statistics.mean(sd) if sd else None,
        "mean_margin_delta":statistics.mean(md) if md else None,
        "median_margin_delta":statistics.median(md) if md else None,
        "positive_score_pairs":sum(x>0 for x in sd),
        "negative_score_pairs":sum(x<0 for x in sd),
        "nonwin_to_win_flips":sum(r["base_score"]<1.0 and r["treatment_score"]==1.0 for r in rows),
        "win_to_nonwin_regressions":sum(r["base_score"]==1.0 and r["treatment_score"]<1.0 for r in rows),
        "mean_fire_count":statistics.mean(r["fire_count"] for r in rows) if rows else None,
        "total_changed_slots":sum(r["changed_slots"] for r in rows),
        "total_cleared_slots":sum(r["cleared_slots"] for r in rows),
        "total_clamped_slots":sum(r["clamped_slots"] for r in rows),
    }

    if mechanical_pass and summary["score_delta"] is not None and summary["score_delta"]>=0.125 and summary["nonwin_to_win_flips"]>=2 and summary["win_to_nonwin_regressions"]==0:
        decision="CQ1_V48_CAUSAL_WL_PASS"
    elif mechanical_pass and summary["score_delta"] is not None and summary["score_delta"]>0:
        decision="CQ1_V48_CAUSAL_WL_WEAK"
    elif mechanical_pass and summary["mean_margin_delta"] is not None and summary["mean_margin_delta"]>0:
        decision="CQ1_V48_CAUSAL_MARGIN_ONLY"
    elif mechanical_pass:
        decision="CQ1_V48_CAUSAL_FAIL"
    else:
        decision="CQ1_V48_CAUSAL_MECHANICS_INVALID"

    result={
        "schema":"kculture-cq1-v48-causal-v1",
        "engine":EXPECTED_ENGINE,
        "operator":{
            "id":"O-CQ1",
            "rule":"sequentially clamp each V47 SELL slot to remaining current own shed inventory; zero becomes []",
            "runtime_uses_v48_code":False,
        },
        "opponent":V48,"seeds":SEEDS,
        "mechanical_pass":mechanical_pass,
        "summary":summary,"decision":decision,
        "rows":rows,"failures":failures,"provenance":provenance,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CQ1_V48_CAUSAL_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mechanical_pass,
        "summary":summary,"failures":len(failures),"seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
