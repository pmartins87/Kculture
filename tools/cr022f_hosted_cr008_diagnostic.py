"""CR022F: diagnose real hosted CR008 episodes without publishing raw replays.

Downloads recent public episodes for a submission using authenticated Kaggle API,
replays the frozen repo CR008 sequentially on stored observations, logs exact
adaptive append interventions by wrapping its frozen intervention function, and
summarizes triggers vs hosted W/L. Raw replay files remain temporary and are not
written to the repository/artifact output.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import statistics
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
CR008 = ROOT / "candidates/cr008_adaptive_frontrun.py"


def as_dict(value):
    if isinstance(value, dict): return value
    fn = getattr(value, "to_dict", None)
    if callable(fn): return fn()
    raise TypeError(type(value))


def load_cr008():
    spec = importlib.util.spec_from_file_location(f"cr022f_cr008_{time.time_ns()}", CR008)
    if spec is None or spec.loader is None: raise RuntimeError(CR008)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=True)


def outcome(delta):
    return "W" if delta > 0 else "L" if delta < 0 else "T"


def public_episodes(api, submission_id, limit):
    rows=[]
    for item in api.competition_list_episodes(int(submission_id)) or []:
        d=as_dict(item)
        if d.get("state")!="COMPLETED" or d.get("type")!="EPISODE_TYPE_PUBLIC": continue
        agents=d.get("agents") or []
        seats=[i for i,a in enumerate(agents) if int(a.get("submissionId") or -1)==int(submission_id)]
        if not seats: continue
        rows.append((d,seats[0]))
    rows.sort(key=lambda x:(str(x[0].get("endTime") or x[0].get("createTime") or ""),int(x[0].get("id") or 0)), reverse=True)
    return rows[:limit]


def download(api, episode_id, folder):
    api.competition_episode_replay(int(episode_id), path=str(folder), quiet=True)
    p=folder/f"episode-{int(episode_id)}-replay.json"
    if not p.exists(): raise RuntimeError(f"missing replay {episode_id}")
    return p


def num(v, default=0.0):
    try:
        x=float(v)
        return x if math.isfinite(x) else default
    except Exception:return default


def episode_analysis(path:Path, seat:int, episode_id:int):
    rep=json.loads(path.read_text(encoding="utf-8")); steps=rep.get("steps") or []
    if len(steps)<720: raise RuntimeError(f"short replay {episode_id}: {len(steps)}")
    final=steps[-1]; sr=num(final[seat].get("reward")); orr=num(final[1-seat].get("reward")); delta=sr-orr
    m=load_cr008(); trigger_log=[]
    orig=m._append_adaptive_sales

    def wrapped(obs, action, player, step):
        before=copy.deepcopy(action.get("market") or [])
        prev=m._HISTORY[player].get(step-24)
        probs={}
        if prev is not None:
            feat=m._public_features(obs,prev,player)
            if feat:
                names=m._MODELS["feature_names"]
                for target,item in m.TARGET_TO_ITEM.items():
                    probs[item]=m._tree_prob(m._MODELS["models"][target],feat,names)
        out=orig(obs,action,player,step)
        after=out.get("market") or []
        if len(after)>len(before):
            market=m._get(obs,"market",{}) or {}; prices=m._get(market,"prices",{}) or {}; inv=m._get(market,"inventory",{}) or {}
            farms=m._get(obs,"farms",[]) or []
            gap=None
            if len(farms)>=2:
                gap=num(m._get(farms[player],"money",0))-num(m._get(farms[1-player],"money",0))
            for pos in range(len(before),len(after)):
                order=after[pos]
                if isinstance(order,list) and len(order)>=3 and order[0]=="SELL":
                    item=str(order[1])
                    trigger_log.append({"step":int(step),"item":item,"qty":int(order[2]),"position":pos,"prob":probs.get(item),"price":num(m._get(prices,item,0)),"inventory":num(m._get(inv,item,0)),"money_gap":gap})
        return out
    m._append_adaptive_sales=wrapped

    mismatches=0; compared=0; mismatch_steps=[]
    for t in range(719):
        obs=steps[t][seat].get("observation") or {}
        actual=steps[t+1][seat].get("action") or {}
        predicted=m.agent(obs,None)
        compared+=1
        if canon(predicted)!=canon(actual):
            mismatches+=1
            if len(mismatch_steps)<10:mismatch_steps.append(t)
    return {"episode_id":episode_id,"seat":seat,"self_reward":sr,"opp_reward":orr,"delta":delta,"outcome":outcome(delta),"trigger_count":len(trigger_log),"triggers":trigger_log,"action_compared":compared,"action_mismatches":mismatches,"first_mismatch_steps":mismatch_steps}


def summarize(rows):
    byout={k:[r for r in rows if r["outcome"]==k] for k in ("W","L","T")}
    def trig_stats(xs):
        counts=[r["trigger_count"] for r in xs]
        events=[e for r in xs for e in r["triggers"]]
        byitem={}
        for item in sorted({e["item"] for e in events}):
            es=[e for e in events if e["item"]==item];qs=[e["qty"] for e in es]
            byitem[item]={"events":len(es),"qty_mean":statistics.mean(qs) if qs else None,"qty_median":statistics.median(qs) if qs else None}
        return {"episodes":len(xs),"zero_trigger_episodes":sum(c==0 for c in counts),"zero_trigger_fraction":sum(c==0 for c in counts)/len(xs) if xs else None,"mean_triggers_per_episode":statistics.mean(counts) if counts else None,"events":len(events),"by_item":byitem}
    seats={}
    for s in (0,1):
        xs=[r for r in rows if r["seat"]==s]
        seats[str(s)]={"episodes":len(xs),"wins":sum(r["outcome"]=="W" for r in xs),"losses":sum(r["outcome"]=="L" for r in xs),"ties":sum(r["outcome"]=="T" for r in xs),"action_mismatch_rate":sum(r["action_mismatches"] for r in xs)/sum(r["action_compared"] for r in xs) if xs else None,"episodes_with_any_action_mismatch":sum(r["action_mismatches"]>0 for r in xs)}
    return {"episodes":len(rows),"wins":len(byout["W"]),"losses":len(byout["L"]),"ties":len(byout["T"]),"by_outcome":{k:trig_stats(v) for k,v in byout.items()},"by_seat":seats,"overall":trig_stats(rows)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--submission-id",type=int,default=55866079);ap.add_argument("--limit",type=int,default=60);ap.add_argument("--output",required=True);args=ap.parse_args()
    api=KaggleApi();api.authenticate();rows=[];errors=[]
    with tempfile.TemporaryDirectory(prefix="kculture-cr022f-") as td:
        root=Path(td)
        for ep,seat in public_episodes(api,args.submission_id,args.limit):
            eid=int(ep["id"])
            try:rows.append(episode_analysis(download(api,eid,root),seat,eid))
            except Exception as exc:errors.append({"episode_id":eid,"seat":seat,"error":repr(exc)})
    payload={"experiment":"CR022F","submission_id":args.submission_id,"requested_limit":args.limit,"summary":summarize(rows),"errors":errors,"episodes":rows,"raw_replays_persisted":false,"identity_policy":"opponent identity is not used as a feature or gate"}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"experiment":"CR022F","submission_id":args.submission_id,"summary":payload["summary"],"error_count":len(errors)},indent=2,sort_keys=True))
    if errors and not rows: raise SystemExit(2)

if __name__=="__main__":main()
