#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
      try:d=json.loads(p.read_text())
      except:continue
      if d.get("schema")=="kculture-v34a-cross-domain-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    modes=sorted({r["mode"] for r in rows});contexts=sorted({(r["opponent_sha"],int(r["seed"]),int(r["seat"])) for r in rows})
    mech=len(docs)==4 and not fails and len(modes)==16 and all(d.get("mechanical_pass") for d in docs)
    by={(r["opponent_sha"],int(r["seed"]),int(r["seat"]),r["mode"]):r for r in rows}
    b=[by[c+("FULL_P0",)] for c in contexts] if mech else []
    br=statistics.fmean(float(r["score"]) for r in b) if b else None
    summaries={};eligible=[]
    if mech:
      for mode in modes:
        z=[by[c+(mode,)] for c in contexts]
        ds=[float(x["score"])-float(y["score"]) for y,x in zip(b,z)]
        dm=[float(x["margin"])-float(y["margin"]) for y,x in zip(b,z)]
        cr=statistics.fmean(float(x["score"]) for x in z)
        pos=[(c,d) for c,d in zip(contexts,ds) if d>0];neg=[d for d in ds if d<0]
        s={"mode":mode,"score_rate":cr,"mean_paired_score_delta":statistics.fmean(ds),"mean_paired_margin_delta":statistics.fmean(dm),
           "positive_contexts":len(pos),"negative_contexts":len(neg),"positive_source_breadth":len({x[0][0] for x in pos}),
           "positive_seed_breadth":len({x[0][1] for x in pos}),"positive_seats":sorted({x[0][2] for x in pos})}
        ishy=mode.startswith("M_")
        ok=bool(ishy and cr>=br+0.10 and s["mean_paired_score_delta"]>=0.10 and s["positive_source_breadth"]>=4 and s["positive_seed_breadth"]>=3 and len(pos)>len(neg) and s["positive_seats"]==[0,1])
        s["eligible"]=ok;summaries[mode]=s
        if ok:eligible.append(s)
    if not mech:decision="V34A_MECHANICS_INVALID";selected=None
    elif eligible:
      eligible.sort(key=lambda s:(-s["score_rate"],-s["mean_paired_score_delta"],-s["mean_paired_margin_delta"],-s["positive_source_breadth"],-s["positive_seed_breadth"],s["mode"]))
      selected=eligible[0];decision="V34A_CROSS_DOMAIN_HYBRID_READY"
    else:selected=None;decision="V34A_NO_HIGH_UPSIDE_CROSS_DOMAIN_HYBRID"
    out={"schema":"kculture-v34a-cross-domain-result-v1","mechanical_pass":mech,"decision":decision,"contexts":len(contexts),
         "primary_score_rate":br,"summaries":summaries,"selected_candidate":selected,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V34A_RESULT",json.dumps(out,sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
