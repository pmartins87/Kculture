"""Analyze exact Kaggriculture hosted replay JSONs for where/why our agent lost.

This tool is intentionally descriptive. It produces phase-level facts and
candidate failure modes; it does not claim causality without a counterfactual.
Replay alignment: action chosen at state t is stored on frame t+1.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import statistics
from pathlib import Path

PHASES = ((0,95),(96,191),(192,287),(288,383),(384,479),(480,575),(576,647),(648,695),(696,718))
MOVES = {"NORTH","SOUTH","EAST","WEST"}
PRODUCTIVE = {"DIG","PLANT","WATER","FERTILIZE","HARVEST","DROP","PICKUP","FEED","CARE","COLLECT_FERTILIZER","PLACE_ANIMAL"}
SELLABLE = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")


def num(d, key):
    try:
        v=float((d or {}).get(key,0) or 0)
        return v if math.isfinite(v) else 0.0
    except Exception:
        return 0.0


def tile_stats(farm):
    c=collections.Counter()
    yield_units=0.0
    for row in (farm or {}).get("tiles",[]) or []:
        if not isinstance(row,list): continue
        for tile in row:
            if not isinstance(tile,dict): continue
            if tile.get("kind")=="PLANT": c[f"crop_{tile.get('crop')}"]+=1
            if tile.get("animal"): c[f"animal_{tile.get('animal')}"]+=1
            if tile.get("kind")=="WEED": c["weeds"]+=1
            try: yield_units += max(0.0,float(tile.get("yield_units",0) or 0))
            except Exception: pass
    c["yield_units"]=yield_units
    return dict(c)


def private_stock(obs):
    priv=obs.get("private") or {}
    shed=priv.get("shed") or {}
    invs=priv.get("inventories") or []
    shed_total=sum(max(0,num(shed,k)) for k in shed)
    carried=0.0
    for inv in invs:
        if isinstance(inv,dict): carried += sum(max(0,num(inv,k)) for k in inv)
    return {"shed_total":shed_total,"carried_total":carried,"shed":dict(shed)}


def action_stats(steps,p,a,b):
    unit=collections.Counter(); market=collections.Counter(); qty=collections.Counter()
    for t in range(a,min(b+1,len(steps)-1)):
        frame=steps[t+1][p] if isinstance(steps[t+1],list) and p < len(steps[t+1]) else {}
        ac=frame.get("action") if isinstance(frame,dict) else None
        if not isinstance(ac,dict): continue
        ops=[ac.get("farmer")]+list(ac.get("hands") or [])
        for op in ops:
            if isinstance(op,list) and op:
                unit[str(op[0])]+=1
        for order in ac.get("market",[]) or []:
            if not (isinstance(order,list) and order): continue
            typ=str(order[0]); item=str(order[1]) if len(order)>1 else "?"
            market[typ]+=1
            if len(order)>=3:
                try: qty[f"{typ}:{item}"] += max(0,int(order[2] or 0))
                except Exception: pass
    total=sum(unit.values())
    return {
        "unit":dict(unit),
        "market_orders":dict(market),
        "market_qty":dict(qty),
        "unit_slots":total,
        "pass":unit.get("PASS",0),
        "movement":sum(unit.get(x,0) for x in MOVES),
        "productive":sum(unit.get(x,0) for x in PRODUCTIVE),
        "nonpass_fraction":((total-unit.get("PASS",0))/total if total else None),
    }


def checkpoint(steps,p,t):
    if t >= len(steps): return None
    frame=steps[t][p]; obs=frame.get("observation") or {}
    farms=obs.get("farms") or []
    if p >= len(farms): return None
    farm=farms[p]
    ts=tile_stats(farm)
    ps=private_stock(obs)
    return {
        "money":num(farm,"money"),
        "hands":len(farm.get("hands",[]) or []),
        "quads":len(farm.get("unlocked_quadrants",[]) or []),
        "yield_units":ts.get("yield_units",0),
        "weeds":ts.get("weeds",0),
        "crops":{k[5:]:v for k,v in ts.items() if k.startswith("crop_")},
        "animals":{k[7:]:v for k,v in ts.items() if k.startswith("animal_")},
        **ps,
    }


def team_names(rep):
    info=rep.get("info") or {}
    names=info.get("TeamNames") or info.get("teamNames") or []
    return list(names) if isinstance(names,list) else []


def detect_player(rep,team_substring,explicit):
    if explicit is not None: return explicit
    if team_substring:
        hits=[]
        for i,n in enumerate(team_names(rep)):
            if team_substring.lower() in str(n).lower(): hits.append(i)
        if len(hits)==1: return hits[0]
    raise ValueError("cannot identify our player; pass --player 0/1 or --team-substring")


def sustained_deficit(steps,p,threshold=5000.0,window=24):
    opp=1-p
    gaps=[]
    for t in range(len(steps)):
        try:
            obs=steps[t][p].get("observation") or {}; farms=obs.get("farms") or []
            gaps.append(num(farms[p],"money")-num(farms[opp],"money"))
        except Exception: gaps.append(0.0)
    for t in range(0,max(0,len(gaps)-window+1)):
        if all(g <= -threshold for g in gaps[t:t+window]): return t
    return None


def analyze_replay(rep,p,source):
    steps=rep.get("steps") or []; opp=1-p
    if len(steps)<2: raise ValueError("replay has no usable steps")
    final=steps[-1]
    rewards=[]
    for i in (0,1):
        try: rewards.append(float(final[i].get("reward")))
        except Exception: rewards.append(None)
    result="unknown"
    if all(isinstance(x,(int,float)) for x in rewards):
        result="win" if rewards[p]>rewards[opp] else "loss" if rewards[p]<rewards[opp] else "tie"
    phases={}
    for a,b in PHASES:
        ours=action_stats(steps,p,a,b); theirs=action_stats(steps,opp,a,b)
        phases[f"{a}_{b}"]={"ours":ours,"opponent":theirs,"pass_gap_ours_minus_opp":ours["pass"]-theirs["pass"],"productive_gap_ours_minus_opp":ours["productive"]-theirs["productive"]}
    cps={}
    for t in (0,96,192,288,384,480,576,648,696,len(steps)-1):
        co=checkpoint(steps,p,t); cx=checkpoint(steps,opp,t)
        cps[str(t)]={"ours":co,"opponent":cx,"money_gap":(co["money"]-cx["money"] if co and cx else None)}
    end_o=checkpoint(steps,p,len(steps)-1); end_x=checkpoint(steps,opp,len(steps)-1)
    flags=[]
    mid_pass=sum(phases[k]["pass_gap_ours_minus_opp"] for k in ("96_191","192_287"))
    if mid_pass >= 40: flags.append({"type":"midgame_idle_gap","evidence":mid_pass})
    if end_o:
        terminal_leak=float(end_o.get("shed_total",0))+float(end_o.get("carried_total",0))+float(end_o.get("yield_units",0))
        if terminal_leak >= 10: flags.append({"type":"terminal_unmonetized_resources","evidence_units":terminal_leak})
    first=sustained_deficit(steps,p)
    if first is not None: flags.append({"type":"first_sustained_money_deficit_5000","step":first})
    return {
        "source":source,"our_player":p,"team_names":team_names(rep),"step_count":len(steps),
        "result":result,"rewards":rewards,"money_delta":(rewards[p]-rewards[opp] if all(isinstance(x,(int,float)) for x in rewards) else None),
        "first_sustained_deficit_step":first,"checkpoints":cps,"phases":phases,"failure_flags":flags,
        "note":"Flags are diagnostics, not causal proof; promote a fix only after same-seed counterfactual testing."
    }


def aggregate(rows):
    losses=[r for r in rows if r["result"]=="loss"]
    wins=[r for r in rows if r["result"]=="win"]
    def mean(xs): return statistics.mean(xs) if xs else None
    flags=collections.Counter(f["type"] for r in losses for f in r["failure_flags"])
    phase_summary={}
    for a,b in PHASES:
        k=f"{a}_{b}"
        phase_summary[k]={
            "loss_mean_pass_gap":mean([r["phases"][k]["pass_gap_ours_minus_opp"] for r in losses]),
            "win_mean_pass_gap":mean([r["phases"][k]["pass_gap_ours_minus_opp"] for r in wins]),
            "loss_mean_productive_gap":mean([r["phases"][k]["productive_gap_ours_minus_opp"] for r in losses]),
            "win_mean_productive_gap":mean([r["phases"][k]["productive_gap_ours_minus_opp"] for r in wins]),
        }
    return {
        "games":len(rows),"wins":len(wins),"losses":len(losses),"ties":sum(r["result"]=="tie" for r in rows),
        "mean_money_delta":mean([r["money_delta"] for r in rows if isinstance(r.get("money_delta"),(int,float))]),
        "loss_flag_counts":dict(flags),"phase_win_loss_contrast":phase_summary,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("replays",nargs="+")
    ap.add_argument("--player",type=int,choices=(0,1),default=None)
    ap.add_argument("--team-substring",default=None)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    rows=[]
    for name in args.replays:
        path=Path(name); rep=json.loads(path.read_text(encoding="utf-8"))
        p=detect_player(rep,args.team_substring,args.player)
        rows.append(analyze_replay(rep,p,str(path)))
    payload={"schema_version":"hosted-loss-forensics-v1","aggregate":aggregate(rows),"games":rows}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(payload["aggregate"],indent=2,sort_keys=True))

if __name__=="__main__": main()
