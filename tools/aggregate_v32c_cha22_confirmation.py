#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v32c-cha22-confirmation-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    srcs={r["opponent_sha"] for r in rows};contexts=sorted({(r["opponent_sha"],int(r["seed"]),int(r["seat"])) for r in rows if r["candidate"]=="PRIMARY"})
    mech=(len(docs)==4 and 8<=len(srcs)<=12 and all(d.get("mechanical_pass") for d in docs) and not fails and len(rows)==len(contexts)*2)
    by={(r["opponent_sha"],int(r["seed"]),int(r["seat"]),r["candidate"]):r for r in rows}
    b=[by[c+("PRIMARY",)] for c in contexts] if mech else [];h=[by[c+("CHA22",)] for c in contexts] if mech else []
    br=statistics.fmean(float(r["score"]) for r in b) if b else None
    hr=statistics.fmean(float(r["score"]) for r in h) if h else None
    ds=[float(x["score"])-float(y["score"]) for y,x in zip(b,h)] if mech else []
    dm=[float(x["margin"])-float(y["margin"]) for y,x in zip(b,h)] if mech else []
    pos=[(c,d) for c,d in zip(contexts,ds) if d>0];neg=[d for d in ds if d<0]
    source_b=len({x[0][0] for x in pos});seed_b=len({x[0][1] for x in pos});seats=sorted({x[0][2] for x in pos})
    confirmed=bool(mech and hr>=br+0.08 and statistics.fmean(ds)>=0.08 and source_b>=4 and seed_b>=4 and len(pos)>len(neg) and seats==[0,1])
    if not mech:decision="V32C_MECHANICS_INVALID"
    elif confirmed:decision="V32C_CHA22_PRIMARY_CONFIRMED"
    else:decision="V32C_CHA22_PRIMARY_NOT_CONFIRMED"
    out={"schema":"kculture-v32c-cha22-confirmation-v1","mechanical_pass":mech,"decision":decision,"contexts":len(contexts),"opponents":len(srcs),
         "primary_score_rate":br,"candidate_score_rate":hr,"mean_paired_score_delta":statistics.fmean(ds) if ds else None,
         "mean_paired_margin_delta":statistics.fmean(dm) if dm else None,"positive_contexts":len(pos),"negative_contexts":len(neg),
         "positive_source_breadth":source_b,"positive_seed_breadth":seed_b,"positive_seats":seats,
         "candidate_ref":"abhinav0370/kaggriculture-cha22-agent","candidate_sha":"127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652",
         "confirmed":confirmed,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V32C_RESULT",json.dumps(out,sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
