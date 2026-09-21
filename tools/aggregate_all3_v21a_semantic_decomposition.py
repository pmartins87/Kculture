#!/usr/bin/env python3
"""Aggregate V21A semantic decomposition and apply frozen W/L selection gate."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

EXPECTED_MODES=[
    "BASE","FULL","EMPTY_ONLY","SELL_ONLY","BUY_ONLY","HIRE_ONLY",
    "FULL_MINUS_EMPTY","FULL_MINUS_SELL","FULL_MINUS_BUY","FULL_MINUS_HIRE",
]
ACTIVE_COUNTS={
    "FULL":4,"EMPTY_ONLY":1,"SELL_ONLY":1,"BUY_ONLY":1,"HIRE_ONLY":1,
    "FULL_MINUS_EMPTY":3,"FULL_MINUS_SELL":3,"FULL_MINUS_BUY":3,"FULL_MINUS_HIRE":3,
}
BINDING_SHA="c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22"

def load_single_json(path):
    p=Path(path)
    if p.is_dir():
        files=sorted(p.rglob("*.json"))
        if len(files)!=1:raise RuntimeError(f"expected one binding JSON under {p}, found {len(files)}")
        p=files[0]
    return json.loads(p.read_text())

def mode_metrics(rows,mode):
    enriched=[]
    for r in rows:
        b=r["results"]["BASE"];t=r["results"][mode]
        enriched.append({
            "main_sha256":r["main_sha256"],"seed":int(r["seed"]),"seat":int(r["seat"]),
            "base_score":float(b["score"]),"treatment_score":float(t["score"]),
            "score_delta":float(t["score"])-float(b["score"]),
            "base_margin":float(b["margin"]),"treatment_margin":float(t["margin"]),
            "margin_delta":float(t["margin"])-float(b["margin"]),
            "fire_count":int(t["fire_count"]),
        })
    pos=[x for x in enriched if x["score_delta"]>0];neg=[x for x in enriched if x["score_delta"]<0]
    pos_sources={x["main_sha256"] for x in pos};pos_seeds={x["seed"] for x in pos}
    win_to_non=[x for x in enriched if x["base_score"]==1.0 and x["treatment_score"]<1.0]
    fire=[x for x in enriched if x["fire_count"]>0]
    mean_score=statistics.fmean(x["score_delta"] for x in enriched)
    mean_margin=statistics.fmean(x["margin_delta"] for x in enriched)
    eligible=(len(pos)>=4 and len(pos_sources)>=2 and len(pos_seeds)>=2 and len(neg)==0 and len(win_to_non)==0
              and mean_score>0 and mean_margin>=0 and len(fire)>=8)
    by_seed={}
    for seed in sorted({x["seed"] for x in enriched}):
        rr=[x for x in enriched if x["seed"]==seed]
        by_seed[str(seed)]={
            "contexts":len(rr),
            "positive":sum(x["score_delta"]>0 for x in rr),
            "negative":sum(x["score_delta"]<0 for x in rr),
            "mean_score_delta":statistics.fmean(x["score_delta"] for x in rr),
            "mean_margin_delta":statistics.fmean(x["margin_delta"] for x in rr),
            "fire_contexts":sum(x["fire_count"]>0 for x in rr),
        }
    return {
        "mode":mode,"positive_score_contexts":len(pos),"negative_score_contexts":len(neg),
        "positive_score_sources":len(pos_sources),"positive_score_seeds":len(pos_seeds),
        "win_to_nonwin":len(win_to_non),"mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
        "fire_contexts":len(fire),"active_category_count":ACTIVE_COUNTS[mode],
        "wl_eligible":eligible,"by_seed":by_seed,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True);ap.add_argument("--v20a-binding",required=True)
    ap.add_argument("--config",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    cfg=json.loads(Path(args.config).read_text())
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    keys={(r["main_sha256"],int(r["seed"]),int(r["seat"])) for r in rows}
    shas={str(d.get("schedule_sha256")) for d in docs}
    category_counts={json.dumps(d.get("category_counts"),sort_keys=True) for d in docs}
    modes={tuple(d.get("modes") or []) for d in docs}
    mech=(len(docs)==10 and len(rows)==120 and len(keys)==120 and not failures and all(d.get("mechanical_pass") for d in docs)
          and shas=={BINDING_SHA} and modes=={tuple(EXPECTED_MODES)}
          and category_counts=={json.dumps(cfg["expected_category_counts"],sort_keys=True)})
    binding=load_single_json(args.v20a_binding)
    if binding.get("decision")!="V20A_GATE_NOT_TRAINABLE" or len(binding.get("rows") or [])!=120:
        mech=False
    bind={(r["main_sha256"],int(r["seed"]),int(r["seat"])):r for r in binding.get("rows") or []}
    base_mismatch=[];full_mismatch=[]
    if mech:
        for r in rows:
            k=(r["main_sha256"],int(r["seed"]),int(r["seat"]))
            b=bind.get(k)
            if b is None:
                base_mismatch.append({"key":k,"reason":"missing_binding"});continue
            nb=r["results"]["BASE"];nf=r["results"]["FULL"]
            if float(nb["score"])!=float(b["base_score"]) or float(nb["margin"])!=float(b["base_margin"]):
                base_mismatch.append({"key":k,"new":[nb["score"],nb["margin"]],"binding":[b["base_score"],b["base_margin"]]})
            if float(nf["score"])!=float(b["treatment_score"]) or float(nf["margin"])!=float(b["treatment_margin"]):
                full_mismatch.append({"key":k,"new":[nf["score"],nf["margin"]],"binding":[b["treatment_score"],b["treatment_margin"]]})
    mech=bool(mech and not base_mismatch and not full_mismatch)
    metrics=[];selected=None
    if mech:
        metrics=[mode_metrics(rows,m) for m in EXPECTED_MODES if m!="BASE"]
        eligible=[m for m in metrics if m["wl_eligible"]]
        if eligible:
            eligible.sort(key=lambda m:(
                -m["positive_score_contexts"],-m["positive_score_seeds"],-m["positive_score_sources"],
                -m["mean_score_delta"],-m["mean_margin_delta"],m["active_category_count"],m["mode"]))
            selected=eligible[0]["mode"];decision="V21A_SEMANTIC_WL_HEADROOM"
        else:
            decision="V21A_SEMANTIC_NO_WL_HEADROOM"
    else:
        decision="V21A_MECHANICS_INVALID"
    result={
        "schema":"kculture-all3-v21a-semantic-decomposition-v1","decision":decision,"mechanical_pass":mech,
        "schedule_sha256":BINDING_SHA,"contexts":len(rows),"failures":failures,
        "base_binding_mismatches":base_mismatch,"full_binding_mismatches":full_mismatch,
        "category_counts":cfg["expected_category_counts"],"modes":EXPECTED_MODES,
        "mode_metrics":metrics,"selected_mode":selected,"validation_seeds":cfg["validation_seeds"],
        "rows":rows,"automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V21A_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mech,"contexts":len(rows),
        "base_binding_mismatches":len(base_mismatch),"full_binding_mismatches":len(full_mismatch),
        "selected_mode":selected,
        "metrics":[{k:m[k] for k in ["mode","positive_score_contexts","negative_score_contexts","positive_score_sources","positive_score_seeds","mean_score_delta","mean_margin_delta","fire_contexts","wl_eligible"]} for m in metrics],
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
