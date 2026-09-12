"""Exploratory, non-promotional CR082 state-signal measurement.

Measures whether same-step one-nearest-neighbor market imitation based only on legal
current economic state improves chronological holdout fidelity over a per-step modal
market baseline. Existing corpora are hypothesis-forming only; results from this tool
must not be used as CR082's fresh Gate A.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

PRODUCTS = ["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO","EGG","MILK","WOOL","FERTILIZER"]
SEEDS = ["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO"]
ANIMALS = ["COW","SHEEP","GOOSE"]
PREFIX = 288


def action_key(a):
    return json.dumps(a, sort_keys=True, separators=(",", ":"))


def semantic_signature(market):
    out=[]
    for o in market or []:
        if not o: continue
        op=o[0]
        out.append(op if op in ("HIRE","BUY_LAND") or len(o)<2 else f"{op}:{o[1]}")
    return tuple(out)


def features(obs, seat):
    farm=obs["farms"][seat]
    priv=obs["private"]
    market=obs["market"]
    shed=priv.get("shed") or {}
    seeds=priv.get("seeds") or {}
    prices=market.get("prices") or {}
    inventory=market.get("inventory") or {}
    vals=[
        obs.get("day",0), obs.get("hour",0), farm.get("money",0),
        len(farm.get("hands") or []), farm.get("hires_today",0),
        len(farm.get("unlocked_quadrants") or []),
    ]
    vals += [shed.get(x,0) for x in PRODUCTS+ANIMALS]
    vals += [seeds.get(x,0) for x in SEEDS]
    vals += [prices.get(x,0) for x in PRODUCTS]
    vals += [inventory.get(x,0) for x in PRODUCTS]
    return np.asarray(vals, dtype=np.float64)


def load_rows(root: Path, team: str):
    rows=[]
    for p in root.rglob("episode-*-replay.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        teams=list(d.get("info",{}).get("TeamNames") or [])
        seats=[i for i,t in enumerate(teams) if t==team]
        if len(seats)!=1 or len(d.get("steps") or [])<PREFIX+1:
            continue
        seat=seats[0]
        ep=int(d.get("info",{}).get("EpisodeId") or p.name.split("-")[1])
        samples=[]
        for t in range(PREFIX):
            obs=d["steps"][t][seat]["observation"]
            action=d["steps"][t+1][seat]["action"].get("market") or []
            samples.append((features(obs,seat),action))
        rows.append((ep,samples))
    rows.sort(key=lambda x:x[0])
    return rows


def evaluate(rows):
    cut=int(len(rows)*0.75)
    dev,hold=rows[:cut],rows[cut:]
    counts=Counter()
    per_step=[]
    for t in range(PREFIX):
        train=[r[1][t] for r in dev]
        hold_s=[r[1][t] for r in hold]
        modal=json.loads(Counter(action_key(a) for _,a in train).most_common(1)[0][0])
        X=np.stack([x for x,_ in train])
        mu=X.mean(axis=0)
        sd=X.std(axis=0)
        sd[sd<1e-9]=1.0
        Xz=(X-mu)/sd
        Q=np.stack([x for x,_ in hold_s])
        Qz=(Q-mu)/sd
        # tiny matrices: brute force is deterministic and dependency-light.
        d2=((Qz[:,None,:]-Xz[None,:,:])**2).sum(axis=2)
        idx=d2.argmin(axis=1)
        step_counts=Counter()
        for (_,actual),j in zip(hold_s,idx):
            pred=train[int(j)][1]
            step_counts["n"]+=1
            step_counts["modal_exact"]+=int(actual==modal)
            step_counts["modal_semantic"]+=int(semantic_signature(actual)==semantic_signature(modal))
            step_counts["knn_exact"]+=int(actual==pred)
            step_counts["knn_semantic"]+=int(semantic_signature(actual)==semantic_signature(pred))
        counts.update(step_counts)
        per_step.append(dict(step_counts))
    n=counts["n"]
    return {
        "episodes":len(rows), "development_episodes":len(dev), "holdout_episodes":len(hold),
        "episode_range":[rows[0][0],rows[-1][0]],
        "prefix_steps":PREFIX,
        "modal_exact":counts["modal_exact"]/n,
        "modal_semantic":counts["modal_semantic"]/n,
        "knn_exact":counts["knn_exact"]/n,
        "knn_semantic":counts["knn_semantic"]/n,
        "exact_delta":(counts["knn_exact"]-counts["modal_exact"])/n,
        "semantic_delta":(counts["knn_semantic"]-counts["modal_semantic"])/n,
        "hypothesis_forming_only":True,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,required=True)
    ap.add_argument("--team",required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    rows=load_rows(a.root,a.team)
    if len(rows)<16: raise RuntimeError(f"insufficient usable episodes: {len(rows)}")
    report={"team":a.team,**evaluate(rows)}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__": main()
