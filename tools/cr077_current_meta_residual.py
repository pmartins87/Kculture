"""CR077 — state-controlled winner/loser residual analysis on current Kaggriculture meta.

Discovery: fit state residualizers on Sep-08 and score a fixed grid of action-family/window
residual associations on Sep-09. Freeze exactly one mechanism. If the Sep-10 official
daily dataset is available, refit residualizers on Sep-08+09 for only that frozen
mechanism and evaluate it OOT on Sep-10. This is mechanism discovery/confirmation,
not strategy promotion. Team/episode/seed identity is never a feature.
"""
from __future__ import annotations

import argparse, collections, csv, json, math, statistics, tempfile
from pathlib import Path
from typing import Any
import numpy as np
import kagglehub
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

WINDOWS=((96,192),(192,360),(360,540),(540,719))
FAMILIES=("HIRE","BUY_LAND","BUY_SEED","BUY_ANIMAL","BUY_PRODUCT","SELL","PASS")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
BOOT=3000
RNG_SEED=20260910


def download(handle:str,filename:str,out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file():raise FileNotFoundError(f'missing {handle}:{filename}:{p}')
    return p


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def fnum(v:Any,default:float=0.0)->float:
    try:
        x=float(v);return x if math.isfinite(x) else default
    except (TypeError,ValueError):return default


def farm_vec(farm:dict,prefix:str)->dict[str,float]:
    c=collections.Counter()
    for row in (farm or {}).get('tiles',[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get('kind')=='PLANT':c[f"crop_{tile.get('crop')}"]+=1
            if tile.get('kind')=='WEED':c['weeds']+=1
            if tile.get('animal'):c[f"animal_{tile.get('animal')}"]+=1
    out={f'{prefix}money':fnum((farm or {}).get('money')),f'{prefix}hands':float(len((farm or {}).get('hands',[]) or [])),f'{prefix}quads':float(len((farm or {}).get('unlocked_quadrants',[]) or [])),f'{prefix}weeds':float(c.get('weeds',0))}
    for x in CROPS:out[f'{prefix}crop_{x.lower()}']=float(c.get(f'crop_{x}',0))
    for x in ANIMALS:out[f'{prefix}animal_{x.lower()}']=float(c.get(f'animal_{x}',0))
    return out


def state_features(obs:dict)->dict[str,float]:
    farms=(obs or {}).get('farms') or []
    if len(farms)<2:return {}
    a=farm_vec(farms[0],'p0_');b=farm_vec(farms[1],'p1_');out={**a,**b}
    for k in sorted(set(x[3:] for x in a if x.startswith('p0_')) & set(x[3:] for x in b if x.startswith('p1_'))):out[f'gap_{k}']=a.get('p0_'+k,0)-b.get('p1_'+k,0)
    market=(obs or {}).get('market') or {};prices=market.get('prices') or {};inv=market.get('inventory') or {}
    for x in PRODUCTS:
        out[f'price_{x.lower()}']=fnum(prices.get(x));out[f'inventory_{x.lower()}']=fnum(inv.get(x))
    out['shop_count']=float(len((((obs or {}).get('town') or {}).get('unlocked_shops') or [])))
    return out


def family_count(steps:list,player:int,start:int,end:int)->dict[str,float]:
    c=collections.Counter()
    for s in range(start,min(end,len(steps)-1)):
        try:a=steps[s+1][player].get('action')
        except Exception:a=None
        if not isinstance(a,dict):continue
        for order in a.get('market',[]) or []:
            if not (isinstance(order,list) and order):continue
            typ=str(order[0])
            if typ in FAMILIES:c[typ]+=1
    return {k:float(c.get(k,0)) for k in FAMILIES}


def rewards(rep:dict)->tuple[float,float]|None:
    try:
        last=rep['steps'][-1];return float(last[0].get('reward')),float(last[1].get('reward'))
    except Exception:return None


def episode_row(rep:dict,date:str,eid:str)->dict[str,Any]|None:
    steps=rep.get('steps') or [];rw=rewards(rep)
    if rw is None or len(steps)<720:return None
    windows={}
    for start,end in WINDOWS:
        try:obs=steps[start][0].get('observation') or {}
        except Exception:obs={}
        st=state_features(obs)
        a0=family_count(steps,0,start,end);a1=family_count(steps,1,start,end)
        windows[f'{start}-{end}']={'state':st,'action_diff':{f:a0[f]-a1[f] for f in FAMILIES},'winner_minus_loser':{f:(a0[f]-a1[f]) if rw[0]>rw[1] else (a1[f]-a0[f]) for f in FAMILIES}}
    return {'date':date,'episode_id':eid,'outcome_margin':rw[0]-rw[1],'windows':windows}


def collect(date:str,top:int,root:Path)->tuple[list[dict],str|None]:
    handle=f'kaggle/kaggriculture-episodes-{date}'
    try:rows=sorted(read_csv(download(handle,'manifest.csv',root/date/'manifest')),key=lambda r:-fnum(r.get('avg_score')))[:top]
    except Exception as exc:return [],repr(exc)
    out=[]
    for r in rows:
        eid=str(r.get('episode_id') or '')
        try:
            p=download(handle,f'{eid}.json',root/date/'episodes'/eid);rep=json.loads(p.read_text(encoding='utf-8'));x=episode_row(rep,date,eid)
            if x:out.append(x)
        except Exception:pass
    return out,None


def matrices(rows:list[dict],window:str,family:str,names:list[str]|None=None):
    if names is None:names=sorted({k for r in rows for k in r['windows'][window]['state']})
    X=np.asarray([[fnum(r['windows'][window]['state'].get(k)) for k in names] for r in rows],float)
    y=np.asarray([fnum(r['outcome_margin']) for r in rows],float)
    a=np.asarray([fnum(r['windows'][window]['action_diff'].get(family)) for r in rows],float)
    return X,y,a,names


def model()->Any:return make_pipeline(StandardScaler(),Ridge(alpha=10.0))


def corr(x:np.ndarray,y:np.ndarray)->float|None:
    if len(x)<6 or float(np.std(x))<1e-9 or float(np.std(y))<1e-9:return None
    return float(np.corrcoef(x,y)[0,1])


def bootstrap_ci(x:np.ndarray,y:np.ndarray,seed:int)->tuple[float|None,float|None]:
    if len(x)<6:return None,None
    rng=np.random.default_rng(seed);vals=[];n=len(x)
    for _ in range(BOOT):
        idx=rng.integers(0,n,n);v=corr(x[idx],y[idx])
        if v is not None and math.isfinite(v):vals.append(v)
    if not vals:return None,None
    return float(np.quantile(vals,.10)),float(np.quantile(vals,.90))


def residual_eval(train:list[dict],test:list[dict],window:str,family:str,seed:int)->dict[str,Any]:
    Xtr,ytr,atr,names=matrices(train,window,family);Xte,yte,ate,_=matrices(test,window,family,names)
    my=model();ma=model();my.fit(Xtr,ytr);ma.fit(Xtr,atr)
    ry=yte-my.predict(Xte);ra=ate-ma.predict(Xte);r=corr(ra,ry);lo,hi=bootstrap_ci(ra,ry,seed)
    wml=[r0['windows'][window]['winner_minus_loser'][family] for r0 in test]
    return {'window':window,'family':family,'train_n':len(train),'test_n':len(test),'residual_corr':r,'bootstrap80':[lo,hi],
            'winner_minus_loser_mean':statistics.mean(wml) if wml else None,'winner_minus_loser_median':statistics.median(wml) if wml else None,
            'action_diff_std':float(np.std(ate))}


def sign_confident(rec:dict)->bool:
    r=rec.get('residual_corr');lo,hi=rec.get('bootstrap80',[None,None])
    return r is not None and lo is not None and hi is not None and ((r>0 and lo>0) or (r<0 and hi<0))


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--top',type=int,default=60);ap.add_argument('--output',required=True);args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='kculture-cr077-') as tmp:
        root=Path(tmp);d8,e8=collect('2026-09-08',args.top,root);d9,e9=collect('2026-09-09',args.top,root);d10,e10=collect('2026-09-10',args.top,root)
    if len(d8)<20 or len(d9)<20:raise SystemExit(f'insufficient discovery data d8={len(d8)} d9={len(d9)} errors={e8,e9}')
    grid=[];i=0
    for start,end in WINDOWS:
        w=f'{start}-{end}'
        for fam in FAMILIES:
            rec=residual_eval(d8,d9,w,fam,RNG_SEED+i);i+=1
            if rec['action_diff_std']>=0.5:grid.append(rec)
    eligible=[r for r in grid if r['residual_corr'] is not None and abs(r['residual_corr'])>=.25 and sign_confident(r)]
    eligible.sort(key=lambda r:(-abs(r['residual_corr']),r['window'],r['family']))
    selected=eligible[0] if eligible else None
    validation=None;confirmed=False
    if selected and len(d10)>=20:
        validation=residual_eval(d8+d9,d10,selected['window'],selected['family'],RNG_SEED+999)
        same_sign=validation['residual_corr'] is not None and selected['residual_corr']*validation['residual_corr']>0
        confirmed=bool(same_sign and abs(validation['residual_corr'])>=.20 and sign_confident(validation))
    if not selected:decision='NO_RESIDUAL_MECHANISM_DISCOVERED'
    elif len(d10)<20:decision='WAIT_FOR_2026_09_10_OOT'
    elif confirmed:decision='BUILD_CR078_CAUSAL_ABLATION'
    else:decision='RESIDUAL_MECHANISM_FAILED_OOT'
    payload={'schema_version':'kculture-cr077-current-meta-residual-v1','purpose':'state_controlled_mechanism_discovery_and_fresh_oot_confirmation_only',
             'datasets':{'2026-09-08':len(d8),'2026-09-09':len(d9),'2026-09-10':len(d10)},'dataset_errors':{'2026-09-08':e8,'2026-09-09':e9,'2026-09-10':e10},
             'fixed_windows':[f'{a}-{b}' for a,b in WINDOWS],'fixed_families':list(FAMILIES),'identity_features':[],
             'discovery_grid':grid,'discovery_gate':'Sep09 residual |corr|>=0.25, action-diff std>=0.5, bootstrap80 excludes zero; select exactly one by largest |corr|',
             'selected_mechanism':selected,'fresh_oot_validation':validation,'fresh_oot_gate':'Sep10 same sign, |residual corr|>=0.20, bootstrap80 excludes zero',
             'decision':decision,'next_if_confirmed':'CR078 one-mechanism causal counterfactual/ablation; no direct strategy promotion from CR077','next_if_failed':'close this residual shortlist; do not choose runner-up post hoc','automatic_strategy_promotion':False,'automatic_kaggle_submission':False}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    md=['# CR077 current-meta residual analysis','',f"Sep08 episodes: **{len(d8)}**",f"Sep09 episodes: **{len(d9)}**",f"Sep10 episodes: **{len(d10)}**",f"Eligible discovery mechanisms: **{len(eligible)}**",f"Selected: **{(selected or {}).get('window','none')} / {(selected or {}).get('family','none')}**",f"Fresh OOT confirmed: **{confirmed}**",'',f"Decision: **{decision}**"]
    out.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print('\n'.join(md))

if __name__=='__main__':main()
