#!/usr/bin/env python3
"""Aggregate V17A3 trigger audit under frozen selection gate."""
from __future__ import annotations
import argparse,json
from pathlib import Path

TRIGGERS=("T0_AVAILABLE","T1_CARRIED20","T2_SHED2","T3_CARRIED20_OR_SHED2")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    targets={tuple(x) for d in docs for x in d.get("assigned_targets",[])}
    mech=(len(docs)==4 and len(rows)==24 and len(targets)==42 and not failures and all(d.get("mechanical_pass") for d in docs))
    source_by_context={str(r["context_id"]):str(r["main_sha256"]) for r in rows}

    summaries={}
    eligible=[]
    for name in TRIGGERS:
        hits={tuple(x) for r in rows for x in (r.get("hits") or {}).get(name,[])}
        tp=hits & targets;fp=hits-targets;fn=targets-hits
        recall=len(tp)/len(targets) if targets else 0.0
        precision=len(tp)/len(hits) if hits else 0.0
        contexts={x[0] for x in tp}
        sources={source_by_context.get(x[0]) for x in tp if source_by_context.get(x[0])}
        s={
          "trigger":name,"fires":len(hits),"true_positives":len(tp),"false_positives":len(fp),"false_negatives":len(fn),
          "recall":recall,"precision":precision,"contexts_covered":len(contexts),"sources_covered":len(sources),
          "false_positive_keys":[list(x) for x in sorted(fp)],
          "false_negative_keys":[list(x) for x in sorted(fn)],
        }
        s["eligible"]=(recall==1.0 and precision>=0.90 and len(contexts)==24 and len(sources)==10)
        summaries[name]=s
        if s["eligible"]:eligible.append(s)

    eligible.sort(key=lambda x:(-x["precision"],x["fires"],x["trigger"]))
    selected=eligible[0] if eligible else None
    if not mech:decision="V17A3_MECHANICS_INVALID"
    elif selected:decision="V17A3_STRAWBERRY_TRIGGER_READY"
    else:decision="V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE"

    result={
      "schema":"kculture-all3-v17a3-trigger-audit-v1","mechanical_pass":mech,"decision":decision,
      "targets":len(targets),"trigger_summaries":summaries,"selected_trigger":selected,
      "rows":rows,"failures":failures,"automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V17A3_RESULT",json.dumps({
      "decision":decision,"mechanical_pass":mech,"targets":len(targets),
      "trigger_summaries":summaries,"selected_trigger":selected,"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
