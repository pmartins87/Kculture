#!/usr/bin/env python3
"""Aggregate V26A ALL3 vs PrizeSolverV4 paired architecture benchmark."""
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

SEEDS=(79501,79502,79503,79504,79505,79506)
SEATS=(0,1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--snapshot-result",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    snap=json.loads(Path(args.snapshot_result).read_text())
    if snap.get("decision")!="V26A_FRONTIER_SNAPSHOT_READY" or not snap.get("mechanical_pass"):
        raise SystemExit("snapshot not ready")
    selected=list(snap["selected_representatives"])
    expected={(str(s["main_sha256"]),seed,seat) for s in selected for seed in SEEDS for seat in SEATS}

    docs=[]
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v26a-base-architecture-benchmark-shard-v1":
            docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])]
    failures=[f for d in docs for f in d.get("failures",[])]
    actual={(str(r["main_sha256"]),int(r["seed"]),int(r["seat"])) for r in rows}

    mech=(
      len(docs)==4 and all(bool(d.get("mechanical_pass")) for d in docs)
      and all(bool(d.get("immutable_snapshot_used")) and not bool(d.get("live_kaggle_reacquisition_used")) for d in docs)
      and not failures and len(rows)==len(expected) and actual==expected
    )

    positive=[r for r in rows if float(r["score_delta"])>0]
    negative=[r for r in rows if float(r["score_delta"])<0]
    neutral=[r for r in rows if float(r["score_delta"])==0]
    regress=[r for r in rows if bool(r["control_win"]) and bool(r["treatment_nonwin"])]

    # Functional clusters are defined outcome-only from CONTROL's 12-tuple
    # (seed,seat,score,margin), before any treatment routing.
    by_sha=defaultdict(list)
    for r in rows:
        by_sha[str(r["main_sha256"])].append(r)
    sig_groups=defaultdict(list)
    for sha,rr in by_sha.items():
        rr=sorted(rr,key=lambda x:(int(x["seed"]),int(x["seat"])))
        sig=tuple((int(x["seed"]),int(x["seat"]),float(x["control_score"]),float(x["control_margin"])) for x in rr)
        sig_groups[sig].append(sha)
    ordered=sorted((sorted(v) for v in sig_groups.values()),key=lambda g:min(int(next(r["source_rank"] for r in rows if r["main_sha256"]==sha)) for sha in g))
    sha2cluster={}
    clusters=[]
    for i,g in enumerate(ordered,1):
        cid=f"F{i:02d}"
        members=[]
        for sha in g:
            rr=[r for r in rows if r["main_sha256"]==sha]
            members.append({
              "sha":sha,
              "rank":min(int(x["source_rank"]) for x in rr),
              "ref":rr[0]["ref"],
            })
            sha2cluster[sha]=cid
        clusters.append({"cluster_id":cid,"members":sorted(members,key=lambda x:x["rank"])})

    pos_shas=sorted({str(r["main_sha256"]) for r in positive})
    pos_seeds=sorted({int(r["seed"]) for r in positive})
    pos_clusters=sorted({sha2cluster[str(r["main_sha256"])] for r in positive})
    mean_score=statistics.fmean(float(r["score_delta"]) for r in rows) if rows else None
    mean_margin=statistics.fmean(float(r["margin_delta"]) for r in rows) if rows else None
    control_rate=statistics.fmean(float(r["control_score"]) for r in rows) if rows else None
    treatment_rate=statistics.fmean(float(r["treatment_score"]) for r in rows) if rows else None

    gate=(
      mech
      and len(positive)>=8
      and len(pos_shas)>=3
      and len(pos_seeds)>=3
      and mean_score is not None and mean_score>0
      and len(negative)<=len(positive)/2
      and len(regress)<=len(positive)/2
      and len(pos_clusters)>=2
    )

    if not mech:
        decision="V26A_MECHANICS_INVALID"
    elif gate:
        decision="V26A_PRIZE_SOLVER_BASE_HEADROOM"
    else:
        decision="V26A_PRIZE_SOLVER_BASE_NOT_READY"

    by_source=[]
    for s in selected:
        sha=str(s["main_sha256"])
        rr=[r for r in rows if str(r["main_sha256"])==sha]
        by_source.append({
          "rank":int(s["representative_rank"]),
          "ref":s["representative_ref"],
          "sha":sha,
          "cluster":sha2cluster.get(sha),
          "contexts":len(rr),
          "control_score_rate":statistics.fmean(float(x["control_score"]) for x in rr) if rr else None,
          "treatment_score_rate":statistics.fmean(float(x["treatment_score"]) for x in rr) if rr else None,
          "mean_score_delta":statistics.fmean(float(x["score_delta"]) for x in rr) if rr else None,
          "mean_margin_delta":statistics.fmean(float(x["margin_delta"]) for x in rr) if rr else None,
          "positive":sum(float(x["score_delta"])>0 for x in rr),
          "negative":sum(float(x["score_delta"])<0 for x in rr),
        })

    result={
      "schema":"kculture-v26a-base-architecture-benchmark-v1",
      "mechanical_pass":mech,
      "decision":decision,
      "contexts":len(rows),
      "selected_sources":len(selected),
      "control_score_rate":control_rate,
      "treatment_score_rate":treatment_rate,
      "mean_score_delta":mean_score,
      "mean_margin_delta":mean_margin,
      "positive_score_contexts":len(positive),
      "neutral_score_contexts":len(neutral),
      "negative_score_contexts":len(negative),
      "control_win_to_treatment_nonwin":len(regress),
      "positive_source_shas":pos_shas,
      "positive_source_count":len(pos_shas),
      "positive_seeds":pos_seeds,
      "positive_seed_count":len(pos_seeds),
      "positive_functional_clusters":pos_clusters,
      "positive_functional_cluster_count":len(pos_clusters),
      "functional_clusters":clusters,
      "gate_pass":gate,
      "by_source":by_source,
      "rows":rows,
      "failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V26A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"contexts":len(rows),
      "control_score_rate":control_rate,"treatment_score_rate":treatment_rate,
      "mean_score_delta":mean_score,"mean_margin_delta":mean_margin,
      "positive_score_contexts":len(positive),"negative_score_contexts":len(negative),
      "control_win_to_treatment_nonwin":len(regress),
      "positive_source_count":len(pos_shas),"positive_seed_count":len(pos_seeds),
      "positive_functional_cluster_count":len(pos_clusters),
      "gate_pass":gate,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
