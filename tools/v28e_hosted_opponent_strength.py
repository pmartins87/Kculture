#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,statistics
from collections import defaultdict
from pathlib import Path

def q(vals,p):
    vals=sorted(vals)
    if not vals:return None
    if len(vals)==1:return vals[0]
    x=(len(vals)-1)*p
    lo=int(x); hi=min(lo+1,len(vals)-1); f=x-lo
    return vals[lo]*(1-f)+vals[hi]*f

def load_csv(path):
    # Full Kaggle leaderboard downloads currently use a UTF-8 BOM and
    # title-cased headers (e.g. TeamName, Score). Normalize header names
    # mechanically; do not alter team-name values used for exact matching.
    text=Path(path).read_text(encoding="utf-8-sig",errors="replace")
    lines=[x for x in text.splitlines() if x.strip()]
    if not lines:
        raise SystemExit("leaderboard empty")
    reader=csv.DictReader(lines)
    field_map={str(k).strip().lower():k for k in (reader.fieldnames or []) if k}
    if "teamname" not in field_map or "score" not in field_map:
        raise SystemExit(f"leaderboard parse failed headers={reader.fieldnames}")
    team_key=field_map["teamname"]
    score_key=field_map["score"]
    out={}
    for r in reader:
        name=str(r.get(team_key,"")).strip()
        try: score=float(r.get(score_key))
        except Exception: continue
        if name and name not in out: out[name]=score
    return out

def find(root,name):
    hits=list(Path(root).rglob(name))
    if len(hits)!=1: raise SystemExit(f"expected exactly one {name}, found {len(hits)}")
    return hits[0]

def eid(g):
    try:return int(str(g.get("episode_id")))
    except Exception:return None

def score_rate(gs):
    return (sum(g["result"]=="W" for g in gs)+.5*sum(g["result"]=="T" for g in gs))/len(gs) if gs else None

def summarize(games,lb):
    mapped=[]; unmapped=[]
    for g in games:
        opp=str(g.get("opponent_team","")).strip()
        if opp in lb:
            mapped.append((g,lb[opp]))
        else: unmapped.append(opp)
    vals=[s for _,s in mapped]
    mg=[g for g,_ in mapped]
    bins=[
      ("lt1500",lambda x:x<1500),
      ("1500_1799",lambda x:1500<=x<1800),
      ("1800_2099",lambda x:1800<=x<2100),
      ("ge2100",lambda x:x>=2100),
    ]
    bout={}
    for name,pred in bins:
        xs=[g for g,s in mapped if pred(s)]
        bout[name]={
          "games":len(xs),
          "score_rate":score_rate(xs),
          "mean_margin":statistics.fmean([float(g["margin"]) for g in xs]) if xs else None,
        }
    return {
      "games_total":len(games),
      "unique_opponents_total":len({str(g.get("opponent_team","")).strip() for g in games}),
      "mapped_games":len(mapped),
      "mapping_game_coverage":len(mapped)/len(games) if games else 0,
      "mapped_unique_opponents":len({str(g.get("opponent_team","")).strip() for g,_ in mapped}),
      "unmapped_opponents":sorted(set(x for x in unmapped if x)),
      "mean_opponent_score":statistics.fmean(vals) if vals else None,
      "median_opponent_score":statistics.median(vals) if vals else None,
      "p25_opponent_score":q(vals,.25),
      "p75_opponent_score":q(vals,.75),
      "min_opponent_score":min(vals) if vals else None,
      "max_opponent_score":max(vals) if vals else None,
      "mapped_score_rate":score_rate(mg),
      "mapped_mean_margin":statistics.fmean([float(g["margin"]) for g in mg]) if mg else None,
      "by_opponent_score_bin":bout,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",required=True)
    ap.add_argument("--leaderboard",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    v=json.loads(find(args.artifact_root,"V47_SUMMARY.json").read_text())
    a=json.loads(find(args.artifact_root,"ALL3_SUMMARY.json").read_text())
    vg=[g for g in v.get("games",[]) if eid(g) is not None]
    ag=[g for g in a.get("games",[]) if eid(g) is not None]
    if not vg or not ag:raise SystemExit("missing games")
    vmin=min(eid(g) for g in vg); vmax=max(eid(g) for g in vg)
    aa=[g for g in ag if vmin<=eid(g)<=vmax]
    lb=load_csv(args.leaderboard)
    sv=summarize(vg,lb); sa=summarize(aa,lb)
    if sv["mapping_game_coverage"]<.60 or sa["mapping_game_coverage"]<.60:
        decision="V28E_MAPPING_INSUFFICIENT"
    else:
        dm=sa["mean_opponent_score"]-sv["mean_opponent_score"]
        dmed=sa["median_opponent_score"]-sv["median_opponent_score"]
        if dm>=100 and dmed>=100:
            decision="V28E_ALL3_FACED_MATERIALLY_STRONGER_POPULATION"
        elif dm<=-100 and dmed<=-100:
            decision="V28E_V47_FACED_MATERIALLY_STRONGER_POPULATION"
        else:
            decision="V28E_OPPONENT_STRENGTH_MIXED_OR_SMALL"
    out={
      "schema":"kculture-v28e-hosted-opponent-strength-attribution-v1",
      "identity_use":"offline forensic only; prohibited as runtime policy feature",
      "v47_submission_id":56466970,
      "all3_submission_id":56367770,
      "v47_episode_window":{"min":vmin,"max":vmax},
      "leaderboard_teams":len(lb),
      "v47":sv,
      "all3_aligned":sa,
      "difficulty_deltas_all3_minus_v47":{
        "mean_opponent_score":(sa["mean_opponent_score"]-sv["mean_opponent_score"]) if sa["mean_opponent_score"] is not None and sv["mean_opponent_score"] is not None else None,
        "median_opponent_score":(sa["median_opponent_score"]-sv["median_opponent_score"]) if sa["median_opponent_score"] is not None and sv["median_opponent_score"] is not None else None,
      },
      "decision":decision
    }
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V28E_RESULT",json.dumps(out,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
