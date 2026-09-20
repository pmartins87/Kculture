#!/usr/bin/env python3
"""Translate selected V14B EARLY|REORDER phenotype into one directional pairwise precedence.

This stage is descriptive/mechanical only.  It consumes the already-selected V14B phenotype
and derives the single most recurrent teacher-preferred pairwise order relation.  No game
outcomes are used.
"""
from __future__ import annotations
import argparse,collections,itertools,json,statistics
from pathlib import Path

SELECTED_GROUP="EARLY|REORDER"

def order_type(item):
    x=list(item or [])
    side=str(x[0]) if x else "EMPTY"
    product=str(x[1]) if len(x)>1 else "_"
    return (side,product)

def first_index(seq,item):
    for i,x in enumerate(seq):
        if x==item:return i
    raise ValueError(item)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--atlas",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    d=json.loads(Path(args.atlas).read_text())
    sel=d.get("selected_phenotype") or {}
    if sel.get("group_key")!=SELECTED_GROUP:
        raise RuntimeError(f"unexpected selected phenotype {sel.get('group_key')}")
    if not d.get("mechanical_pass"):
        raise RuntimeError("V14B atlas was not mechanically valid")

    events=[]
    for row in d.get("event_rows") or []:
        ev=row.get("event") or {}
        if ev.get("phase")=="EARLY" and bool(ev.get("reordered_only")):
            events.append((row,ev))
    if len(events)!=int(sel.get("dominant_occurrences",0)):
        raise RuntimeError(f"selected event count mismatch {len(events)} != {sel.get('dominant_occurrences')}")

    unordered=collections.defaultdict(list)
    for row,ev in events:
        b=[order_type(x) for x in ev.get("base_sequence") or []]
        t=[order_type(x) for x in ev.get("teacher_sequence") or []]
        common=sorted(set(b)&set(t))
        for a,b2 in itertools.combinations(common,2):
            before_base=first_index(b,a)<first_index(b,b2)
            before_teacher=first_index(t,a)<first_index(t,b2)
            if before_base==before_teacher:
                continue
            key=tuple(sorted((a,b2)))
            teacher_rel=(a,b2) if before_teacher else (b2,a)
            unordered[key].append({
              "teacher_precedence":[list(teacher_rel[0]),list(teacher_rel[1])],
              "context_id":row["context_id"],
              "main_sha256":row["main_sha256"],
              "turn":int(ev["turn"]),
            })

    candidates=[]
    for pair,rr in unordered.items():
        dirs=collections.Counter(
            (tuple(x["teacher_precedence"][0]),tuple(x["teacher_precedence"][1])) for x in rr
        )
        (earlier,later),count=sorted(dirs.items(),key=lambda kv:(-kv[1],kv[0]))[0]
        dom=[x for x in rr if tuple(x["teacher_precedence"][0])==earlier and tuple(x["teacher_precedence"][1])==later]
        contexts=sorted({x["context_id"] for x in dom})
        sources=sorted({x["main_sha256"] for x in dom})
        turns=[x["turn"] for x in dom]
        c={
          "pair":[list(pair[0]),list(pair[1])],
          "preferred_earlier":list(earlier),
          "preferred_later":list(later),
          "occurrences":len(rr),
          "dominant_occurrences":len(dom),
          "direction_share":len(dom)/len(rr),
          "context_support":len(contexts),
          "source_support":len(sources),
          "contexts":contexts,
          "source_shas":sources,
          "median_turn":statistics.median(turns) if turns else None,
          "turns":sorted(set(turns)),
        }
        c["recurrent"]=(
            c["context_support"]>=4 and c["source_support"]>=2 and c["direction_share"]>=0.75
        )
        candidates.append(c)

    recurrent=[x for x in candidates if x["recurrent"]]
    recurrent.sort(key=lambda x:(
        -x["source_support"],
        -x["context_support"],
        -x["dominant_occurrences"],
        float(x["median_turn"] if x["median_turn"] is not None else 1e9),
        json.dumps(x["preferred_earlier"],sort_keys=True),
        json.dumps(x["preferred_later"],sort_keys=True),
    ))
    selected=recurrent[0] if recurrent else None
    decision="V14B_REORDER_DIRECTION_READY" if selected else "V14B_REORDER_DIRECTION_NOT_COMPRESSIBLE"
    result={
      "schema":"kculture-all3-v14b-reorder-direction-v1",
      "source_atlas_workflow":35526759114,
      "source_selected_phenotype":sel,
      "selected_event_count":len(events),
      "pairwise_candidates":sorted(candidates,key=lambda x:(-x["source_support"],-x["context_support"],-x["dominant_occurrences"],x["median_turn"] or 1e9)),
      "recurrent_candidates":recurrent,
      "selected_relation":selected,
      "decision":decision,
      "outcomes_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V14B_REORDER_TRANSLATION_RESULT",json.dumps({
      "decision":decision,
      "selected_relation":selected,
      "recurrent_count":len(recurrent),
    },sort_keys=True),flush=True)
    if selected is None:raise SystemExit(2)

if __name__=="__main__":
    main()
