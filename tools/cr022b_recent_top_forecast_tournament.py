"""CR022B — refresh opponent SELL forecasting on the newest official top-episode datasets.

Research only. No strategy candidate is produced. Identity/provenance fields are
used only for grouped splitting and reporting, never as model features.

Protocol:
- attempt official Kaggriculture episode datasets for 2026-08-27..29;
- use the newest >=2 available dates, chronological OOT (latest date = test);
- rank manifest by avg_score and use top N episodes per date;
- collect every second state 96..695 from both player perspectives;
- legal public features are CR004 plus robust day/hour clock and simple market ratios;
- target = opponent SELL of each crop within current..next 3 turns (4-turn horizon);
- episode-grouped fit/calibration split on pre-test dates;
- compare regularized logistic and HistGradientBoosting with Platt calibration;
- evaluate frozen CR007 pure trees/thresholds for CARROT/STRAWBERRY on the same OOT test.

The output includes first-sale delay, quantity and order-position distributions
for later counterfactual response work, but no quantity model is promoted here.
"""
from __future__ import annotations

import argparse, collections, hashlib, json, math, statistics, tempfile
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
from tools.cr004_adaptation_signal import download, read_csv, public_features

PRODUCTS=("CARROT","TOMATO","STRAWBERRY","MELON")
BASE_PRICE={"CARROT":35.0,"TOMATO":60.0,"STRAWBERRY":120.0,"MELON":100.0}
DATES=("2026-08-27","2026-08-28","2026-08-29")
START,END,STRIDE,HORIZON=96,695,2,4
RANDOM_STATE=2026082922


def stable_bucket(value:str,mod:int=5)->int:
    return int(hashlib.sha256(value.encode()).hexdigest()[:8],16)%mod


def first_sell(steps,opponent,t,product):
    last=min(t+HORIZON-1,len(steps)-2)
    for s in range(t,last+1):
        frame=steps[s+1][opponent]
        action=frame.get('action') if isinstance(frame,dict) else None
        if not isinstance(action,dict):continue
        for pos,order in enumerate(action.get('market',[]) or []):
            if isinstance(order,list) and len(order)>=3 and order[0]=='SELL' and order[1]==product:
                try:q=max(0,int(order[2] or 0))
                except Exception:q=0
                return {'event':1,'delay':s-t,'quantity':q,'position':pos}
    return {'event':0,'delay':None,'quantity':0,'position':None}


def enrich_features(obs,prev,player):
    f=public_features(obs,prev,player)
    if not f:return f
    try:clock=float(int((obs or {}).get('day',0) or 0)*24+int((obs or {}).get('hour',0) or 0))
    except Exception:clock=float(f.get('step',0.0))
    f['clock_step']=clock; f['clock_day']=clock/24.0
    for p in PRODUCTS:
        lo=p.lower(); price=float(f.get(f'market_price_{lo}',0.0) or 0.0); inv=float(f.get(f'market_inventory_{lo}',0.0) or 0.0)
        f[f'market_price_ratio_{lo}']=price/BASE_PRICE[p] if BASE_PRICE[p]>0 else 0.0
        f[f'market_inventory_excess_{lo}']=inv-10000.0
    return f


def collect_date(date,top,root):
    handle=f'kaggle/kaggriculture-episodes-{date}'
    try:
        manifest=sorted(read_csv(download(handle,'manifest.csv',root/date/'manifest')),key=lambda r:-float(r.get('avg_score') or 0))[:top]
    except Exception as exc:
        print(f'UNAVAILABLE {date}: {exc!r}')
        return []
    rows=[]
    for mr in manifest:
        eid=str(mr['episode_id'])
        try:p=download(handle,f'{eid}.json',root/date/'episodes'/eid);rep=json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc:
            print(f'SKIP episode {date}/{eid}: {exc!r}');continue
        steps=rep.get('steps') or []
        if len(steps)<720:continue
        for player in (0,1):
            for t in range(START,END+1,STRIDE):
                if t-24<0 or t+HORIZON>=len(steps):continue
                obs=steps[t][player].get('observation') or {};prev=steps[t-24][player].get('observation') or {}
                feat=enrich_features(obs,prev,player)
                if not feat:continue
                targets={p:first_sell(steps,1-player,t,p) for p in PRODUCTS}
                rows.append({'date':date,'episode_id':eid,'player':player,'t':t,'features':feat,'targets':targets,'avg_score':float(mr.get('avg_score') or 0)})
    print(f'COLLECTED {date}: episodes={len(set(r["episode_id"] for r in rows))} rows={len(rows)}')
    return rows


