#!/usr/bin/env python3
"""Combine V6A Batch A aggregate with fresh Batch B shards."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

OPPS=("v47_mirror","ready_stock","v48","router_2715","conditional_memory","tactical_memory","best_market")

def severity_key(r):
    cls=0 if float(r["score"])==0 else 1
    return (cls,abs(float(r["margin"])),str(r["opponent"]),int(r["seed"]),int(r["seat"]))

def select_diverse(nonwins,limit=12):
    buckets={o:sorted([r for r in nonwins if r["opponent"]==o],key=severity_key) for o in OPPS}
    chosen=[]
    for o in OPPS:
        if buckets[o] and len(chosen)<limit:
            chosen.append(buckets[o].pop(0))
    while len(chosen)<limit:
        heads=[b[0] for b in buckets.values() if b]
        if not heads: break
        nxt=min(heads,key=severity_key)
        chosen.append(nxt);buckets[nxt["opponent"]].pop(0)
    return chosen

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prior",required=True)
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    prior=json.loads(Path(args.prior).read_text())
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[]
    for s in shards: rows+=s.get("rows",[]);failures+=s.get("failures",[])
    mech=len(shards)==7 and len(rows)==112 and not failures and all(s.get("mechanical_pass") for s in shards)
    batch_nonwins=[r for r in rows if float(r["score"])<1.0]
    all_nonwins=list(prior.get("all_nonwins") or [])+batch_nonwins
    selected=select_diverse(all_nonwins,12) if mech else []

    by={}
    prior_by=prior.get("by_opponent") or {}
    for o in OPPS:
        xs=[r for r in rows if r["opponent"]==o]
        pb=prior_by.get(o,{})
        by[o]={
          "contexts":int(pb.get("contexts",0))+len(xs),
          "wins":int(pb.get("wins",0))+sum(float(r["score"])==1 for r in xs),
          "ties":int(pb.get("ties",0))+sum(float(r["score"])==0.5 for r in xs),
          "losses":int(pb.get("losses",0))+sum(float(r["score"])==0 for r in xs),
          "batch_b_mean_margin":statistics.fmean(float(r["margin"]) for r in xs) if xs else None,
          "batch_b_min_margin":min((float(r["margin"]) for r in xs),default=None),
        }
    if not mech:
        decision="V6A_BATCH_B_MECHANICS_INVALID"
    elif len(all_nonwins)>=4:
        decision="V6A_HARD_CONTEXTS_READY"
    else:
        decision="V6A_STILL_SPARSE_RECONSIDER"

    result={
      "schema":"kculture-all3-v6a-hard-context-combined-ab-v1",
      "mechanical_pass":mech,"decision":decision,
      "batch_a_contexts":int(prior.get("contexts",112)),
      "batch_b_contexts":len(rows),
      "combined_contexts":int(prior.get("contexts",112))+len(rows),
      "batch_a_nonwins":len(prior.get("all_nonwins") or []),
      "batch_b_nonwins":len(batch_nonwins),
      "nonwin_count":len(all_nonwins),
      "selected_count":len(selected),
      "selected_hard_contexts":selected,
      "all_nonwins":sorted(all_nonwins,key=severity_key),
      "by_opponent":by,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V6AB_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,
      "batch_b_nonwins":len(batch_nonwins),"nonwin_count":len(all_nonwins),
      "selected_count":len(selected),"selected_hard_contexts":selected,
      "by_opponent":by,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__":main()
