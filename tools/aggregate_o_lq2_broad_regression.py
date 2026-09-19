#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input-dir",required=True); ap.add_argument("--out",required=True); args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];failures=[]
    for s in shards: rows+=s.get("rows",[]); failures+=s.get("failures",[])
    mech=len(shards)==7 and len(rows)==56 and not failures and all(s.get("mechanical_pass") for s in shards)
    by={}
    for opp in sorted({r["opponent"] for r in rows}):
        xs=[r for r in rows if r["opponent"]==opp]
        by[opp]={"contexts":len(xs),"mean_score_delta":statistics.mean(r["score_delta"] for r in xs),"mean_margin_delta":statistics.mean(r["margin_delta"] for r in xs),"negative_score_contexts":sum(r["score_delta"]<0 for r in xs),"positive_score_contexts":sum(r["score_delta"]>0 for r in xs),"base_score_rate":statistics.mean(r["base_score"] for r in xs),"treatment_score_rate":statistics.mean(r["treatment_score"] for r in xs)}
    overall={"contexts":len(rows),"mean_score_delta":statistics.mean(r["score_delta"] for r in rows) if rows else None,"mean_margin_delta":statistics.mean(r["margin_delta"] for r in rows) if rows else None,"negative_score_contexts":sum(r["score_delta"]<0 for r in rows),"positive_score_contexts":sum(r["score_delta"]>0 for r in rows)}
    v48=by.get("v48",{})
    if mech and v48.get("mean_score_delta",0)>=0.5 and overall["mean_score_delta"]>0 and overall["negative_score_contexts"]==0 and all(x["mean_score_delta"]>=0 for x in by.values()) and overall["mean_margin_delta"]>0:
        decision="O_LQ2_BROAD_SAFE_PASS"
    elif mech and v48.get("mean_score_delta",0)>0 and overall["mean_score_delta"]>0:
        decision="O_LQ2_BROAD_ROUTER_REQUIRED"
    elif mech:
        decision="O_LQ2_BROAD_FAIL"
    else:
        decision="O_LQ2_BROAD_MECHANICS_INVALID"
    result={"schema":"kculture-o-lq2-broad-regression-v1","mechanical_pass":mech,"decision":decision,"overall":overall,"by_opponent":by,"rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("O_LQ2_BROAD_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"overall":overall,"by_opponent":by,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