def feature_names(rows):
    return sorted({k for r in rows for k in r['features']})


def xy(rows,names,product):
    X=np.asarray([[float(r['features'].get(n,0.0)) for n in names] for r in rows],dtype=float)
    y=np.asarray([int(r['targets'][product]['event']) for r in rows],dtype=int)
    return X,y


def raw_prob(model,X):
    p=model.predict_proba(X);classes=list(model.classes_)
    if 1 not in classes:return np.zeros(len(X),dtype=float)
    return np.asarray(p[:,classes.index(1)],dtype=float)


def logit(p):
    p=np.clip(np.asarray(p,dtype=float),1e-6,1-1e-6);return np.log(p/(1-p)).reshape(-1,1)


def platt_fit(p,y):
    if len(set(map(int,y)))<2:return None
    c=LogisticRegression(C=1.0,solver='lbfgs',max_iter=1000,random_state=RANDOM_STATE)
    c.fit(logit(p),y);return c


def calibrate(c,p):
    if c is None:return np.asarray(p,dtype=float)
    return c.predict_proba(logit(p))[:,list(c.classes_).index(1)]


def ece(y,p,bins=10):
    y=np.asarray(y);p=np.asarray(p);total=len(y);out=0.0
    for lo in np.linspace(0,1,bins,endpoint=False):
        hi=lo+1/bins;mask=(p>=lo)&((p<hi) if hi<1 else (p<=hi))
        if mask.any():out+=mask.mean()*abs(float(y[mask].mean())-float(p[mask].mean()))
    return float(out)


def choose_threshold(y,p,min_precision=.85):
    candidates=sorted(set(float(x) for x in p),reverse=True)
    best=None
    for th in candidates:
        pred=p>=th;n=int(pred.sum())
        if n==0:continue
        precision=float(y[pred].mean());coverage=n/len(y)
        if precision>=min_precision and (best is None or coverage>best['coverage']):best={'threshold':th,'precision':precision,'coverage':coverage,'positives':n}
    return best or {'threshold':1.000001,'precision':None,'coverage':0.0,'positives':0}


def metrics(y,p,threshold):
    pred=p>=float(threshold);tp=int(((pred)&(y==1)).sum());fp=int(((pred)&(y==0)).sum())
    return {
        'support_positive':int(y.sum()),'support_negative':int(len(y)-y.sum()),
        'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,np.clip(p,1e-8,1-1e-8),labels=[0,1])),
        'roc_auc':float(roc_auc_score(y,p)) if len(set(map(int,y)))==2 else None,
        'pr_auc':float(average_precision_score(y,p)) if int(y.sum())>0 else None,'ece10':ece(y,p),
        'threshold':float(threshold),'trigger_count':int(pred.sum()),'precision':float(tp/(tp+fp)) if tp+fp else None,'coverage':float(pred.mean()),
    }


def fit_models(fit_rows,cal_rows,test_rows,names,product):
    Xf,yf=xy(fit_rows,names,product);Xc,yc=xy(cal_rows,names,product);Xt,yt=xy(test_rows,names,product)
    specs={
      'logistic_l2':make_pipeline(StandardScaler(),LogisticRegression(C=0.5,class_weight='balanced',solver='lbfgs',max_iter=1500,random_state=RANDOM_STATE)),
      'hist_gbdt':HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=15,learning_rate=.06,l2_regularization=2.0,min_samples_leaf=40,random_state=RANDOM_STATE),
    }
    out={}
    for name,m in specs.items():
        m.fit(Xf,yf);pc0=raw_prob(m,Xc);cal=platt_fit(pc0,yc);pc=calibrate(cal,pc0);pt=calibrate(cal,raw_prob(m,Xt));choice=choose_threshold(yc,pc,.85)
        out[name]={'calibration_choice':choice,'test':metrics(yt,pt,choice['threshold'])}
    return out


