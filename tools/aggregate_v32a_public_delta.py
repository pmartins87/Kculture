#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--delta",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    delta=json.loads(Path(a.delta).read_text());nnew=int(delta["new_candidate_count"])
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v32a-public-delta-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    srcs={r["opponent_sha"] for r in rows};mech=(len(docs)==4 and all(d.get("mechanical_pass") for d in docs) and not fails and 8<=len(srcs)<=12)
    if nnew==0:
        decision="V32A_NO_NEW_PUBLIC_POLICY" if mech else "V32A_MECHANICS_INVALID"
        out={"schema":"kculture-v32a-public-delta-benchmark-v1","mechanical_pass":mech,"decision":decision,"new_candidate_count":0,
             "summaries":{},"selected_candidate":None,"automatic_kaggle_submission":False}
    else:
        contexts=sorted({(r["opponent_sha"],int(r["seed"]),int(r["seat"])) for r in rows if r["candidate"]=="PRIMARY"})
        by={(r["opponent_sha"],int(r["seed"]),int(r["seat"]),r["candidate"]):r for r in rows}
        expected=len(srcs)*4*2*(1+nnew)
        if len(rows)!=expected:mech=False
        primary=[by[c+("PRIMARY",)] for c in contexts] if mech else []
        br=statistics.fmean(float(r["score"]) for r in primary) if primary else None
        summaries={};eligible=[]
        for c in delta["new_candidates"]:
          key=c["sha"];z=[by[x+(key,)] for x in contexts] if mech else []
          ds=[float(h["score"])-float(b["score"]) for b,h in zip(primary,z)] if mech else []
          dm=[float(h["margin"])-float(b["margin"]) for b,h in zip(primary,z)] if mech else []
          pos=[(ctx,d) for ctx,d in zip(contexts,ds) if d>0];neg=[d for d in ds if d<0]
          s={"sha":key,"ref":c["ref"],"rank":c["rank"],"score_rate":statistics.fmean(float(r["score"]) for r in z) if z else None,
             "mean_paired_score_delta":statistics.fmean(ds) if ds else None,"mean_paired_margin_delta":statistics.fmean(dm) if dm else None,
             "positive_contexts":len(pos),"negative_contexts":len(neg),"positive_source_breadth":len({x[0][0] for x in pos}),
             "positive_seed_breadth":len({x[0][1] for x in pos}),"positive_seats":sorted({x[0][2] for x in pos})}
          ok=bool(mech and s["score_rate"]>=br+0.08 and s["mean_paired_score_delta"]>=0.08 and
                  s["positive_source_breadth"]>=4 and s["positive_seed_breadth"]>=3 and
                  s["positive_contexts"]>s["negative_contexts"] and s["positive_seats"]==[0,1])
          s["eligible"]=ok;summaries[key]=s
          if ok:eligible.append(s)
        if not mech:decision="V32A_MECHANICS_INVALID";selected=None
        elif eligible:
          eligible.sort(key=lambda s:(-s["score_rate"],-s["mean_paired_score_delta"],-s["mean_paired_margin_delta"],
                                      -s["positive_source_breadth"],-s["positive_seed_breadth"],s["rank"],s["sha"]))
          selected=eligible[0];decision="V32A_NEW_PUBLIC_POLICY_CANDIDATE_READY"
        else:selected=None;decision="V32A_NEW_PUBLIC_POLICIES_NO_ADVANTAGE"
        out={"schema":"kculture-v32a-public-delta-benchmark-v1","mechanical_pass":mech,"decision":decision,"new_candidate_count":nnew,
             "primary_score_rate":br,"summaries":summaries,"selected_candidate":selected,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V32A_RESULT",json.dumps(out,sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
