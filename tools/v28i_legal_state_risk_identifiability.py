#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,os,sys
from pathlib import Path
import numpy as np
from kaggle_environments import make
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix,precision_score,recall_score,balanced_accuracy_score

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from solver.programme_features import features,ITEMS,SHOPS,KINDS
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

SEEDS=range(80401,80407); SEATS=(0,1)

def feature_names():
    out=['step','day','hour','own_money','opp_money','own_hands_plus1','opp_hands_plus1','own_unlocked_quadrants','opp_unlocked_quadrants','own_hires_today','opp_hires_today']
    for field in ('market_inventory','market_prices'): out += [f'{field}:{x}' for x in ITEMS[:9]]
    out += [f'town_unlocked_shop:{x}' for x in SHOPS]
    for side in ('own','opp'):
        out += [f'{side}_tiles_kind:{x}' for x in KINDS]
        out += [f'{side}_tiles_item:{x}' for x in ITEMS]
        out += [f'{side}_yield_units',f'{side}_consecutive_need',f'{side}_watered_today',f'{side}_fed_today',f'{side}_cared_today',f'{side}_fertilizer_available']
    out += [f'private_shed:{x}' for x in ITEMS]
    out += [f'private_seeds:{x}' for x in ITEMS[:5]]
    out += [f'private_inventories_sum:{x}' for x in ITEMS]
    assert len(out)==114
    return out

class CaptureAll3:
    def __init__(self,base_main,checkpoint):
        purge_package_modules(base_main.parent); self.base=load_public_agent(base_main); self.host=OptionHostState(); self.checkpoint=int(checkpoint); self.vector=None
    def __call__(self,obs,config=None):
        if int((obs or {}).get('step',-1))==self.checkpoint:
            self.vector=features(copy.deepcopy(obs)).astype(float).tolist()
        base=canonical_action(call_agent(self.base,obs,config))
        return apply_option_host(obs,config,base,self.host,use_rw=True,use_tw=True,use_lq2=True)

def run_one(base_main,opp_main,seed,seat,checkpoint):
    purge_package_modules(base_main.parent); purge_package_modules(opp_main.parent)
    cand=CaptureAll3(base_main,checkpoint); purge_package_modules(opp_main.parent); opp=load_public_agent(opp_main)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False)
    env.run([cand,opp] if int(seat)==0 else [opp,cand])
    rep=env.toJSON(); sts=[str(x) for x in rep.get('statuses',[])]; rw=[float(x) for x in rep.get('rewards',[])]
    if sts!=['DONE','DONE'] or len(rw)!=2 or len(rep.get('steps') or [])<720 or not all(math.isfinite(x) for x in rw): raise RuntimeError(f'invalid episode {sts} {rw}')
    if cand.vector is None or len(cand.vector)!=114: raise RuntimeError('missing checkpoint feature vector')
    mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0])
    score=1.0 if mine>other else 0.0 if mine<other else 0.5
    return score,mine-other,cand.vector

