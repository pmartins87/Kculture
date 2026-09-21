#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

BINDING_SHA="c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22"

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    keys=[(r["main_sha256"],int(r["seed"]),int(r["seat"])) for r in rows]
    shas={str(d.get("schedule_sha256")) for d in docs}
    mech=(len(docs)==4 and len(rows)==80 and len(set(keys))==80 and not failures
          and all(d.get("mechanical_pass") for d in docs) and shas=={BINDING_SHA})
    fire=[r for r in rows if int(r["fire_count"])>0]
    pos=[r for r in rows if float(r["score_delta"])>0]
    neg=[r for r in rows if float(r["score_delta"])<0]
    pos_sources={r["main_sha256"] for r in pos}
    win_to_nonwin=[r for r in rows if float(r["base_score"])==1.0 and float(r["treatment_score"])<1.0]
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else 0.0
    mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    coverage=(mech and len(fire)>=20)
    pass_gate=(coverage and len(pos)>=2 and len(pos_sources)>=2 and len(neg)==0 and len(win_to_nonwin)==0 and mean_score>0 and mean_margin>=0)
    if not mech:decision="V19C_MECHANICS_INVALID"
    elif not coverage:decision="V19C_CONSENSUS_UNDERPOWERED"
    elif pass_gate:decision="V19C_CONSENSUS_FRESH_PASS"
    else:decision="V19C_CONSENSUS_FRESH_FAIL_CLOSE"
    result={"schema":"kculture-all3-v19c-consensus-fresh-v1","schedule_sha256":BINDING_SHA,
      "mechanical_pass":mech,"coverage_pass":coverage,"decision":decision,
      "pairs":len(rows),"fire_contexts":len(fire),
      "positive_score_contexts":len(pos),"positive_score_sources":len(pos_sources),
      "negative_score_contexts":len(neg),"win_to_nonwin":len(win_to_nonwin),
      "mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
      "rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V19C_RESULT",json.dumps({k:result[k] for k in [
      "decision","mechanical_pass","coverage_pass","pairs","fire_contexts","positive_score_contexts",
      "positive_score_sources","negative_score_contexts","win_to_nonwin","mean_score_delta","mean_margin_delta"]},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
