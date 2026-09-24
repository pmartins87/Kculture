#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--census",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    census=json.loads(Path(a.census).read_text());n=int(census["selected_count"])
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
      try:d=json.loads(p.read_text())
      except:continue
      if d.get("schema")=="kculture-v33a-expanded-public-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    if n==0:
      mech=not fails and len(docs)==8
      decision="V33A_NO_NEW_EXPANDED_PUBLIC_POLICY" if mech else "V33A_MECHANICS_INVALID"
      out={"schema":"kculture-v33a-expanded-public-result-v1","mechanical_pass":mech,"decision":decision,"selected_count":0,"summaries":{},"selected_candidate":None,"automatic_kaggle_submission":False}
    else:
      cands=sorted({r["candidate_sha"] for r in rows if r["candidate_key"]=="CANDIDATE"})
      summaries={};eligible=[];mech=not fails and len(docs)==8 and len(cands)==n
      for sha in cands:
        z=[r for r in rows if r["candidate_sha"]==sha and r["candidate_key"]=="CANDIDATE"]
        ctx={(r["opponent_sha"],int(r["seed"]),int(r["seat"])):r for r in z}
        bz=[r for r in rows if r["candidate_key"]=="PRIMARY" and (r["opponent_sha"],int(r["seed"]),int(r["seat"])) in ctx]
        bmap={(r["opponent_sha"],int(r["seed"]),int(r["seat"])):r for r in bz}
        keys=sorted(ctx)
        if len(keys)==0 or any(k not in bmap for k in keys):mech=False;continue
        ds=[float(ctx[k]["score"])-float(bmap[k]["score"]) for k in keys]
        dm=[float(ctx[k]["margin"])-float(bmap[k]["margin"]) for k in keys]
        cr=statistics.fmean(float(ctx[k]["score"]) for k in keys);br=statistics.fmean(float(bmap[k]["score"]) for k in keys)
        pos=[(k,d) for k,d in zip(keys,ds) if d>0];neg=[d for d in ds if d<0]
        first=ctx[keys[0]]
        s={"sha":sha,"ref":first["candidate_ref"],"rank":int(first["candidate_rank"]),"score_rate":cr,"primary_score_rate":br,
           "mean_paired_score_delta":statistics.fmean(ds),"mean_paired_margin_delta":statistics.fmean(dm),
           "positive_contexts":len(pos),"negative_contexts":len(neg),"positive_source_breadth":len({x[0][0] for x in pos}),
           "positive_seed_breadth":len({x[0][1] for x in pos}),"positive_seats":sorted({x[0][2] for x in pos})}
        ok=bool(cr>=br+0.10 and s["mean_paired_score_delta"]>=0.10 and s["positive_source_breadth"]>=4 and s["positive_seed_breadth"]==3 and len(pos)>len(neg) and s["positive_seats"]==[0,1])
        s["eligible"]=ok;summaries[sha]=s
        if ok:eligible.append(s)
      if not mech:decision="V33A_MECHANICS_INVALID";selected=None
      elif eligible:
        eligible.sort(key=lambda s:(-s["score_rate"],-s["mean_paired_score_delta"],-s["mean_paired_margin_delta"],-s["positive_source_breadth"],s["rank"],s["sha"]))
        selected=eligible[0];decision="V33A_EXPANDED_PUBLIC_CHALLENGER_READY"
      else:selected=None;decision="V33A_EXPANDED_PUBLIC_NO_HIGH_UPSIDE"
      out={"schema":"kculture-v33a-expanded-public-result-v1","mechanical_pass":mech,"decision":decision,"selected_count":n,"summaries":summaries,"selected_candidate":selected,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"
")
    print("V33A_RESULT",json.dumps(out,sort_keys=True))
    if not out["mechanical_pass"]:raise SystemExit(2)
if __name__=="__main__":main()
