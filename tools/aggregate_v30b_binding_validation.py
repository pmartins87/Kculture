#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
FROZEN_REF="arsgorynich/herd-safe-v3-experimental-risk-aware-feed"
FROZEN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
SEEDS=(80511,80512,80513,80514,80515,80516)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--preflight",required=True);ap.add_argument("--frontier-result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    pre=json.loads(Path(a.preflight).read_text());fr=json.loads(Path(a.frontier_result).read_text())
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v30b-binding-validation-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    sources=sorted({str(r["opponent_sha"]) for r in rows})
    expected=len(sources)*len(SEEDS)*2*2
    mech=(pre.get("mechanical_pass") and pre.get("parity_exact")==8 and fr.get("decision")=="V28B_FRONTIER_SNAPSHOT_READY"
          and 8<=len(sources)<=12 and len(docs)==4 and all(d.get("mechanical_pass") for d in docs) and not fails and len(rows)==expected)
    by={(r["opponent_sha"],int(r["seed"]),int(r["seat"]),r["candidate"]):r for r in rows}
    paired=[]
    if mech:
      for src in sources:
       for seed in SEEDS:
        for seat in (0,1):
         b=by[(src,seed,seat,"ALL3")];c=by[(src,seed,seat,"PUBLIC")]
         paired.append({"source":src,"seed":seed,"seat":seat,"score_delta":float(c["score"])-float(b["score"]),"margin_delta":float(c["margin"])-float(b["margin"])})
    def score_rate(k):
        z=[r for r in rows if r["candidate"]==k]
        return statistics.fmean(float(r["score"]) for r in z) if z else None
    bsr=score_rate("ALL3");csr=score_rate("PUBLIC")
    msd=statistics.fmean(x["score_delta"] for x in paired) if paired else None
    mmd=statistics.fmean(x["margin_delta"] for x in paired) if paired else None
    med=statistics.median(x["margin_delta"] for x in paired) if paired else None
    pos=[x for x in paired if x["score_delta"]>0];neg=[x for x in paired if x["score_delta"]<0]
    sb=len({x["source"] for x in pos});seedb=len({x["seed"] for x in pos});seats=sorted({x["seat"] for x in pos})
    eligible=bool(mech and csr>=bsr+0.05 and msd>=0.05 and sb>=4 and seedb>=4 and len(pos)>len(neg) and seats==[0,1])
    if not mech:decision="V30B_MECHANICS_INVALID"
    elif eligible:decision="V30B_PUBLIC_PERSISTENT_POLICY_VALIDATED_READY_FOR_USER_DECISION"
    else:decision="V30B_PUBLIC_PERSISTENT_POLICY_VALIDATION_FAIL"
    out={"schema":"kculture-v30b-binding-original-protocol-v1","decision":decision,"mechanical_pass":bool(mech),
         "candidate_ref":FROZEN_REF,"candidate_sha":FROZEN_SHA,"package_parity_pass":bool(pre.get("parity_exact")==8),
         "package_parity_exact":pre.get("parity_exact"),"archive_sha256":pre.get("archive_sha256"),
         "fresh_opponents":len(sources),"seeds":list(SEEDS),"seats":[0,1],"all3_score_rate":bsr,"candidate_score_rate":csr,
         "mean_paired_score_delta":msd,"mean_paired_margin_delta":mmd,"median_paired_margin_delta":med,
         "positive_contexts":len(pos),"negative_contexts":len(neg),"neutral_contexts":len(paired)-len(pos)-len(neg),
         "positive_source_breadth":sb,"positive_seed_breadth":seedb,"positive_seats":seats,"promotion_eligible":eligible,
         "failures":fails,"automatic_kaggle_submission":False}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V30B_BINDING_RESULT",json.dumps(out,sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
