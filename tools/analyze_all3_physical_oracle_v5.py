#!/usr/bin/env python3
"""Analyze winning localized transforms from ALL3 Physical Proposal Oracle V5."""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter,defaultdict
from pathlib import Path

def unit_op(u):
    return str(u[0]) if isinstance(u,list) and u else "NONE"

def transform_key(r):
    o=r["oracle"]
    return json.dumps({
      "locus":o.get("locus"),
      "old_op":unit_op(o.get("old_unit")),
      "old_unit":o.get("old_unit"),
      "new_op":unit_op(o.get("new_unit")),
      "new_unit":o.get("new_unit"),
    },sort_keys=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    d=json.loads(Path(args.input).read_text())
    rows=d.get("rows",[])
    improved=[r for r in rows if float(r["oracle"]["score"])>float(r["base"]["score"])]
    margin=[r for r in rows if float(r["oracle"]["score"])==float(r["base"]["score"]) and float(r["oracle"]["margin"])>float(r["base"]["margin"])]
    groups=defaultdict(list)
    for r in improved:
        groups[transform_key(r)].append(r)
    ranked=[]
    for k,xs in groups.items():
        spec=json.loads(k)
        ranked.append({
          **spec,
          "states":len(xs),
          "opponents":sorted({r["opponent"] for r in xs}),
          "families":sorted({str(r.get("family")) for r in xs}),
          "steps":[int(r["step"]) for r in xs],
          "mean_step":statistics.fmean(int(r["step"]) for r in xs),
          "score_gain_sum":sum(float(r["oracle"]["score"])-float(r["base"]["score"]) for r in xs),
          "mean_margin_delta":statistics.fmean(float(r["oracle"]["margin"])-float(r["base"]["margin"]) for r in xs),
          "sources":dict(Counter(s for r in xs for s in r["oracle"].get("sources",[]))),
          "contexts":[{
             "opponent":r["opponent"],"seed":r["seed"],"seat":r["seat"],"step":r["step"],
             "base_score":r["base"]["score"],"oracle_score":r["oracle"]["score"],
             "margin_delta":float(r["oracle"]["margin"])-float(r["base"]["margin"]),
          } for r in xs],
        })
    ranked.sort(key=lambda x:(-x["score_gain_sum"],-len(x["opponents"]),-x["states"],-x["mean_margin_delta"]))

    result={
      "schema":"kculture-v5-physical-transform-analysis-v1",
      "source_decision":d.get("decision"),
      "mechanical_pass":d.get("mechanical_pass"),
      "branch_states":len(rows),
      "wl_improved_states":len(improved),
      "margin_only_improved_states":len(margin),
      "winning_transform_groups":ranked,
      "recurring_multi_state":[x for x in ranked if x["states"]>=2],
      "recurring_multi_opponent":[x for x in ranked if len(x["opponents"])>=2],
      "note":"Discovery only. No third-party transform is deployable until rewritten first-party and fresh-causally validated."
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V5_TRANSFORM_ANALYSIS",json.dumps({
      "source_decision":result["source_decision"],
      "branch_states":result["branch_states"],
      "wl_improved_states":result["wl_improved_states"],
      "margin_only_improved_states":result["margin_only_improved_states"],
      "top_groups":ranked[:10],
    },sort_keys=True))

if __name__=="__main__":main()
