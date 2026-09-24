#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
KEYS=("V47","A","B")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    docs=[]
    for p in Path(a.input_dir).rglob("*.json"):
        try:d=json.loads(p.read_text())
        except Exception:continue
        if d.get("schema")=="kculture-v31c-near-miss-confirmation-shard-v1":docs.append(d)
    rows=[r for d in docs for r in d.get("rows",[])];fails=[x for d in docs for x in d.get("failures",[])]
    srcs={r["opponent_sha"] for r in rows};expected=len(srcs)*6*2*4
    mech=(len(docs)==4 and 8<=len(srcs)<=12 and all(d.get("mechanical_pass") for d in docs) and not fails and len(rows)==expected)
    by={(r["opponent_sha"],int(r["seed"]),int(r["seat"]),r["policy"]):r for r in rows}
    contexts=sorted({(r["opponent_sha"],int(r["seed"]),int(r["seat"])) for r in rows})
    primary=[by[c+("PRIMARY",)] for c in contexts] if mech else []
    primary_rate=statistics.fmean(float(r["score"]) for r in primary) if primary else None
    summaries={}
    for key in KEYS:
      hz=[by[c+(key,)] for c in contexts] if mech else []
      standalone=statistics.fmean(float(r["score"]) for r in hz) if hz else None
      pair=[];improve=[];losswin=[];losstie=[];nonwinwin=[]
      for c,p,h in zip(contexts,primary,hz):
        ps=float(p["score"]);hs=float(h["score"])
        pair.append(max(ps,hs))
        if hs>ps:improve.append((c,p,h))
        if ps==0 and hs==1:losswin.append((c,p,h))
        if ps==0 and hs==0.5:losstie.append((c,p,h))
        if ps<1 and hs==1:nonwinwin.append((c,p,h))
      nonwin_margins=[float(h["margin"]) for p,h in zip(primary,hz) if float(p["score"])<1] if mech else []
      summaries[key]={
        "policy_ref":hz[0]["policy_ref"] if hz else None,"policy_sha":hz[0]["policy_sha"] if hz else None,
        "standalone_score_rate":standalone,"pair_score_rate":statistics.fmean(pair) if pair else None,
        "pair_score_delta_vs_primary":statistics.fmean(pair)-primary_rate if pair else None,
        "loss_to_hedge_win_conversions":len(losswin),"loss_to_hedge_tie_conversions":len(losstie),
        "nonwin_to_hedge_win_conversions":len(nonwinwin),"residual_improvements":len(improve),
        "rescue_source_breadth":len({x[0][0] for x in improve}),
        "rescue_seed_breadth":len({x[0][1] for x in improve}),
        "rescue_seats":sorted({x[0][2] for x in improve}),
        "mean_residual_hedge_margin":statistics.fmean(nonwin_margins) if nonwin_margins else None
      }
    v=summaries.get("V47")
    eligible=[]
    if mech:
      for key in ("A","B"):
        s=summaries[key]
        ok=(s["pair_score_rate"]>=v["pair_score_rate"]+0.03 and
            s["loss_to_hedge_win_conversions"]>=v["loss_to_hedge_win_conversions"]+3 and
            s["rescue_source_breadth"]>=v["rescue_source_breadth"] and
            s["rescue_seed_breadth"]>=v["rescue_seed_breadth"] and s["rescue_seats"]==[0,1])
        s["replacement_eligible"]=bool(ok)
        if ok:eligible.append((key,s))
      v["replacement_eligible"]=False
    if not mech:
      decision="V31C_MECHANICS_INVALID";selected=None
    elif eligible:
      eligible.sort(key=lambda kv:(-kv[1]["pair_score_rate"],-kv[1]["loss_to_hedge_win_conversions"],
                                   -kv[1]["rescue_source_breadth"],-kv[1]["rescue_seed_breadth"],
                                   -kv[1]["mean_residual_hedge_margin"],kv[1]["policy_sha"]))
      selected={"key":eligible[0][0],**eligible[0][1]};decision="V31C_SECOND_SLOT_REPLACEMENT_CONFIRMED"
    else:
      selected=None;decision="V31C_RETAIN_V47_CONFIRMED"
    out={"schema":"kculture-v31c-near-miss-confirmation-v1","mechanical_pass":mech,"decision":decision,
         "contexts":len(contexts),"opponents":len(srcs),"primary_score_rate":primary_rate,
         "summaries":summaries,"selected_candidate":selected,"failures":fails,"automatic_kaggle_submission":False}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V31C_RESULT",json.dumps({k:v for k,v in out.items() if k not in ("summaries","failures")},sort_keys=True))
    print("V31C_SUMMARIES",json.dumps(summaries,sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
