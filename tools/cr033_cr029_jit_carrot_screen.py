"""CR033: causal JIT CARROT seed screen on the CR029 backbone.

The exact CR029 tape has six CARROT plant intents at 608,610,612,616,618,622,
while its late seed purchases are WHEAT-only.  At step 607 the frozen tape has
free market capacity.  This screen changes exactly one thing: if public CARROT
price makes one mature q=3 route positive and observed private CARROT seed stock
is below a fixed target, append one BUY_SEED CARROT row for the deficit.

Targets 1/3/6 are screened.  No plant action is changed: the frozen CR029 tape
naturally consumes any seed that arrives.  Uses only CR029's already-open 12
official source scenarios.  Fresh/held-out data remain untouched.
"""
from __future__ import annotations

import copy
import hashlib
import json
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'configs/cr031_elite_round_robin.json'
OUT=ROOT/'artifacts/cr033_cr029_jit_carrot_screen'
HANDLE='kaggle/kaggriculture-episodes-2026-09-05'
BUY_STEP=607
TARGETS=(1,3,6)
SEED_COST=20.0
YIELD_Q=3.0
MAX_MARKET_ORDERS=10


def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def tsha(t): return hashlib.sha256(canon(t).encode()).hexdigest()

def acts(rep,seat):
    st=rep.get('steps') or []
    return [copy.deepcopy((st[t][seat] or {}).get('action') or {}) for t in range(1,len(st))]

def get(o,k,d=None):
    try:return o.get(k,d)
    except Exception:
        try:return o[k]
        except Exception:return d

def step(obs):
    try:
        v=get(obs,'step',None)
        if v is not None:return max(0,int(v))
    except Exception:pass
    try:return max(0,int(get(obs,'day',0) or 0))*24+max(0,int(get(obs,'hour',0) or 0))
    except Exception:return 0

def carrot_seed_stock(obs):
    try:return max(0,int(get(get(get(obs,'private',{}) or {},'seeds',{}) or {},'CARROT',0) or 0))
    except Exception:return 0

def carrot_price(obs):
    try:
        v=float(get(get(get(obs,'market',{}) or {},'prices',{}) or {},'CARROT',0) or 0)
        return v if v>0 else None
    except Exception:return None

def tape_agent(tape):
    def agent(obs,config=None):
        s=max(0,min(718,step(obs)))
        return copy.deepcopy(tape[s])
    return agent

def jit_agent(tape,target,stats):
    def agent(obs,config=None):
        s=max(0,min(718,step(obs)))
        a=copy.deepcopy(tape[s])
        if s!=BUY_STEP:return a
        stats['observed']+=1
        stock=carrot_seed_stock(obs); price=carrot_price(obs)
        stats['stocks'].append(stock); stats['prices'].append(price)
        market=list(a.get('market') or [])
        # Cost is fixed 20; q=3 comes from prior mechanics experiments.  This
        # is deliberately a weak viability gate, not a fitted threshold.
        viable=price is not None and YIELD_Q*price-SEED_COST>0
        deficit=max(0,int(target)-stock)
        if viable and deficit>0 and len(market)<MAX_MARKET_ORDERS:
            market.append(['BUY_SEED','CARROT',deficit])
            a['market']=market
            stats['triggered']+=1; stats['qty']+=deficit
        return a
    return agent

def final(rep):
    st=rep.get('steps') or []
    if len(st)!=720: raise RuntimeError(f'steps={len(st)}')
    last=st[-1]
    statuses=[last[i].get('status') for i in (0,1)]
    if statuses!=['DONE','DONE']: raise RuntimeError(f'statuses={statuses}')
    return [float(last[i].get('reward')) for i in (0,1)]
def wl(d): return 1.0 if d>0 else 0.0 if d<0 else .5

def play(agent,opp,seed,seat,configuration):
    c=copy.deepcopy(configuration) if isinstance(configuration,dict) else {}
    c['episodeSteps']=720;c['seed']=int(seed)
    env=make('kaggriculture',configuration=c,debug=True)
    env.run([agent,opp] if seat==0 else [opp,agent])
    r=final(env.toJSON()); d=r[seat]-r[1-seat]
    return {'self_reward':r[seat],'opp_reward':r[1-seat],'delta':d,'score':wl(d)}

def summary(rows):
    ds=[r['delta'] for r in rows]; ss=[r['score'] for r in rows]
    return {'games':len(rows),'wins':sum(x==1 for x in ss),'losses':sum(x==0 for x in ss),'ties':sum(x==.5 for x in ss),
            'score_total':sum(ss),'score_rate':sum(ss)/len(ss) if ss else None,
            'mean_delta':statistics.mean(ds) if ds else None,'median_delta':statistics.median(ds) if ds else None}

