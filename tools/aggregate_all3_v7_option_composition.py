#!/usr/bin/env python3
"""Aggregate V7 option-composition attribution."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

COMPS=["V47","RW","TW","LQ2","RW_TW","RW_LQ2","TW_LQ2","ALL3"]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    mech=len(docs)==4 and not failures and all(d.get("mechanical_pass") for d in docs)
    rows=[r for d in docs for r in d.get("rows",[])]
    by={}
    for c in COMPS:
        xs=[r for r in rows if r["composition"]==c]
        by[c]={
          "contexts":len(xs),
          "wins":sum(float(r["score"])==1 for r in xs),
          "ties":sum(float(r["score"])==0.5 for r in xs),
          "losses":sum(float(r["score"])==0 for r in xs),
          "mean_margin":statistics.fmean(float(r["margin"]) for r in xs) if xs else None,
          "margins":[float(r["margin"]) for r in xs],
          "changed_steps":[int(r["changed_steps"]) for r in xs],
          "rw_used_contexts":sum(bool(r["rw_used"]) for r in xs),
          "tw_used_contexts":sum(bool(r["tw_used"]) for r in xs),
        }
    all3_by_index={int(d["index"]):next(r for r in d["rows"] if r["composition"]=="ALL3") for d in docs}
    rescues={c:[] for c in COMPS if c!="ALL3"}
    for d in docs:
        idx=int(d["index"]);a=all3_by_index[idx]
        for r in d["rows"]:
            if r["composition"]=="ALL3":continue
            if float(a["score"])<1 and float(r["score"])==1:
                rescues[r["composition"]].append({
                  "index":idx,"opponent":r["opponent"],"family":r.get("family"),
                  "seed":r["seed"],"seat":r["seat"],
                  "all3_margin":a["margin"],"composition_margin":r["margin"],
                  "margin_delta":float(r["margin"])-float(a["margin"]),
                })
    repeat=[c for c,x in rescues.items() if len(x)>=2]
    any_rescue=sum(len(x) for x in rescues.values())
    all3_mean=by["ALL3"]["mean_margin"]
    best_alt=max((c for c in COMPS if c!="ALL3"),key=lambda c:(by[c]["wins"],by[c]["mean_margin"],c))
    best_alt_mean=by[best_alt]["mean_margin"]
    if not mech:decision="V7_STATIC_COMPOSITION_MECHANICS_INVALID"
    elif repeat:decision="V7_STATIC_COMPOSITION_HEADROOM_REPEATABLE"
    elif any_rescue:decision="V7_STATIC_COMPOSITION_HEADROOM_NARROW"
    elif best_alt_mean is not None and all3_mean is not None and best_alt_mean>all3_mean:
        decision="V7_STATIC_COMPOSITION_MARGIN_ONLY"
    else:decision="V7_STATIC_COMPOSITION_NO_HEADROOM"

    result={
      "schema":"kculture-v7-option-composition-attribution-v1",
      "mechanical_pass":mech,"decision":decision,"by_composition":by,
      "rescues":rescues,"repeatable_rescue_compositions":repeat,
      "best_alternative":best_alt,"best_alternative_mean_margin":best_alt_mean,
      "all3_mean_margin":all3_mean,"context_docs":docs,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V7_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"by_composition":by,
      "rescues":rescues,"repeatable_rescue_compositions":repeat,
      "best_alternative":best_alt,"best_alternative_mean_margin":best_alt_mean,
      "all3_mean_margin":all3_mean,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
