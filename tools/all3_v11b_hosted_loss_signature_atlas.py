#!/usr/bin/env python3
"""V11B hosted loss-signature atlas from mature ALL3 public replays.

Descriptive only.  This script intentionally separates:
- current ALL3 own-state/macro rigidity;
- public opponent-relative state signatures associated with hosted losses.

It does NOT infer causality and does not use opponent identity as a candidate feature.
"""
from __future__ import annotations
import argparse, collections, json, math, statistics
from pathlib import Path

TARGET="Paulo Martins"
CHECKPOINTS=[120,240,336,360,408,456,480,504,552,600,648,672,696,718]
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")

def crop_animal_counts(farm):
    c=collections.Counter()
    active=empty=locked=0
    for row in farm.get("tiles",[]) or []:
        for t in row:
            if t=="LOCKED":
                locked+=1
            elif t is None:
                empty+=1
            elif isinstance(t,dict):
                active+=1
                k=str(t.get("kind"))
                c[f"kind_{k}"]+=1
                if k=="PLANT":
                    c[f"crop_{t.get('crop')}"]+=1
                elif k=="PASTURE":
                    c[f"animal_{t.get('animal')}"]+=1
    c["active_tiles"]=active;c["empty_unlocked"]=empty;c["locked_tiles"]=locked
    return c

def cohort(margin):
    if -1000 <= margin < 0:return "close_loss"
    if 0 < margin <=1000:return "close_win"
    if margin <= -3000:return "severe_loss"
    if margin >= 3000:return "strong_win"
    return "mid"

def mean(xs):
    return statistics.fmean(xs) if xs else None

def stdev(xs):
    return statistics.stdev(xs) if len(xs)>=2 else 0.0

def effect(a,b):
    if not a or not b:return None
    va=statistics.variance(a) if len(a)>=2 else 0.0
    vb=statistics.variance(b) if len(b)>=2 else 0.0
    pooled=math.sqrt((va+vb)/2.0)
    return (mean(a)-mean(b))/pooled if pooled>0 else 0.0

def feature_row(d,path):
    names=(d.get("info") or {}).get("TeamNames") or []
    if TARGET not in names:return None
    t=names.index(TARGET);opp=1-t
    rewards=d.get("rewards") or [d["steps"][-1][0].get("reward"),d["steps"][-1][1].get("reward")]
    mine=float(rewards[t]); other=float(rewards[opp]); margin=mine-other
    result="W" if margin>0 else ("L" if margin<0 else "T")
    game={
      "file":path.name,"episode_id":str(d.get("id") or ""),
      "opponent_team":names[opp] if opp<len(names) else f"p{opp}",
      "seat":t,"margin":margin,"result":result,"cohort":cohort(margin),
      "checkpoints":{}
    }
    for step in CHECKPOINTS:
        if step>=len(d.get("steps") or []):continue
        obs=d["steps"][step][t].get("observation") or {}
        farms=obs.get("farms") or []
        if len(farms)!=2:continue
        own=farms[t];of=farms[opp]
        oc=crop_animal_counts(own);pc=crop_animal_counts(of)
        priv=obs.get("private") or {};shed=priv.get("shed") or {};prices=(obs.get("market") or {}).get("prices") or {}
        inventories=priv.get("inventories") or [];seeds=priv.get("seeds") or {}
        carried=sum(sum(max(0,int(v or 0)) for v in bag.values()) for bag in inventories if isinstance(bag,dict))
        feat={
          "own_money":float(own.get("money",0) or 0),
          "opp_money":float(of.get("money",0) or 0),
          "money_gap":float(own.get("money",0) or 0)-float(of.get("money",0) or 0),
          "own_hands":len(own.get("hands") or []),"opp_hands":len(of.get("hands") or []),
          "own_quads":len(own.get("unlocked_quadrants") or []),"opp_quads":len(of.get("unlocked_quadrants") or []),
          "own_active":int(oc["active_tiles"]),"opp_active":int(pc["active_tiles"]),
          "own_plants":int(oc["kind_PLANT"]),"opp_plants":int(pc["kind_PLANT"]),
          "own_pastures":int(oc["kind_PASTURE"]),"opp_pastures":int(pc["kind_PASTURE"]),
          "shed_units":sum(max(0,int(shed.get(x,0) or 0)) for x in PRODUCTS),
          "shed_value":sum(max(0,int(shed.get(x,0) or 0))*float(prices.get(x,0) or 0) for x in PRODUCTS),
          "carried_units":carried,
          "seed_units":sum(max(0,int(v or 0)) for v in seeds.values()),
        }
        for x in CROPS:
            feat[f"own_crop_{x}"]=int(oc[f"crop_{x}"])
            feat[f"opp_crop_{x}"]=int(pc[f"crop_{x}"])
            feat[f"crop_gap_{x}"]=int(oc[f"crop_{x}"]-pc[f"crop_{x}"])
        for x in ANIMALS:
            feat[f"own_animal_{x}"]=int(oc[f"animal_{x}"])
            feat[f"opp_animal_{x}"]=int(pc[f"animal_{x}"])
            feat[f"animal_gap_{x}"]=int(oc[f"animal_{x}"]-pc[f"animal_{x}"])
        feat["opp_carrot_adv"]=feat["opp_crop_CARROT"]>feat["own_crop_CARROT"]
        feat["opp_carrot_adv4_wheat_def4"]=(
          feat["opp_crop_CARROT"]-feat["own_crop_CARROT"]>=4
          and feat["own_crop_WHEAT"]-feat["opp_crop_WHEAT"]>=4
        )
        game["checkpoints"][str(step)]=feat
    return game

