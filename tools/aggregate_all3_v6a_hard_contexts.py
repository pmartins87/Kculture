#!/usr/bin/env python3
"""Aggregate V6A and deterministically freeze up to 12 fresh ALL3 hard contexts."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

OPPS=("v47_mirror","ready_stock","v48","router_2715","conditional_memory","tactical_memory","best_market")

def severity_key(r):
    # losses first, then ties; closest absolute margin first.
    cls=0 if float(r["score"])==0 else 1
    return (cls,abs(float(r["margin"])),str(r["opponent"]),int(r["seed"]),int(r["seat"]))

def select_diverse(nonwins,limit=12):
    buckets={o:sorted([r for r in nonwins if r["opponent"]==o],key=severity_key) for o in OPPS}
    chosen=[]
    # One from each producing family first.
    for o in OPPS:
        if buckets[o] and len(chosen)<limit:
            chosen.append(buckets[o].pop(0))
    # Then deterministic round-robin by current best severity.
    while len(chosen)<limit:
        heads=[b[0] for b in buckets.values() if b]
        if not heads: break
        nxt=min(heads,key=severity_key)
        chosen.append(nxt)
        buckets[nxt["opponent"]].pop(0)
    return chosen

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[]
    for s in shards: rows+=s.get("rows",[]);failures+=s.get("failures",[])
    mech=len(shards)==7 and len(rows)==112 and not failures and all(s.get("mechanical_pass") for s in shards)
    nonwins=[r for r in rows if float(r["score"])<1.0]
    closewins=sorted([r for r in rows if float(r["score"])==1.0 and float(r["margin"])<=500],key=lambda r:(float(r["margin"]),r["opponent"],r["seed"],r["seat"]))
    selected=select_diverse(nonwins,12) if mech else []
    by={}
    for o in OPPS:
        xs=[r for r in rows if r["opponent"]==o]
        by[o]={
          "contexts":len(xs),"wins":sum(float(r["score"])==1 for r in xs),
          "ties":sum(float(r["score"])==0.5 for r in xs),
          "losses":sum(float(r["score"])==0 for r in xs),
          "mean_margin":statistics.fmean(float(r["margin"]) for r in xs) if xs else None,
          "min_margin":min((float(r["margin"]) for r in xs),default=None),
        }
    if not mech: decision="V6A_MECHANICS_INVALID"
    elif len(nonwins)>=4: decision="V6A_HARD_CONTEXTS_READY"
    else: decision="V6A_EXPAND_HARD_CENSUS"
    result={
      "schema":"kculture-all3-v6a-hard-context-census-v1",
      "mechanical_pass":mech,"decision":decision,"contexts":len(rows),
      "nonwin_count":len(nonwins),"selected_count":len(selected),
      "selected_hard_contexts":selected,"all_nonwins":sorted(nonwins,key=severity_key),
      "close_wins_diagnostic":closewins[:20],"by_opponent":by,
      "failures":failures,"automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V6A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"nonwin_count":len(nonwins),
      "selected_count":len(selected),"selected_hard_contexts":selected,"by_opponent":by,
      "failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__":main()
