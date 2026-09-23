#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,sys
from pathlib import Path
import numpy as np
from kaggle_environments import make
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix,precision_score,recall_score,balanced_accuracy_score
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from solver.programme_features import features
from tools.v28i_legal_state_risk_identifiability import feature_names
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE
SEEDS=range(80401,80407);SEATS=(0,1);CHECKPOINTS=(384,416,448,480)
class Capture:
 def __init__(self,base): purge_package_modules(base.parent);self.base=load_public_agent(base);self.host=OptionHostState();self.v={}
 def __call__(self,obs,config=None):
  s=int((obs or {}).get('step',-1))
  if s in CHECKPOINTS:self.v[s]=features(copy.deepcopy(obs)).astype(float).tolist()
  b=canonical_action(call_agent(self.base,obs,config));return apply_option_host(obs,config,b,self.host,use_rw=True,use_tw=True,use_lq2=True)
def run(base,opp,seed,seat):
 purge_package_modules(base.parent);purge_package_modules(opp.parent);c=Capture(base);purge_package_modules(opp.parent);o=load_public_agent(opp);e=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False);e.run([c,o] if seat==0 else [o,c]);p=e.toJSON();st=[str(x) for x in p.get('statuses',[])];rw=[float(x) for x in p.get('rewards',[])]
 if st!=['DONE','DONE'] or len(p.get('steps') or [])<720 or set(c.v)!=set(CHECKPOINTS) or not all(math.isfinite(x) for x in rw):raise RuntimeError(f'invalid replay {st} checkpoints={sorted(c.v)}')
 mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0]);score=1.0 if mine>other else 0.0 if mine<other else .5
 raw=[]
 for s in CHECKPOINTS:raw+=c.v[s]
 delta=[]
 for a,b in zip(CHECKPOINTS,CHECKPOINTS[1:]):delta += [y-x for x,y in zip(c.v[a],c.v[b])]
 vec=raw+delta
 if len(vec)!=798:raise RuntimeError('history vector size mismatch')
 return score,mine-other,vec