def cond_summary(games,step,key):
    rows=[]
    for g in games:
        f=g["checkpoints"].get(str(step))
        if f and bool(f.get(key)):rows.append(g)
    return {
      "support":len(rows),
      "losses":sum(g["result"]=="L" for g in rows),
      "wins":sum(g["result"]=="W" for g in rows),
      "ties":sum(g["result"]=="T" for g in rows),
      "loss_rate":sum(g["result"]=="L" for g in rows)/len(rows) if rows else None,
      "mean_margin":mean([float(g["margin"]) for g in rows]),
      "opponents_unique":len({g["opponent_team"] for g in rows}),
      "episodes":[{"episode_id":g["episode_id"],"file":g["file"],"opponent_team":g["opponent_team"],"margin":g["margin"]} for g in sorted(rows,key=lambda x:x["margin"])],
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--replay-root",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    games=[];failures=[]
    for p in sorted(Path(args.replay_root).glob("*.json")):
        try:
            d=json.loads(p.read_text())
            g=feature_row(d,p)
            if g:games.append(g)
        except Exception as exc:
            failures.append({"file":p.name,"error":f"{type(exc).__name__}: {exc}"})

    feature_names=[
      "money_gap","own_money","opp_money","own_quads","opp_quads","own_active","opp_active",
      "own_plants","opp_plants","own_pastures","opp_pastures","shed_units","shed_value","carried_units","seed_units",
      *[f"crop_gap_{x}" for x in CROPS],*[f"animal_gap_{x}" for x in ANIMALS],
    ]
    checkpoint_summary={}
    for step in CHECKPOINTS:
        loss=[g for g in games if g["result"]=="L" and str(step) in g["checkpoints"]]
        win=[g for g in games if g["result"]=="W" and str(step) in g["checkpoints"]]
        cl=[g for g in games if g["cohort"]=="close_loss" and str(step) in g["checkpoints"]]
        cw=[g for g in games if g["cohort"]=="close_win" and str(step) in g["checkpoints"]]
        effects=[]
        for f in feature_names:
            a=[float(g["checkpoints"][str(step)].get(f,0)) for g in loss]
            b=[float(g["checkpoints"][str(step)].get(f,0)) for g in win]
            d=effect(a,b)
            ca=[float(g["checkpoints"][str(step)].get(f,0)) for g in cl]
            cb=[float(g["checkpoints"][str(step)].get(f,0)) for g in cw]
            cd=effect(ca,cb)
            effects.append({
              "feature":f,"loss_mean":mean(a),"win_mean":mean(b),"std_effect_loss_minus_win":d,
              "close_loss_mean":mean(ca),"close_win_mean":mean(cb),"std_effect_close_loss_minus_close_win":cd
            })
        macro=collections.Counter()
        for g in games:
            f=g["checkpoints"].get(str(step))
            if not f:continue
            key=tuple([f[f"own_crop_{x}"] for x in CROPS]+[f[f"own_animal_{x}"] for x in ANIMALS]+[f["own_quads"]])
            macro[key]+=1
        checkpoint_summary[str(step)]={
          "loss_vs_win_top_effects":sorted(effects,key=lambda x:abs(x["std_effect_loss_minus_win"] or 0),reverse=True)[:12],
          "close_loss_vs_close_win_top_effects":sorted(effects,key=lambda x:abs(x["std_effect_close_loss_minus_close_win"] or 0),reverse=True)[:12],
          "own_macro_unique_profiles":len(macro),
          "own_macro_modal_count":macro.most_common(1)[0][1] if macro else 0,
          "own_macro_modal_share":macro.most_common(1)[0][1]/len(games) if macro and games else None,
          "own_macro_modal_profile":list(macro.most_common(1)[0][0]) if macro else None,
        }

    regimes={}
    for step in CHECKPOINTS:
        regimes[str(step)]={
          "opp_carrot_adv":cond_summary(games,step,"opp_carrot_adv"),
          "opp_carrot_adv4_wheat_def4":cond_summary(games,step,"opp_carrot_adv4_wheat_def4"),
        }

    first_carrot=[]
    for g in games:
        first=None
        for step in CHECKPOINTS:
            f=g["checkpoints"].get(str(step))
            if f and f["opp_carrot_adv"]:
                first=step;break
        if first is not None:first_carrot.append((g,first))
    by_cutoff={}
    for cutoff in [360,408,456,480,504,552,600,648,672,696]:
        rr=[g for g,s in first_carrot if s<=cutoff]
        by_cutoff[str(cutoff)]={
          "support":len(rr),"losses":sum(g["result"]=="L" for g in rr),"wins":sum(g["result"]=="W" for g in rr),
          "loss_rate":sum(g["result"]=="L" for g in rr)/len(rr) if rr else None,
          "mean_margin":mean([g["margin"] for g in rr]),
        }

    ready=False
    qualifying=[]
    for step in CHECKPOINTS:
        x=regimes[str(step)]["opp_carrot_adv"]
        if step<=600 and x["support"]>=8 and x["loss_rate"] is not None and x["loss_rate"]>=0.9:
            qualifying.append({"step":step,**x})
    if qualifying:ready=True

    result={
      "schema":"kculture-all3-v11b-hosted-loss-signature-atlas-v1",
      "descriptive_only":True,
      "causal_claim_authorized":False,
      "games":len(games),"wins":sum(g["result"]=="W" for g in games),"losses":sum(g["result"]=="L" for g in games),
      "ties":sum(g["result"]=="T" for g in games),
      "cohort_counts":dict(collections.Counter(g["cohort"] for g in games)),
      "checkpoints":CHECKPOINTS,
      "checkpoint_summary":checkpoint_summary,
      "public_regimes":regimes,
      "first_carrot_adv_by_cutoff":by_cutoff,
      "qualifying_public_regime_signals":qualifying,
      "decision":"V11B_PUBLIC_CROP_SHIFT_REGIME_SIGNAL" if ready else "V11B_NO_SIMPLE_PUBLIC_REGIME_SIGNAL",
      "failures":failures,
      "games_detail":games,
      "automatic_kaggle_submission":False,
      "runtime_identity_feature_allowed":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V11B_RESULT",json.dumps({
      "decision":result["decision"],"games":len(games),"wins":result["wins"],"losses":result["losses"],
      "failures":len(failures),"qualifying_signals":[
        {"step":x["step"],"support":x["support"],"losses":x["losses"],"wins":x["wins"],"loss_rate":x["loss_rate"],"mean_margin":x["mean_margin"]}
        for x in qualifying
      ],
      "first_carrot_adv_by_cutoff":by_cutoff,
      "step600_carrot_adv":regimes["600"]["opp_carrot_adv"],
      "step600_strict":regimes["600"]["opp_carrot_adv4_wheat_def4"],
      "step600_macro":checkpoint_summary["600"],
    },sort_keys=True))
    if failures:raise SystemExit(2)

if __name__=="__main__":main()
