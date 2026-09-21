#!/usr/bin/env python3
"""Aggregate V25A shadow-prefix basin horizon shards."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

HORIZONS=(0,4,8,16,32,64,128,256,720)
FINITE=(4,8,16,32,64,128,256)

def summarize(rows,base_by,sha2cluster):
    improved=[];regressed=[]
    deltas=[];md=[]
    for r in rows:
        b=base_by[str(r["context_id"])]
        sd=float(r["score"])-float(b["score"])
        mdel=float(r["margin"])-float(b["margin"])
        deltas.append(sd);md.append(mdel)
        rr={**r,"score_delta":sd,"margin_delta":mdel}
        if sd>0:improved.append(rr)
        elif sd<0:regressed.append(rr)
    return {
      "contexts":len(rows),
      "improved_score_contexts":len(improved),
      "regressed_score_contexts":len(regressed),
      "improved_source_shas":sorted({r["main_sha256"] for r in improved}),
      "improved_sources":len({r["main_sha256"] for r in improved}),
      "improved_clusters":sorted({sha2cluster[r["main_sha256"]] for r in improved}),
      "improved_cluster_count":len({sha2cluster[r["main_sha256"]] for r in improved}),
      "improved_seeds":sorted({int(r["seed"]) for r in improved}),
      "improved_seed_count":len({int(r["seed"]) for r in improved}),
      "mean_score_delta":statistics.fmean(deltas) if deltas else None,
      "mean_margin_delta":statistics.fmean(md) if md else None,
    }

def pass_gate(s):
    return (
      s["improved_score_contexts"]>=4
      and s["improved_sources"]>=2
      and s["improved_cluster_count"]>=2
      and s["improved_seed_count"]>=2
      and s["mean_score_delta"]>0
      and s["regressed_score_contexts"]<=s["improved_score_contexts"]/2
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--cluster-map",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    cfg=json.loads(Path(args.hard_config).read_text())
    cmap=json.loads(Path(args.cluster_map).read_text())
    contexts=list(cfg["hard_contexts"]);expected_ids={str(c["context_id"]) for c in contexts}
    sha2cluster=dict(cmap["sha_to_cluster"])

    docs=[]
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-all3-v25a-shadow-prefix-basin-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    expected_keys={(cid,h) for cid in expected_ids for h in HORIZONS}
    actual_keys={(str(r["context_id"]),int(r["horizon"])) for r in rows}
    mech=(
      len(docs)==4 and all(bool(d.get("mechanical_pass")) for d in docs)
      and not failures and len(rows)==len(expected_keys) and actual_keys==expected_keys
    )

    base_rows=[r for r in rows if int(r["horizon"])==0]
    base_by={str(r["context_id"]):r for r in base_rows}
    by_h={}
    for h in HORIZONS:
        rr=[r for r in rows if int(r["horizon"])==h]
        by_h[str(h)]=summarize(rr,base_by,sha2cluster)

    passing=[h for h in FINITE if pass_gate(by_h[str(h)])]
    selected=min(passing) if passing else None

    full_pass=pass_gate(by_h["720"])
    if not mech:
        decision="V25A_MECHANICS_INVALID"
    elif selected is not None and selected<=32:
        decision="V25A_EARLY_STATE_BASIN_HEADROOM"
    elif selected is not None:
        decision="V25A_LONG_STATE_BASIN_HEADROOM"
    elif full_pass:
        decision="V25A_PERSISTENT_POLICY_REQUIRED"
    else:
        decision="V25A_NO_REPRODUCIBLE_SHADOW_HEADROOM"

    result={
      "schema":"kculture-all3-v25a-shadow-prefix-basin-v1","mechanical_pass":mech,
      "decision":decision,"hard_contexts":len(contexts),"horizons":list(HORIZONS),
      "by_horizon":by_h,"passing_finite_horizons":passing,"selected_horizon":selected,
      "full_shadow_gate_pass":full_pass,"rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V25A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"hard_contexts":len(contexts),
      "passing_finite_horizons":passing,"selected_horizon":selected,
      "full_shadow_gate_pass":full_pass,
      "by_horizon":by_h,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
