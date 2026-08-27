"""KEXP-039: exact terminal SELL timing in official high-Elo public replays.

Observational only. Uses corrected replay alignment: state t is paired with the
action stored on frame t+1. Measures SELL quantities and order slots at states
712..718 for winners and losers across recent official daily top episodes.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE="kaggle/kaggriculture-episodes-index"
DATES=("2026-08-23","2026-08-24","2026-08-25","2026-08-26")
START,END=712,718


def download(handle,filename,out):
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file(): raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as fh: return list(csv.DictReader(fh))


def final_rewards(rep):
    try:
        f=rep["steps"][-1]
        return [float(f[p].get("reward")) for p in (0,1)]
    except Exception: return [None,None]


def sell_rows(action):
    out=[]
    if not isinstance(action,dict): return out
    for slot,order in enumerate(action.get("market",[]) or []):
        if not (isinstance(order,list) and len(order)>=3 and order[0]=="SELL"): continue
        try: q=max(0,int(order[2] or 0))
        except Exception: q=0
        if q>0: out.append({"slot":slot,"item":str(order[1]),"qty":q})
    return out


def collect_date(date,top,root):
    handle=f"kaggle/kaggriculture-episodes-{date}"
    manifest=sorted(read_csv(download(handle,"manifest.csv",root/date/"manifest")),key=lambda r:-float(r["avg_score"]))[:top]
    players=[]
    for mr in manifest:
        eid=str(mr["episode_id"])
        rep=json.loads(download(handle,f"{eid}.json",root/date/"episodes"/eid).read_text(encoding="utf-8"))
        steps=rep.get("steps") or []; rewards=final_rewards(rep)
        if len(steps)<END+2 or any(r is None for r in rewards): continue
        best=max(rewards)
        names=(rep.get("info") or {}).get("TeamNames") or ["p0","p1"]
        for p in (0,1):
            events=[]
            for t in range(START,END+1):
                action=steps[t+1][p].get("action") or {}
                for row in sell_rows(action):
                    events.append({"state_step":t,**row})
            players.append({
                "date":date,"episode_id":eid,"player":p,"team":names[p] if p<len(names) else f"p{p}",
                "reward":rewards[p],"winner":rewards[p]==best,"events":events,
            })
    return players


def summarize(rows):
    out={}
    for cohort in ("winner","loser","all"):
        rr=rows if cohort=="all" else [r for r in rows if bool(r["winner"])==(cohort=="winner")]
        step_qty=collections.Counter(); step_orders=collections.Counter(); item_qty=collections.Counter(); step_item_qty=collections.Counter(); slot_qty=collections.Counter()
        episodes_with=collections.Counter()
        for r in rr:
            seen_steps=set()
            for e in r["events"]:
                t=e["state_step"]; q=e["qty"]
                step_qty[t]+=q; step_orders[t]+=1; item_qty[e["item"]]+=q; step_item_qty[f"{t}:{e['item']}"]+=q; slot_qty[e["slot"]]+=q; seen_steps.add(t)
            for t in seen_steps: episodes_with[t]+=1
        n=len(rr) or 1
        out[cohort]={
            "players":len(rr),
            "mean_sell_qty_by_state_step":{str(t):step_qty[t]/n for t in range(START,END+1)},
            "mean_sell_orders_by_state_step":{str(t):step_orders[t]/n for t in range(START,END+1)},
            "fraction_players_selling_by_state_step":{str(t):episodes_with[t]/n for t in range(START,END+1)},
            "total_item_qty":dict(sorted(item_qty.items())),
            "total_step_item_qty":dict(sorted(step_item_qty.items())),
            "total_slot_qty":dict(sorted(slot_qty.items())),
            "qty_717":step_qty[717],"qty_718":step_qty[718],
            "share_qty_717_of_717_718":step_qty[717]/(step_qty[717]+step_qty[718]) if step_qty[717]+step_qty[718] else None,
        }
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--top",type=int,default=20); ap.add_argument("--output",required=True); args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="kculture-kexp039-") as tmp:
        root=Path(tmp); idx=read_csv(download(INDEX_HANDLE,"manifest.csv",root/"index")); available={r["date"] for r in idx}
        missing=[d for d in DATES if d not in available]
        if missing: raise RuntimeError(f"dates absent from official index: {missing}")
        rows=[]
        for d in DATES: rows.extend(collect_date(d,args.top,root))
    by_date={d:summarize([r for r in rows if r["date"]==d]) for d in DATES}
    payload={"schema_version":"live-terminal-sell-timing-v1","alignment":"state t paired with action frame t+1","dates":list(DATES),"top_n_per_date":args.top,"window":[START,END],"overall":summarize(rows),"by_date":by_date,"players":rows}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"overall":payload["overall"],"by_date":by_date},indent=2,sort_keys=True))

if __name__=="__main__": main()
