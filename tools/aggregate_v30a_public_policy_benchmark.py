#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

def summary(rows):
    sc=[float(r["score"]) for r in rows];mg=[float(r["margin"]) for r in rows]
    return {"contexts":len(rows),"wins":sum(x==1 for x in sc),"ties":sum(x==.5 for x in sc),"losses":sum(x==0 for x in sc),
            "score_rate":statistics.fmean(sc),"mean_margin":statistics.fmean(mg),"median_margin":statistics.median(mg)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",required=True)
    ap.add_argument("--snapshot-result",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    docs=[]
    for p in sorted(Path(a.input_dir).rglob("*.json")):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v30a-public-persistent-policy-shard-v1":docs.append(d)
    snap=json.loads(Path(a.snapshot_result).read_text())
    failures=[x for d in docs for x in d.get("failures",[])]
    rows=[r for d in docs for r in d.get("rows",[])]
    candidates=docs[0]["candidates"] if docs else []
    opp_count=docs[0]["opponent_count"] if docs else 0
    expected=opp_count*4*2*len(candidates) if docs else 0
    mech=(len(docs)==4 and all(d.get("mechanical_pass") for d in docs) and not failures
          and snap.get("decision")=="V28B_FRONTIER_SNAPSHOT_READY"
          and len(rows)==expected
          and len({(r["opponent_sha"],r["seed"],r["seat"],r["candidate_key"]) for r in rows})==expected)

    by={}
    for key in candidates:
        rr=[r for r in rows if r["candidate_key"]==key]
        s=summary(rr) if rr else {}
        s["by_opponent"]={sha:summary([x for x in rr if x["opponent_sha"]==sha]) for sha in sorted({x["opponent_sha"] for x in rr})}
        s["by_seed"]={str(seed):summary([x for x in rr if int(x["seed"])==seed]) for seed in sorted({int(x["seed"]) for x in rr})}
        if key!="ALL3" and rr:
            s["candidate_sha"]=rr[0]["candidate_sha"];s["candidate_ref"]=rr[0]["candidate_ref"];s["candidate_rank"]=rr[0]["candidate_rank"]
        by[key]=s

    base={(r["opponent_sha"],int(r["seed"]),int(r["seat"])):r for r in rows if r["candidate_key"]=="ALL3"}
    paired={}
    eligible=[]
    for key in candidates:
        if key=="ALL3":continue
        rr=[r for r in rows if r["candidate_key"]==key]
        pos=neg=neu=0;sd=[];md=[];pos_seats=set()
        source_delta=defaultdict(list);seed_delta=defaultdict(list)
        for r in rr:
            b=base[(r["opponent_sha"],int(r["seed"]),int(r["seat"]))]
            d=float(r["score"])-float(b["score"]);m=float(r["margin"])-float(b["margin"])
            sd.append(d);md.append(m)
            if d>0:pos+=1;pos_seats.add(int(r["seat"]))
            elif d<0:neg+=1
            else:neu+=1
            source_delta[r["opponent_sha"]].append(d)
            seed_delta[int(r["seed"])].append(d)
        p={"positive_score_contexts":pos,"negative_score_contexts":neg,"neutral_contexts":neu,
           "mean_score_delta":statistics.fmean(sd),"mean_margin_delta":statistics.fmean(md),"median_margin_delta":statistics.median(md),
           "positive_source_breadth":sum(statistics.fmean(v)>0 for v in source_delta.values()),
           "positive_seed_breadth":sum(statistics.fmean(v)>0 for v in seed_delta.values()),
           "positive_seats":sorted(pos_seats)}
        paired[key]=p
        s=by[key];b=by.get("ALL3",{})
        ok=(mech and s.get("score_rate",0)>=b.get("score_rate",0)+.08 and p["mean_score_delta"]>=.08
            and p["positive_source_breadth"]>=4 and p["positive_seed_breadth"]>=3
            and p["positive_score_contexts"]>p["negative_score_contexts"] and p["positive_seats"]==[0,1])
        p["promotion_eligible"]=bool(ok)
        if ok:eligible.append(key)

    def rank_key(k):
        s=by[k];p=paired[k]
        return (-s["score_rate"],-p["mean_score_delta"],-p["mean_margin_delta"],int(s["candidate_rank"]),str(s["candidate_sha"]))
    eligible.sort(key=rank_key)
    winner=eligible[0] if eligible else None

    decision="V30A_MECHANICS_INVALID" if not mech else ("V30A_PUBLIC_PERSISTENT_POLICY_CANDIDATE_READY" if winner else "V30A_NO_PUBLIC_PERSISTENT_POLICY_ADVANTAGE")
    result={"schema":"kculture-v30a-public-persistent-policy-benchmark-v1","mechanical_pass":mech,"decision":decision,
            "snapshot_decision":snap.get("decision"),"opponent_count":opp_count,"candidate_count":len(candidates),
            "contexts_per_candidate":opp_count*4*2 if opp_count else 0,
            "summaries":by,"paired_vs_all3":paired,"eligible_candidates":eligible,
            "selected_candidate":None if winner is None else {"key":winner,**{x:by[winner][x] for x in ("candidate_sha","candidate_ref","candidate_rank","score_rate","mean_margin")},**paired[winner]},
            "rows":rows,"failures":failures,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V30A_RESULT",json.dumps({"mechanical_pass":mech,"decision":decision,"all3":by.get("ALL3"),"eligible_candidates":eligible,
          "selected_candidate":result["selected_candidate"],
          "public_summaries":{k:{"ref":v.get("candidate_ref"),"rank":v.get("candidate_rank"),"score_rate":v.get("score_rate"),"mean_margin":v.get("mean_margin"),"paired":paired.get(k)} for k,v in by.items() if k!="ALL3"},
          "failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
