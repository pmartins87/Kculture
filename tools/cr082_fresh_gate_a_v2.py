"""CR082 fresh Gate A v2 — strictly forward temporal evidence only.

This tightens the evidence filter before any CR082 executable candidate exists.
The v1 collector called all EpisodeIds absent from old64 'new'; audit showed that 38
were older unseen episodes. v2 changes no model, features, k, p95, prefix or threshold.
It evaluates only EpisodeId > max(original old64), i.e. strictly later episodes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np

PRODUCTS=["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO","EGG","MILK","WOOL","FERTILIZER"]
SEEDS=["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO"]
ANIMALS=["COW","SHEEP","GOOSE"]
PREFIX=288
MIN_FRESH=24
DELTA_GATE=0.03


def action_key(a): return json.dumps(a,sort_keys=True,separators=(",",":"))
def semantic_signature(m):
    out=[]
    for o in m or []:
        if not o: continue
        op=o[0]
        out.append(op if op in ("HIRE","BUY_LAND") or len(o)<2 else f"{op}:{o[1]}")
    return tuple(out)


def features(obs,seat):
    farm=obs["farms"][seat];priv=obs["private"];market=obs["market"]
    shed=priv.get("shed") or {};seeds=priv.get("seeds") or {};prices=market.get("prices") or {};inventory=market.get("inventory") or {}
    vals=[obs.get("day",0),obs.get("hour",0),farm.get("money",0),len(farm.get("hands") or []),farm.get("hires_today",0),len(farm.get("unlocked_quadrants") or [])]
    vals += [shed.get(x,0) for x in PRODUCTS+ANIMALS]
    vals += [seeds.get(x,0) for x in SEEDS]
    vals += [prices.get(x,0) for x in PRODUCTS]
    vals += [inventory.get(x,0) for x in PRODUCTS]
    return np.asarray(vals,dtype=np.float64)


def load_rows(root:Path,team:str):
    rows=[]
    for p in root.rglob("episode-*-replay.json"):
        d=json.loads(p.read_text(encoding="utf-8"));teams=list(d.get("info",{}).get("TeamNames") or []);seats=[i for i,t in enumerate(teams) if t==team]
        if len(seats)!=1 or len(d.get("steps") or [])<PREFIX+1: continue
        seat=seats[0];ep=int(d.get("info",{}).get("EpisodeId") or p.name.split("-")[1]);samples=[]
        for t in range(PREFIX):
            samples.append((features(d["steps"][t][seat]["observation"],seat),d["steps"][t+1][seat]["action"].get("market") or []))
        rows.append((ep,samples))
    rows.sort(key=lambda x:x[0]);return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--old-root",type=Path,required=True);ap.add_argument("--fresh-root",type=Path,required=True);ap.add_argument("--team",default="Majkel1337");ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    old=load_rows(a.old_root,a.team)
    if len(old)<64: raise RuntimeError(f"expected original 64 Majkel episodes, got {len(old)}")
    old_ids={ep for ep,_ in old};old_max=max(old_ids);cut=int(len(old)*0.75);dev=old[:cut]
    fresh_all=load_rows(a.fresh_root,a.team)
    unseen=[r for r in fresh_all if r[0] not in old_ids]
    fresh=[r for r in fresh_all if r[0] > old_max]
    report={
        "schema_version":"cr082-fresh-gate-a-v2-strict-forward",
        "team":a.team,
        "old_episodes":len(old),
        "old_max_episode_id":old_max,
        "frozen_development_episodes":len(dev),
        "fresh_download_usable":len(fresh_all),
        "unseen_but_not_necessarily_forward":len(unseen),
        "strictly_forward_episodes":len(fresh),
        "strictly_forward_episode_range":[fresh[0][0],fresh[-1][0]] if fresh else None,
        "min_fresh_required":MIN_FRESH,
        "delta_gate":DELTA_GATE,
        "hypothesis_forming_old_holdout_reused_for_training":False,
        "v1_loose_filter_result_invalid_for_promotion":True,
        "filter_change_only_no_model_or_threshold_change":True,
    }
    if len(fresh)<MIN_FRESH:
        report.update({"pass":False,"pending":True,"decision":"PENDING_MORE_STRICTLY_FORWARD_MAJKEL_EPISODES"})
    else:
        counts=Counter();fallback=0;queries=0
        for t in range(PREFIX):
            train=[r[1][t] for r in dev]
            modal=json.loads(Counter(action_key(m) for _,m in train).most_common(1)[0][0])
            X=np.stack([x for x,_ in train]);mu=X.mean(axis=0);sd=X.std(axis=0);sd[sd<1e-9]=1.0;Xz=(X-mu)/sd
            dtrain=((Xz[:,None,:]-Xz[None,:,:])**2).sum(axis=2);np.fill_diagonal(dtrain,np.inf)
            threshold=float(np.quantile(np.sqrt(dtrain.min(axis=1)),0.95))
            Q=np.stack([r[1][t][0] for r in fresh]);Qz=(Q-mu)/sd
            d2=((Qz[:,None,:]-Xz[None,:,:])**2).sum(axis=2);idx=d2.argmin(axis=1);dist=np.sqrt(d2[np.arange(len(fresh)),idx])
            for row,j,dd in zip(fresh,idx,dist):
                actual=row[1][t][1];raw=train[int(j)][1];pred=raw if dd<=threshold else modal
                queries+=1;fallback+=int(dd>threshold)
                counts["modal_exact"]+=int(actual==modal);counts["modal_semantic"]+=int(semantic_signature(actual)==semantic_signature(modal))
                counts["knn_exact"]+=int(actual==pred);counts["knn_semantic"]+=int(semantic_signature(actual)==semantic_signature(pred))
        exact_delta=(counts["knn_exact"]-counts["modal_exact"])/queries
        semantic_delta=(counts["knn_semantic"]-counts["modal_semantic"])/queries
        checks={
            "strictly_forward_at_least_24":len(fresh)>=MIN_FRESH,
            "exact_delta_at_least_0_03":exact_delta>=DELTA_GATE,
            "semantic_delta_at_least_0_03":semantic_delta>=DELTA_GATE,
            "legal_current_features_only":True,
            "single_step_no_replay_continuation":True,
        }
        report.update({
            "pending":False,"queries":queries,"ood_fallback_rate":fallback/queries,
            "modal_exact":counts["modal_exact"]/queries,"knn_exact":counts["knn_exact"]/queries,"exact_delta":exact_delta,
            "modal_semantic":counts["modal_semantic"]/queries,"knn_semantic":counts["knn_semantic"]/queries,"semantic_delta":semantic_delta,
            "checks":checks,"pass":all(checks.values()),
            "decision":"ELIGIBLE_TO_BUILD_ONE_CR082_CANDIDATE" if all(checks.values()) else "CLOSE_CR082_1NN_MOVE_TO_EXPLICIT_ECONOMIC_VALUE_MODEL",
        })
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8");print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
