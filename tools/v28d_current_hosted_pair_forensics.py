#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, statistics
from collections import defaultdict
from pathlib import Path

def load_summary(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def eid(x):
    try: return int(str(x.get("episode_id")))
    except Exception: return None

def score(games):
    if not games: return None
    return (sum(g.get("result")=="W" for g in games)+0.5*sum(g.get("result")=="T" for g in games))/len(games)

def avg(games,key):
    vals=[float(g[key]) for g in games if g.get(key) is not None]
    return statistics.fmean(vals) if vals else None

def med(games,key):
    vals=[float(g[key]) for g in games if g.get(key) is not None]
    return statistics.median(vals) if vals else None

def basic(games):
    return {
      "games":len(games),
      "wins":sum(g.get("result")=="W" for g in games),
      "losses":sum(g.get("result")=="L" for g in games),
      "ties":sum(g.get("result")=="T" for g in games),
      "score_rate":score(games),
      "mean_margin":avg(games,"margin"),
      "median_margin":med(games,"margin"),
      "opponents_unique":len({g.get("opponent_team") for g in games}),
      "min_episode_id":min((eid(g) for g in games if eid(g) is not None),default=None),
      "max_episode_id":max((eid(g) for g in games if eid(g) is not None),default=None),
    }

def groups(games):
    d=defaultdict(list)
    for g in games:
        d[str(g.get("opponent_team"))].append(g)
    return d

def group_stats(gs):
    return {
      "games":len(gs),
      "wins":sum(g.get("result")=="W" for g in gs),
      "losses":sum(g.get("result")=="L" for g in gs),
      "ties":sum(g.get("result")=="T" for g in gs),
      "score_rate":score(gs),
      "mean_margin":avg(gs,"margin"),
      "median_margin":med(gs,"margin"),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v47-summary",required=True)
    ap.add_argument("--all3-summary",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    v=load_summary(args.v47_summary)
    a=load_summary(args.all3_summary)
    vg=[g for g in v.get("games",[]) if eid(g) is not None]
    ag=[g for g in a.get("games",[]) if eid(g) is not None]
    if not vg or not ag:
        raise SystemExit("missing resolved games")

    vmin=min(eid(g) for g in vg); vmax=max(eid(g) for g in vg)
    exact=[g for g in ag if vmin <= eid(g) <= vmax]
    mode="exact_v47_episode_id_range"
    aligned=exact
    if len(aligned)<20:
        aligned=[g for g in ag if eid(g)>=vmin]
        mode="all3_since_v47_min_episode"
    if len(aligned)<20:
        aligned=sorted(ag,key=eid)[-min(96,len(ag)):]
        mode="fallback_newest_all3_96"

    gv=groups(vg); ga=groups(aligned)
    common=sorted(set(gv)&set(ga))
    per=[]
    for opp in common:
        sv=group_stats(gv[opp]); sa=group_stats(ga[opp])
        per.append({
          "opponent_team":opp,
          "v47":sv,
          "all3":sa,
          "score_rate_delta_v47_minus_all3":(sv["score_rate"]-sa["score_rate"]) if sv["score_rate"] is not None and sa["score_rate"] is not None else None,
          "mean_margin_delta_v47_minus_all3":(sv["mean_margin"]-sa["mean_margin"]) if sv["mean_margin"] is not None and sa["mean_margin"] is not None else None,
        })

    def macro(key):
        vals=[]
        for x in per:
            vv=x["v47"][key]; aa=x["all3"][key]
            if vv is not None and aa is not None: vals.append(vv-aa)
        return statistics.fmean(vals) if vals else None

    common_v=[g for o in common for g in gv[o]]
    common_a=[g for o in common for g in ga[o]]
    bv=basic(vg); ba=basic(aligned)
    bcv=basic(common_v); bca=basic(common_a)
    out={
      "schema":"kculture-v28d-current-hosted-pair-forensics-v1",
      "identity_use":"offline forensic only; prohibited as runtime policy feature",
      "v47_submission_id":56466970,
      "all3_submission_id":56367770,
      "v47_episode_window":{"min":vmin,"max":vmax},
      "alignment_mode":mode,
      "v47_overall":bv,
      "all3_aligned":ba,
      "overall_deltas_v47_minus_all3":{
        "score_rate":bv["score_rate"]-ba["score_rate"],
        "mean_margin":bv["mean_margin"]-ba["mean_margin"],
      },
      "common_opponents":common,
      "common_opponent_count":len(common),
      "v47_only_opponents":sorted(set(gv)-set(ga)),
      "all3_only_opponents":sorted(set(ga)-set(gv)),
      "common_micro":{
        "v47":bcv,
        "all3":bca,
        "score_rate_delta_v47_minus_all3":bcv["score_rate"]-bca["score_rate"] if bcv["score_rate"] is not None and bca["score_rate"] is not None else None,
        "mean_margin_delta_v47_minus_all3":bcv["mean_margin"]-bca["mean_margin"] if bcv["mean_margin"] is not None and bca["mean_margin"] is not None else None,
      },
      "common_macro_deltas_v47_minus_all3":{
        "score_rate":macro("score_rate"),
        "mean_margin":macro("mean_margin"),
      },
      "per_common_opponent":per,
    }

    overall=out["overall_deltas_v47_minus_all3"]["score_rate"]
    macro_score=out["common_macro_deltas_v47_minus_all3"]["score_rate"]
    if len(common)>=3 and overall<=-0.10 and macro_score is not None and macro_score<=-0.08:
        decision="V28D_CURRENT_META_V47_UNDERPERFORMANCE_SIGNAL"
    elif overall>=0 and macro_score is not None and macro_score>=0:
        decision="V28D_NO_CURRENT_META_V47_UNDERPERFORMANCE_SIGNAL"
    else:
        decision="V28D_CURRENT_META_EVIDENCE_MIXED"
    out["decision"]=decision
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V28D_RESULT",json.dumps({
      "decision":decision,
      "alignment_mode":mode,
      "v47_overall":bv,
      "all3_aligned":ba,
      "overall_deltas":out["overall_deltas_v47_minus_all3"],
      "common_opponent_count":len(common),
      "common_macro_deltas":out["common_macro_deltas_v47_minus_all3"],
      "common_micro":out["common_micro"],
      "per_common_opponent":per,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
