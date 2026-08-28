"""Authenticated, resume-safe snapshot of current Kaggriculture ladder replays.

This tool independently implements the public Kaggle API workflow for:
leaderboard -> best team submission -> completed public episodes -> replay JSON.
API-method discovery and manifest-hardening ideas were informed by the public
MIT-licensed Seyamalam/Kaggriculture `scripts/leaderboard_benchmark.py` project;
this implementation is intentionally narrower and stores only provenance plus
raw public replays for later Kculture analyses.

Requires Kaggle authentication (prefer KAGGLE_API_TOKEN in CI). Never commit
credentials. Replays are kept under artifacts/ and should not be committed,
because competition data redistribution is restricted by the live rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kaggle.api.kaggle_api_extended import KaggleApi


def as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    fn=getattr(value,'to_dict',None)
    if callable(fn): return fn()
    raise TypeError(f'unsupported Kaggle API object {type(value)!r}')


def num(v,default=0.0):
    try:return float(v)
    except (TypeError,ValueError):return default


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def valid_replay(path:Path,episode_id:int)->bool:
    try:
        obj=json.loads(path.read_text())
        return int((obj.get('info') or {}).get('EpisodeId'))==int(episode_id) and isinstance(obj.get('steps'),list) and bool(obj['steps'])
    except Exception:return False


def leaderboard(api,competition,top):
    raw=api.competition_leaderboard_view(competition,page_size=top) or []
    out=[]
    for rank,item in enumerate(raw[:top],1):
        d=as_dict(item)
        out.append({'rank':rank,'team_id':int(d['teamId']),'team_name':str(d['teamName']),'leaderboard_rating':num(d.get('score')),'submission_date':d.get('submissionDate')})
    return out


def best_submission(api,team_id):
    raw=api.competition_team_submissions(team_id) or []
    rows=[as_dict(x) for x in raw]
    if not rows:return None
    best=max(rows,key=lambda d:(num(d.get('publicScore'),float('-inf')),str(d.get('dateSubmitted') or ''),int(d.get('id') or 0)))
    return {'submission_id':int(best['id']),'submission_rating':num(best.get('publicScore')),'submitted_at':best.get('dateSubmitted')}


def public_episodes(api,submission_id,limit):
    rows=[]
    for item in api.competition_list_episodes(submission_id) or []:
        d=as_dict(item)
        if d.get('state')!='COMPLETED' or d.get('type')!='EPISODE_TYPE_PUBLIC':continue
        agents=d.get('agents') or []
        if not any(int(a.get('submissionId') or -1)==submission_id for a in agents):continue
        rows.append(d)
    rows.sort(key=lambda d:(str(d.get('endTime') or d.get('createTime') or ''),int(d.get('id') or 0)),reverse=True)
    return rows[:limit]


def recorded_seats(ep,submission_id):
    seats=[]
    for i,a in enumerate(ep.get('agents') or []):
        if int(a.get('submissionId') or -1)==submission_id:seats.append(i)
    return seats


def download(api,episode_id,folder,refresh=False):
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/f'episode-{episode_id}-replay.json'
    if refresh or not valid_replay(path,episode_id):
        if path.exists():path.unlink()
        api.competition_episode_replay(episode_id,path=str(folder),quiet=True)
    if not valid_replay(path,episode_id):raise RuntimeError(f'invalid replay {episode_id}')
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--competition',default='kaggriculture')
    ap.add_argument('--top',type=int,default=10)
    ap.add_argument('--episodes-per-team',type=int,default=2)
    ap.add_argument('--output-dir',default='artifacts/top-ladder-snapshot')
    ap.add_argument('--refresh',action='store_true')
    args=ap.parse_args()
    root=Path(args.output_dir); root.mkdir(parents=True,exist_ok=True)
    api=KaggleApi(); api.authenticate()
    snapshot={'schema_version':'kculture-top-ladder-snapshot-v1','competition':args.competition,'captured_at_utc':datetime.now(timezone.utc).isoformat(),'top_requested':args.top,'episodes_per_team_requested':args.episodes_per_team,'teams':[],'errors':[]}
    for team in leaderboard(api,args.competition,args.top):
        rec=dict(team)
        try:
            sub=best_submission(api,team['team_id'])
            rec['best_submission']=sub; rec['episodes']=[]
            if sub:
                for ep in public_episodes(api,sub['submission_id'],args.episodes_per_team):
                    eid=int(ep['id']); path=download(api,eid,root/'replays',args.refresh)
                    rec['episodes'].append({'episode_id':eid,'recorded_seats':recorded_seats(ep,sub['submission_id']),'state':ep.get('state'),'type':ep.get('type'),'create_time':ep.get('createTime'),'end_time':ep.get('endTime'),'replay_path':str(path),'replay_sha256':sha256_file(path),'replay_bytes':path.stat().st_size})
        except Exception as exc:
            snapshot['errors'].append({'team_id':team['team_id'],'team_name':team['team_name'],'error':repr(exc)})
        snapshot['teams'].append(rec)
    snapshot['summary']={'teams':len(snapshot['teams']),'teams_with_submission':sum(bool(t.get('best_submission')) for t in snapshot['teams']),'episodes':sum(len(t.get('episodes') or []) for t in snapshot['teams']),'errors':len(snapshot['errors'])}
    (root/'snapshot.json').write_text(json.dumps(snapshot,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(snapshot['summary'],indent=2,sort_keys=True))
    if snapshot['errors']:raise SystemExit(2)

if __name__=='__main__':main()
