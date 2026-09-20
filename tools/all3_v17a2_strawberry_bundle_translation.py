#!/usr/bin/env python3
"""V17A2 outcome-free translation audit for selected W2 STRAWBERRY ADD/+2 bundle."""
from __future__ import annotations
import argparse,collections,json,statistics
from pathlib import Path

SELECTED={"PRESENCE|SELL|STRAWBERRY|ADD","QTY|SELL|STRAWBERRY|2|INC"}

def order_type(o):
    x=list(o or [])
    side=str(x[0]) if x else "EMPTY"
    product=str(x[1]) if len(x)>1 else "_"
    qty=None
    if len(x)>2:
        try:qty=int(x[2])
        except:qty=None
    return side,product,qty

def norm(e):
    kind=str(e.get("kind",""));direction=str(e.get("direction",""))
    if kind=="PRESENCE" and str(e.get("side"))=="SELL" and str(e.get("product"))=="STRAWBERRY":
        return f"PRESENCE|SELL|STRAWBERRY|{direction}"
    if kind=="QTY" and str(e.get("side"))=="SELL" and str(e.get("product"))=="STRAWBERRY":
        return f"QTY|SELL|STRAWBERRY|{e.get('magnitude_bucket')}|{direction}"
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--atlas",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    d=json.loads(Path(args.atlas).read_text())
    if not d.get("mechanical_pass"):raise RuntimeError("V14B atlas not mechanically valid")
    selected=[]
    for row in d.get("event_rows") or []:
        ev=row.get("event") or {}
        if ev.get("phase")!="W2":continue
        sigs={x for x in (norm(e) for e in ev.get("elementary") or []) if x}
        # exact selected pair among strawberry-specific normalized edits
        if sigs!=SELECTED:continue
        base=list(ev.get("base_market") or [])
        teacher=list(ev.get("teacher_market") or [])
        add_idxs=[]
        details=[]
        empties=[j for j,x in enumerate(base) if not list(x or [])]
        first_free_index=empties[0] if empties else len(base)
        last_free_index=empties[-1] if empties else len(base)
        for i,to in enumerate(teacher):
            ts,tp,tq=order_type(to)
            bo=base[i] if i<len(base) else None
            bs,bp,bq=order_type(bo) if bo is not None else ("MISSING","_",None)
            if ts=="SELL" and tp=="STRAWBERRY" and not (bs=="SELL" and bp=="STRAWBERRY"):
                add_idxs.append(i)
                nonempty_before=sum(1 for x in base[:min(i,len(base))] if list(x or []))
                nonempty_after=sum(1 for x in base[min(i+1,len(base)):] if list(x or []))
                details.append({
                  "index":i,"teacher_qty":tq,"base_order":bo,
                  "base_empty":(bo is None or not bool(list(bo or []))),
                  "base_missing":bo is None,
                  "first_empty_index":empties[0] if empties else None,
                  "last_empty_index":empties[-1] if empties else None,
                  "first_free_index":first_free_index,
                  "last_free_index":last_free_index,
                  "is_first_empty":bool(empties and i==empties[0]),
                  "is_last_empty":bool(empties and i==empties[-1]),
                  "is_first_free":i==first_free_index,
                  "is_last_free":i==last_free_index,
                  "nonempty_before":nonempty_before,
                  "nonempty_after":nonempty_after,
                })
        if not add_idxs:
            raise RuntimeError(f"selected bundle but no added strawberry order in {row['context_id']} turn {ev.get('turn')}")
        selected.append({
          "context_id":row["context_id"],"main_sha256":row["main_sha256"],"rank":row.get("rank"),
          "turn":int(ev["turn"]),"base_market":base,"teacher_market":teacher,
          "added_indices":add_idxs,"details":details,
        })

    if len(selected)!=42:
        raise RuntimeError(f"expected 42 selected events, got {len(selected)}")

    flat=[x for r in selected for x in r["details"]]
    contexts=collections.Counter(r["context_id"] for r in selected)
    turns=collections.Counter(r["turn"] for r in selected)
    idxs=collections.Counter(x["index"] for x in flat)
    qtys=collections.Counter(x["teacher_qty"] for x in flat)
    base_empty=sum(bool(x["base_empty"]) for x in flat)/len(flat)
    first_empty=sum(bool(x["is_first_empty"]) for x in flat)/len(flat)
    last_empty=sum(bool(x["is_last_empty"]) for x in flat)/len(flat)
    first_free=sum(bool(x["is_first_free"]) for x in flat)/len(flat)
    last_free=sum(bool(x["is_last_free"]) for x in flat)/len(flat)

    fixed_index=None;fixed_index_share=0.0
    if idxs:
        fixed_index,count=idxs.most_common(1)[0];fixed_index_share=count/len(flat)
    qty=None;qty_share=0.0
    if qtys:
        qty,count=qtys.most_common(1)[0];qty_share=count/len(flat)

    candidates=[
      ("first_free",first_free),
      ("last_free",last_free),
      ("first_empty",first_empty),
      ("last_empty",last_empty),
      ("fixed_index",fixed_index_share),
    ]
    chosen=None
    for name,share in candidates:
        if share>=0.95:
            chosen={"rule":name,"agreement":share}
            if name=="fixed_index":chosen["index"]=fixed_index
            break

    # Optional before/after uniquely identified order type if first three fail.
    relation_counts=collections.Counter()
    if chosen is None:
        for r in selected:
            base=r["base_market"]
            for det in r["details"]:
                i=det["index"]
                # nearest nonempty predecessor/successor order type.
                prev=None;next_=None
                for j in range(i-1,-1,-1):
                    if list(base[j] or []):
                        prev=order_type(base[j])[:2];break
                for j in range(i+1,len(base)):
                    if list(base[j] or []):
                        next_=order_type(base[j])[:2];break
                if prev:relation_counts[("after",prev)]+=1
                if next_:relation_counts[("before",next_)]+=1
        if relation_counts:
            rel,count=relation_counts.most_common(1)[0]
            share=count/len(flat)
            if share>=0.95:
                chosen={"rule":rel[0],"order_type":list(rel[1]),"agreement":share}

    if chosen and qty_share>=0.95:
        quantity_rule={"quantity":int(qty),"agreement":qty_share,"fallback_bucket_min":2}
    else:
        quantity_rule={"quantity":2,"agreement":qty_share,"fallback_bucket_min":2}

    decision="V17A2_STRAWBERRY_INSERTION_READY" if chosen else "V17A2_STRAWBERRY_INSERTION_NOT_COMPRESSIBLE"
    result={
      "schema":"kculture-all3-v17a2-strawberry-translation-v1",
      "source_v14b_workflow":35526759114,
      "source_v17a_workflow":35538621223,
      "decision":decision,
      "selected_events":selected,
      "event_count":len(selected),
      "context_occurrence_counts":dict(sorted(contexts.items())),
      "turn_distribution":dict(sorted(turns.items())),
      "index_distribution":{str(k):v for k,v in sorted(idxs.items())},
      "quantity_distribution":{str(k):v for k,v in sorted(qtys.items(),key=lambda kv:(str(kv[0]),kv[1]))},
      "base_empty_share":base_empty,
      "first_empty_share":first_empty,
      "last_empty_share":last_empty,
      "first_free_share":first_free,
      "last_free_share":last_free,
      "fixed_index_share":fixed_index_share,
      "fixed_index":fixed_index,
      "chosen_insertion_rule":chosen,
      "quantity_rule":quantity_rule,
      "outcomes_used":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V17A2_RESULT",json.dumps({
      "decision":decision,"event_count":len(selected),"turn_distribution":result["turn_distribution"],
      "context_occurrence_counts":result["context_occurrence_counts"],
      "index_distribution":result["index_distribution"],
      "quantity_distribution":result["quantity_distribution"],
      "base_empty_share":base_empty,"first_empty_share":first_empty,"last_empty_share":last_empty,
      "first_free_share":first_free,"last_free_share":last_free,
      "chosen_insertion_rule":chosen,"quantity_rule":quantity_rule
    },sort_keys=True),flush=True)
    if chosen is None:raise SystemExit(2)

if __name__=="__main__":main()
