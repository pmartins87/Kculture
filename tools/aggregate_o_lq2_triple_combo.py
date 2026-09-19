#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
VARIANTS=("base","old","lq2","all3")
def summarize(rows):
    out={"contexts":len(rows)}
    for v in VARIANTS:
        out[v]={"score_rate":statistics.mean(r[v]["score"] for r in rows),"mean_margin":statistics.mean(r[v]["margin"] for r in rows)}
    out["all3_vs_base"]=out["all3"]["score_rate"]-out["base"]["score_rate"]
    out["all3_vs_old"]=out["all3"]["score_rate"]-out["old"]["score_rate"]
    out["all3_vs_lq2"]=out["all3"]["score_rate"]-out["lq2"]["score_rate"]
    out["all3_negative_vs_base"]=sum(r["all3"]["score"]<r["base"]["score"] for r in rows)
    out["all3_positive_vs_base"]=sum(r["all3"]["score"]>r["base"]["score"] for r in rows)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    shards=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[];fails=[]
    for s in shards: rows+=s.get("rows",[]);fails+=s.get("failures",[])
    mech=len(shards)==7 and len(rows)==56 and not fails and all(s.get("mechanical_pass") for s in shards)
    overall=summarize(rows) if rows else {}
    by={opp:summarize([r for r in rows if r["opponent"]==opp]) for opp in sorted({r["opponent"] for r in rows})}
    safe_blocks=all(x["all3_vs_base"]>=0 for x in by.values()) if by else False
    if mech and overall["all3"]["score_rate"]>=max(overall["old"]["score_rate"],overall["lq2"]["score_rate"]) and overall["all3_vs_base"]>0 and safe_blocks and overall["all3_negative_vs_base"]==0:
        decision="TRIPLE_COMBO_SAFE_ADVANCE"
    elif mech and safe_blocks and overall["all3_negative_vs_base"]==0:
        decision="TRIPLE_COMBO_SAFE_NO_INCREMENT"
    elif mech and overall["lq2"]["score_rate"]>overall["base"]["score_rate"]:
        decision="TRIPLE_COMBO_ROUTER_REQUIRED"
    elif mech:
        decision="TRIPLE_COMBO_FAIL"
    else:
        decision="TRIPLE_COMBO_MECHANICS_INVALID"
    result={"schema":"kculture-triple-combo-v1","mechanical_pass":mech,"decision":decision,"overall":overall,"by_opponent":by,"rows":rows,"failures":fails,"automatic_kaggle_submission":False}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("TRIPLE_COMBO_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"overall":overall,"by_opponent":by,"failures":len(fails)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
