#!/usr/bin/env python3
"""V16A deterministic W2 SELL-quantity phenotype selection from binding V14B atlas."""
from __future__ import annotations
import argparse,json
from pathlib import Path

BUCKET_MIN={"1":1,"2":2,"3-4":3,"5+":5}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--atlas",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    d=json.loads(Path(args.atlas).read_text())
    if not d.get("mechanical_pass"):raise RuntimeError("binding V14B atlas not mechanically valid")
    eligible=[]
    for f in d.get("recurrent_families") or []:
        g=str(f.get("group_key",""))
        parts=g.split("|")
        if len(parts)!=5:continue
        phase,kind,side,product,bucket=parts
        if phase!="W2" or kind!="QTY" or side!="SELL":continue
        if product in ("","_","EMPTY"):continue
        if bucket not in BUCKET_MIN:continue
        rep=f.get("representative_element") or {}
        if str(rep.get("kind"))!="QTY" or str(rep.get("side"))!="SELL":continue
        direction=str(f.get("dominant_direction"))
        if direction not in ("INC","DEC"):continue
        if int(f.get("context_support",0))<4 or int(f.get("source_support",0))<2 or float(f.get("direction_share",0))<0.75:continue
        x={
          "group_key":g,"product":product,"bucket":bucket,"direction":direction,
          "source_support":int(f["source_support"]),"context_support":int(f["context_support"]),
          "dominant_occurrences":int(f.get("dominant_occurrences",0)),
          "direction_share":float(f["direction_share"]),"median_turn":float(f["median_turn"]),
          "source_shas":f.get("source_shas") or [],"contexts":f.get("contexts") or [],
          "bucket_min_integer":BUCKET_MIN[bucket],
        }
        eligible.append(x)
    eligible.sort(key=lambda x:(-x["source_support"],-x["context_support"],x["median_turn"],x["group_key"]))
    selected=eligible[0] if eligible else None
    decision="V16A_W2_SELL_QUANTITY_PHENOTYPE_READY" if selected else "V16A_W2_SELL_QUANTITY_NOT_COMPRESSIBLE"
    result={
      "schema":"kculture-all3-v16a-w2-sell-quantity-v1",
      "source_v14b_workflow":35526759114,
      "decision":decision,
      "eligible_families":eligible,
      "selected_family":selected,
      "outcomes_used_for_ranking":False,
      "automatic_kaggle_submission":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V16A_RESULT",json.dumps({"decision":decision,"eligible_count":len(eligible),"selected_family":selected},sort_keys=True),flush=True)
    if selected is None:raise SystemExit(2)

if __name__=="__main__":main()
