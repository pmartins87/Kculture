#!/usr/bin/env python3
"""O-CQ1 parity audit: can a first-party inventory clamp reproduce V48 queue clearing?

Candidate rule, using only legal own current state:
- preserve exact V47 farmer/hands and every non-SELL market slot;
- for SELL(product, qty), cap qty to currently available own shed inventory remaining
  after earlier SELL slots of the same product;
- replace a zero-available SELL slot with [] so market slot structure is preserved.

This is an observational mechanism audit only; it does not promote the option.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    action_key,call_agent,canonical_action,plain,
)

EXPECTED_ENGINE="1.32.7"
BASE={
    "key":"v47","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
    "key":"v48","handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS=list(range(73101,73105))


def getv(obj:Any,key:str,default=None):
    if isinstance(obj,dict):
        return obj.get(key,default)
    try:
        return obj[key]
    except Exception:
        return getattr(obj,key,default)


def as_int(x,default=0):
    try:
        return int(x)
    except Exception:
        return default


def own_shed(obs:Any)->dict[str,int]:
    p=plain(obs)
    private=getv(p,"private",{}) or {}
    shed=getv(private,"shed",{}) or {}
    out={}
    if hasattr(shed,"items"):
        for k,v in shed.items():
            out[str(k)]=max(0,as_int(v,0))
    return out


def cq1_action(obs:Any,base_action:dict)->dict:
    a=canonical_action(base_action)
    remaining=own_shed(obs)
    market=[]
    for raw in list(a["market"] or []):
        order=copy.deepcopy(list(raw))
        if len(order)>=3 and str(order[0])=="SELL":
            product=str(order[1])
            qty=max(0,as_int(order[2],0))
            avail=max(0,as_int(remaining.get(product,0),0))
            take=min(qty,avail)
            remaining[product]=max(0,avail-take)
            if take<=0:
                market.append([])
            else:
                order[2]=take
                market.append(order)
        else:
            market.append(order)
    return {
        "farmer":copy.deepcopy(a["farmer"]),
        "hands":copy.deepcopy(a["hands"]),
        "market":market,
    }


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


class AuditWrapper:
    def __init__(self,base_main,v48_main):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.rows=[]

    def __call__(self,obs,config=None):
        step=int(getv(plain(obs),"step",len(self.rows)))
        b=canonical_action(call_agent(self.base,obs,config))
        v=canonical_action(call_agent(self.v48,obs,config))
        c=cq1_action(obs,b)
        same_physical=(b["farmer"]==v["farmer"] and b["hands"]==v["hands"])
        base_key=action_key(b)
        v_key=action_key(v)
        c_key=action_key(c)
        self.rows.append({
            "step":step,
            "same_physical":same_physical,
            "v48_diff":v_key!=base_key,
            "cq1_diff":c_key!=base_key,
            "cq1_exact_v48":c_key==v_key,
            "base_key":base_key,
            "v48_key":v_key,
            "cq1_key":c_key,
            "shed":own_shed(obs),
        })
        return b


def finish(env):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards):
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards}")
    return {"statuses":statuses,"rewards":rewards,"steps":len(p.get("steps") or [])}


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k)
        purge_package_modules(p.parent)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/cq1-parity-audit/CQ1_PARITY_AUDIT.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    out_path=Path(args.out); out_path.parent.mkdir(parents=True,exist_ok=True)
    episodes=[]; failures=[]; provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="cq1-parity-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]
            for seed in SEEDS:
                for seat in (0,1):
                    key={"seed":seed,"seat":seat}
                    try:
                        purge(paths)
                        cand=AuditWrapper(base_main,v48_main)
                        opp=load_public_agent(v48_main)
                        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
                        if seat==0: env.run([cand,opp])
                        else: env.run([opp,cand])
                        fin=finish(env)
                        episodes.append({**key,"episode":fin,"rows":cand.rows})
                    except Exception as exc:
                        failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    rows=[x for e in episodes for x in e["rows"] if x["same_physical"]]
    vdiff=[x for x in rows if x["v48_diff"]]
    cdiff=[x for x in rows if x["cq1_diff"]]
    exact=[x for x in rows if x["v48_diff"] and x["cq1_diff"] and x["cq1_exact_v48"]]
    false_pos=[x for x in rows if x["cq1_diff"] and not x["v48_diff"]]
    misses=[x for x in rows if x["v48_diff"] and not x["cq1_diff"]]
    mismatched=[x for x in rows if x["v48_diff"] and x["cq1_diff"] and not x["cq1_exact_v48"]]

    precision=(len(exact)/len(cdiff)) if cdiff else None
    recall=(len(exact)/len(vdiff)) if vdiff else None
    step_exact=Counter(x["step"] for x in exact)
    step_miss=Counter(x["step"] for x in misses)
    step_mismatch=Counter(x["step"] for x in mismatched)

    mechanical_pass=not failures and len(episodes)==len(SEEDS)*2
    if mechanical_pass and precision is not None and recall is not None and precision>=0.85 and recall>=0.85:
        decision="CQ1_PARITY_PASS"
    elif mechanical_pass and precision is not None and recall is not None and precision>=0.60 and recall>=0.60:
        decision="CQ1_PARITY_PARTIAL_REFINE"
    elif mechanical_pass:
        decision="CQ1_PARITY_FAIL"
    else:
        decision="CQ1_PARITY_MECHANICS_INVALID"

    result={
        "schema":"kculture-cq1-parity-audit-v1",
        "engine":EXPECTED_ENGINE,
        "candidate":{
            "id":"O-CQ1",
            "rule":"sequentially clamp each V47 SELL slot to remaining current own shed inventory; zero becomes []",
            "runtime_inputs":["current V47 action","own private current shed"],
            "forbidden_inputs":["opponent identity","rating","EpisodeId","seed","future state","opponent private state"],
        },
        "seeds":SEEDS,
        "episodes":len(episodes),
        "mechanical_pass":mechanical_pass,
        "same_physical_rows":len(rows),
        "v48_market_divergence_rows":len(vdiff),
        "cq1_changed_rows":len(cdiff),
        "exact_v48_matches":len(exact),
        "false_positive_changes":len(false_pos),
        "missed_v48_changes":len(misses),
        "changed_but_not_exact":len(mismatched),
        "precision":precision,
        "recall":recall,
        "top_exact_steps":step_exact.most_common(25),
        "top_missed_steps":step_miss.most_common(25),
        "top_mismatch_steps":step_mismatch.most_common(25),
        "mismatch_examples":mismatched[:40],
        "miss_examples":misses[:40],
        "false_positive_examples":false_pos[:40],
        "failures":failures,
        "provenance":provenance,
        "decision":decision,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CQ1_PARITY_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mechanical_pass,
        "v48_market_divergence_rows":len(vdiff),"cq1_changed_rows":len(cdiff),
        "exact_v48_matches":len(exact),"false_positive_changes":len(false_pos),
        "missed_v48_changes":len(misses),"changed_but_not_exact":len(mismatched),
        "precision":precision,"recall":recall,"failures":len(failures),
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
