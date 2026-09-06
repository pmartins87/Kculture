"""CR034: can early public behavior distinguish the two elite strategy regimes?

Uses exact already-open CR029 official source tapes.  CR029 is replayed against
each tape in both seats. At horizons 24/48/72/96 we extract public-only features
from CR029's observation. A leave-one-episode-out decision-stump test measures
whether the keiz-vs-Jesse strategic regimes are behaviorally separable without
identity, seed, submission id, or future information.
"""
from __future__ import annotations

import copy, hashlib, json, math, statistics, tempfile
from pathlib import Path
import kagglehub
from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'configs/cr031_elite_round_robin.json'
OUT=ROOT/'artifacts/cr034_public_regime_fingerprint'
HANDLE='kaggle/kaggriculture-episodes-2026-09-05'
HORIZONS=(24,48,72,96)
PRODUCTS=('WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL','FERTILIZER')

def get(o,k,d=None):
    try:return o.get(k,d)
    except Exception:
        try:return o[k]
        except Exception:return d

def num(o,k):
    try:
        x=float(get(o,k,0) or 0);return x if math.isfinite(x) else 0.0
    except Exception:return 0.0

def step(obs):
    try:
        x=get(obs,'step',None)
        if x is not None:return max(0,int(x))
    except Exception:pass
    try:return max(0,int(get(obs,'day',0) or 0))*24+max(0,int(get(obs,'hour',0) or 0))
    except Exception:return 0

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def tsha(t):return hashlib.sha256(canon(t).encode()).hexdigest()
def actions(rep,seat):
    st=rep.get('steps') or []
    return [copy.deepcopy((st[t][seat] or {}).get('action') or {}) for t in range(1,len(st))]

