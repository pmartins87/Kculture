#!/usr/bin/env python3
"""O-CQ2 development parity matrix: projected same-turn queue sanitation.

Development only. Multiple compact first-party transforms are evaluated against
exact V48 action output on fresh development seeds. One configuration may be selected
here, but MUST be frozen and re-tested on separate validation seeds before any causal gate.

All candidate inputs are legal own current state + exact V47 current action.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import tempfile
import time
from collections import defaultdict
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
    "key":"v47",
    "handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
    "key":"v48",
    "handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS=list(range(73301,73305))
MODES=("slot_projected","compact_projected","shortage_merge_compact","shortage_merge_keep_slots")
MIN_STEPS=(0,216,240,252,264,288,312,336,360,384,408,432)
ANIMAL_STRUCTURES={"COW":"PASTURE","SHEEP":"PASTURE","GOOSE":"COOP"}


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


def acquire(spec,tmp):
    main,receipt=acquire_public_main(spec["handle"],tmp)
    observed=sha256_bytes(main.read_bytes())
    if observed!=spec["expected_main_sha256"]:
        raise RuntimeError(f"{spec['key']} identity mismatch: {observed}")
    return main,{"key":spec["key"],"handle":spec["handle"],"observed_main_sha256":observed,**receipt}


def shed_adjacent(pos,board_size):
    half=board_size//2
    return tuple(pos) in {
        (half-1,half-1),(half,half-1),(half-1,half),(half,half)
    }


def shed_total(shed):
    return sum(max(0,as_int(v,0)) for v in shed.values())


def projected_shed_after_physical(obs:Any,config:Any,base_action:dict)->dict[str,int]:
    """Exact projection for physical operations that can change shed this turn.

    Kaggriculture processes farmer then hands before market. Only DROP/PICKUP/PLACE
    can mutate shed directly. Other physical actions may mutate per-unit inventory but
    cannot then also DROP in the same turn because each unit gets one action.
    """
    p=plain(obs)
    player=as_int(getv(p,"player",0),0)
    farms=list(getv(p,"farms",[]) or [])
    if player<0 or player>=len(farms):
        raise RuntimeError(f"bad player index {player}")
    farm=copy.deepcopy(farms[player])
    private=copy.deepcopy(getv(p,"private",{}) or {})
    shed={str(k):max(0,as_int(v,0)) for k,v in dict(getv(private,"shed",{}) or {}).items()}
    inventories=[
        {str(k):max(0,as_int(v,0)) for k,v in dict(inv or {}).items()}
        for inv in list(getv(private,"inventories",[]) or [])
    ]
    actions=canonical_action(base_action)
    unit_actions=[actions["farmer"],*actions["hands"]]
    board_size=max(2,as_int(getv(config or {},"boardSize",len(farm.get("tiles") or [])),10))
    capacity=max(0,as_int(getv(config or {},"shedCapacity",100),100))
    farmer_pos=list(farm.get("farmer") or [])
    hand_pos=list(farm.get("hands") or [])

    while len(inventories)<len(unit_actions):
        inventories.append({})

    for idx,action in enumerate(unit_actions):
        if not isinstance(action,list) or not action:
            continue
        pos=farmer_pos if idx==0 else (hand_pos[idx-1] if idx-1<len(hand_pos) else None)
        if not pos or len(pos)<2:
            continue
        x,y=as_int(pos[0],-1),as_int(pos[1],-1)
        inv=inventories[idx]
        op=str(action[0])

        if op=="DROP":
            if not shed_adjacent((x,y),board_size):
                continue
            for item,n0 in list(inv.items()):
                n=max(0,as_int(n0,0))
                if n<=0:
                    continue
                room=max(0,capacity-shed_total(shed))
                take=min(n,room)
                if take>0:
                    shed[item]=shed.get(item,0)+take
                    inv[item]-=take
            continue

        if op=="PICKUP":
            if not shed_adjacent((x,y),board_size) or len(action)<2:
                continue
            item=str(action[1])
            n=as_int(action[2],1) if len(action)>=3 else 1
            n=min(max(0,n),max(0,shed.get(item,0)))
            if n>0:
                shed[item]=shed.get(item,0)-n
                inv[item]=inv.get(item,0)+n
            continue

        if op=="PLACE":
            if len(action)<2:
                continue
            item=str(action[1])
            # Animal placement on matching current tile consumes inventory and does not
            # deposit in shed.
            tile=None
            tiles=farm.get("tiles") or []
            if 0<=y<len(tiles) and 0<=x<len(tiles[y]):
                tile=tiles[y][x]
            if item in ANIMAL_STRUCTURES and isinstance(tile,dict) and (
                str(tile.get("kind"))==ANIMAL_STRUCTURES[item] and "animal" not in tile
            ):
                if inv.get(item,0)>0:
                    inv[item]-=1
                continue
            if not shed_adjacent((x,y),board_size):
                continue
            n=as_int(action[2],1) if len(action)>=3 else 1
            n=min(max(0,n),max(0,inv.get(item,0)))
            room=max(0,capacity-shed_total(shed))
            n=min(n,room)
            if n>0:
                inv[item]=inv.get(item,0)-n
                shed[item]=shed.get(item,0)+n
            continue

    return shed


def is_sell(order):
    return isinstance(order,list) and len(order)>=3 and str(order[0])=="SELL"


def apply_non_sell_inventory_effect(order,shed,capacity):
    """Inventory-only projection of earlier market slots.

    This intentionally ignores price/opponent effects; it only models that BUY_PRODUCT
    and BUY_ANIMAL can put requested units into shed before later slots, subject to cap.
    """
    if not isinstance(order,list) or not order:
        return
    op=str(order[0])
    if op not in ("BUY_PRODUCT","BUY_ANIMAL") or len(order)<2:
        return
    item=str(order[1])
    qty=max(0,as_int(order[2],1) if len(order)>=3 else 1)
    room=max(0,capacity-shed_total(shed))
    take=min(qty,room)
    if take>0:
        shed[item]=shed.get(item,0)+take


def sanitize_sell_run(run,shed,mode):
    """Return rewritten consecutive SELL run and consume projected sold inventory."""
    available={k:max(0,as_int(v,0)) for k,v in shed.items()}
    raw=[copy.deepcopy(x) for x in run]

    if mode in ("slot_projected","compact_projected"):
        rewritten=[]
        for order in raw:
            item=str(order[1]); qty=max(0,as_int(order[2],0))
            take=min(qty,max(0,available.get(item,0)))
            available[item]=max(0,available.get(item,0)-take)
            if take<=0:
                rewritten.append([])
            else:
                o=copy.deepcopy(order); o[2]=take; rewritten.append(o)

    elif mode in ("shortage_merge_compact","shortage_merge_keep_slots"):
        totals=defaultdict(int)
        for order in raw:
            totals[str(order[1])]+=max(0,as_int(order[2],0))
        first_seen=set()
        rewritten=[]
        for order in raw:
            item=str(order[1]); qty=max(0,as_int(order[2],0))
            avail=max(0,available.get(item,0))
            if totals[item]>avail:
                if item in first_seen:
                    rewritten.append([])
                    continue
                first_seen.add(item)
                take=min(totals[item],avail)
                available[item]=max(0,avail-take)
                if take<=0:
                    rewritten.append([])
                else:
                    o=copy.deepcopy(order); o[2]=take; rewritten.append(o)
            else:
                take=min(qty,avail)
                available[item]=max(0,avail-take)
                first_seen.add(item)
                if take<=0:
                    rewritten.append([])
                else:
                    o=copy.deepcopy(order); o[2]=take; rewritten.append(o)
    else:
        raise ValueError(mode)

    if mode in ("compact_projected","shortage_merge_compact"):
        nonempty=[x for x in rewritten if x]
        rewritten=nonempty+[[] for _ in range(len(run)-len(nonempty))]

    # Commit consumed inventory back to shed.
    for k,v in available.items():
        shed[k]=v
    return rewritten


def cq2_action(obs,config,base_action,mode,min_step,projected_shed=None):
    b=canonical_action(base_action)
    step=as_int(getv(plain(obs),"step",0),0)
    if step<min_step:
        return b

    shed=(
        copy.deepcopy(projected_shed)
        if projected_shed is not None
        else projected_shed_after_physical(obs,config,b)
    )
    capacity=max(0,as_int(getv(config or {},"shedCapacity",100),100))
    market=copy.deepcopy(b["market"])
    out=[]
    i=0
    while i<len(market):
        order=market[i]
        if is_sell(order):
            j=i
            run=[]
            while j<len(market) and is_sell(market[j]):
                run.append(market[j]); j+=1
            out.extend(sanitize_sell_run(run,shed,mode))
            i=j
            continue
        out.append(copy.deepcopy(order))
        apply_non_sell_inventory_effect(order,shed,capacity)
        i+=1

    return {
        "farmer":copy.deepcopy(b["farmer"]),
        "hands":copy.deepcopy(b["hands"]),
        "market":out,
    }


class MatrixWrapper:
    def __init__(self,base_main,v48_main):
        self.base=load_public_agent(base_main)
        self.v48=load_public_agent(v48_main)
        self.rows=[]

    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.base,obs,config))
        v=canonical_action(call_agent(self.v48,obs,config))
        self.rows.append({
            "obs":copy.deepcopy(plain(obs)),
            "config":copy.deepcopy(plain(config or {})),
            "base":b,
            "v48":v,
        })
        return b


def finish(env):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards) or steps<720:
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")


def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k)
        purge_package_modules(p.parent)


def metrics(rows,mode,min_step):
    vdiff=0; changed=0; exact=0; fp=0; mismatch=0; misses=0; full_exact=0
    step_fp=defaultdict(int); step_exact=defaultdict(int); step_mismatch=defaultdict(int)
    for r in rows:
        b=r["base"]; v=r["v48"]
        c=cq2_action(
            r["obs"],r["config"],b,mode,min_step,
            projected_shed=r.get("projected_shed"),
        )
        bk=action_key(b); vk=action_key(v); ck=action_key(c)
        vd=vk!=bk; cd=ck!=bk
        if ck==vk:
            full_exact+=1
        if vd: vdiff+=1
        if cd: changed+=1
        if vd and cd and ck==vk:
            exact+=1; step_exact[as_int(r["obs"].get("step",0))]+=1
        elif cd and not vd:
            fp+=1; step_fp[as_int(r["obs"].get("step",0))]+=1
        elif vd and not cd:
            misses+=1
        elif vd and cd and ck!=vk:
            mismatch+=1; step_mismatch[as_int(r["obs"].get("step",0))]+=1

    precision=(exact/changed) if changed else 0.0
    recall=(exact/vdiff) if vdiff else 0.0
    f1=(2*precision*recall/(precision+recall)) if precision+recall>0 else 0.0
    return {
        "mode":mode,"min_step":min_step,"rows":len(rows),
        "v48_divergences":vdiff,"candidate_changes":changed,
        "exact_divergence_matches":exact,"false_positive_changes":fp,
        "missed_v48_changes":misses,"changed_but_not_exact":mismatch,
        "precision":precision,"recall":recall,"f1":f1,
        "full_action_accuracy":full_exact/len(rows) if rows else 0.0,
        "top_false_positive_steps":sorted(step_fp.items(),key=lambda kv:(-kv[1],kv[0]))[:12],
        "top_exact_steps":sorted(step_exact.items(),key=lambda kv:(-kv[1],kv[0]))[:12],
        "top_mismatch_steps":sorted(step_mismatch.items(),key=lambda kv:(-kv[1],kv[0]))[:12],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/cq2-dev-matrix/CQ2_DEV_MATRIX.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    episode_rows=[]; failures=[]; provenance={}
    started=time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="cq2-dev-") as td:
            tmp=Path(td)
            base_main,provenance["base"]=acquire(BASE,tmp/"base")
            v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
            paths=[base_main,v48_main]
            for seed in SEEDS:
                for seat in (0,1):
                    try:
                        purge(paths)
                        cand=MatrixWrapper(base_main,v48_main)
                        opp=load_public_agent(v48_main)
                        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
                        if seat==0: env.run([cand,opp])
                        else: env.run([opp,cand])
                        finish(env)
                        episode_rows.extend(cand.rows)
                    except Exception as exc:
                        failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
                    finally:
                        purge(paths)
    except Exception as exc:
        failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    grid=[]
    if not failures:
        # Projection is deterministic from legal current state + exact V47 action.
        # Cache it once per decision; the 48 candidate configurations then differ
        # only in queue rewrite/activation semantics.
        for r in episode_rows:
            r["projected_shed"]=projected_shed_after_physical(
                r["obs"],r["config"],r["base"]
            )
        for mode in MODES:
            for min_step in MIN_STEPS:
                grid.append(metrics(episode_rows,mode,min_step))

    ranked=sorted(
        grid,
        key=lambda x:(x["f1"],x["precision"],x["recall"],x["full_action_accuracy"],-x["min_step"]),
        reverse=True,
    )
    best=ranked[0] if ranked else None
    # episodeSteps=720 records 720 states but the agent is called for 719 decisions
    # (steps 0..718). CQ1's clean audit independently observed exactly 719 calls/episode.
    expected_action_rows=len(SEEDS)*2*719
    mechanical_pass=not failures and len(episode_rows)==expected_action_rows

    if mechanical_pass and best and best["precision"]>=0.80 and best["recall"]>=0.80:
        decision="CQ2_DEV_STRONG_FREEZE_FOR_VALIDATION"
    elif mechanical_pass and best and best["precision"]>=0.60 and best["recall"]>=0.60:
        decision="CQ2_DEV_PROMISING_FREEZE_FOR_VALIDATION"
    elif mechanical_pass:
        decision="CQ2_DEV_WEAK_USE_V4A"
    else:
        decision="CQ2_DEV_MECHANICS_INVALID"

    result={
        "schema":"kculture-cq2-projected-queue-dev-matrix-v1",
        "engine":EXPECTED_ENGINE,
        "development_seeds":SEEDS,
        "modes":MODES,
        "min_steps":MIN_STEPS,
        "episodes":len(SEEDS)*2,
        "row_count":len(episode_rows),
        "expected_action_rows":expected_action_rows,
        "mechanical_pass":mechanical_pass,
        "best":best,
        "top10":ranked[:10],
        "grid":grid,
        "decision":decision,
        "failures":failures,
        "provenance":provenance,
        "seconds":time.perf_counter()-started,
        "development_only":True,
        "must_validate_on_new_seeds_before_causal":True,
        "automatic_kaggle_submission":False,
    }
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CQ2_DEV_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mechanical_pass,
        "best":best,"top3":ranked[:3],"failures":len(failures),
        "seconds":result["seconds"],
    },sort_keys=True),flush=True)
    if not mechanical_pass:
        raise SystemExit(2)


if __name__=="__main__":
    main()
