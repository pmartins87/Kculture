#!/usr/bin/env python3
"""Materialize V23B hard contexts and V23 functional clusters from binding V23A."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v23a-result",required=True)
    ap.add_argument("--hard-config-out",required=True)
    ap.add_argument("--cluster-map-out",required=True)
    args=ap.parse_args()

    d=json.loads(Path(args.v23a_result).read_text())
    if d.get("decision")!="V23A_IMMUTABLE_HARD_POPULATION_READY" or not d.get("mechanical_pass"):
        raise SystemExit(f"V23A not READY: {d.get('decision')} mechanical={d.get('mechanical_pass')}")

    rows=list(d.get("rows") or [])
    hard=sorted(
        [r for r in rows if float(r["score"])<1.0],
        key=lambda r:(int(r["rank"]),str(r["main_sha256"]),int(r["seed"]),int(r["seat"]))
    )
    shas=sorted({str(r["main_sha256"]) for r in hard})
    seeds=sorted({int(r["seed"]) for r in hard})
    if len(hard)<12 or len(shas)<4 or len(seeds)<3:
        raise SystemExit("hard gate mismatch")

    contexts=[]
    for i,r in enumerate(hard):
        contexts.append({
          "context_id":f"v23a_hard_{i:03d}",
          "rank":int(r["rank"]),"ref":str(r["ref"]),"main_sha256":str(r["main_sha256"]),
          "seed":int(r["seed"]),"seat":int(r["seat"]),
          "base_score":float(r["score"]),"base_margin":float(r["margin"]),"base_result":str(r["result"]),
        })

    cfg={
      "schema":"kculture-all3-v23b-hard-context-config-v1",
      "source_v23a_decision":d["decision"],
      "source_v23a_discovery_seeds":d["discovery_seeds"],
      "source_v23a_seats":d["seats"],
      "source_v23a_selected_representatives":d["selected_representatives"],
      "source_v23a_snapshot_manifest":d["snapshot_manifest"],
      "hard_context_count":len(contexts),"hard_source_shas":shas,"hard_seeds":seeds,
      "hard_contexts":contexts,
      "selection_rule":"all and only binding V23A rows with score < 1.0",
      "manual_context_selection_allowed":False,"automatic_kaggle_submission":False,
    }

    by_sha={}
    for r in rows:
        by_sha.setdefault(str(r["main_sha256"]),[]).append(r)
    groups={}
    for sha,rr in by_sha.items():
        rr=sorted(rr,key=lambda x:(int(x["seed"]),int(x["seat"])))
        sig="|".join(f"{x['seed']}:{x['seat']}:{float(x['score'])}:{float(x['margin'])}" for x in rr)
        groups.setdefault(sig,[]).append({
          "rank":min(int(x["rank"]) for x in rr),
          "ref":rr[0]["ref"],"sha":sha
        })
    ordered=sorted((sorted(v,key=lambda x:x["rank"]) for v in groups.values()),key=lambda g:g[0]["rank"])
    clusters=[]; sha_to_cluster={}
    for i,g in enumerate(ordered,1):
        cid=f"F{str(i).zfill(2)}"
        clusters.append({"cluster_id":cid,"members":g})
        for m in g: sha_to_cluster[m["sha"]]=cid
    cmap={
      "schema":"kculture-all3-v23-functional-cluster-map-v1",
      "source_definition":"exact equality of the 12 binding V23A BASE outcome tuples (seed,seat,score,margin)",
      "functional_cluster_count":len(clusters),"clusters":clusters,"sha_to_cluster":sha_to_cluster,
      "immutable_for_v23b_outcome_routing":True,"automatic_kaggle_submission":False,
    }

    hp=Path(args.hard_config_out); hp.parent.mkdir(parents=True,exist_ok=True)
    cp=Path(args.cluster_map_out); cp.parent.mkdir(parents=True,exist_ok=True)
    hp.write_text(json.dumps(cfg,indent=2,sort_keys=True)+"\n")
    cp.write_text(json.dumps(cmap,indent=2,sort_keys=True)+"\n")
    print("V23_MATERIALIZE_RESULT",json.dumps({"hard_contexts":len(contexts),"hard_sources":len(shas),"hard_seeds":len(seeds),"functional_clusters":len(clusters)},sort_keys=True))

if __name__=="__main__":
    main()
