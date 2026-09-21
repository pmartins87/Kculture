#!/usr/bin/env python3
"""Aggregate dormant V21B untouched semantic fresh validation."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

BINDING_SHA="c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22"
VALIDATION_SEEDS={78901,78902,78903,78904}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])];failures=[f for d in docs for f in d.get("failures",[])]
    keys={(r["main_sha256"],int(r["seed"]),int(r["seat"])) for r in rows}
    modes={str(d.get("selected_mode")) for d in docs};v21a_shas={str(d.get("v21a_sha256")) for d in docs};schedule_shas={str(d.get("schedule_sha256")) for d in docs}
    mech=(len(docs)==5 and len(rows)==80 and len(keys)==80 and not failures and all(d.get("mechanical_pass") for d in docs)
          and len(modes)==1 and len(v21a_shas)==1 and schedule_shas=={BINDING_SHA}
          and {int(r["seed"]) for r in rows}==VALIDATION_SEEDS)
    fire=[r for r in rows if int(r.get("fire_count",0))>0]
    pos=[r for r in rows if float(r["score_delta"])>0];neg=[r for r in rows if float(r["score_delta"])<0]
    pos_sources={r["main_sha256"] for r in pos};pos_seeds={int(r["seed"]) for r in pos}
    win_to_non=[r for r in rows if float(r["base_score"])==1.0 and float(r["treatment_score"])<1.0]
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else 0.0
    mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    coverage=bool(mech and len(fire)>=8)
    passed=(coverage and len(pos)>=2 and len(pos_sources)>=2 and len(pos_seeds)>=2 and len(neg)==0
            and len(win_to_non)==0 and mean_score>0 and mean_margin>=0)
    if not mech:decision="V21B_MECHANICS_INVALID"
    elif not coverage:decision="V21B_SEMANTIC_UNDERPOWERED"
    elif passed:decision="V21B_SEMANTIC_FRESH_PASS"
    else:decision="V21B_SEMANTIC_FRESH_FAIL_CLOSE"
    by_seed={}
    for seed in sorted(VALIDATION_SEEDS):
        rr=[r for r in rows if int(r["seed"])==seed]
        by_seed[str(seed)]={"contexts":len(rr),"positive":sum(float(r["score_delta"])>0 for r in rr),
            "negative":sum(float(r["score_delta"])<0 for r in rr),
            "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rr) if rr else 0.0,
            "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rr) if rr else 0.0,
            "fire_contexts":sum(int(r.get("fire_count",0))>0 for r in rr)}
    result={"schema":"kculture-all3-v21b-semantic-fresh-v1","decision":decision,"mechanical_pass":mech,"coverage_pass":coverage,
        "schedule_sha256":BINDING_SHA,"v21a_sha256":next(iter(v21a_shas)) if len(v21a_shas)==1 else None,
        "selected_mode":next(iter(modes)) if len(modes)==1 else None,"pairs":len(rows),"fire_contexts":len(fire),
        "positive_score_contexts":len(pos),"positive_score_sources":len(pos_sources),"positive_score_seeds":len(pos_seeds),
        "negative_score_contexts":len(neg),"win_to_nonwin":len(win_to_non),"mean_score_delta":mean_score,
        "mean_margin_delta":mean_margin,"by_seed":by_seed,"rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V21B_RESULT",json.dumps({k:result[k] for k in ["decision","mechanical_pass","coverage_pass","selected_mode","pairs","fire_contexts","positive_score_contexts","positive_score_sources","positive_score_seeds","negative_score_contexts","win_to_nonwin","mean_score_delta","mean_margin_delta"]},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
