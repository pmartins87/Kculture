#!/usr/bin/env python3
"""V17A4 rising-edge trigger audit from frozen V17A3 stateless hit sequences."""
from __future__ import annotations
import argparse,json
from pathlib import Path

STATELESS=("T0_AVAILABLE","T1_CARRIED20","T2_SHED2","T3_CARRIED20_OR_SHED2")
EDGE={
 "T0_AVAILABLE":"E0_AVAILABLE_RISING",
 "T1_CARRIED20":"E1_CARRIED20_RISING",
 "T2_SHED2":"E2_SHED2_RISING",
 "T3_CARRIED20_OR_SHED2":"E3_CARRIED20_OR_SHED2_RISING",
}

def targets_from_v17a3(d):
    targets=set()
    # Reconstruct the exact target set from stateless T0:
    # V17A3 T0 had recall 1.0 by binding result, and its false positives are explicitly listed.
    s=(d.get("trigger_summaries") or {}).get("T0_AVAILABLE") or {}
    if float(s.get("recall",0))!=1.0:
        raise RuntimeError("binding V17A3 T0 recall is not 1.0")
    t0hits={tuple(x) for r in d.get("rows") or [] for x in (r.get("hits") or {}).get("T0_AVAILABLE",[])}
    fp={tuple(x) for x in s.get("false_positive_keys") or []}
    targets=t0hits-fp
    if len(targets)!=42:
        raise RuntimeError(f"target reconstruction mismatch {len(targets)} != 42")
    return targets

def edge_hits(turns):
    s=set(int(t) for t in turns)
    return {t for t in s if (t-1) not in s}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--v17a3",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    d=json.loads(Path(args.v17a3).read_text())
    if not d.get("mechanical_pass"):raise RuntimeError("V17A3 aggregate not mechanically valid")
    if d.get("decision")!="V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE":
        raise RuntimeError(f"unexpected V17A3 decision {d.get('decision')}")
    rows=list(d.get("rows") or [])
    if len(rows)!=24:raise RuntimeError(f"expected 24 rows, got {len(rows)}")
    targets=targets_from_v17a3(d)
    source_by_context={str(r["context_id"]):str(r["main_sha256"]) for r in rows}

    summaries={}
    eligible=[]
    per_context={}
    for stateless in STATELESS:
        name=EDGE[stateless]
        hits=set()
        ctx_map={}
        for r in rows:
            cid=str(r["context_id"])
            turns=[int(x[1]) for x in (r.get("hits") or {}).get(stateless,[])]
            eh=edge_hits(turns)
            ctx_map[cid]=sorted(eh)
            hits.update((cid,t) for t in eh)
        tp=hits&targets;fp=hits-targets;fn=targets-hits
        recall=len(tp)/len(targets) if targets else 0.0
        precision=len(tp)/len(hits) if hits else 0.0
        contexts={x[0] for x in tp}
        sources={source_by_context.get(x[0]) for x in tp if source_by_context.get(x[0])}
        s={
          "edge_trigger":name,"from_stateless":stateless,
          "fires":len(hits),"true_positives":len(tp),"false_positives":len(fp),"false_negatives":len(fn),
          "recall":recall,"precision":precision,"contexts_covered":len(contexts),"sources_covered":len(sources),
          "false_positive_keys":[list(x) for x in sorted(fp)],
          "false_negative_keys":[list(x) for x in sorted(fn)],
          "eligible":(recall==1.0 and precision>=0.90 and len(contexts)==24 and len(sources)==10),
        }
        summaries[name]=s;per_context[name]=ctx_map
        if s["eligible"]:eligible.append(s)

    eligible.sort(key=lambda x:(-x["precision"],x["fires"],x["edge_trigger"]))
    selected=eligible[0] if eligible else None
    decision="V17A4_STRAWBERRY_EDGE_TRIGGER_READY" if selected else "V17A4_STRAWBERRY_EDGE_TRIGGER_NOT_COMPRESSIBLE"
    result={
      "schema":"kculture-all3-v17a4-strawberry-edge-trigger-v1",
      "source_v17a3_workflow":35539020930,
      "decision":decision,"targets":len(targets),
      "edge_trigger_summaries":summaries,
      "per_context_edge_hits":per_context,
      "selected_edge_trigger":selected,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V17A4_RESULT",json.dumps({
      "decision":decision,"targets":len(targets),
      "edge_trigger_summaries":summaries,"selected_edge_trigger":selected
    },sort_keys=True),flush=True)
    if selected is None:raise SystemExit(2)

if __name__=="__main__":main()
