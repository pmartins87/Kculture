#!/usr/bin/env python3
"""V17A deterministic extraction of recurrent W2 joint market-edit bundles."""
from __future__ import annotations
import argparse,collections,json,statistics
from pathlib import Path

REAL_PRODUCTS={"WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER"}

def normalize_element(e):
    kind=str(e.get("kind",""))
    direction=str(e.get("direction",""))
    if kind=="QTY":
        side=str(e.get("side",""));product=str(e.get("product",""));bucket=str(e.get("magnitude_bucket",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"QTY|SELL|{product}|{bucket}|{direction}"
    if kind=="PRESENCE":
        side=str(e.get("side",""));product=str(e.get("product",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"PRESENCE|SELL|{product}|{direction}"
    if kind=="DUPLICATE":
        side=str(e.get("side",""));product=str(e.get("product",""))
        if side!="SELL" or product not in REAL_PRODUCTS:return None
        return f"DUPLICATE|SELL|{product}|{direction}"
    if kind=="ORDER_COUNT":
        bucket=str(e.get("magnitude_bucket",""))
        return f"ORDER_COUNT|{bucket}|{direction}"
    if kind=="REORDER":
        return f"REORDER|{direction}"
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--atlas",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    d=json.loads(Path(args.atlas).read_text())
    if not d.get("mechanical_pass"):raise RuntimeError("binding V14B atlas not mechanically valid")

    recurrent_groups={str(x["group_key"]) for x in (d.get("recurrent_families") or []) if x.get("recurrent")}
    rows=[]
    for row in d.get("event_rows") or []:
        ev=row.get("event") or {}
        if ev.get("phase")!="W2":continue
        sigs=[]
        for e in ev.get("elementary") or []:
            if str(e.get("group_key","")) not in recurrent_groups:continue
            n=normalize_element(e)
            if n:sigs.append(n)
        sigs=sorted(set(sigs))
        if len(sigs)<2:continue
        key=" || ".join(sigs)
        rows.append({
          "bundle_key":key,
          "signatures":sigs,
          "context_id":row["context_id"],
          "main_sha256":row["main_sha256"],
          "turn":int(ev["turn"]),
          "rank":row.get("rank"),
        })

    groups=collections.defaultdict(list)
    for r in rows:groups[r["bundle_key"]].append(r)

    bundles=[]
    for key,rr in groups.items():
        contexts=sorted({x["context_id"] for x in rr})
        sources=sorted({x["main_sha256"] for x in rr})
        turns=[x["turn"] for x in rr]
        b={
          "bundle_key":key,
          "signatures":rr[0]["signatures"],
          "occurrences":len(rr),
          "context_support":len(contexts),
          "source_support":len(sources),
          "contexts":contexts,
          "source_shas":sources,
          "median_turn":statistics.median(turns) if turns else None,
          "turns":sorted(set(turns)),
        }
        b["recurrent"]=b["context_support"]>=4 and b["source_support"]>=2
        bundles.append(b)

    recurrent=[x for x in bundles if x["recurrent"]]
    recurrent.sort(key=lambda x:(
      -x["source_support"],-x["context_support"],-x["occurrences"],
      float(x["median_turn"] if x["median_turn"] is not None else 1e9),x["bundle_key"]
    ))
    selected=recurrent[0] if recurrent else None
    decision="V17A_W2_JOINT_MARKET_BUNDLE_READY" if selected else "V17A_W2_JOINT_MARKET_BUNDLE_NOT_COMPRESSIBLE"
    result={
      "schema":"kculture-all3-v17a-w2-joint-market-bundle-v1",
      "source_v14b_workflow":35526759114,
      "decision":decision,
      "eligible_event_rows":rows,
      "bundle_count":len(bundles),
      "recurrent_bundles":recurrent,
      "selected_bundle":selected,
      "outcomes_used_for_ranking":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V17A_RESULT",json.dumps({
      "decision":decision,"bundle_count":len(bundles),"recurrent_count":len(recurrent),
      "selected_bundle":selected,"eligible_event_count":len(rows)
    },sort_keys=True),flush=True)
    if selected is None:raise SystemExit(2)

if __name__=="__main__":main()
