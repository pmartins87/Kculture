"""Collect hosted Kaggriculture evidence for Kculture submissions via official CLI.

Requires KAGGLE_API_TOKEN in the environment. The collector lists every episode
for each submission, classifies outcomes from episode metadata when available,
and downloads replays sequentially for all losses/ties plus a bounded sample of
wins. It intentionally avoids parallel replay bursts.
"""
from __future__ import annotations

import argparse, json, os, subprocess, time
from pathlib import Path


def run_json(args):
    p=subprocess.run(args,check=True,text=True,capture_output=True)
    text=p.stdout.strip()
    if not text:
        raise RuntimeError(f"empty JSON output: {args}")
    return json.loads(text)


def norm_episode_list(obj):
    if isinstance(obj,list): return obj
    if isinstance(obj,dict):
        for k in ("episodes","items","results","data"):
            if isinstance(obj.get(k),list): return obj[k]
    raise RuntimeError(f"unrecognized episodes JSON shape: {type(obj)}")


def getv(d,*keys):
    for k in keys:
        if isinstance(d,dict) and k in d:return d[k]
    return None


def ep_id(ep):
    v=getv(ep,"id","episodeId","episode_id","Id","EpisodeId")
    return int(v) if v is not None else None


def outcome(ep,sid):
    agents=getv(ep,"agents","Agents") or []
    if not isinstance(agents,list):return "UNKNOWN",None
    mine=None;rewards=[];my_index=None
    for i,a in enumerate(agents):
        if not isinstance(a,dict):continue
        r=getv(a,"reward","Reward")
        try:r=float(r)
        except Exception:r=None
        if r is not None:rewards.append(r)
        sub=getv(a,"submissionId","submission_id","SubmissionId")
        try:sub=int(sub)
        except Exception:sub=None
        if sub==sid:
            mine=r;my_index=i
    if mine is None or not rewards:return "UNKNOWN",my_index
    best=max(r for r in rewards if r is not None)
    if mine<best:return "LOSS",my_index
    tied=sum(1 for r in rewards if r==best)>1
    return ("TIE" if tied else "WIN"),my_index


def sort_key(ep):
    for k in ("createTime","date","startedAt","endTime","id","episodeId"):
        v=getv(ep,k)
        if v is not None:return str(v)
    return ""


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--submission",action="append",required=True,help="label:id")
    ap.add_argument("--output",required=True)
    ap.add_argument("--win-sample",type=int,default=25)
    ap.add_argument("--max-replays",type=int,default=120)
    ap.add_argument("--delay",type=float,default=0.8)
    args=ap.parse_args()
    if not os.environ.get("KAGGLE_API_TOKEN"):
        raise SystemExit("KAGGLE_API_TOKEN is required")
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    summary={"schema_version":"authenticated-hosted-forensics-v1","submissions":{}}
    for spec in args.submission:
        label,sid_text=spec.split(":",1);sid=int(sid_text);sroot=root/label;sroot.mkdir(exist_ok=True)
        obj=run_json(["kaggle","competitions","episodes",str(sid),"--format","json","--quiet"])
        (sroot/"episodes.json").write_text(json.dumps(obj,indent=2,sort_keys=True),encoding="utf-8")
        eps=norm_episode_list(obj);rows=[]
        for ep in eps:
            eid=ep_id(ep)
            if eid is None:continue
            out,idx=outcome(ep,sid)
            rows.append({"episode_id":eid,"outcome":out,"agent_index":idx,"metadata":ep})
        rows.sort(key=lambda x:sort_key(x["metadata"]),reverse=True)
        losses=[r for r in rows if r["outcome"]=="LOSS"]
        ties=[r for r in rows if r["outcome"]=="TIE"]
        unknown=[r for r in rows if r["outcome"]=="UNKNOWN"]
        wins=[r for r in rows if r["outcome"]=="WIN"][:args.win_sample]
        selected=[];seen=set()
        for group in (losses,ties,unknown,wins):
            for r in group:
                if r["episode_id"] not in seen:
                    selected.append(r);seen.add(r["episode_id"])
                if len(selected)>=args.max_replays:break
            if len(selected)>=args.max_replays:break
        repdir=sroot/"replays";repdir.mkdir(exist_ok=True);downloaded=[];failed=[]
        for i,r in enumerate(selected):
            eid=r["episode_id"]
            p=subprocess.run(["kaggle","competitions","replay",str(eid),"-p",str(repdir),"-q"],text=True,capture_output=True)
            if p.returncode==0:downloaded.append(eid)
            else:failed.append({"episode_id":eid,"stderr":p.stderr[-1000:],"stdout":p.stdout[-1000:]})
            if i+1<len(selected):time.sleep(args.delay)
        compact=[{k:v for k,v in r.items() if k!="metadata"} for r in rows]
        (sroot/"index.json").write_text(json.dumps({"submission_id":sid,"episodes":compact,"selected_for_replay":[r["episode_id"] for r in selected],"downloaded":downloaded,"failed":failed},indent=2,sort_keys=True),encoding="utf-8")
        counts={k:sum(r["outcome"]==k for r in rows) for k in ("WIN","LOSS","TIE","UNKNOWN")}
        summary["submissions"][label]={"submission_id":sid,"episode_count":len(rows),"outcomes":counts,"selected":len(selected),"downloaded":len(downloaded),"failed":len(failed)}
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":main()
