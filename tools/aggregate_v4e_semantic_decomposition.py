#!/usr/bin/env python3
"""Aggregate V4E semantic-category decomposition shards."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

VARIANTS=[
 "FULL","ONLY_SANITATION","ONLY_REPLACE","ONLY_QTY_UP","ONLY_STRUCTURAL",
 "FULL_MINUS_SANITATION","FULL_MINUS_REPLACE","FULL_MINUS_QTY_UP","FULL_MINUS_STRUCTURAL",
]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    files=sorted(Path(args.input_dir).rglob("*.json"))
    shards=[json.loads(p.read_text()) for p in files]
    rows=[];failures=[]
    for s in shards: rows.extend(s.get("rows",[]));failures.extend(s.get("failures",[]))
    summary={}
    for variant in VARIANTS:
        vals=[r["variants"][variant] for r in rows]
        summary[variant]={
            "contexts":len(vals),
            "score_rate":statistics.mean(float(v["score"]) for v in vals) if vals else None,
            "mean_score_delta":statistics.mean(float(v["score_delta"]) for v in vals) if vals else None,
            "mean_margin_delta":statistics.mean(float(v["margin_delta"]) for v in vals) if vals else None,
            "reproduced_contexts":sum(bool(v["reproduces_loss_to_tie"]) for v in vals),
            "physical_fallback_turns":sum(int(v["physical_fallback_turns"]) for v in vals),
            "mean_applied_turns":statistics.mean(int(v["applied_turns"]) for v in vals) if vals else None,
            "category_application_counts":{k:sum(int(v["category_application_counts"].get(k,0)) for v in vals) for k in ["CLEAR","QTY_DOWN","QTY_UP","REPLACE","OTHER"]},
        }
    full=summary.get("FULL",{})
    full_ok=(full.get("reproduced_contexts")==12 and full.get("physical_fallback_turns")==0)
    mech=(len(shards)==6 and len(rows)==12 and not failures and all(s.get("mechanical_pass") for s in shards) and full_ok)
    sufficient=[v for v in ["ONLY_SANITATION","ONLY_REPLACE","ONLY_QTY_UP","ONLY_STRUCTURAL"] if summary[v]["reproduced_contexts"]>=10]
    ablation_map={
      "FULL_MINUS_SANITATION":"SANITATION",
      "FULL_MINUS_REPLACE":"REPLACE",
      "FULL_MINUS_QTY_UP":"QTY_UP",
      "FULL_MINUS_STRUCTURAL":"STRUCTURAL",
    }
    necessary=[name for variant,name in ablation_map.items() if 12-summary[variant]["reproduced_contexts"]>=4]
    if mech and "ONLY_STRUCTURAL" in sufficient and "SANITATION" not in necessary:
        decision="V4E_STRUCTURAL_SUFFICIENT_SANITATION_NOT_NECESSARY"
    elif mech and sufficient:
        decision="V4E_SUFFICIENT_CATEGORY_FOUND"
    elif mech and necessary:
        decision="V4E_NECESSARY_CATEGORY_OR_INTERACTION_FOUND"
    elif mech:
        decision="V4E_DISTRIBUTED_INTERACTION"
    else:
        decision="V4E_MECHANICS_INVALID"
    result={
      "schema":"kculture-v4e-semantic-decomposition-v1","mechanical_pass":mech,
      "contexts":len(rows),"summary":summary,"sufficient_categories":sufficient,
      "necessary_categories":necessary,"decision":decision,
      "rows":rows,"failures":failures,"automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V4E_RESULT",json.dumps({"decision":decision,"mechanical_pass":mech,"sufficient_categories":sufficient,"necessary_categories":necessary,"summary":summary,"failures":len(failures)},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)

if __name__=="__main__": main()
