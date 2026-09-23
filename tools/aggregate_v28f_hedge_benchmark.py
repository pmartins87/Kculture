#!/usr/bin/env python3
"""Aggregate V28F and apply frozen ALL3-centered hedge selector."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

SEEDS=(80401,80402,80403,80404,80405,80406)
SEATS=(0,1)
CANDIDATES=("ALL3","V47","ORW1","CR053","CR029")
HEDGES=("V47","ORW1","CR053","CR029")

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
    ap.add_argument("--candidate-prep",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    snap=json.loads(Path(a.snapshot_result).read_text())
    prep=json.loads(Path(a.candidate_prep).read_text())
    if snap.get("decision")!="V28B_FRONTIER_SNAPSHOT_READY" or not snap.get("mechanical_pass"):
        raise SystemExit("frontier snapshot not ready")
    if not prep.get("mechanical_pass"):
        raise SystemExit("hedge candidate prep not ready")
    selected=list(snap["selected_representatives"])
    expected={(str(s["main_sha256"]),seed,seat,c) for s in selected for seed in SEEDS for seat in SEATS for c in CANDIDATES}

    docs=[]
    for p in sorted(Path(a.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v28f-hedge-benchmark-shard-v1": docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    actual={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"]),str(r["candidate"])) for r in rows}
    mech=(len(docs)==4 and all(bool(d.get("mechanical_pass")) for d in docs)
          and all(bool(d.get("immutable_snapshot_used")) and not bool(d.get("live_kaggle_reacquisition_used")) for d in docs)
          and not failures and len(rows)==len(expected) and actual==expected)

    by={}
    for c in CANDIDATES:
        rr=[r for r in rows if r["candidate"]==c]
        s=summary(rr)
        source_rates={sha:summary([r for r in rr if r["main_sha256"]==sha])["score_rate"] for sha in sorted({r["main_sha256"] for r in rr})}
        seed_rates={str(seed):summary([r for r in rr if int(r["seed"])==seed])["score_rate"] for seed in SEEDS}
        s["source_score_rates"]=source_rates
        s["sources_at_or_above_half"]=sum(v>=.5 for v in source_rates.values())
        s["seed_score_rates"]=seed_rates
        s["seeds_at_or_above_half"]=sum(v>=.5 for v in seed_rates.values())
        by[c]=s

    details={}
    winner=None; material=False
    if mech:
        ctx={(r["main_sha256"],int(r["seed"]),int(r["seat"]),r["candidate"]):r for r in rows}
        for h in HEDGES:
            conv=[]; loss_conv=0; tie_conv=0
            pair_scores=[]; source_set=set(); seed_set=set()
            for src in selected:
                sha=str(src["main_sha256"])
                for seed in SEEDS:
                    for seat in SEATS:
                        p=ctx[(sha,seed,seat,"ALL3")]; q=ctx[(sha,seed,seat,h)]
                        ps=float(p["score"]); hs=float(q["score"])
                        pair_scores.append(max(ps,hs))
                        if ps<1.0 and hs==1.0:
                            conv.append((sha,seed,seat))
                            source_set.add(sha); seed_set.add(seed)
                            if ps==0.0: loss_conv+=1
                            elif ps==0.5: tie_conv+=1
            details[h]={
              "primary_nonwin_to_hedge_win":len(conv),
              "primary_loss_to_hedge_win":loss_conv,
              "primary_tie_to_hedge_win":tie_conv,
              "source_complement_breadth":len(source_set),
              "seed_complement_breadth":len(seed_set),
              "best_of_two_pair_score_rate":statistics.fmean(pair_scores),
              "pair_score_rate_delta_vs_all3":statistics.fmean(pair_scores)-float(by["ALL3"]["score_rate"]),
              "standalone_score_rate":float(by[h]["score_rate"]),
              "standalone_mean_margin":float(by[h]["mean_margin"]),
            }
        ranked=sorted(HEDGES,key=lambda h:(
          -details[h]["best_of_two_pair_score_rate"],
          -details[h]["source_complement_breadth"],
          -details[h]["primary_loss_to_hedge_win"],
          -details[h]["standalone_score_rate"],
          -details[h]["standalone_mean_margin"],
          h,
        ))
        winner=ranked[0]
        if winner!="V47":
            material=(details[winner]["primary_nonwin_to_hedge_win"] >= details["V47"]["primary_nonwin_to_hedge_win"]+3
                      and details[winner]["source_complement_breadth"] >= details["V47"]["source_complement_breadth"])

    if not mech: decision="V28F_MECHANICS_INVALID"
    elif winner=="V47": decision="V28F_KEEP_V47_HEDGE_READY"
    elif material: decision="V28F_ALTERNATE_HEDGE_RECOMMENDATION_READY"
    else: decision="V28F_NO_MATERIAL_HEDGE_REPLACEMENT"

    out={
      "schema":"kculture-v28f-all3-hedge-complementarity-v1",
      "mechanical_pass":mech,"decision":decision,
      "primary_candidate":"ALL3","hedge_candidates":list(HEDGES),
      "selected_sources":len(selected),"contexts_per_candidate":len(selected)*len(SEEDS)*len(SEATS),
      "candidates":by,"hedge_detail":details,"selector_winner":winner,
      "material_replacement_gate_pass":material,
      "current_active_pair":["ALL3","V47"],
      "recommended_pair":["ALL3",winner] if mech else None,
      "failures":failures,"rows":rows,"automatic_kaggle_submission":False,
    }
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28F_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"selector_winner":winner,
      "all3":{k:by.get("ALL3",{}).get(k) for k in ("score_rate","wins","ties","losses","mean_margin")},
      "hedge_detail":details,
      "standalone":{h:{k:by.get(h,{}).get(k) for k in ("score_rate","wins","ties","losses","mean_margin")} for h in HEDGES},
      "material_replacement_gate_pass":material,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
