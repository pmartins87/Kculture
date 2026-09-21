#!/usr/bin/env python3
"""Aggregate V24A coupled divergence trace shards and apply frozen selector."""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter,defaultdict
from pathlib import Path

def median(xs):
    return statistics.median(xs) if xs else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--hard-config",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    cfg=json.loads(Path(args.hard_config).read_text())
    expected={str(c["context_id"]) for c in cfg["hard_contexts"]}

    docs=[]
    for p in sorted(Path(args.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-all3-v24a-coupled-divergence-trace-shard-v1":
            docs.append(d)

    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    actual=[str(r["context_id"]) for r in rows]
    mech=(
      len(docs)==4 and all(bool(d.get("mechanical_pass")) for d in docs)
      and not failures and len(rows)==len(expected)
      and len(set(actual))==len(expected) and set(actual)==expected
    )

    fam_occ=defaultdict(list)
    for r in rows:
        for e in r.get("events",[]):
            rec={
              "context_id":r["context_id"],"main_sha256":r["main_sha256"],"cluster":r["cluster"],
              "seed":int(r["seed"]),"seat":int(r["seat"]),"annotation":r["annotation"],
              "source_rank":r["source_rank"],**e
            }
            fam_occ[e["family"]].append(rec)

    summaries=[]
    for family,occ in sorted(fam_occ.items()):
        ix=[x for x in occ if x["annotation"]=="INTERACTION_EXCLUSIVE"]
        ctrl=[x for x in occ if x["annotation"]!="INTERACTION_EXCLUSIVE"]
        clusters=sorted({x["cluster"] for x in ix})
        shas=sorted({x["main_sha256"] for x in ix})
        seeds=sorted({int(x["seed"]) for x in ix})
        contexts=sorted({x["context_id"] for x in ix})
        eligible=(len(contexts)>=4 and len(shas)>=2 and len(clusters)>=2 and len(seeds)>=2)
        summaries.append({
          "family":family,
          "topology":ix[0]["topology"] if ix else (occ[0]["topology"] if occ else None),
          "physical_kind":ix[0]["physical_kind"] if ix else (occ[0]["physical_kind"] if occ else None),
          "lag":int(ix[0]["lag"] if ix else occ[0]["lag"]) if occ else None,
          "interaction_contexts":len(contexts),
          "interaction_source_shas":len(shas),
          "interaction_clusters":len(clusters),
          "interaction_cluster_ids":clusters,
          "interaction_seeds":len(seeds),
          "interaction_seed_ids":seeds,
          "other_hard_contexts":len({x["context_id"] for x in ctrl}),
          "median_end_step":median([int(x["end_step"]) for x in ix]),
          "median_start_step":median([int(x["start_step"]) for x in ix]),
          "median_lag":median([int(x["lag"]) for x in ix]),
          "eligible":eligible,
        })

    eligible=[x for x in summaries if x["eligible"]]
    selected=None
    if eligible:
        selected=sorted(
          eligible,
          key=lambda x:(
            float(x["median_end_step"]),
            -int(x["interaction_clusters"]),
            -int(x["interaction_source_shas"]),
            -int(x["interaction_seeds"]),
            -int(x["interaction_contexts"]),
            float(x["median_lag"]),
            str(x["family"]),
          )
        )[0]

    if not mech:decision="V24A_MECHANICS_INVALID"
    elif selected is not None:decision="V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND"
    else:decision="V24A_NO_COMPACT_RECURRENT_INTERACTION"

    selected_occ=[]
    action_pairs=[]
    if selected is not None:
        selected_occ=[x for x in fam_occ[selected["family"]] if x["annotation"]=="INTERACTION_EXCLUSIVE"]
        ctr=Counter()
        for x in selected_occ:
            key=json.dumps({
              "start_base":x["start_base"]["action_key"],
              "start_shadow":x["start_shadow"]["action_key"],
              "end_base":x["end_base"]["action_key"],
              "end_shadow":x["end_shadow"]["action_key"],
            },sort_keys=True,separators=(",",":"))
            ctr[key]+=1
        action_pairs=[{"signature":k,"count":v} for k,v in ctr.most_common(30)]

    result={
      "schema":"kculture-all3-v24a-coupled-divergence-trace-v1",
      "mechanical_pass":mech,"decision":decision,"hard_contexts":len(expected),
      "interaction_exclusive_contexts":sum(r["annotation"]=="INTERACTION_EXCLUSIVE" for r in rows),
      "families":summaries,"eligible_family_count":len(eligible),"selected_family":selected,
      "selected_occurrences":selected_occ,
      "selected_top_action_signatures":action_pairs,
      "rows":rows,"failures":failures,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V24A_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"hard_contexts":len(expected),
      "interaction_exclusive_contexts":result["interaction_exclusive_contexts"],
      "eligible_family_count":len(eligible),
      "selected_family":selected,
      "failures":len(failures),
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":
    main()
