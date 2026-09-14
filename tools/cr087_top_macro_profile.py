"""CR087: profile macroeconomic structure of current top Kaggriculture replays.

Discovery-only. The script reads public replay JSONs and the previously frozen
`episodes.json`, then extracts state/action features for the top submission seat.
Identity/rank is metadata for offline comparison only, never a runtime feature.
"""
from __future__ import annotations
import argparse, collections, csv, json, math, statistics
from pathlib import Path

CROPS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS = ("GOOSE","COW","SHEEP")
PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
PREMIUM = ("CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL")


def private_total(private: dict, item: str) -> int:
    return int(private.get("shed",{}).get(item,0)) + sum(int(x.get(item,0)) for x in private.get("inventories",[]) or [])


def public_counts(farm: dict) -> dict:
    out=collections.Counter()
    for row in farm.get("tiles",[]):
        for tile in row:
            if not isinstance(tile,dict):
                continue
            kind=tile.get("kind")
            if kind=="PLANT": out[f"crop_{tile.get('crop')}"] += 1
            animal=tile.get("animal")
            if animal: out[f"animal_{animal}"] += 1
            if kind in ("PASTURE","COOP") and not animal: out[f"empty_{kind}"] += 1
    return out


def action_counter(action: dict) -> collections.Counter:
    c=collections.Counter()
    for cmd in [action.get("farmer"), *(action.get("hands") or [])]:
        if not isinstance(cmd,list) or not cmd: continue
        op=str(cmd[0]); key=f"phys:{op}"
        if op in ("PLANT","PICKUP","PLACE") and len(cmd)>1: key += f":{cmd[1]}"
        c[key]+=1
    for cmd in action.get("market") or []:
        if not isinstance(cmd,list) or not cmd: continue
        op=str(cmd[0]); key=f"market:{op}"
        if op in ("SELL","BUY_SEED","BUY_PRODUCT","BUY_ANIMAL") and len(cmd)>1: key += f":{cmd[1]}"
        qty=1
        if len(cmd)>2:
            try: qty=max(1,int(cmd[2]))
            except: qty=1
        c[key]+=qty if op in ("SELL","BUY_SEED","BUY_PRODUCT","BUY_ANIMAL") else 1
    return c


def snapshot(obs: dict, step: int, meta: dict) -> dict:
    seat=int(meta["seat"]); farm=obs["farms"][seat]; private=obs.get("private",{})
    c=public_counts(farm)
    row={
        "team_id":meta["team_id"],"team_name":meta["team_name"],"rank":meta["leaderboard_rank"],"score":meta["leaderboard_score"],
        "submission_id":meta["submission_id"],"episode_id":meta["episode_id"],"seat":seat,
        "step":step,"day":step//24,"hour":step%24,"money":float(farm.get("money",0)),
        "hands":len(farm.get("hands",[]) or []),"lands":len(farm.get("unlocked_quadrants",[]) or []),
    }
    for crop in CROPS: row[f"crop_{crop}"]=int(c.get(f"crop_{crop}",0))
    for animal in ANIMALS: row[f"animal_{animal}"]=int(c.get(f"animal_{animal}",0))
    row["animals_total"]=sum(row[f"animal_{a}"] for a in ANIMALS)
    row["crops_total"]=sum(row[f"crop_{x}"] for x in CROPS)
    for item in PREMIUM:
        row[f"own_{item}"]=private_total(private,item)
        row[f"price_{item}"]=int(obs.get("market",{}).get("prices",{}).get(item,0))
        row[f"marketinv_{item}"]=int(obs.get("market",{}).get("inventory",{}).get(item,0))
    return row


