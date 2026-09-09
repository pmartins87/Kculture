"""CR074 — dynamic current hosted-meta atlas from official Kaggriculture top episodes.

Research/diagnostic only. This script discovers the latest daily episode datasets
from kaggle/kaggriculture-episodes-index, downloads only the highest-avg-score
replays from each selected date, and compares winners with losers on public,
architecture-level features. It does not build or promote an agent.

Promotion discipline: a hypothesis may only be nominated when its winner-minus-
loser direction repeats on >=2 independently dated datasets. Identity is never
an agent feature.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import statistics
import tempfile
from pathlib import Path
from typing import Any

import kagglehub

PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
CHECKPOINTS=(24,72,144,288,432,576,696)


def num(v,default=0.0):
    try:
        x=float(v)
        return x if math.isfinite(x) else default
    except (TypeError,ValueError):
        return default


def get(o,k,d=None):
    try:return o.get(k,d)
    except AttributeError:
        try:return o[k]
        except Exception:return d


def download(handle:str,filename:str,out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file():raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def farm_counts(farm:dict)->collections.Counter:
    c=collections.Counter()
    for row in get(farm,"tiles",[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get("kind")=="PLANT" and tile.get("crop"):
                c[f"crop_{tile['crop']}"]+=1
            if tile.get("animal"):
                c[f"animal_{tile['animal']}"]+=1
            if tile.get("kind")=="WEED":c["weeds"]+=1
    return c


def farm_state(obs:dict,seat:int)->dict[str,float]:
    farms=get(obs,"farms",[]) or []
    farm=farms[seat] if seat<len(farms) else {}
    c=farm_counts(farm)
    out={
        "money":num(get(farm,"money",0)),
        "hands":float(len(get(farm,"hands",[]) or [])),
        "quads":float(len(get(farm,"unlocked_quadrants",[]) or [])),
        "weeds":float(c.get("weeds",0)),
    }
    for crop in CROPS:out[f"crop_{crop.lower()}"]=float(c.get(f"crop_{crop}",0))
    for animal in ANIMALS:out[f"animal_{animal.lower()}"]=float(c.get(f"animal_{animal}",0))
    return out


def obs_at(steps:list,seat:int,t:int)->dict:
    if not steps:return {}
    t=max(0,min(int(t),len(steps)-1))
    try:return (steps[t][seat].get("observation") or {})
    except Exception:return {}


def flatten_strings(v:Any):
    if isinstance(v,str):
        yield v
    elif isinstance(v,dict):
        for x in v.values():yield from flatten_strings(x)
    elif isinstance(v,(list,tuple)):
        for x in v:yield from flatten_strings(x)


def first_state_events(steps:list,seat:int)->dict[str,float|None]:
    if not steps:return {}
    base=farm_state(obs_at(steps,seat,0),seat)
    wanted={
        "first_hand_growth":lambda s:s["hands"]>base["hands"],
        "first_quad_growth":lambda s:s["quads"]>base["quads"],
    }
    for a in ANIMALS:wanted[f"first_{a.lower()}"]=lambda s,a=a:s[f"animal_{a.lower()}"]>0
    for c in CROPS:wanted[f"first_crop_{c.lower()}"]=lambda s,c=c:s[f"crop_{c.lower()}"]>0
    out={k:None for k in wanted}
    for t in range(len(steps)):
        st=farm_state(obs_at(steps,seat,t),seat)
        for k,fn in wanted.items():
            if out[k] is None and fn(st):out[k]=float(t)
        if all(v is not None for v in out.values()):break
    return out


def action_metrics(steps:list,seat:int)->dict[str,float]:
    c=collections.Counter()
    sell_qty=collections.Counter();buy_qty=collections.Counter()
    sell_orders=collections.Counter();buy_orders=collections.Counter()
    sell_pos=collections.defaultdict(list)
    phase_sell=collections.Counter()
    token_counts=collections.Counter()
    for t in range(max(0,len(steps)-1)):
        try:action=steps[t+1][seat].get("action") or {}
        except Exception:continue
        for tok in flatten_strings(action):token_counts[str(tok).upper()]+=1
        market=get(action,"market",[]) or []
        for pos,order in enumerate(market):
            if not(isinstance(order,(list,tuple)) and len(order)>=1):continue
            op=str(order[0]).upper();p=str(order[1]).upper() if len(order)>=2 else "UNKNOWN";q=max(0.0,num(order[2],0)) if len(order)>=3 else 0.0
            c["market_orders"]+=1;c[f"market_op_{op}"]+=1
            if op=="SELL":
                sell_qty[p]+=q;sell_orders[p]+=1;sell_pos[p].append(float(pos));phase_sell[(t//144,p)]+=q
            elif op in ("BUY","BUY_PRODUCT"):
                buy_qty[p]+=q;buy_orders[p]+=1
    out={"market_orders":float(c["market_orders"])}
    for p in PRODUCTS:
        out[f"sell_qty_{p.lower()}"]=float(sell_qty[p]);out[f"sell_orders_{p.lower()}"]=float(sell_orders[p])
        out[f"buy_qty_{p.lower()}"]=float(buy_qty[p]);out[f"buy_orders_{p.lower()}"]=float(buy_orders[p])
        out[f"sell_pos_mean_{p.lower()}"]=statistics.mean(sell_pos[p]) if sell_pos[p] else 0.0
        for phase in range(5):out[f"sell_p{phase}_{p.lower()}"]=float(phase_sell[(phase,p)])
    for tok in ("HIRE","BUY_LAND","DIG","PLANT","WATER","FEED","CARE","HARVEST"):
        out[f"token_{tok.lower()}"]=float(token_counts[tok])
    return out


def final_money(steps:list,seat:int)->float:
    for t in range(len(steps)-1,-1,-1):
        obs=obs_at(steps,seat,t)
        farms=get(obs,"farms",[]) or []
        if seat<len(farms) and get(farms[seat],"money",None) is not None:return num(get(farms[seat],"money",0))
    return 0.0


def player_record(date:str,episode_id:str,avg_score:float,steps:list,seat:int)->dict:
    rec={"date":date,"episode_id":episode_id,"avg_score":avg_score,"seat":seat,"final_money":final_money(steps,seat)}
    for cp in CHECKPOINTS:
        st=farm_state(obs_at(steps,seat,cp),seat)
        for k,v in st.items():rec[f"cp{cp}_{k}"]=v
    rec.update(first_state_events(steps,seat));rec.update(action_metrics(steps,seat))
    return rec


def median(vals):
    vals=[float(v) for v in vals if v is not None and math.isfinite(float(v))]
    return statistics.median(vals) if vals else None


def add_outcomes(rows:list[dict]):
    by=collections.defaultdict(list)
    for r in rows:by[(r["date"],r["episode_id"])].append(r)
    for pair in by.values():
        if len(pair)!=2:continue
        a,b=pair
        if a["final_money"]>b["final_money"]:a["outcome"]="winner";b["outcome"]="loser"
        elif b["final_money"]>a["final_money"]:b["outcome"]="winner";a["outcome"]="loser"
        else:a["outcome"]=b["outcome"]="tie"


def metric_names(rows:list[dict])->list[str]:
    blocked={"date","episode_id","avg_score","seat","outcome","final_money"}
    names=[]
    for k in sorted({k for r in rows for k in r}):
        if k in blocked:continue
        if any(isinstance(r.get(k),(int,float)) for r in rows):names.append(k)
    return names


def summarize_date(date:str,rows:list[dict],names:list[str])->dict:
    rr=[r for r in rows if r["date"]==date]
    win=[r for r in rr if r.get("outcome")=="winner"];lose=[r for r in rr if r.get("outcome")=="loser"]
    metrics={}
    for n in names:
        w=median([r.get(n) for r in win]);l=median([r.get(n) for r in lose])
        metrics[n]={"winner_median":w,"loser_median":l,"delta":None if w is None or l is None else w-l}
    return {"date":date,"players":len(rr),"winners":len(win),"losers":len(lose),"ties":sum(r.get("outcome")=="tie" for r in rr),"metrics":metrics}


def stable_signals(date_summaries:list[dict],names:list[str])->list[dict]:
    out=[]
    for n in names:
        vals=[]
        for d in date_summaries:
            m=d["metrics"].get(n) or {};diff=m.get("delta")
            if diff is None or abs(diff)<1e-12:continue
            base=abs(num(m.get("loser_median"),0))+1.0
            vals.append({"date":d["date"],"delta":float(diff),"relative":abs(float(diff))/base})
        if len(vals)<2:continue
        signs={1 if x["delta"]>0 else -1 for x in vals}
        if len(signs)!=1:continue
        mean_rel=statistics.mean(x["relative"] for x in vals)
        if mean_rel<0.05:continue
        out.append({"metric":n,"direction":"winner_higher" if vals[0]["delta"]>0 else "winner_lower","dates_supporting":len(vals),"mean_relative_effect":mean_rel,"per_date":vals})
    return sorted(out,key=lambda x:(x["dates_supporting"],x["mean_relative_effect"]),reverse=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--latest-dates",type=int,default=3);ap.add_argument("--top-per-date",type=int,default=12);ap.add_argument("--output-dir",required=True);args=ap.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kculture-cr074-") as td:
        root=Path(td)
        idx=read_csv(download("kaggle/kaggriculture-episodes-index","manifest.csv",root/"index"))
        idx=[r for r in idx if r.get("date") and r.get("daily_dataset_slug")]
        idx.sort(key=lambda r:r["date"])
        selected=idx[-max(2,args.latest_dates):]
        rows=[];source=[];errors=[]
        for ir in selected:
            date=ir["date"];slug=ir["daily_dataset_slug"];handle=slug if "/" in slug else f"kaggle/{slug}"
            try:manifest=read_csv(download(handle,"manifest.csv",root/date/"manifest"))
            except Exception as exc:
                errors.append({"date":date,"stage":"manifest","error":repr(exc)});continue
            ranked=sorted(manifest,key=lambda r:-num(r.get("avg_score"),float("-inf")))[:args.top_per_date]
            source.append({"date":date,"daily_dataset_slug":slug,"index_top_avg_score":num(ir.get("top_avg_score")),"index_median_avg_score":num(ir.get("median_avg_score")),"episodes_selected":len(ranked)})
            for mr in ranked:
                eid=str(mr.get("episode_id") or mr.get("id") or "")
                if not eid:continue
                try:
                    p=download(handle,f"{eid}.json",root/date/"episodes"/eid);rep=json.loads(p.read_text(encoding="utf-8"));steps=rep.get("steps") or []
                    if len(steps)<700:raise ValueError(f"short replay {len(steps)}")
                    for seat in (0,1):rows.append(player_record(date,eid,num(mr.get("avg_score")),steps,seat))
                except Exception as exc:errors.append({"date":date,"episode_id":eid,"stage":"replay","error":repr(exc)})
    if len({r["date"] for r in rows})<2:raise SystemExit(f"CR074 requires >=2 usable dates; errors={errors[:5]}")
    add_outcomes(rows);names=metric_names(rows);dates=sorted({r["date"] for r in rows});summaries=[summarize_date(d,rows,names) for d in dates];signals=stable_signals(summaries,names)
    payload={
        "schema_version":"kculture-cr074-current-hosted-meta-atlas-v1","purpose":"hosted_meta_architecture_discovery_only","source":"kaggle/kaggriculture-episodes-index","selected_index_rows":source,
        "dates":dates,"episodes_analyzed":len({(r['date'],r['episode_id']) for r in rows}),"players_analyzed":len(rows),"errors":errors,"checkpoints":CHECKPOINTS,
        "date_summaries":summaries,"stable_winner_loser_signals":signals[:40],
        "gate":{"minimum_independent_dates":2,"one_day_signal_can_promote":False,"candidate_build_allowed":bool(signals),"note":"A stable descriptive signal nominates a hypothesis only; causal local/mechanical validation is still required before any hosted candidate."},
    }
    (out/"atlas.json").write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    with (out/"player_rows.jsonl").open("w",encoding="utf-8") as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+"\n")
    md=["# CR074 — Current Hosted Meta Atlas","",f"Dates: **{', '.join(dates)}**",f"Episodes analyzed: **{payload['episodes_analyzed']}**",f"Player records: **{len(rows)}**",f"Replay errors: **{len(errors)}**","","## Stable winner-vs-loser architectural signals","","| Metric | Direction | Dates | Mean relative effect |","|---|---|---:|---:|"]
    for s in signals[:25]:md.append(f"| `{s['metric']}` | {s['direction']} | {s['dates_supporting']} | {s['mean_relative_effect']:.3f} |")
    if not signals:md.append("| none passed the frozen cross-date gate | — | — | — |")
    md += ["","## Gate","",f"Candidate-build gate: **{'OPEN FOR ONE HYPOTHESIS' if signals else 'CLOSED'}**","","A passing descriptive signal is not itself a strategy promotion. The next candidate must target one high-impact repeated mechanism and pass exact mechanical/causal validation before consuming a hosted slot."]
    (out/"atlas.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print("\n".join(md))

if __name__=="__main__":main()