def met(y,p):
 cm=confusion_matrix(y,p,labels=[0,1]);tn,fp,fn,tp=[int(x) for x in cm.ravel()];return {'confusion_matrix':[[tn,fp],[fn,tp]],'precision':float(precision_score(y,p,zero_division=0)),'recall':float(recall_score(y,p,zero_division=0)),'specificity':tn/(tn+fp) if tn+fp else 0.0,'balanced_accuracy':float(balanced_accuracy_score(y,p)),'positive_prediction_rate':float(np.mean(p)),'n':len(y)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot-dir',required=True);ap.add_argument('--v28f',required=True);ap.add_argument('--v28g',required=True);ap.add_argument('--v28h',required=True);ap.add_argument('--v28i',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 import kaggle_environments
 if str(getattr(kaggle_environments,'__version__',''))!=EXPECTED_ENGINE:raise SystemExit('engine mismatch')
 root=Path(a.snapshot_dir);man=json.loads((root/'MANIFEST.json').read_text());f=json.loads(Path(a.v28f).read_text());g=json.loads(Path(a.v28g).read_text());h=json.loads(Path(a.v28h).read_text());i=json.loads(Path(a.v28i).read_text())
 if not i.get('mechanical_pass') or i.get('decision')!='V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE':raise SystemExit('V28I binding mismatch')
 if int(h.get('selected_checkpoint',-1))!=480 or not h.get('mechanical_pass'):raise SystemExit('V28H binding mismatch')
 base=root/man['base']['path'];
 if sha256_bytes(base.read_bytes())!=BASE['expected_main_sha256']:raise SystemExit('base SHA mismatch')
 paths={str(s['sha']):root/s['path'] for s in man['sources']};meta={str(s['sha']):s for s in man['sources']}
 for sha,p in paths.items():
  if sha256_bytes(p.read_bytes())!=sha:raise SystemExit(f'source SHA mismatch {sha}')
 binding={(str(r['main_sha256']),int(r['seed']),int(r['seat'])):r for r in f['rows'] if r['candidate']=='ALL3'}
 if len(binding)!=144:raise SystemExit('V28F rows mismatch')
 train=set(i['train_sources']);hold=set(i['holdout_sources'])
 if train|hold!=set(paths) or train&hold or len(train)!=8 or len(hold)!=4:raise SystemExit('V28I split mismatch')
 bysrc={str(x['main_sha256']):x for x in g['by_source']};hard={s for s,x in bysrc.items() if int(x['losses'])>=1}
 rows=[];fail=[]
 for sha in sorted(paths,key=lambda z:(int(meta[z]['representative_rank']),z)):
  for seed in SEEDS:
   for seat in SEATS:
    exp=binding[(sha,int(seed),int(seat))]
    try:
     sc,ma,v=run(base,paths[sha],seed,seat)
     if float(sc)!=float(exp['score']) or float(ma)!=float(exp['margin']):raise RuntimeError(f'V28F terminal replay mismatch observed={(sc,ma)} expected={(exp["score"],exp["margin"])}')
     rows.append({'sha':sha,'split':'holdout' if sha in hold else 'train','group':'hard' if sha in hard else 'easy','label':1 if float(exp['score'])==0 else 0,'features':v})
    except Exception as e:fail.append({'sha':sha,'seed':seed,'seat':seat,'error':f'{type(e).__name__}: {e}'})
    finally:purge_package_modules(base.parent);purge_package_modules(paths[sha].parent)
 mech=not fail and len(rows)==144 and sum(r['label'] for r in rows)==66
 out={'schema':'kculture-v28j-bounded-legal-history-risk-identifiability-v1','mechanical_pass':mech,'decision':'V28J_MECHANICS_INVALID','checkpoints':list(CHECKPOINTS),'feature_count':798,'rows_count':len(rows),'positive_count':sum(r['label'] for r in rows),'failures':fail,'forbidden_field_entered_matrix':False,'train_sources':sorted(train),'holdout_sources':sorted(hold),'automatic_kaggle_submission':False}
 if mech:
  tr=[r for r in rows if r['split']=='train'];ho=[r for r in rows if r['split']=='holdout'];X=np.asarray([r['features'] for r in tr]);y=np.asarray([r['label'] for r in tr]);Xh=np.asarray([r['features'] for r in ho]);yh=np.asarray([r['label'] for r in ho]);clf=DecisionTreeClassifier(max_depth=3,min_samples_leaf=8,class_weight='balanced',random_state=20260922);clf.fit(X,y);pt=clf.predict(X);ph=clf.predict(Xh);out['train_metrics']=met(y,pt);out['holdout_metrics']=met(yh,ph);out['tree_depth']=int(clf.get_depth());out['tree_leaves']=int(clf.get_n_leaves());out['min_samples_leaf']=8
  base_names=feature_names();names=[]
  for s in CHECKPOINTS:names += [f's{s}:{n}' for n in base_names]
  for x,z in zip(CHECKPOINTS,CHECKPOINTS[1:]):names += [f'd{s if False else z}-{x}:{n}' for n in base_names]
  used=sorted(set(int(x) for x in clf.tree_.feature if int(x)>=0));out['used_features']=[{'index':u,'name':names[u]} for u in used]
  per={};hardok=True;easyok=True
  for sha in sorted(hold):
   idx=[j for j,r in enumerate(ho) if r['sha']==sha];m=met(yh[idx],ph[idx]);m['group']='hard' if sha in hard else 'easy';per[sha]=m
   if sha in hard and m['recall']<.5:hardok=False
   if sha not in hard and m['specificity']<.75:easyok=False
  out['holdout_by_source']=per;m=out['holdout_metrics'];ok=m['precision']>=.70 and m['recall']>=.60 and m['balanced_accuracy']>=.75 and hardok and easyok and out['tree_depth']<=3;out['decision']='V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_IDENTIFIABLE' if ok else 'V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_NOT_IDENTIFIABLE'
 p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('V28J_RESULT',json.dumps({k:out.get(k) for k in ('mechanical_pass','decision','positive_count','train_metrics','holdout_metrics','tree_depth','tree_leaves','used_features')},sort_keys=True),flush=True)
 if not mech:raise SystemExit(2)
if __name__=='__main__':main()