def metrics(y,p):
    cm=confusion_matrix(y,p,labels=[0,1]); tn,fp,fn,tp=[int(x) for x in cm.ravel()]
    spec=tn/(tn+fp) if tn+fp else 0.0
    return {'confusion_matrix':[[tn,fp],[fn,tp]],'precision':float(precision_score(y,p,zero_division=0)),'recall':float(recall_score(y,p,zero_division=0)),'specificity':float(spec),'balanced_accuracy':float(balanced_accuracy_score(y,p)),'positive_prediction_rate':float(np.mean(p)),'n':len(y)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--snapshot-dir',required=True); ap.add_argument('--v28f',required=True); ap.add_argument('--v28g',required=True); ap.add_argument('--v28h',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,'__version__',''))!=EXPECTED_ENGINE: raise SystemExit('engine mismatch')
    root=Path(a.snapshot_dir); man=json.loads((root/'MANIFEST.json').read_text()); f=json.loads(Path(a.v28f).read_text()); g=json.loads(Path(a.v28g).read_text()); h=json.loads(Path(a.v28h).read_text())
    if not f.get('mechanical_pass') or f.get('decision')!='V28F_NO_MATERIAL_HEDGE_REPLACEMENT': raise SystemExit('V28F binding mismatch')
    if not g.get('mechanical_pass') or g.get('decision')!='V28G_SOURCE_CLUSTERED_HARD_CORE': raise SystemExit('V28G binding mismatch')
    if not h.get('mechanical_pass') or h.get('decision') not in ('V28H_EARLY_STRUCTURAL_SEPARATION','V28H_MIDGAME_STRUCTURAL_SEPARATION','V28H_LATE_STRUCTURAL_SEPARATION'): raise SystemExit('V28H binding mismatch')
    checkpoint=int(h['selected_checkpoint'])
    base=root/man['base']['path'];
    if sha256_bytes(base.read_bytes())!=BASE['expected_main_sha256']: raise SystemExit('base SHA mismatch')
    paths={str(s['sha']):root/s['path'] for s in man['sources']}; meta={str(s['sha']):s for s in man['sources']}
    for sha,p in paths.items():
        if sha256_bytes(p.read_bytes())!=sha: raise SystemExit(f'source SHA mismatch {sha}')
    binding={(str(r['main_sha256']),int(r['seed']),int(r['seat'])):r for r in f['rows'] if r['candidate']=='ALL3'}
    if len(binding)!=144: raise SystemExit(f'expected 144 ALL3 binding rows got {len(binding)}')
    bysrc={str(x['main_sha256']):x for x in g['by_source']}
    hard=sorted([sha for sha,x in bysrc.items() if int(x['losses'])>=1],key=lambda sha:(int(meta[sha]['representative_rank']),sha)); easy=sorted([sha for sha,x in bysrc.items() if int(x['losses'])==0],key=lambda sha:(int(meta[sha]['representative_rank']),sha))
    if len(hard)!=6 or len(easy)!=6: raise SystemExit(f'expected 6/6 groups got {len(hard)}/{len(easy)}')
    hold=set([sha for group in (hard,easy) for i,sha in enumerate(group) if i%3==2]); train=set(paths)-hold
    if len(train)!=8 or len(hold)!=4: raise SystemExit('split size mismatch')
    rows=[]; failures=[]
    for sha in sorted(paths,key=lambda z:(int(meta[z]['representative_rank']),z)):
      for seed in SEEDS:
       for seat in SEATS:
        key=(sha,int(seed),int(seat)); exp=binding[key]
        try:
            score,margin,vec=run_one(base,paths[sha],seed,seat,checkpoint)
            if float(score)!=float(exp['score']) or float(margin)!=float(exp['margin']): raise RuntimeError(f'V28F terminal replay mismatch observed={(score,margin)} expected={(exp["score"],exp["margin"])}')
            rows.append({'main_sha256':sha,'representative_rank':int(meta[sha]['representative_rank']),'representative_ref':meta[sha]['representative_ref'],'seed':int(seed),'seat':int(seat),'split':'holdout' if sha in hold else 'train','group':'hard' if sha in hard else 'easy','label':1 if float(exp['score'])==0.0 else 0,'features':vec})
        except Exception as e: failures.append({'sha':sha,'seed':int(seed),'seat':int(seat),'error':f'{type(e).__name__}: {e}'})
        finally: purge_package_modules(base.parent);purge_package_modules(paths[sha].parent)
    mech=not failures and len(rows)==144 and sum(r['label'] for r in rows)==66
    result={'schema':'kculture-v28i-legal-state-risk-identifiability-v1','mechanical_pass':mech,'decision':'V28I_MECHANICS_INVALID','selected_checkpoint':checkpoint,'rows_count':len(rows),'positive_count':sum(r['label'] for r in rows),'failures':failures,'forbidden_field_entered_matrix':False,'feature_count':114,'feature_names':feature_names(),'train_sources':sorted(train),'holdout_sources':sorted(hold),'automatic_kaggle_submission':False}
    if mech:
        tr=[r for r in rows if r['split']=='train']; ho=[r for r in rows if r['split']=='holdout']; X=np.asarray([r['features'] for r in tr]);y=np.asarray([r['label'] for r in tr]); Xh=np.asarray([r['features'] for r in ho]);yh=np.asarray([r['label'] for r in ho])
        clf=DecisionTreeClassifier(max_depth=3,min_samples_leaf=8,class_weight='balanced',random_state=20260922);clf.fit(X,y);pt=clf.predict(X);ph=clf.predict(Xh)
        result['train_metrics']=metrics(y,pt);result['holdout_metrics']=metrics(yh,ph);result['tree_depth']=int(clf.get_depth());result['tree_leaves']=int(clf.get_n_leaves());result['min_samples_leaf']=8
        used=sorted(set(int(x) for x in clf.tree_.feature if int(x)>=0)); names=feature_names();result['used_feature_indices']=used;result['used_features']=[{'index':i,'name':names[i]} for i in used]
        per={}
        hard_ok=True;easy_ok=True
        for sha in sorted(hold):
            idx=[i for i,r in enumerate(ho) if r['main_sha256']==sha]; yy=yh[idx];pp=ph[idx];m=metrics(yy,pp);m['group']='hard' if sha in hard else 'easy';m['representative_rank']=int(meta[sha]['representative_rank']);m['representative_ref']=meta[sha]['representative_ref'];per[sha]=m
            if sha in hard and m['recall']<.50: hard_ok=False
            if sha in easy and m['specificity']<.75: easy_ok=False
        result['holdout_by_source']=per;m=result['holdout_metrics']
        ok=m['precision']>=.70 and m['recall']>=.60 and m['balanced_accuracy']>=.75 and hard_ok and easy_ok and result['tree_depth']<=3
        result['decision']='V28I_LEGAL_STATE_RISK_PHENOTYPE_IDENTIFIABLE' if ok else 'V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE'
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('V28I_RESULT',json.dumps({k:result.get(k) for k in ('mechanical_pass','decision','selected_checkpoint','positive_count','train_metrics','holdout_metrics','tree_depth','tree_leaves','used_features')},sort_keys=True),flush=True)
    if not mech: raise SystemExit(2)
if __name__=='__main__':main()