def med(xs):
    return statistics.median(xs) if xs else None


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--episodes",required=True); ap.add_argument("--replays-dir",required=True); ap.add_argument("--output-dir",required=True); args=ap.parse_args()
    metas=json.loads(Path(args.episodes).read_text()); replay_dir=Path(args.replays_dir); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    snapshots=[]; action_rows=[]; errors=[]
    for meta in metas:
        eid=int(meta["episode_id"]); seat=int(meta["seat"]); p=replay_dir/f"{eid}.json"
        try:
            rep=json.loads(p.read_text()); steps=rep.get("steps") or []
            if len(steps)<720: raise RuntimeError(f"short replay {len(steps)}")
            # beginning of each day plus terminal observation if available
            for step in list(range(0,720,24)):
                obs=steps[step][seat].get("observation") or {}
                snapshots.append(snapshot(obs,step,meta))
            dayc={d:collections.Counter() for d in range(30)}
            for t in range(719):
                a=(steps[t+1][seat] or {}).get("action") or {"farmer":["PASS"],"hands":[],"market":[]}
                dayc[t//24].update(action_counter(a))
            keys=sorted({k for c in dayc.values() for k in c})
            for d,c in dayc.items():
                r={"team_id":meta["team_id"],"team_name":meta["team_name"],"rank":meta["leaderboard_rank"],"score":meta["leaderboard_score"],"submission_id":meta["submission_id"],"episode_id":eid,"seat":seat,"day":d}
                r.update({k:int(c.get(k,0)) for k in keys}); action_rows.append(r)
        except Exception as exc:
            errors.append({"episode_id":eid,"submission_id":meta.get("submission_id"),"error":repr(exc)[:1000]})
    if not snapshots: raise RuntimeError("no replay snapshots parsed")
    # stable per-team median trajectory over the 3 sampled replays
    numeric=[k for k,v in snapshots[0].items() if isinstance(v,(int,float)) and k not in {"team_id","rank","submission_id","episode_id","seat","step","day","hour"}]
    teams=sorted({(r["team_id"],r["team_name"],r["rank"],r["score"]) for r in snapshots},key=lambda x:x[2])
    team_day=[]
    for tid,name,rank,score in teams:
        for day in range(30):
            rs=[r for r in snapshots if r["team_id"]==tid and r["day"]==day]
            if not rs: continue
            q={"team_id":tid,"team_name":name,"rank":rank,"score":score,"day":day,"replays":len(rs)}
            for k in numeric: q[k]=med([float(r[k]) for r in rs])
            team_day.append(q)
    # cross-top median and dispersion by day, useful for common macro structure
    top_day=[]
    for day in range(30):
        rs=[r for r in team_day if r["day"]==day]
        q={"day":day,"teams":len(rs)}
        for k in numeric:
            vals=[float(r[k]) for r in rs]
            q[f"{k}_median"]=med(vals); q[f"{k}_min"]=min(vals); q[f"{k}_max"]=max(vals)
        top_day.append(q)
    # aggregate action totals by team and phase (early/mid/late)
    phases={"early":range(0,10),"mid":range(10,20),"late":range(20,30)}
    action_keys=sorted({k for r in action_rows for k in r if k.startswith("phys:") or k.startswith("market:")})
    team_phase=[]
    for tid,name,rank,score in teams:
        for ph,days in phases.items():
            rs=[r for r in action_rows if r["team_id"]==tid and r["day"] in days]
            q={"team_id":tid,"team_name":name,"rank":rank,"score":score,"phase":ph,"replay_days":len(rs)}
            # median total across replays: sum each episode first, then median
            eids=sorted({r["episode_id"] for r in rs})
            for k in action_keys:
                totals=[sum(int(r.get(k,0)) for r in rs if r["episode_id"]==eid) for eid in eids]
                q[k]=med(totals) or 0
            team_phase.append(q)
    def dump_csv(path, rs):
        if not rs: return
        keys=[]
        for r in rs:
            for k in r:
                if k not in keys: keys.append(k)
        with Path(path).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rs)
    dump_csv(out/"snapshots.csv",snapshots); dump_csv(out/"team_day_medians.csv",team_day); dump_csv(out/"top_day_ranges.csv",top_day); dump_csv(out/"team_phase_actions.csv",team_phase)
    summary={"schema":"cr087-top-macro-profile-v1","episodes_requested":len(metas),"episodes_parsed":len({r['episode_id'] for r in snapshots}),"errors":errors,"teams":len(teams),"snapshot_rows":len(snapshots),"action_day_rows":len(action_rows),"outputs":["snapshots.csv","team_day_medians.csv","top_day_ranges.csv","team_phase_actions.csv"]}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)); print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__": main()
