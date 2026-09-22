#!/usr/bin/env python3
"""Aggregate V28B fresh final-slot benchmark and apply frozen pair selector."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

SEEDS=(80301,80302,80303,80304,80305,80306)
SEATS=(0,1)
CANDIDATES=("V47","ORW1","ALL3")

def summary(rows):
    if not rows:return {}
    return {
      "contexts":len(rows),
      "score_rate":statistics.fmean(float(r["score"]) for r in rows),
      "wins":sum(float(r["score"])==1.0 for r in rows),
      "ties":sum(float(r["score"])==0.5 for r in rows),
      "losses":sum(float(r["score"])==0.0 for r in rows),
      "mean_margin":statistics.fmean(float(r["margin"]) for r in rows),
      "median_margin":statistics.median(float(r["margin"]) for r in rows),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--snapshot-result",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    snap=json.loads(Path(a.snapshot_result).read_text())
    if snap.get("decision")!="V28B_FRONTIER_SNAPSHOT_READY" or not snap.get("mechanical_pass"):
        raise SystemExit("V28B snapshot not ready")
    selected=list(snap["selected_representatives"])
    expected={(str(s["main_sha256"]),seed,seat,c) for s in selected for seed in SEEDS for seat in SEATS for c in CANDIDATES}

    docs=[]
    for p in sorted(Path(a.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v28b-final-slot-benchmark-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    actual={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]),str(r["candidate"])) for r in rows}
    mech=(
      len(docs)==4
      and all(bool(d.get("mechanical_pass")) for d in docs)
      and all(bool(d.get("immutable_snapshot_used")) and not bool(d.get("live_kaggle_reacquisition_used")) for d in docs)
      and not failures and len(rows)==len(expected) and actual==expected
    )

    by_candidate={}
    for c in CANDIDATES:
        rr=[r for r in rows if r["candidate"]==c]
        s=summary(rr)
        source_rates={}
        for sha in sorted({r["main_sha256"] for r in rr}):
            source_rates[sha]=summary([r for r in rr if r["main_sha256"]==sha])["score_rate"]
        seed_rates={}
        for seed in SEEDS:
            seed_rates[str(seed)]=summary([r for r in rr if int(r["seed"])==seed])["score_rate"]
        s["source_score_rates"]=source_rates
        s["sources_at_or_above_half"]=sum(v>=0.5 for v in source_rates.values())
        s["seed_score_rates"]=seed_rates
        s["seeds_at_or_above_half"]=sum(v>=0.5 for v in seed_rates.values())
        by_candidate[c]=s

    pairwise={}
    for i,a1 in enumerate(CANDIDATES):
        for b1 in CANDIDATES[i+1:]:
            amap={(r["main_sha256"],int(r["seed"]),int(r["seat"])):r for r in rows if r["candidate"]==a1}
            bmap={(r["main_sha256"],int(r["seed"]),int(r["seat"])):r for r in rows if r["candidate"]==b1}
            keys=sorted(set(amap)&set(bmap))
            pairwise[f"{a1}_vs_{b1}"]={
              "contexts":len(keys),
              "a_better":sum(float(amap[k]["score"])>float(bmap[k]["score"]) for k in keys),
              "b_better":sum(float(amap[k]["score"])<float(bmap[k]["score"]) for k in keys),
              "score_rate_delta_a_minus_b":statistics.fmean(float(amap[k]["score"])-float(bmap[k]["score"]) for k in keys),
              "mean_margin_delta_a_minus_b":statistics.fmean(float(amap[k]["margin"])-float(bmap[k]["margin"]) for k in keys),
            }

    def primary_key(c):
        s=by_candidate[c]
        return (
          -float(s["score_rate"]),
          -int(s["sources_at_or_above_half"]),
          -int(s["seeds_at_or_above_half"]),
          -float(s["mean_margin"]),
          str(c),
        )

    primary=sorted(CANDIDATES,key=primary_key)[0] if mech else None

    hedge=None
    hedge_detail={}
    if mech:
        context={(r["main_sha256"],int(r["seed"]),int(r["seat"]),r["candidate"]):r for r in rows}
        nonprimary=[c for c in CANDIDATES if c!=primary]
        hrows=[]
        for c in nonprimary:
            complement=0
            for s in selected:
                sha=str(s["main_sha256"])
                for seed in SEEDS:
                    for seat in SEATS:
                        p=context[(sha,seed,seat,primary)]
                        h=context[(sha,seed,seat,c)]
                        if float(p["score"])<1.0 and float(h["score"])==1.0:
                            complement+=1
            s=by_candidate[c]
            hrows.append((c,complement,float(s["score_rate"]),int(s["sources_at_or_above_half"]),float(s["mean_margin"])))
            hedge_detail[c]={"primary_nonwin_to_hedge_win":complement}
        hrows.sort(key=lambda x:(-x[1],-x[2],-x[3],-x[4],x[0]))
        hedge=hrows[0][0]

    decision="V28B_FINAL_PAIR_RECOMMENDATION_READY" if mech else "V28B_MECHANICS_INVALID"

    result={
      "schema":"kculture-v28b-final-slot-benchmark-v1",
      "mechanical_pass":mech,"decision":decision,
      "selected_sources":len(selected),"contexts_per_candidate":len(selected)*len(SEEDS)*len(SEATS),
      "candidates":by_candidate,"pairwise":pairwise,
      "primary_candidate":primary,"hedge_candidate":hedge,"hedge_detail":hedge_detail,
      "current_active_pair":["ALL3","ORW1"],
      "recommended_pair":[primary,hedge] if mech else None,
      "rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V28B_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,
      "primary_candidate":primary,"hedge_candidate":hedge,
      "candidates":{k:{kk:v[kk] for kk in ("score_rate","wins","ties","losses","mean_margin","sources_at_or_above_half","seeds_at_or_above_half")} for k,v in by_candidate.items()},
      "hedge_detail":hedge_detail,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
