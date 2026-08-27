"""Compare CR-008 vs frozen R4B on identical opponent/seed/seat tuples."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def load_one(root: str):
    files=list(Path(root).glob("*/tournament.json"))
    if len(files)!=1: raise RuntimeError(f"expected one tournament.json under {root}, got {files}")
    return json.loads(files[0].read_text(encoding="utf-8"))


def score(e):
    return 1.0 if e["outcome"]=="WIN" else 0.5 if e["outcome"]=="TIE" else 0.0 if e["outcome"]=="LOSS" else None


def mean(xs): return statistics.mean(xs) if xs else None


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-root",required=True); ap.add_argument("--base-root",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
    c=load_one(args.candidate_root); b=load_one(args.base_root)
    def key(e): return (e["opponent"],int(e["seed"]),int(e["candidate_seat"]))
    cm={key(e):e for e in c["episodes"]}; bm={key(e):e for e in b["episodes"]}
    keys=sorted(set(cm)&set(bm)); all_keys_equal=set(cm)==set(bm)
    pairs=[]
    for k in keys:
        ce,be=cm[k],bm[k]
        if ce["money_delta"] is None or be["money_delta"] is None: continue
        pairs.append({"opponent":k[0],"seed":k[1],"seat":k[2],"candidate_reward":ce["candidate_reward"],"base_reward":be["candidate_reward"],"self_reward_gain":float(ce["candidate_reward"])-float(be["candidate_reward"]),"candidate_money_delta":ce["money_delta"],"base_money_delta":be["money_delta"],"relative_delta_gain":float(ce["money_delta"])-float(be["money_delta"]),"candidate_score":score(ce),"base_score":score(be)})
    opponents=sorted({p["opponent"] for p in pairs})
    per={}
    for o in opponents:
        xs=[p for p in pairs if p["opponent"]==o]
        per[o]={"pairs":len(xs),"mean_self_reward_gain":mean([x["self_reward_gain"] for x in xs]),"mean_relative_delta_gain":mean([x["relative_delta_gain"] for x in xs]),"candidate_score_rate":mean([x["candidate_score"] for x in xs]),"base_score_rate":mean([x["base_score"] for x in xs]),"score_rate_gain":mean([x["candidate_score"]-x["base_score"] for x in xs])}
    self_gains=[p["self_reward_gain"] for p in pairs]; rel_gains=[p["relative_delta_gain"] for p in pairs]; score_gains=[p["candidate_score"]-p["base_score"] for p in pairs]
    positive_families=sum(1 for d in per.values() if d["mean_self_reward_gain"] is not None and d["mean_self_reward_gain"]>0)
    worst_family_score_gain=min((d["score_rate_gain"] for d in per.values()),default=None)
    gate={
      "complete_pair_coverage":all_keys_equal and len(pairs)==len(cm)==len(bm),
      "zero_errors":c["overall"]["errors"]==0 and b["overall"]["errors"]==0,
      "overall_mean_self_reward_gain_positive":bool(self_gains) and mean(self_gains)>0,
      "overall_mean_relative_delta_gain_positive":bool(rel_gains) and mean(rel_gains)>0,
      "positive_self_reward_families_ge_2":positive_families>=2,
      "overall_score_rate_not_worse_by_0_02":bool(score_gains) and mean(score_gains)>=-0.02,
      "no_family_score_rate_regression_gt_0_08":worst_family_score_gain is not None and worst_family_score_gain>=-0.08,
    }
    passed=all(gate.values())
    payload={"experiment":"CR-008-paired-current-meta","status":"ADAPTIVE_CAUSAL_FIELD_PASS" if passed else "ADAPTIVE_CAUSAL_FIELD_FAIL","candidate":c["candidate"],"base":b["candidate"],"pairs":len(pairs),"opponent_count":len(opponents),"summary":{"mean_self_reward_gain":mean(self_gains),"median_self_reward_gain":statistics.median(self_gains) if self_gains else None,"mean_relative_delta_gain":mean(rel_gains),"mean_score_rate_gain":mean(score_gains),"positive_self_reward_families":positive_families,"worst_family_score_rate_gain":worst_family_score_gain,"candidate_overall":c["overall"],"base_overall":b["overall"]},"per_opponent":per,"gate":gate,"paired_rows":pairs}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps({k:v for k,v in payload.items() if k!="paired_rows"},indent=2,sort_keys=True))
    if not passed: raise SystemExit(2)

if __name__=="__main__": main()