def main():
    cfg=json.loads(CFG.read_text())
    OUT.mkdir(parents=True,exist_ok=True)
    api=KaggleApi();api.authenticate();errors=[];rows=[]
    with tempfile.TemporaryDirectory(prefix='cr033-') as td0:
        td=Path(td0); recent=cfg['recent_top']
        api.competition_episode_replay(int(recent['episode_id']),path=str(td),quiet=True)
        rep=json.loads((td/f"episode-{int(recent['episode_id'])}-replay.json").read_text())
        base=acts(rep,int(recent['source_seat']))
        if len(base)!=719 or tsha(base)!=recent['tape_sha256']:raise RuntimeError('CR029 provenance mismatch')
        # Assert the causal opportunity is exactly what was preregistered.
        expected={608,610,612,616,618,622}
        got=set()
        for t in range(608,623):
            a=base[t]
            ops=[a.get('farmer')]+list(a.get('hands') or [])
            if any(isinstance(op,list) and op[:2]==['PLANT','CARROT'] for op in ops):got.add(t)
        if got!=expected:raise RuntimeError(f'CARROT plant-intent drift: {sorted(got)}')
        if len(base[BUY_STEP].get('market') or [])>=MAX_MARKET_ORDERS:raise RuntimeError('step607 no longer has free market capacity')

        scenarios=[]
        for s in cfg['scenarios']:
            eid=int(s['episode_id']);rank=int(s['rank'])
            p=Path(kagglehub.dataset_download(HANDLE,path=f'{eid}.json',output_dir=str(td/f'e{eid}'),force_download=True))
            rr=json.loads(p.read_text()); tp=acts(rr,int(s['winner_seat']))
            if len(tp)!=719 or tsha(tp)!=s['tape_sha256']:raise RuntimeError(f'rank{rank} provenance mismatch')
            scenarios.append((s,rr,tp))

        all_variants=['cr029']+[f'jit_target_{q}' for q in TARGETS]
        stats={v:{'observed':0,'triggered':0,'qty':0,'stocks':[],'prices':[]} for v in all_variants}
        for s,rr,tp in scenarios:
            rank=int(s['rank']); seed=int(s['seed']); conf=rr.get('configuration') or {}
            for seat in (0,1):
                for v in all_variants:
                    try:
                        if v=='cr029': ag=tape_agent(base)
                        else: ag=jit_agent(base,int(v.rsplit('_',1)[1]),stats[v])
                        z=play(ag,tape_agent(tp),seed,seat,conf)
                        rows.append({'variant':v,'opponent_rank':rank,'opponent_team':s['team'],'seed':seed,'seat':seat,**z})
                    except Exception as exc:
                        errors.append({'variant':v,'opponent_rank':rank,'seat':seat,'error':repr(exc)})

    base_rows=[r for r in rows if r['variant']=='cr029']; bm=summary(base_rows)
    results=[]
    for q in TARGETS:
        v=f'jit_target_{q}'; vr=[r for r in rows if r['variant']==v]; m=summary(vr)
        paired=[];fav=unfav=0
        lookup={(r['opponent_rank'],r['seat']):r for r in base_rows}
        for r in vr:
            b=lookup[(r['opponent_rank'],r['seat'])]
            paired.append(r['delta']-b['delta'])
            if r['score']>b['score']:fav+=1
            elif r['score']<b['score']:unfav+=1
        gain=m['score_total']-bm['score_total']
        mean_gain=statistics.mean(paired) if paired else None
        st=stats[v]
        results.append({'variant':v,'target':q,'metrics':m,'score_gain_vs_cr029':gain,'mean_paired_delta_gain':mean_gain,
                        'favorable_conversions':fav,'unfavorable_conversions':unfav,'net_conversions':fav-unfav,
                        'triggered_games':st['triggered'],'total_seed_qty':st['qty'],'step607_stock_min':min(st['stocks']) if st['stocks'] else None,
                        'step607_stock_max':max(st['stocks']) if st['stocks'] else None,'step607_price_min':min([x for x in st['prices'] if x is not None],default=None),
                        'step607_price_max':max([x for x in st['prices'] if x is not None],default=None)})
    results.sort(key=lambda x:(x['score_gain_vs_cr029'],x['net_conversions'],x['mean_paired_delta_gain'] or -1e30),reverse=True)
    # Screen gate is intentionally modest; any real paired W/L improvement with
    # positive mean margin earns a fresh validation because hosted slots are not scarce.
    promoted=[x['variant'] for x in results if x['score_gain_vs_cr029']>=1 and x['net_conversions']>=1 and (x['mean_paired_delta_gain'] or 0)>0 and x['unfavorable_conversions']<=2]
    out={'experiment':'CR033_CR029_JIT_CARROT_SCREEN_V1','baseline':bm,'results':results,'promoted':promoted,
         'decision':'CR033_FRESH_VALIDATE' if promoted else 'CR033_NO_JIT_PROMOTION','errors':errors,'rows':rows,
         'source_scenarios_already_open':True,'fresh_validation_touched':False,'held_out_touched':False,'runtime_identity_features':False}
    (OUT/'report.json').write_text(json.dumps(out,indent=2,sort_keys=True))
    compact={k:v for k,v in out.items() if k!='rows'}
    (OUT/'summary.json').write_text(json.dumps(compact,indent=2,sort_keys=True))
    print(json.dumps(compact,indent=2,sort_keys=True))
    if errors:raise SystemExit(3)
if __name__=='__main__':main()
