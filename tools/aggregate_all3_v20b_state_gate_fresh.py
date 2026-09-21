#!/usr/bin/env python3
"""Aggregate untouched V20B validation for O-TM2 state-gated consensus."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

BINDING_SCHEDULE_SHA="c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22"
VALIDATION_SEEDS={78801,78802,78803,78804}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])];failures=[f for d in docs for f in d.get("failures",[])]
    keys={(r["main_sha256"],int(r["seed"]),int(r["seat"])) for r in rows};schedule_shas={str(d.get("schedule_sha256")) for d in docs};gate_shas={str(d.get("gate_sha256")) for d in docs}
    mech=(len(docs)==5 and len(rows)==80 and len(keys)==80 and not failures and all(d.get("mechanical_pass") for d in docs)
          and schedule_shas=={BINDING_SCHEDULE_SHA} and len(gate_shas)==1 and all(int(r.get("gate_decisions",0))==1 for r in rows)
          and {int(r["seed"]) for r in rows}==VALIDATION_SEEDS)
    active=[r for r in rows if bool(r.get("gate_on"))];fire=[r for r in rows if int(r.get("fire_count",0))>0]
    active_seeds={int(r["seed"]) for r in active};active_sources={r["main_sha256"] for r in active}
    coverage=(mech and len(active)>=8 and len(active_seeds)>=2 and len(active_sources)>=2 and len(fire)>=8)
    pos=[r for r in rows if float(r["score_delta"])>0];neg=[r for r in rows if float(r["score_delta"])<0];pos_sources={r["main_sha256"] for r in pos}
    win_to_non=[r for r in rows if float(r["base_score"])==1.0 and float(r["treatment_score"])<1.0]
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else 0.0;mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else 0.0
    passed=(coverage and len(pos)>=2 and len(pos_sources)>=2 and len(neg)==0 and len(win_to_non)==0 and mean_score>0 and mean_margin>=0)
    if not mech:decision="V20B_MECHANICS_INVALID"
    elif not coverage:decision="V20B_STATE_GATE_UNDERPOWERED"
    elif passed:decision="V20B_STATE_GATE_FRESH_PASS"
    else:decision="V20B_STATE_GATE_FRESH_FAIL_CLOSE"
    by_seed={}
    for seed in sorted(VALIDATION_SEEDS):
        rr=[r for r in rows if int(r["seed"])==seed]
        by_seed[str(seed)]={"contexts":len(rr),"gate_on":sum(bool(r.get("gate_on")) for r in rr),"fires":sum(int(r.get("fire_count",0))>0 for r in rr),
                            "positive":sum(float(r["score_delta"])>0 for r in rr),"negative":sum(float(r["score_delta"])<0 for r in rr),
                            "mean_score_delta":statistics.fmean(float(r["score_delta"]) for r in rr) if rr else 0.0,
                            "mean_margin_delta":statistics.fmean(float(r["margin_delta"]) for r in rr) if rr else 0.0}
    result={"schema":"kculture-all3-v20b-state-gate-fresh-v1","decision":decision,"mechanical_pass":mech,"coverage_pass":coverage,"schedule_sha256":BINDING_SCHEDULE_SHA,
            "gate_sha256":next(iter(gate_shas)) if len(gate_shas)==1 else None,"pairs":len(rows),"gate_on_contexts":len(active),"gate_on_seeds":len(active_seeds),"gate_on_sources":len(active_sources),
            "fire_contexts":len(fire),"positive_score_contexts":len(pos),"positive_score_sources":len(pos_sources),"negative_score_contexts":len(neg),"win_to_nonwin":len(win_to_non),
            "mean_score_delta":mean_score,"mean_margin_delta":mean_margin,"by_seed":by_seed,"rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V20B_RESULT",json.dumps({k:result[k] for k in ["decision","mechanical_pass","coverage_pass","pairs","gate_on_contexts","gate_on_seeds","gate_on_sources","fire_contexts","positive_score_contexts","positive_score_sources","negative_score_contexts","win_to_nonwin","mean_score_delta","mean_margin_delta"]},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
