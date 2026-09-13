#!/usr/bin/env python3
"""Read-only forensic summary for hosted Kaggriculture episode replays.

This script never contacts Kaggle and never mutates submissions. It reads replay JSON
files already downloaded by a workflow and attempts to locate the target submission
seat from replay metadata, then summarizes final rewards/margins.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def walk(obj: Any, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, path + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + (str(i),))
    else:
        yield path, obj


def find_target_paths(data: Any, target: str):
    out=[]
    for p,v in walk(data):
        s=str(v)
        if s == target or target in s:
            out.append(p)
    return out


def infer_seat(data: dict, target: str):
    # Common metadata layouts first.
    for key in ("agents", "submissions", "participants", "players"):
        arr=data.get(key)
        if isinstance(arr,list):
            for i,x in enumerate(arr):
                if target in json.dumps(x, default=str):
                    return i, f"top.{key}[{i}]"
    info=data.get("info")
    if isinstance(info,dict):
        for key,val in info.items():
            if isinstance(val,list):
                for i,x in enumerate(val):
                    if target in json.dumps(x, default=str):
                        return i, f"info.{key}[{i}]"
    # Generic heuristic: if a target occurrence sits under a numeric index 0/1,
    # prefer the nearest such index in the path.
    paths=find_target_paths(data,target)
    votes=[]
    for p in paths:
        nums=[int(x) for x in p if x in ("0","1")]
        if nums:
            votes.append(nums[-1])
    if votes and all(v==votes[0] for v in votes):
        return votes[0], "generic-path"
    return None, None


def final_rewards(data: dict):
    steps=data.get("steps")
    if not isinstance(steps,list) or not steps:
        return None
    final=steps[-1]
    if not isinstance(final,list) or len(final)<2:
        return None
    vals=[]
    for a in final[:2]:
        if isinstance(a,dict):
            vals.append(a.get("reward"))
        else:
            vals.append(None)
    if any(v is None for v in vals):
        return None
    try:
        return [float(v) for v in vals]
    except Exception:
        return None


def episode_id(path: Path, data: dict):
    for k in ("id","episodeId","episode_id"):
        if k in data:
            return str(data[k])
    digits=''.join(c for c in path.stem if c.isdigit())
    return digits or path.stem


def compact_metadata(data: dict):
    out={}
    for key in ("id","episodeId","agents","submissions","participants","players","info"):
        if key in data:
            v=data[key]
            text=json.dumps(v,default=str)
            if len(text)>3000:
                text=text[:3000]+"..."
            out[key]=text
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--replay-root",required=True)
    ap.add_argument("--target-submission",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    root=Path(args.replay_root)
    files=sorted(root.rglob("*.json"))
    rows=[]
    unresolved=[]
    for p in files:
        try:
            data=json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            unresolved.append({"file":str(p),"error":repr(e)})
            continue
        rewards=final_rewards(data)
        seat,seat_source=infer_seat(data,str(args.target_submission))
        eid=episode_id(p,data)
        rec={"episode_id":eid,"file":str(p),"seat":seat,"seat_source":seat_source,"rewards":rewards}
        if rewards is not None and seat in (0,1):
            margin=rewards[seat]-rewards[1-seat]
            rec.update({"target_reward":rewards[seat],"opponent_reward":rewards[1-seat],"margin":margin,"result":"W" if margin>0 else "L" if margin<0 else "T"})
            rows.append(rec)
        else:
            rec["target_paths"]=[list(x) for x in find_target_paths(data,str(args.target_submission))[:20]]
            rec["metadata_sample"]=compact_metadata(data)
            unresolved.append(rec)
    margins=[r["margin"] for r in rows]
    summary={
        "schema_version":"cr083-hosted-forensics-v1",
        "target_submission":str(args.target_submission),
        "replay_json_files":len(files),
        "resolved_games":len(rows),
        "unresolved_games":len(unresolved),
        "wins":sum(r["result"]=="W" for r in rows),
        "losses":sum(r["result"]=="L" for r in rows),
        "ties":sum(r["result"]=="T" for r in rows),
        "mean_margin":statistics.fmean(margins) if margins else None,
        "median_margin":statistics.median(margins) if margins else None,
        "worst":sorted(rows,key=lambda r:r["margin"])[:10],
        "best":sorted(rows,key=lambda r:r["margin"],reverse=True)[:10],
        "unresolved":unresolved[:5],
    }
    Path(args.output).write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