def tree_prob(model,feat,names):
    node=0;left=model['children_left'];right=model['children_right'];features=model['feature'];threshold=model['threshold']
    while left[node]!=-1 and right[node]!=-1:
        idx=features[node];node=left[node] if float(feat.get(names[idx],0.0))<=threshold[node] else right[node]
    vals=model['value'][node];classes=model['classes'];total=sum(vals)
    return float(vals[classes.index(1)])/float(total) if total>0 and 1 in classes else 0.0


def eval_cr007(test_rows,product):
    obj=json.loads((ROOT/'models/cr007_pure_models.json').read_text(encoding='utf-8'));target=f'SELL_{product}'
    if target not in obj.get('models',{}):return None
    names=obj['feature_names'];model=obj['models'][target];th=float(obj['thresholds'][target]);y=np.asarray([int(r['targets'][product]['event']) for r in test_rows]);p=np.asarray([tree_prob(model,r['features'],names) for r in test_rows])
    return metrics(y,p,th)


def target_distribution(rows,product):
    ev=[r['targets'][product] for r in rows if r['targets'][product]['event']]
    return {'events':len(ev),'delay_counts':dict(collections.Counter(str(x['delay']) for x in ev)),'quantity_median':statistics.median([x['quantity'] for x in ev]) if ev else None,'quantity_mean':statistics.mean([x['quantity'] for x in ev]) if ev else None,'position_counts':dict(collections.Counter(str(x['position']) for x in ev))}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--top',type=int,default=20);ap.add_argument('--output',required=True);args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='kculture-cr022b-') as tmp:
        rows=[]
        for d in DATES:rows.extend(collect_date(d,args.top,Path(tmp)))
    available=sorted({r['date'] for r in rows})
    if len(available)<2:raise SystemExit(f'need >=2 available dates, got {available}')
    test_date=available[-1];train_dates=available[:-1];pre=[r for r in rows if r['date'] in train_dates];test=[r for r in rows if r['date']==test_date]
    # Deterministic episode-grouped calibration split; no episode appears in both fit/cal.
    cal_eps={e for e in {r['episode_id'] for r in pre} if stable_bucket(e)==0}
    cal=[r for r in pre if r['episode_id'] in cal_eps];fit=[r for r in pre if r['episode_id'] not in cal_eps]
    if not cal or not fit:raise SystemExit('empty grouped fit/cal split')
    names=feature_names(rows);details={}
    for product in PRODUCTS:
        details[product]={'models':fit_models(fit,cal,test,names,product),'frozen_cr007':eval_cr007(test,product),'test_target_distribution':target_distribution(test,product)}
    ranking=[]
    for p,rec in details.items():
        for m,v in rec['models'].items():ranking.append((p,m,v['test']['brier'],v['test']['pr_auc'],v['test']['precision'],v['test']['coverage']))
    payload={'experiment':'CR-022B','status':'FORECAST_TOURNAMENT_COMPLETE','available_dates':available,'train_dates':train_dates,'test_date':test_date,'top_episodes_per_date':args.top,'sampling':{'start':START,'end':END,'stride':STRIDE,'horizon':HORIZON},'rows':{'fit':len(fit),'calibration':len(cal),'test':len(test)},'episodes':{'fit':len({r['episode_id'] for r in fit}),'calibration':len({r['episode_id'] for r in cal}),'test':len({r['episode_id'] for r in test})},'feature_count':len(names),'identity_features':[],'details':details,'ranking_by_brier':sorted(ranking,key=lambda x:x[2]),'policy':'Diagnostic/model-selection evidence only. Do not build a strategy candidate until response counterfactual CR022C is complete.'}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({k:v for k,v in payload.items() if k not in ('details',)},indent=2,sort_keys=True))

if __name__=='__main__':main()
