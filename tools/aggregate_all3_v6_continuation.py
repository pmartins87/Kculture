#!/usr/bin/env python3
"""Aggregate V6 hard-context continuation oracle."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    active=[d for d in docs if d.get("active")]
    failures=[f for d in active for f in d.get("failures",[])]
    mech=bool(active) and not failures and all(d.get("mechanical_pass") for d in active)
    rows=[]
    for d in active:
        base=d["base"];oracle=d["oracle"];ctx=d["context"]
        rows.append({
          "index":d["index"],"opponent":ctx["opponent"],"family":ctx.get("family"),
          "seed":ctx["seed"],"seat":ctx["seat"],
          "base_score":base["score"],"base_margin":base["margin"],
          "oracle_score":oracle["score"],"oracle_margin":oracle["margin"],
          "score_delta":float(oracle["score"])-float(base["score"]),
          "margin_delta":float(oracle["margin"])-float(base["margin"]),
          "oracle":oracle,
        })
    flips=[r for r in rows if float(r["base_score"])<1 and float(r["oracle_score"])==1]
    families=sorted({str(r.get("family")) for r in flips})
    mean_md=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    if not mech:decision="V6_CONTINUATION_MECHANICS_INVALID"
    elif len(flips)>=2 and len(families)>=2:decision="V6_CONTINUATION_HEADROOM_PASS"
    elif len(flips)>=1:decision="V6_CONTINUATION_HEADROOM_NARROW"
    elif mean_md>0:decision="V6_CONTINUATION_MARGIN_ONLY"
    else:decision="V6_CONTINUATION_NO_HEADROOM"
    result={
      "schema":"kculture-v6-bounded-physical-continuation-v1",
      "mechanical_pass":mech,"decision":decision,"active_contexts":len(active),
      "flipped_to_win":len(flips),"flip_families":families,
      "mean_oracle_margin_delta":mean_md,"rows":rows,"context_docs":docs,
      "failures":failures,"automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V6_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"active_contexts":len(active),
      "flipped_to_win":len(flips),"flip_families":families,
      "mean_oracle_margin_delta":mean_md,
      "flips":flips,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
