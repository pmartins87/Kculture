#!/usr/bin/env python3
"""Analyze recurring market transforms inside V4D minimal reproducer intervals."""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

def order_key(o):
    if not isinstance(o,list) or not o:
        return ("EMPTY",)
    op=str(o[0]); item=str(o[1]) if len(o)>1 else ""
    qty=o[2] if len(o)>2 else None
    return (op,item,qty)

def classify_slot(b,v):
    if b==v:
        return "UNCHANGED"
    if (not b) and v:
        return "FILL_EMPTY"
    if b and (not v):
        return "CLEAR_SLOT"
    if not isinstance(b,list) or not isinstance(v,list):
        return "OTHER"
    bop=str(b[0]) if b else ""
    vop=str(v[0]) if v else ""
    bi=str(b[1]) if len(b)>1 else ""
    vi=str(v[1]) if len(v)>1 else ""
    bq=b[2] if len(b)>2 else None
    vq=v[2] if len(v)>2 else None
    if bop==vop and bi==vi and bq!=vq:
        try:
            if float(vq)<float(bq): return "SAME_ORDER_QTY_DOWN"
            if float(vq)>float(bq): return "SAME_ORDER_QTY_UP"
        except Exception:
            pass
        return "SAME_ORDER_QTY_CHANGE"
    if bop=="SELL" and vop=="SELL" and bi!=vi:
        return "SELL_PRODUCT_REPLACE"
    if bop==vop and bi!=vi:
        return "SAME_OP_PRODUCT_REPLACE"
    return "OTHER"

def signature(base,v48):
    n=max(len(base),len(v48))
    cats=[]
    for i in range(n):
        b=base[i] if i<len(base) else []
        v=v48[i] if i<len(v48) else []
        cats.append(classify_slot(b,v))
    # detect multiset-preserving slot movement/compaction
    bnon=[json.dumps(x,sort_keys=True) for x in base if x]
    vnon=[json.dumps(x,sort_keys=True) for x in v48 if x]
    if sorted(bnon)==sorted(vnon) and bnon!=vnon:
        cats.append("REORDER_OR_COMPACT")
    return tuple(cats)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    data=json.loads(Path(args.input).read_text())
    rows=data.get("rows",[])
    sigs=Counter(); slots=Counter(); exact=Counter(); by_label=Counter(); by_step=Counter()
    examples=defaultdict(list)
    total=0
    for ctx in rows:
        m=ctx.get("minimal_reproducer")
        if not m: continue
        label=m.get("label")
        by_label[label]+=1
        for r in m.get("applied_rows",[]):
            b=r.get("base_market",[]); v=r.get("v48_market",[])
            total+=1
            sig=signature(b,v)
            sigs[sig]+=1
            by_step[int(r.get("step",-1))]+=1
            exact[(json.dumps(b,sort_keys=True,separators=(",",":")),
                   json.dumps(v,sort_keys=True,separators=(",",":")))]+=1
            n=max(len(b),len(v))
            for i in range(n):
                bo=b[i] if i<len(b) else []
                vo=v[i] if i<len(v) else []
                slots[classify_slot(bo,vo)]+=1
            if len(examples[sig])<8:
                examples[sig].append({"step":r.get("step"),"base_market":b,"v48_market":v})
    top_sigs=[
        {"signature":list(k),"count":v,"examples":examples[k]}
        for k,v in sigs.most_common(25)
    ]
    top_exact=[
        {"count":v,"base_market":json.loads(k[0]),"v48_market":json.loads(k[1])}
        for k,v in exact.most_common(25)
    ]
    result={
        "schema":"kculture-v4d-market-transform-analysis-v1",
        "minimal_reproducer_contexts":sum(by_label.values()),
        "minimal_reproducer_label_counts":dict(by_label),
        "applied_market_turns_analyzed":total,
        "slot_transform_counts":dict(slots),
        "top_signatures":top_sigs,
        "top_exact_pairs":top_exact,
        "top_steps":by_step.most_common(40),
        "automatic_kaggle_submission":False,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V4D_TRANSFORM_ANALYSIS",json.dumps({
        "minimal_reproducer_label_counts":dict(by_label),
        "applied_market_turns_analyzed":total,
        "slot_transform_counts":dict(slots),
        "top_signatures":[{"signature":x["signature"],"count":x["count"]} for x in top_sigs[:10]]
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