def tile_features(farm,prefix):
    out={f'{prefix}money':num(farm,'money'),f'{prefix}hands':float(len(get(farm,'hands',[]) or [])),f'{prefix}quads':float(len(get(farm,'unlocked_quadrants',[]) or []))}
    counts={};yld=0.0
    for row in get(farm,'tiles',[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            kind=str(tile.get('kind') or 'NONE');counts[f'kind_{kind}']=counts.get(f'kind_{kind}',0)+1
            crop=tile.get('crop')
            if crop:counts[f'crop_{crop}']=counts.get(f'crop_{crop}',0)+1
            animal=tile.get('animal')
            if animal:counts[f'animal_{animal}']=counts.get(f'animal_{animal}',0)+1
            try:yld+=max(0.0,float(tile.get('yield_units',0) or 0))
            except Exception:pass
    out[f'{prefix}yield_units']=yld
    for k,v in counts.items():out[f'{prefix}{k.lower()}']=float(v)
    return out

def public_features(obs):
    farms=get(obs,'farms',[]) or []; p=int(get(obs,'player',0) or 0);o=1-p
    if len(farms)<2:return {}
    f={};f.update(tile_features(farms[p],'self_'));f.update(tile_features(farms[o],'opp_'))
    f['gap_money']=f.get('self_money',0)-f.get('opp_money',0);f['gap_hands']=f.get('self_hands',0)-f.get('opp_hands',0);f['gap_quads']=f.get('self_quads',0)-f.get('opp_quads',0)
    m=get(obs,'market',{}) or {};pr=get(m,'prices',{}) or {};inv=get(m,'inventory',{}) or {}
    for x in PRODUCTS:
        f[f'price_{x.lower()}']=num(pr,x);f[f'inventory_{x.lower()}']=num(inv,x)
    town=get(obs,'town',{}) or {};f['shop_count']=float(len(get(town,'unlocked_shops',[]) or []))
    return f

def tape_agent(tape,probe=None):
    def agent(obs,config=None):
        s=max(0,min(718,step(obs)))
        if probe is not None and s in HORIZONS and s not in probe:
            probe[s]=public_features(obs)
        return copy.deepcopy(tape[s])
    return agent

def final_ok(rep):
    st=rep.get('steps') or []
    return len(st)==720 and [st[-1][i].get('status') for i in (0,1)]==['DONE','DONE']

def best_stump(train,features):
    best=None
    for feat in features:
        vals=sorted(set(float(r['features'].get(feat,0.0)) for r in train))
        if len(vals)<2:continue
        thresholds=[(a+b)/2 for a,b in zip(vals,vals[1:])]
        for th in thresholds:
            for keiz_high in (False,True):
                correct=0
                for r in train:
                    v=float(r['features'].get(feat,0.0));pred='keiz' if ((v>th)==keiz_high) else 'Jesse Bullard'
                    correct+=pred==r['label']
                acc=correct/len(train)
                key=(acc,-len(thresholds),feat,th,keiz_high)
                if best is None or key>best['key']:best={'feature':feat,'threshold':th,'keiz_high':keiz_high,'train_accuracy':acc,'key':key}
    return best

def predict(stump,r):
    v=float(r['features'].get(stump['feature'],0.0));return 'keiz' if ((v>stump['threshold'])==stump['keiz_high']) else 'Jesse Bullard'

def loeo(rows):
    features=sorted(set(k for r in rows for k in r['features']))
    eps=sorted(set(r['episode_id'] for r in rows));preds=[]
    for eid in eps:
        train=[r for r in rows if r['episode_id']!=eid];test=[r for r in rows if r['episode_id']==eid]
        st=best_stump(train,features)
        if st is None:continue
        for r in test:
            preds.append({'episode_id':eid,'seat':r['seat'],'label':r['label'],'prediction':predict(st,r),'feature':st['feature'],'threshold':st['threshold'],'keiz_high':st['keiz_high'],'correct':predict(st,r)==r['label']})
    acc=sum(p['correct'] for p in preds)/len(preds) if preds else 0
    final=best_stump(rows,features)
    return {'accuracy':acc,'correct':sum(p['correct'] for p in preds),'total':len(preds),'predictions':preds,'full_data_stump':{k:v for k,v in final.items() if k!='key'} if final else None}

def main():
    cfg=json.loads(CFG.read_text());OUT.mkdir(parents=True,exist_ok=True);api=KaggleApi();api.authenticate();rows=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='cr034-') as td0:
        td=Path(td0);recent=cfg['recent_top'];api.competition_episode_replay(int(recent['episode_id']),path=str(td),quiet=True)
        rr=json.loads((td/f"episode-{int(recent['episode_id'])}-replay.json").read_text());base=actions(rr,int(recent['source_seat']))
        if len(base)!=719 or tsha(base)!=recent['tape_sha256']:raise RuntimeError('CR029 provenance mismatch')
        for s in cfg['scenarios']:
            eid=int(s['episode_id']);rank=int(s['rank']);label=s['team']
            p=Path(kagglehub.dataset_download(HANDLE,path=f'{eid}.json',output_dir=str(td/f'e{eid}'),force_download=True));rep=json.loads(p.read_text());tp=actions(rep,int(s['winner_seat']))
            if len(tp)!=719 or tsha(tp)!=s['tape_sha256']:raise RuntimeError(f'rank {rank} provenance mismatch')
            conf=copy.deepcopy(rep.get('configuration') or {});conf['episodeSteps']=720;conf['seed']=int(s['seed'])
            for seat in (0,1):
                probe={}
                env=make('kaggriculture',configuration=conf,debug=True);env.run([tape_agent(base,probe),tape_agent(tp)] if seat==0 else [tape_agent(tp),tape_agent(base,probe)])
                if not final_ok(env.toJSON()):errors.append({'rank':rank,'seat':seat,'error':'non-DONE'});continue
                for h in HORIZONS:
                    if h not in probe:errors.append({'rank':rank,'seat':seat,'horizon':h,'error':'missing probe'});continue
                    rows.append({'rank':rank,'episode_id':eid,'seat':seat,'label':label,'horizon':h,'features':probe[h]})
    results={}
    for h in HORIZONS:
        x=[r for r in rows if r['horizon']==h];results[str(h)]=loeo(x)
    out={'experiment':'CR034_PUBLIC_REGIME_FINGERPRINT_V1','results':results,'rows':rows,'errors':errors,
         'identity_features_used':False,'source_scenarios_already_open':True,'fresh_validation_touched':False,'held_out_touched':False}
    (OUT/'report.json').write_text(json.dumps(out,indent=2,sort_keys=True))
    compact={'experiment':out['experiment'],'errors':errors,'results':{h:{k:v for k,v in d.items() if k!='predictions'} for h,d in results.items()},'held_out_touched':False,'identity_features_used':False}
    (OUT/'summary.json').write_text(json.dumps(compact,indent=2,sort_keys=True));print(json.dumps(compact,indent=2,sort_keys=True))
    if errors:raise SystemExit(3)
if __name__=='__main__':main()
