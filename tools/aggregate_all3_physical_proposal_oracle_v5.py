#!/usr/bin/env python3
"""Aggregate ALL3 Physical Proposal Oracle V5 screen."""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter
from pathlib import Path

OPPS=("v47_mirror","v48","router_2715","tactical_memory")

def summarize(rows):
    if not rows:return {}
    bs=[float(r["base"]["score"]) for r in rows];os=[float(r["oracle"]["score"]) for r in rows]
    md=[float(r["oracle"]["margin"]-r["base"]["margin"]) for r in rows]
    return {
      "branch_states":len(rows),"base_score_rate":statistics.fmean(bs),"oracle_score_rate":statistics.fmean(os),
      "score_delta":statistics.fmean(os)-statistics.fmean(bs),
      "mean_oracle_margin_delta":statistics.fmean(md),"median_oracle_margin_delta":statistics.median(md),
      "nonwin_to_win_flips":sum(r["base"]["score"]<1 and r["oracle"]["score"]==1 for r in rows),
      "loss_to_win_flips":sum(r["base"]["score"]==0 and r["oracle"]["score"]==1 for r in rows),
      "positive_margin_states":sum(x>0 for x in md),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[];matchups=[]
    for s in shards:
        rows+=s.get("rows",[]);failures+=s.get("failures",[]);matchups+=s.get("matchups",[])
    mech=len(shards)==4 and not failures and all(s.get("mechanical_pass") for s in shards) and len(rows)>=12
    overall=summarize(rows)
    by={o:summarize([r for r in rows if r["opponent"]==o]) for o in OPPS}
    positive=[o for o,v in by.items() if v and float(v.get("score_delta",0))>0]
    transforms=Counter()
    sources=Counter()
    for r in rows:
        o=r["oracle"]
        if o.get("label")!="BASE":
            key=json.dumps({"locus":o.get("locus"),"old":o.get("old_unit"),"new":o.get("new_unit")},sort_keys=True)
            transforms[key]+=1
            for s in o.get("sources",[]):sources[s]+=1

    flips=int(overall.get("nonwin_to_win_flips",0) or 0)
    if mech and flips>=2 and len(positive)>=2:
        decision="V5_PHYSICAL_DIVERSE_WL_HEADROOM_PASS"
    elif mech and (flips>=1 or len(positive)>=1):
        decision="V5_PHYSICAL_WL_HEADROOM_WEAK"
    elif mech and float(overall.get("mean_oracle_margin_delta",0) or 0)>0:
        decision="V5_PHYSICAL_MARGIN_ONLY"
    elif mech:
        decision="V5_PHYSICAL_NO_HEADROOM"
    else:
        decision="V5_PHYSICAL_MECHANICS_INVALID"

    result={
      "schema":"kculture-all3-physical-proposal-v5","mechanical_pass":mech,"decision":decision,
      "summary":overall,"by_opponent":by,"positive_opponents":positive,
      "oracle_transform_counts":dict(transforms),"oracle_source_counts":dict(sources),
      "rows":rows,"matchups":matchups,"failures":failures,
      "offline_oracle_only":True,"automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V5_PHYSICAL_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"summary":overall,"by_opponent":by,
      "positive_opponents":positive,"oracle_transform_counts":dict(transforms),
      "oracle_source_counts":dict(sources),"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
