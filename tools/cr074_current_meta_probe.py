"""CR074 — current hosted-meta probe for Kaggriculture.

Purpose: discover the newest public official daily episode datasets, freeze a
small current-meta corpus, summarize winner/loser behavior, and try to locate a
known Kculture hosted submission/episode. This is calibration evidence only;
it does not build or promote a strategy candidate.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import statistics
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import kagglehub

PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
CHECKPOINTS=(24,96,192,360,540,719)


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def download(handle:str,filename:str,out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f'missing {handle}:{filename}: {p}')
    return p


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def fnum(v:Any,default:float=0.0)->float:
    try:return float(v)
    except (TypeError,ValueError):return default


def dates_between(start:str,end:str)->list[str]:
    a=date.fromisoformat(start);b=date.fromisoformat(end)
    out=[]
    while a<=b:
        out.append(a.isoformat());a+=timedelta(days=1)
    return out


def tile_summary(farm:dict)->dict[str,int]:
    c=collections.Counter()
    for row in (farm or {}).get('tiles',[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get('kind')=='PLANT':c[f"crop_{tile.get('crop')}"]+=1
            if tile.get('kind')=='WEED':c['weeds']+=1
            if tile.get('animal'):c[f"animal_{tile.get('animal')}"]+=1
    return dict(c)


def checkpoint(obs:dict,player:int)->dict[str,Any]:
    farms=(obs or {}).get('farms') or []
    if len(farms)<2:return {}
    farm=farms[player] or {};t=tile_summary(farm)
    return {
        'money':fnum(farm.get('money')),
        'hands':len(farm.get('hands',[]) or []),
        'quadrants':len(farm.get('unlocked_quadrants',[]) or []),
        'weeds':int(t.get('weeds',0)),
        'crops':{x:int(t.get(f'crop_{x}',0)) for x in CROPS},
        'animals':{x:int(t.get(f'animal_{x}',0)) for x in ANIMALS},
    }


def action_stats(steps:list,player:int)->dict[str,Any]:
    market=collections.Counter();market_qty=collections.Counter();farm=collections.Counter();market_positions=collections.Counter()
    nonempty_turns=0
    for s in range(max(0,len(steps)-1)):
        try:act=steps[s+1][player].get('action')
        except Exception:act=None
        if not isinstance(act,dict):continue
        touched=False
        for pos,order in enumerate(act.get('market',[]) or []):
            if not (isinstance(order,list) and order):continue
            typ=str(order[0]);item=str(order[1]) if len(order)>1 else ''
            try:qty=max(0,int(order[2] or 0)) if len(order)>2 else 0
            except Exception:qty=0
            market[f'{typ}:{item}']+=1;market_qty[f'{typ}:{item}']+=qty;market_positions[f'{typ}:{item}:pos{pos}']+=1;touched=True
        for k,v in act.items():
            if k=='market':continue
            if v in (None,False,[],{},''):continue
            farm[str(k)]+=1;touched=True
        if touched:nonempty_turns+=1
    return {
        'nonempty_action_turns':nonempty_turns,
        'market_order_counts':dict(market),
        'market_quantity_totals':dict(market_qty),
        'market_position_counts':dict(market_positions),
        'farm_action_counts':dict(farm),
    }


def rewards(rep:dict)->list[float|None]:
    try:
        last=rep['steps'][-1]
        return [float(last[i].get('reward')) for i in (0,1)]
    except Exception:return [None,None]


def episode_summary(rep:dict,source_date:str,episode_id:str,manifest_row:dict|None=None)->dict[str,Any]:
    steps=rep.get('steps') or [];rw=rewards(rep)
    if len(steps)<2:return {'episode_id':episode_id,'source_date':source_date,'valid':False}
    winner=None
    if rw[0] is not None and rw[1] is not None:
        winner=0 if rw[0]>rw[1] else (1 if rw[1]>rw[0] else None)
    players=[]
    for p in (0,1):
        cps={}
        for t in CHECKPOINTS:
            if t>=len(steps):continue
            try:obs=steps[t][p].get('observation') or {}
            except Exception:obs={}
            cps[str(t)]=checkpoint(obs,p)
        players.append({'player':p,'reward':rw[p], 'is_winner':winner==p, 'actions':action_stats(steps,p), 'checkpoints':cps})
    info=rep.get('info') or {}
    return {
        'episode_id':episode_id,'source_date':source_date,'valid':True,'steps':len(steps),
        'winner':winner,'rewards':rw,'manifest':manifest_row or {},'info':info,'players':players,
    }


def row_contains_submission(row:dict,submission_id:str)->bool:
    needle=str(submission_id)
    return any(needle in str(v) for v in row.values())


def mean_metric(players:list[dict],keypath:list[str])->float|None:
    vals=[]
    for p in players:
        cur:Any=p
        try:
            for k in keypath:cur=cur[k]
            vals.append(float(cur))
        except Exception:pass
    return statistics.mean(vals) if vals else None


def aggregate(episodes:list[dict])->dict[str,Any]:
    winners=[];losers=[]
    for e in episodes:
        if not e.get('valid') or e.get('winner') is None:continue
        for p in e['players']:
            (winners if p['is_winner'] else losers).append(p)
    metrics={}
    for t in CHECKPOINTS:
        metrics[str(t)]={
            'winner_money_mean':mean_metric(winners,['checkpoints',str(t),'money']),
            'loser_money_mean':mean_metric(losers,['checkpoints',str(t),'money']),
            'winner_hands_mean':mean_metric(winners,['checkpoints',str(t),'hands']),
            'loser_hands_mean':mean_metric(losers,['checkpoints',str(t),'hands']),
            'winner_quadrants_mean':mean_metric(winners,['checkpoints',str(t),'quadrants']),
            'loser_quadrants_mean':mean_metric(losers,['checkpoints',str(t),'quadrants']),
        }
    def sum_counter(group:list[dict],field:str)->dict[str,int]:
        c=collections.Counter()
        for p in group:c.update(p.get('actions',{}).get(field,{}) or {})
        return dict(c)
    return {
        'decisive_episodes':len(winners),
        'checkpoint_means':metrics,
        'winner_market_order_counts':sum_counter(winners,'market_order_counts'),
        'loser_market_order_counts':sum_counter(losers,'market_order_counts'),
        'winner_market_quantity_totals':sum_counter(winners,'market_quantity_totals'),
        'loser_market_quantity_totals':sum_counter(losers,'market_quantity_totals'),
        'winner_farm_action_counts':sum_counter(winners,'farm_action_counts'),
        'loser_farm_action_counts':sum_counter(losers,'farm_action_counts'),
    }


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--start-date',default='2026-09-05')
    ap.add_argument('--end-date',default='2026-09-09')
    ap.add_argument('--top',type=int,default=30)
    ap.add_argument('--submission-id',default='56124705')
    ap.add_argument('--known-episode',default='107148813')
    ap.add_argument('--output-dir',required=True)
    args=ap.parse_args()
    root=Path(args.output_dir);root.mkdir(parents=True,exist_ok=True)
    available=[];manifest_meta={};manifest_matches=[]
    manifests={}
    for d in dates_between(args.start_date,args.end_date):
        handle=f'kaggle/kaggriculture-episodes-{d}'
        try:
            p=download(handle,'manifest.csv',root/'download'/d/'manifest')
            rows=read_csv(p);manifests[d]=rows;available.append(d)
            manifest_meta[d]={'rows':len(rows),'columns':list(rows[0].keys()) if rows else [],'sha256':sha256_file(p)}
            for r in rows:
                if row_contains_submission(r,args.submission_id):manifest_matches.append({'date':d,'row':r})
            print('AVAILABLE',d,len(rows))
        except Exception as exc:
            manifest_meta[d]={'error':repr(exc)};print('UNAVAILABLE',d,repr(exc))
    selected=available[-2:] if len(available)>=2 else available[-1:]
    episodes=[];download_errors=[]
    for d in selected:
        rows=sorted(manifests[d],key=lambda r:-fnum(r.get('avg_score')))
        for r in rows[:args.top]:
            eid=str(r.get('episode_id') or '')
            if not eid:continue
            try:
                p=download(f'kaggle/kaggriculture-episodes-{d}',f'{eid}.json',root/'download'/d/'episodes'/eid)
                rep=json.loads(p.read_text(encoding='utf-8'));episodes.append(episode_summary(rep,d,eid,r))
            except Exception as exc:download_errors.append({'date':d,'episode_id':eid,'error':repr(exc)})
    known=None
    for d in reversed(available):
        try:
            p=download(f'kaggle/kaggriculture-episodes-{d}',f'{args.known_episode}.json',root/'download'/d/'known'/args.known_episode)
            rep=json.loads(p.read_text(encoding='utf-8'));known=episode_summary(rep,d,args.known_episode,None);known['sha256']=sha256_file(p);break
        except Exception:pass
    payload={
        'schema_version':'kculture-cr074-current-meta-probe-v1','purpose':'hosted_current_meta_calibration_only',
        'requested_dates':dates_between(args.start_date,args.end_date),'available_dates':available,'selected_dates':selected,
        'top_per_date':args.top,'submission_id':args.submission_id,'known_episode':args.known_episode,
        'manifest_meta':manifest_meta,'manifest_submission_matches':manifest_matches,
        'episodes':episodes,'aggregate':aggregate(episodes),'known_episode_summary':known,
        'download_errors':download_errors,'automatic_strategy_promotion':False,'automatic_kaggle_submission':False,
    }
    (root/'summary.json').write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    lines=['# CR074 current hosted-meta probe','',f"Available dates: **{available}**",f"Selected dates: **{selected}**",f"Top episodes collected: **{len(episodes)}**",f"Manifest matches for submission {args.submission_id}: **{len(manifest_matches)}**",f"Known episode {args.known_episode} found: **{known is not None}**",'', 'Decision: calibration corpus only; no automatic strategy promotion.']
    (root/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    if not available:raise SystemExit('no current official daily dataset available in requested window')

if __name__=='__main__':main()
