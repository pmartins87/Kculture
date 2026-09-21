#!/usr/bin/env python3
"""V19A source-balanced exact P2 consensus market schedule from frozen V18B dataset."""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

START,END=464,591

def canon_market(m):
    return json.dumps(m or [],sort_keys=True,separators=(",",":"))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    docs=[json.loads(p.read_text()) for p in sorted(Path(args.input_dir).rglob("*.json"))]
    failures=[f for d in docs for f in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    if len(docs)!=4 or failures or len(rows)!=3072 or not all(d.get("mechanical_pass") for d in docs):
        raise RuntimeError(f"dataset invalid docs={len(docs)} rows={len(rows)} failures={len(failures)}")
    sources=sorted({str(r["main_sha256"]) for r in rows})
    contexts=sorted({str(r["context_id"]) for r in rows})
    if len(sources)!=10 or len(contexts)!=24:raise RuntimeError("support mismatch")

    schedule={}
    per_turn=[]
    for t in range(START,END+1):
        tr=[r for r in rows if int(r["turn"])==t]
        if len(tr)!=24:raise RuntimeError(f"turn {t} row count {len(tr)} !=24")
        source_vote={}
        for s in sources:
            sr=[r for r in tr if str(r["main_sha256"])==s]
            if not sr:raise RuntimeError(f"turn {t} source {s} absent")
            c=collections.Counter(canon_market(r["teacher_market"]) for r in sr)
            best_count=max(c.values())
            candidates=sorted(k for k,v in c.items() if v==best_count)
            source_vote[s]=candidates[0]
        cc=collections.Counter(source_vote.values())
        best=max(cc.values())
        winners=sorted(k for k,v in cc.items() if v==best)
        market_key=winners[0]
        market=json.loads(market_key)
        src_support=int(cc[market_key])
        ctx_support=sum(1 for r in tr if canon_market(r["teacher_market"])==market_key)
        selected=(src_support>=8 and ctx_support>=16)
        rec={
          "turn":t,"market":market,"source_support":src_support,"context_support":ctx_support,
          "selected":selected,
        }
        per_turn.append(rec)
        if selected:schedule[str(t)]={"market":market,"source_support":src_support,"context_support":ctx_support}

    selected_turns=sorted(int(k) for k in schedule)
    decision="V19A_CONSENSUS_SCHEDULE_READY" if len(selected_turns)>=20 else "V19A_CONSENSUS_SCHEDULE_NOT_READY"
    source_supports=[schedule[str(t)]["source_support"] for t in selected_turns]
    context_supports=[schedule[str(t)]["context_support"] for t in selected_turns]
    result={
      "schema":"kculture-all3-v19a-p2-consensus-schedule-v1",
      "source_dataset_workflow":35552335995,
      "scope":[START,END],
      "decision":decision,
      "scheduled_turns":len(selected_turns),
      "turns":selected_turns,
      "schedule":schedule,
      "per_turn":per_turn,
      "min_source_support":min(source_supports) if source_supports else 0,
      "min_context_support":min(context_supports) if context_supports else 0,
      "sources":10,"contexts":24,
      "runtime_identity_feature_allowed":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V19A_RESULT",json.dumps({
      "decision":decision,"scheduled_turns":len(selected_turns),
      "min_source_support":result["min_source_support"],"min_context_support":result["min_context_support"],
      "turns":selected_turns,
      "schedule":schedule
    },sort_keys=True),flush=True)
    if decision!="V19A_CONSENSUS_SCHEDULE_READY":raise SystemExit(2)

if __name__=="__main__":main()
