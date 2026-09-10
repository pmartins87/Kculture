"""CR075 — fingerprint current Kaggriculture replay rungs.

Downloads recent official public episode datasets transiently, hashes ordered
action prefixes, and reports cross-team shared lineages. Raw replay/action data
are not written to the result. Calibration/discovery only; no automatic agent
promotion or submission.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import itertools
import json
import statistics
import tempfile
from pathlib import Path
from typing import Any

import kagglehub

PREFIXES=(1,8,24,48,96,192,360,719)


def download(handle:str,filename:str,out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file():raise FileNotFoundError(f'missing {handle}:{filename}: {p}')
    return p


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def fnum(v:Any,default:float=0.0)->float:
    try:return float(v)
    except (TypeError,ValueError):return default


def canon_action(action:Any,structural:bool=False)->str:
    if not isinstance(action,dict):action={}
    obj={}
    for k,v in sorted(action.items(),key=lambda kv:str(kv[0])):
        if k=='market' and isinstance(v,list):
            orders=[]
            for order in v:
                if not isinstance(order,list):
                    orders.append(order);continue
                if structural:
                    # Preserve order type/item and order position, remove numeric quantity.
                    orders.append(order[:2])
                else:orders.append(order)
            obj[k]=orders
        elif structural and k in ('farmer','hands'):
            # Keep the command/channel but normalize payload details.
            if isinstance(v,list):obj[k]=['*']*len(v)
            elif isinstance(v,dict):obj[k]=sorted(v.keys())
            else:obj[k]=bool(v)
        else:obj[k]=v
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def action_sequence(steps:list,player:int,structural:bool=False)->list[str]:
    seq=[]
    for s in range(max(0,len(steps)-1)):
        try:act=steps[s+1][player].get('action')
        except Exception:act=None
        seq.append(canon_action(act,structural))
    return seq


def digest(seq:list[str],n:int)->str:
    raw='\n'.join(seq[:min(n,len(seq))]).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def lcp(a:list[str],b:list[str])->int:
    n=min(len(a),len(b))
    for i in range(n):
        if a[i]!=b[i]:return i
    return n


def rewards(rep:dict)->list[float|None]:
    try:
        final=rep['steps'][-1]
        return [float(final[i].get('reward')) for i in (0,1)]
    except Exception:return [None,None]


def trace_record(rep:dict,row:dict,date:str,eid:str,player:int)->dict[str,Any]:
    steps=rep.get('steps') or [];info=rep.get('info') or {};teams=info.get('TeamNames') or []
    team=str(teams[player]) if player<len(teams) else f'player{player}'
    rw=rewards(rep);win=None
    if rw[0] is not None and rw[1] is not None and rw[0]!=rw[1]:win=(rw[player]>rw[1-player])
    exact=action_sequence(steps,player,False);struct=action_sequence(steps,player,True)
    return {
        'date':date,'episode_id':eid,'player':player,'team':team,'reward':rw[player],'win':win,
        'episode_avg_score':fnum(row.get('avg_score')),'length':len(exact),
        'exact_prefix_hash':{str(n):digest(exact,n) for n in PREFIXES},
        'struct_prefix_hash':{str(n):digest(struct,n) for n in PREFIXES},
        '_exact':exact,'_struct':struct,
    }


def prefix_groups(traces:list[dict],kind:str,n:int)->list[dict[str,Any]]:
    key=f'{kind}_prefix_hash';groups=collections.defaultdict(list)
    for t in traces:groups[t[key][str(n)]].append(t)
    out=[]
    for h,items in groups.items():
        teams=sorted({x['team'] for x in items})
        if len(teams)<2:continue
        wins=[x['win'] for x in items if x['win'] is not None]
        rewards=[x['reward'] for x in items if x['reward'] is not None]
        scores=[x['episode_avg_score'] for x in items]
        out.append({
            'hash':h,'prefix_len':n,'kind':kind,'traces':len(items),'distinct_teams':len(teams),'teams':teams,
            'win_rate':(sum(bool(x) for x in wins)/len(wins)) if wins else None,
            'mean_reward':statistics.mean(rewards) if rewards else None,
            'mean_episode_avg_score':statistics.mean(scores) if scores else None,
            'dates':dict(collections.Counter(x['date'] for x in items)),
        })
    out.sort(key=lambda x:(-x['distinct_teams'],-x['traces'],-(x['mean_episode_avg_score'] or 0)))
    return out


def pairwise_cross_team(traces:list[dict],kind:str)->dict[str,Any]:
    field='_exact' if kind=='exact' else '_struct'
    vals=[];best=[];by_pair=collections.defaultdict(list)
    for a,b in itertools.combinations(traces,2):
        if a['team']==b['team']:continue
        k=lcp(a[field],b[field]);vals.append(k)
        pair=tuple(sorted((a['team'],b['team'])));by_pair[pair].append(k)
        rec={'lcp':k,'team_a':a['team'],'team_b':b['team'],'date_a':a['date'],'date_b':b['date'],'episode_a':a['episode_id'],'episode_b':b['episode_id']}
        if len(best)<20 or k>best[-1]['lcp']:
            best.append(rec);best.sort(key=lambda x:-x['lcp']);best=best[:20]
    pair_rows=[]
    for pair,xs in by_pair.items():
        pair_rows.append({'teams':list(pair),'comparisons':len(xs),'max_lcp':max(xs),'median_lcp':statistics.median(xs),'mean_lcp':statistics.mean(xs)})
    pair_rows.sort(key=lambda x:(-x['max_lcp'],-x['median_lcp'],-x['comparisons']))
    return {
        'comparisons':len(vals),'median_lcp':statistics.median(vals) if vals else None,'mean_lcp':statistics.mean(vals) if vals else None,
        'max_lcp':max(vals) if vals else None,'top_cross_team_pairs':best,'team_pair_summary':pair_rows[:40],
    }


def team_summary(traces:list[dict])->list[dict[str,Any]]:
    by=collections.defaultdict(list)
    for t in traces:by[t['team']].append(t)
    out=[]
    for team,items in by.items():
        wins=[x['win'] for x in items if x['win'] is not None];rw=[x['reward'] for x in items if x['reward'] is not None]
        out.append({'team':team,'traces':len(items),'wins':sum(bool(x) for x in wins),'decisive':len(wins),'win_rate':sum(bool(x) for x in wins)/len(wins) if wins else None,'mean_reward':statistics.mean(rw) if rw else None,'dates':dict(collections.Counter(x['date'] for x in items))})
    out.sort(key=lambda x:(-x['traces'],-(x['win_rate'] or 0)))
    return out


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--dates',nargs='+',default=['2026-09-08','2026-09-09']);ap.add_argument('--top',type=int,default=40);ap.add_argument('--output',required=True);args=ap.parse_args()
    traces=[];errors=[];manifest_stats={}
    with tempfile.TemporaryDirectory(prefix='kculture-cr075-') as tmp:
        root=Path(tmp)
        for d in args.dates:
            handle=f'kaggle/kaggriculture-episodes-{d}'
            try:rows=sorted(read_csv(download(handle,'manifest.csv',root/d/'manifest')),key=lambda r:-fnum(r.get('avg_score')))[:args.top]
            except Exception as exc:
                errors.append({'date':d,'stage':'manifest','error':repr(exc)});continue
            manifest_stats[d]={'selected':len(rows),'max_avg_score':max((fnum(r.get('avg_score')) for r in rows),default=None),'min_avg_score':min((fnum(r.get('avg_score')) for r in rows),default=None),'mean_avg_score':statistics.mean([fnum(r.get('avg_score')) for r in rows]) if rows else None}
            for row in rows:
                eid=str(row.get('episode_id') or '')
                try:
                    p=download(handle,f'{eid}.json',root/d/'episodes'/eid);rep=json.loads(p.read_text(encoding='utf-8'))
                    if len(rep.get('steps') or [])<2:continue
                    traces.extend(trace_record(rep,row,d,eid,pidx) for pidx in (0,1))
                except Exception as exc:errors.append({'date':d,'episode_id':eid,'error':repr(exc)})
    # Results contain only hashes/statistics; strip action sequences.
    exact_groups={str(n):prefix_groups(traces,'exact',n)[:30] for n in PREFIXES}
    struct_groups={str(n):prefix_groups(traces,'struct',n)[:30] for n in PREFIXES}
    exact_pairs=pairwise_cross_team(traces,'exact');struct_pairs=pairwise_cross_team(traces,'struct')
    sanitized=[]
    for t in traces:
        sanitized.append({k:v for k,v in t.items() if not k.startswith('_')})
    strongest=[]
    for kind,groups in [('exact',exact_groups),('struct',struct_groups)]:
        for n,items in groups.items():
            for g in items:
                strongest.append({'kind':kind,**g})
    strongest.sort(key=lambda x:(-x['prefix_len'],-x['distinct_teams'],-x['traces']))
    payload={
        'schema_version':'kculture-cr075-current-rung-fingerprint-v1','purpose':'current_meta_lineage_discovery_only','dates':args.dates,'top_per_date':args.top,
        'manifest_stats':manifest_stats,'trace_count':len(traces),'teams':team_summary(traces),'errors':errors,
        'exact_prefix_groups':exact_groups,'struct_prefix_groups':struct_groups,'exact_pairwise':exact_pairs,'struct_pairwise':struct_pairs,
        'longest_shared_cross_team_groups':strongest[:40],
        'traces':sanitized,
        'decision_rule':{
            'dominant_rung_if':'cross-team exact or structural prefix >=96 actions shared by >=3 distinct teams, with representation in latest date',
            'if_dominant_rung':'use as temporal reference and perform causal divergence analysis versus current winners; do not submit unchanged public trace',
            'if_no_dominant_rung':'shift to adaptive winner-vs-loser state/action residual analysis rather than replay cloning',
        },
        'automatic_strategy_promotion':False,'automatic_kaggle_submission':False,
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    dom=[]
    for kind,groups in [('exact',exact_groups),('struct',struct_groups)]:
        for n,items in groups.items():
            for g in items:
                if int(n)>=96 and g['distinct_teams']>=3 and g['dates'].get(args.dates[-1],0)>0:dom.append(g)
    md=['# CR075 current replay-rung fingerprint','',f"Traces: **{len(traces)}**",f"Teams: **{len({t['team'] for t in traces})}**",f"Errors: **{len(errors)}**",f"Max exact cross-team LCP: **{exact_pairs['max_lcp']}**",f"Max structural cross-team LCP: **{struct_pairs['max_lcp']}**",f"Dominant-rung criterion hits: **{len(dom)}**",'', 'Decision: **'+('DOMINANT_RUNG_PRESENT' if dom else 'NO_DOMINANT_RUNG')+'**']
    out.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print('\n'.join(md))
    if errors and not traces:raise SystemExit('no usable traces')

if __name__=='__main__':main()
