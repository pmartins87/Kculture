"""CR022A: build a behavior atlas from authenticated current-top public replays.

Input is the ignored artifact produced by collect_top_ladder_snapshot.py.
Outputs are analysis artifacts only: atlas.json plus training_rows.jsonl. Team and
submission identity are provenance/grouping fields, never model features.

Replay alignment is the frozen Kculture convention: observation state t ->
submitted action stored at replay frame t+1.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")


def get(o,k,d=None):
    try:return o.get(k,d)
    except AttributeError:
        try:return o[k]
        except Exception:return d


def num(v,d=0.0):
    try:
        x=float(v)
        return x if math.isfinite(x) else d
    except Exception:return d


def canon(v:Any)->str:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def digest(v:Any)->str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def farm_counts(farm):
    out=collections.Counter()
    for row in get(farm,"tiles",[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get("kind")=="PLANT" and tile.get("crop"):
                out[f"crop_{tile['crop']}"]+=1
            if tile.get("animal"):
                out[f"animal_{tile['animal']}"]+=1
            if tile.get("kind")=="WEED":out["weeds"]+=1
            out["yield_units"]+=num(tile.get("yield_units",0))
    return out


def public_features(obs,seat):
    farms=get(obs,"farms",[]) or []
    own=farms[seat] if seat<len(farms) else {}
    opp=farms[1-seat] if 1-seat<len(farms) else {}
    oc=farm_counts(own); pc=farm_counts(opp)
    market=get(obs,"market",{}) or {}; prices=get(market,"prices",{}) or {}; inv=get(market,"inventory",{}) or {}
    town=get(obs,"town",{}) or {}; shops=set(get(town,"unlocked_shops",[]) or [])
    try:
        raw=get(obs,"step",None)
        step=int(raw) if raw is not None else int(get(obs,"day",0) or 0)*24+int(get(obs,"hour",0) or 0)
    except Exception:step=0
    f={
        "step":step,"day":int(get(obs,"day",step//24) or 0),"hour":int(get(obs,"hour",step%24) or 0),
        "self_money":num(get(own,"money",0)),"opp_money":num(get(opp,"money",0)),
        "gap_money":num(get(own,"money",0))-num(get(opp,"money",0)),
        "self_hands":len(get(own,"hands",[]) or []),"opp_hands":len(get(opp,"hands",[]) or []),
        "self_quads":len(get(own,"unlocked_quadrants",[]) or []),"opp_quads":len(get(opp,"unlocked_quadrants",[]) or []),
        "shop_count":len(shops),
    }
    for p in PRODUCTS:
        f[f"market_price_{p.lower()}"]=num(get(prices,p,0))
        f[f"market_inventory_{p.lower()}"]=num(get(inv,p,0))
    for c in CROPS:
        f[f"self_crop_{c.lower()}"]=num(oc.get(f"crop_{c}",0)); f[f"opp_crop_{c.lower()}"]=num(pc.get(f"crop_{c}",0))
    for a in ANIMALS:
        f[f"self_animal_{a.lower()}"]=num(oc.get(f"animal_{a}",0)); f[f"opp_animal_{a.lower()}"]=num(pc.get(f"animal_{a}",0))
    for s in ("BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET"):
        f[f"shop_{s.lower()}"]=1 if s in shops else 0
    return f


def action_signature(action):
    a=action or {}
    return canon({"farmer":a.get("farmer"),"hands":a.get("hands") or [],"market":a.get("market") or []})


def physical_signature(action):
    a=action or {}
    return canon({"farmer":a.get("farmer"),"hands":a.get("hands") or []})


def market_signature(action):
    return canon((action or {}).get("market") or [])


def sell_rows(action,features):
    out=[]
    for pos,o in enumerate((action or {}).get("market") or []):
        if not(isinstance(o,list) and len(o)>=3 and o[0]=="SELL"):continue
        p=str(o[1]);q=int(num(o[2],0))
        out.append({"product":p,"quantity":q,"order_position":pos,"price":features.get(f"market_price_{p.lower()}",0),"inventory":features.get(f"market_inventory_{p.lower()}",0)})
    return out


def replay_path(snapshot_path,raw):
    p=Path(raw)
    if p.exists():return p
    # collector normally stores path relative to repository/workflow cwd
    candidates=[snapshot_path.parent/p.name, snapshot_path.parent/"replays"/p.name, Path.cwd()/p]
    for q in candidates:
        if q.exists():return q
    raise FileNotFoundError(raw)


def episode_records(snapshot_path,team,ep):
    path=replay_path(snapshot_path,ep["replay_path"]); rep=json.loads(path.read_text(encoding="utf-8")); steps=rep.get("steps") or []
    rows=[]
    for seat in ep.get("recorded_seats") or []:
        for t in range(max(0,len(steps)-1)):
            try:
                obs=(steps[t][seat].get("observation") or {}); action=(steps[t+1][seat].get("action") or {})
            except Exception:continue
            f=public_features(obs,seat); sells=sell_rows(action,f)
            rows.append({
                "rank":team.get("rank"),"team_id":team.get("team_id"),"team_name":team.get("team_name"),
                "submission_id":(team.get("best_submission") or {}).get("submission_id"),"episode_id":ep.get("episode_id"),"seat":seat,"t":t,
                "features":f,"action":action,"action_sig":action_signature(action),"physical_sig":physical_signature(action),"market_sig":market_signature(action),"sells":sells,
            })
    return rows


def modal_agreement(rows,field,horizon):
    by=collections.defaultdict(list)
    for r in rows:
        if r["t"]<horizon:by[r["t"]].append(r[field])
    match=total=variable_turns=0
    for vals in by.values():
        if len(vals)<2:continue
        c=collections.Counter(vals);match+=c.most_common(1)[0][1];total+=len(vals)
        variable_turns+=int(len(c)>1)
    return {"agreement":match/total if total else None,"comparable_actions":total,"variable_turns":variable_turns,"turns_compared":len(by)}


def entropy(vals):
    if not vals:return 0.0
    c=collections.Counter(vals);n=len(vals);return -sum((v/n)*math.log2(v/n) for v in c.values())


def summarize_team(team,rows):
    eps=sorted({r["episode_id"] for r in rows}); sells=[s|{"t":r["t"],"episode_id":r["episode_id"]} for r in rows for s in r["sells"]]
    byprod=collections.Counter(s["product"] for s in sells); qty=collections.defaultdict(list);pos=collections.defaultdict(list)
    for s in sells:qty[s["product"]].append(s["quantity"]);pos[s["product"]].append(s["order_position"])
    return {
        "rank":team.get("rank"),"team_id":team.get("team_id"),"team_name":team.get("team_name"),"leaderboard_rating":team.get("leaderboard_rating"),
        "submission":team.get("best_submission"),"episodes":eps,"action_rows":len(rows),
        "all_action_agreement_72":modal_agreement(rows,"action_sig",72),"all_action_agreement_144":modal_agreement(rows,"action_sig",144),"all_action_agreement_full":modal_agreement(rows,"action_sig",10**9),
        "physical_agreement_144":modal_agreement(rows,"physical_sig",144),"market_agreement_144":modal_agreement(rows,"market_sig",144),
        "action_entropy_bits":entropy([r["action_sig"] for r in rows]),"sell_orders":len(sells),"sell_by_product":dict(byprod),
        "sell_quantity_mean":{p:statistics.mean(v) for p,v in qty.items()},"sell_position_mean":{p:statistics.mean(v) for p,v in pos.items()},
        "opening72_hashes":sorted({digest([r["action_sig"] for r in rows if r["episode_id"]==e and r["t"]<72]) for e in eps}),
        "opening144_hashes":sorted({digest([r["action_sig"] for r in rows if r["episode_id"]==e and r["t"]<144]) for e in eps}),
    }


def training_row(r):
    # source_group is for split/provenance only and must never enter agent features.
    sells={s["product"]:{"quantity":s["quantity"],"position":s["order_position"]} for s in r["sells"]}
    return {"source_group":{"team_id":r["team_id"],"submission_id":r["submission_id"],"episode_id":r["episode_id"],"rank":r["rank"],"seat":r["seat"]},"t":r["t"],"features":r["features"],"targets":{"sell":sells,"market_action":r["action"].get("market") or []},"action":r["action"]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--snapshot",required=True);ap.add_argument("--output-dir",required=True);args=ap.parse_args()
    snap_path=Path(args.snapshot);snap=json.loads(snap_path.read_text(encoding="utf-8"));out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    all_rows=[];teams=[];errors=[]
    for team in snap.get("teams") or []:
        rows=[]
        for ep in team.get("episodes") or []:
            try:rows.extend(episode_records(snap_path,team,ep))
            except Exception as exc:errors.append({"team_id":team.get("team_id"),"episode_id":ep.get("episode_id"),"error":repr(exc)})
        if rows:teams.append(summarize_team(team,rows));all_rows.extend(rows)
    sell_events=[(r,s) for r in all_rows for s in r["sells"]]
    atlas={
        "schema_version":"kculture-top-ladder-behavior-atlas-v1","source_snapshot":str(snap_path),"source_capture":snap.get("captured_at_utc"),
        "summary":{"teams_analyzed":len(teams),"episodes_analyzed":len({r["episode_id"] for r in all_rows}),"state_action_rows":len(all_rows),"sell_orders":len(sell_events),"errors":len(errors)},
        "teams":teams,
        "global_sell_by_product":dict(collections.Counter(s["product"] for _,s in sell_events)),
        "errors":errors,
        "notes":["Identity fields are provenance/group keys only; never agent features.","Observation t is aligned to action frame t+1.","Agreement measures route rigidity within a current submission; low agreement is evidence of state response, not proof of optimal adaptation."],
    }
    (out/"atlas.json").write_text(json.dumps(atlas,indent=2,sort_keys=True),encoding="utf-8")
    with (out/"training_rows.jsonl").open("w",encoding="utf-8") as f:
        for r in all_rows:f.write(json.dumps(training_row(r),sort_keys=True)+"\n")
    print(json.dumps(atlas["summary"],indent=2,sort_keys=True))
    if errors and not all_rows:raise SystemExit(2)

if __name__=="__main__":main()
