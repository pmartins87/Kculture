#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
PRIMARY_TOTAL=144
PRIMARY_SCORE_TOTAL=131.0

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v31a-second-slot-complementarity-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    hedge_meta={}
    for d in docs:
      for h in d.get("hedges",[]): hedge_meta[str(h["key"])]=h
    mechanics=(len(docs)==4 and len(hedge_meta)==12 and all(d.get("mechanical_pass") for d in docs) and not fails
               and all(int(d.get("primary_full_contexts",0))==144 and int(d.get("primary_residual_contexts",0))==13 for d in docs))
    summaries={}
    for key,h in hedge_meta.items():
        z=[r for r in rows if str(r["hedge_key"])==key]
        if len(z)!=13: mechanics=False
        wins=[r for r in z if float(r["hedge_score"])==1.0]
        ties=[r for r in z if float(r["hedge_score"])==0.5]
        losses=[r for r in z if float(r["hedge_score"])==0.0]
        rescue_score=sum(float(r["hedge_score"]) for r in z)
        pair_score=(PRIMARY_SCORE_TOTAL+rescue_score)/PRIMARY_TOTAL
        src=len({r["opponent_sha"] for r in wins});seed=len({int(r["seed"]) for r in wins});seats=sorted({int(r["seat"]) for r in wins})
        summaries[key]={
          **h,"residual_contexts":len(z),"rescue_wins":len(wins),"rescue_ties":len(ties),"residual_losses":len(losses),
          "pair_score_rate":pair_score,"pair_score_delta_vs_primary":pair_score-(PRIMARY_SCORE_TOTAL/PRIMARY_TOTAL),
          "rescue_source_breadth":src,"rescue_seed_breadth":seed,"rescue_seats":seats,
          "mean_residual_hedge_margin":statistics.fmean(float(r["hedge_margin"]) for r in z) if z else None
        }
    v47=summaries.get("V47")
    if v47 is None: mechanics=False
    eligible=[]
    if mechanics:
      for key,s in summaries.items():
        if key=="V47": continue
        ok=(s["pair_score_rate"]>=v47["pair_score_rate"]+0.03
            and s["rescue_wins"]>=v47["rescue_wins"]+3
            and s["rescue_source_breadth"]>=v47["rescue_source_breadth"]
            and s["rescue_seed_breadth"]>=v47["rescue_seed_breadth"]
            and s["rescue_seats"]==[0,1])
        s["material_replacement_eligible"]=bool(ok)
        if ok: eligible.append(s)
      v47["material_replacement_eligible"]=False

    selected=None
    if mechanics and eligible:
        eligible.sort(key=lambda s:(-s["pair_score_rate"],-s["rescue_wins"],-s["rescue_source_breadth"],-s["rescue_seed_breadth"],
                                    -s["mean_residual_hedge_margin"],s["rank"],s["sha"]))
        selected=eligible[0]
        decision="V31A_SECOND_SLOT_REPLACEMENT_CANDIDATE_READY"
    elif mechanics:
        decision="V31A_RETAIN_V47_SECOND_SLOT"
    else:
        decision="V31A_MECHANICS_INVALID"

    out={"schema":"kculture-v31a-second-slot-complementarity-v1","mechanical_pass":mechanics,"decision":decision,
         "primary_score_rate":PRIMARY_SCORE_TOTAL/PRIMARY_TOTAL,"primary_contexts":PRIMARY_TOTAL,"primary_residual_contexts":13,
         "v47":v47,"eligible_candidates":[s["key"] for s in eligible],"selected_candidate":selected,
         "summaries":summaries,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V31A_RESULT",json.dumps({k:v for k,v in out.items() if k not in ("summaries","failures")},sort_keys=True))
    if not mechanics: raise SystemExit(2)

if __name__=="__main__":main()
