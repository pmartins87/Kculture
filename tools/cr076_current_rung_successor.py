"""CR076 — analyze successor branches inside the current dominant replay rung.

Discovery/calibration only. Downloads the same recent official daily episode datasets
used by CR075, identifies the dominant exact 96-action cross-team rung, then compares
shared post-prefix continuations and winner/loser public-state checkpoints. Raw replay
or full action sequences are not written to output.
"""
from __future__ import annotations

import argparse, collections, csv, hashlib, json, statistics, tempfile
from pathlib import Path
from typing import Any
import kagglehub

PREFIX=96
SUCCESSOR_PREFIXES=(120,144,168,192)
CHECKPOINTS=(96,120,144,168,192,360,540,719)
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")


def download(handle:str, filename:str, out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file(): raise FileNotFoundError(f'missing {handle}:{filename}: {p}')
    return p


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open('r',encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))


def fnum(v:Any, default:float=0.0)->float:
    try:return float(v)
    except (TypeError,ValueError):return default


def canon_action(action:Any)->str:
    if not isinstance(action,dict): action={}
    return json.dumps(action,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def action_sequence(steps:list,player:int)->list[str]:
    out=[]
    for s in range(max(0,len(steps)-1)):
        try:a=steps[s+1][player].get('action')
        except Exception:a=None
        out.append(canon_action(a))
    return out


def digest(seq:list[str], n:int)->str:
    return hashlib.sha256('\n'.join(seq[:min(n,len(seq))]).encode('utf-8')).hexdigest()


def rewards(rep:dict)->list[float|None]:
    try:
        last=rep['steps'][-1]
        return [float(last[i].get('reward')) for i in (0,1)]
    except Exception:return [None,None]


def tile_counts(farm:dict)->collections.Counter:
    c=collections.Counter()
    for row in (farm or {}).get('tiles',[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get('kind')=='PLANT':c[f"crop_{tile.get('crop')}"]+=1
            if tile.get('kind')=='WEED':c['weeds']+=1
            if tile.get('animal'):c[f"animal_{tile.get('animal')}"]+=1
    return c


def public_checkpoint(obs:dict, player:int)->dict[str,float]:
    farms=(obs or {}).get('farms') or []
    if len(farms)<2:return {}
    own=farms[player] or {};opp=farms[1-player] or {};a=tile_counts(own);b=tile_counts(opp)
    d={
      'self_money':fnum(own.get('money')),'opp_money':fnum(opp.get('money')),
      'money_gap':fnum(own.get('money'))-fnum(opp.get('money')),
      'self_hands':len(own.get('hands',[]) or []),'opp_hands':len(opp.get('hands',[]) or []),
      'self_quads':len(own.get('unlocked_quadrants',[]) or []),'opp_quads':len(opp.get('unlocked_quadrants',[]) or []),
      'self_weeds':float(a.get('weeds',0)),'opp_weeds':float(b.get('weeds',0)),
    }
    for x in CROPS:
        d[f'self_crop_{x.lower()}']=float(a.get(f'crop_{x}',0));d[f'opp_crop_{x.lower()}']=float(b.get(f'crop_{x}',0))
    for x in ANIMALS:
        d[f'self_animal_{x.lower()}']=float(a.get(f'animal_{x}',0));d[f'opp_animal_{x.lower()}']=float(b.get(f'animal_{x}',0))
    return d


def trace_record(rep:dict,row:dict,date:str,eid:str,player:int)->dict[str,Any]:
    steps=rep.get('steps') or [];rw=rewards(rep);teams=(rep.get('info') or {}).get('TeamNames') or []
    team=str(teams[player]) if player<len(teams) else f'player{player}'
    win=None
    if rw[0] is not None and rw[1] is not None and rw[0]!=rw[1]:win=rw[player]>rw[1-player]
    seq=action_sequence(steps,player)
    cps={}
    for t in CHECKPOINTS:
        if t<len(steps):
            try:obs=steps[t][player].get('observation') or {}
            except Exception:obs={}
            cps[str(t)]=public_checkpoint(obs,player)
    return {'date':date,'episode_id':eid,'player':player,'team':team,'reward':rw[player],'win':win,
            'episode_avg_score':fnum(row.get('avg_score')),'seq':seq,'checkpoints':cps}


def branch_summary(items:list[dict], n:int)->list[dict[str,Any]]:
    groups=collections.defaultdict(list)
    for t in items:groups[digest(t['seq'],n)].append(t)
    rows=[]
    for h,g in groups.items():
        wins=[x for x in g if x['win'] is not None];teams=sorted({x['team'] for x in g})
        rows.append({'prefix_len':n,'hash':h,'traces':len(g),'distinct_teams':len(teams),'teams':teams,
                     'dates':dict(collections.Counter(x['date'] for x in g)),
                     'wins':sum(bool(x['win']) for x in wins),'decisive':len(wins),
                     'win_rate':sum(bool(x['win']) for x in wins)/len(wins) if wins else None,
                     'mean_reward':statistics.mean([x['reward'] for x in g if x['reward'] is not None]),
                     'mean_episode_avg_score':statistics.mean(x['episode_avg_score'] for x in g)})
    rows.sort(key=lambda r:(-r['traces'],-r['distinct_teams'],-(r['win_rate'] or 0)))
    return rows


def checkpoint_contrast(items:list[dict])->dict[str,Any]:
    out={}
    for t in CHECKPOINTS:
        key=str(t);win=[x['checkpoints'].get(key,{}) for x in items if x['win'] is True];loss=[x['checkpoints'].get(key,{}) for x in items if x['win'] is False]
        feats=sorted({k for d in win+loss for k in d})
        rec={}
        for f in feats:
            w=[fnum(d.get(f)) for d in win if f in d];l=[fnum(d.get(f)) for d in loss if f in d]
            if w and l:rec[f]={'winner_mean':statistics.mean(w),'loser_mean':statistics.mean(l),'delta':statistics.mean(w)-statistics.mean(l),'winner_median':statistics.median(w),'loser_median':statistics.median(l)}
        out[key]=rec
    return out


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--dates',nargs='+',default=['2026-09-08','2026-09-09']);ap.add_argument('--top',type=int,default=40);ap.add_argument('--output',required=True);args=ap.parse_args()
    traces=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='kculture-cr076-') as tmp:
        root=Path(tmp)
        for d in args.dates:
            handle=f'kaggle/kaggriculture-episodes-{d}'
            rows=sorted(read_csv(download(handle,'manifest.csv',root/d/'manifest')),key=lambda r:-fnum(r.get('avg_score')))[:args.top]
            for row in rows:
                eid=str(row.get('episode_id') or '')
                try:
                    p=download(handle,f'{eid}.json',root/d/'episodes'/eid);rep=json.loads(p.read_text(encoding='utf-8'))
                    traces.extend(trace_record(rep,row,d,eid,p) for p in (0,1))
                except Exception as exc:errors.append({'date':d,'episode_id':eid,'error':repr(exc)})
    # Select dominant exact 96-action cross-team group with latest-date representation.
    g=collections.defaultdict(list)
    for t in traces:g[digest(t['seq'],PREFIX)].append(t)
    eligible=[]
    for h,items in g.items():
        teams={x['team'] for x in items};latest=sum(x['date']==args.dates[-1] for x in items)
        if len(teams)>=3 and latest>0:eligible.append((len(items),len(teams),latest,h,items))
    if not eligible:raise SystemExit('CR075 dominant exact rung not reproduced')
    eligible.sort(reverse=True,key=lambda x:(x[0],x[1],x[2]));_,_,_,rung_hash,rung=eligible[0]
    branches={str(n):branch_summary(rung,n) for n in SUCCESSOR_PREFIXES}
    # Frozen successor gate.
    candidates=[]
    for n in SUCCESSOR_PREFIXES:
        rows=branches[str(n)];comparables=[r for r in rows if r['traces']>=4]
        for r in comparables:
            others=[x for x in comparables if x['hash']!=r['hash']]
            best_other=max((x['win_rate'] for x in others if x['win_rate'] is not None),default=None)
            advantage=None if best_other is None or r['win_rate'] is None else r['win_rate']-best_other
            if r['traces']>=4 and r['distinct_teams']>=2 and r['dates'].get(args.dates[-1],0)>0 and (r['win_rate'] or 0)>=0.60 and advantage is not None and advantage>=0.20:
                candidates.append({**r,'advantage_vs_best_other':advantage})
    candidates.sort(key=lambda r:(-r['win_rate'],-r['advantage_vs_best_other'],-r['traces'],-r['prefix_len']))
    selected=candidates[0] if candidates else None
    rep=None
    if selected:
        members=[x for x in rung if digest(x['seq'],selected['prefix_len'])==selected['hash'] and x['date']==args.dates[-1] and x['win'] is True]
        if members:
            q=max(members,key=lambda x:(x['episode_avg_score'],x['reward']))
            rep={'date':q['date'],'episode_id':q['episode_id'],'player':q['player'],'team':q['team'],'reward':q['reward'],'episode_avg_score':q['episode_avg_score']}
    wins=sum(x['win'] is True for x in rung);losses=sum(x['win'] is False for x in rung)
    payload={'schema_version':'kculture-cr076-current-rung-successor-v1','purpose':'current_rung_successor_discovery_only','dates':args.dates,'top_per_date':args.top,
             'rung':{'exact_prefix_len':PREFIX,'hash':rung_hash,'traces':len(rung),'teams':sorted({x['team'] for x in rung}),'dates':dict(collections.Counter(x['date'] for x in rung)),'wins':wins,'losses':losses,'win_rate':wins/(wins+losses) if wins+losses else None},
             'successor_branches':branches,'winner_loser_checkpoint_contrast':checkpoint_contrast(rung),'qualified_successors':candidates,'selected_successor':selected,'representative_latest_winner':rep,'errors':errors,
             'decision_rule':{'qualify':'post-prefix exact branch at 120/144/168/192 with >=4 traces, >=2 teams, latest-date presence, win_rate>=0.60, and >=0.20 advantage over best comparable branch','if_qualified':'build one CR077 derivative around this successor, then fresh validation + hosted probe gate','if_none':'close replay-successor branch and move to winner-vs-loser residual/adaptive analysis'},
             'decision':'BUILD_CR077_CURRENT_RUNG_DERIVATIVE' if selected else 'SHIFT_TO_WINNER_LOSER_RESIDUAL','automatic_kaggle_submission':False,'automatic_strategy_promotion':False}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    md=['# CR076 current-rung successor analysis','',f"Dominant rung traces: **{len(rung)}**",f"Teams: **{sorted({x['team'] for x in rung})}**",f"Rung W-L: **{wins}-{losses}**",f"Qualified successor branches: **{len(candidates)}**",'',f"Decision: **{payload['decision']}**"]
    out.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print('\n'.join(md))

if __name__=='__main__':main()
