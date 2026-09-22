#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,os,sys,tempfile
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
TEACHER_SHA='a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c'
SEEDS=(79801,79802,79803); SEATS=(0,1)
CHECKPOINTS=(0,1,2,3,4,8,16,32,64,128,256,384,512,640,718)
HORIZONS=(0,1,2,4,8,16,32,64,128,256,512,'FULL')

def comp(a,b,k): return a.get(k)==b.get(k)

def replay_action(main,history,current,config,h):
    purge_package_modules(main.parent); fn=load_public_agent(main)
    if h=='FULL': prior=history
    else: prior=history[max(0,len(history)-int(h)):]
    for ob in prior: canonical_action(call_agent(fn,copy.deepcopy(ob),copy.deepcopy(config)))
    out=canonical_action(call_agent(fn,copy.deepcopy(current),copy.deepcopy(config)))
    purge_package_modules(main.parent); return out

class Candidate:
    def __init__(self,main,fresh):
        purge_package_modules(main.parent); self.fn=load_public_agent(main); self.fresh=fresh; self.hist=[]; self.samples=[]
    def __call__(self,obs,config=None):
        step=int(obs.get('step',len(self.hist))); ongoing=canonical_action(call_agent(self.fn,obs,config))
        if step in CHECKPOINTS:
            hs={}
            for h in HORIZONS:
                a=replay_action(self.fresh,self.hist,obs,config or {},h)
                hs[str(h)]={'full_equal':a==ongoing,'market_equal':comp(a,ongoing,'market'),'farmer_equal':comp(a,ongoing,'farmer'),'hands_equal':comp(a,ongoing,'hands')}
            self.samples.append({'step':step,'horizons':hs})
        self.hist.append(copy.deepcopy(obs)); return ongoing

def run(main,fresh,opp,seed,seat):
    purge_package_modules(opp.parent); c=Candidate(main,fresh); purge_package_modules(opp.parent); o=load_public_agent(opp)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False)
    env.run([c,o] if seat==0 else [o,c]); p=env.toJSON(); sts=[str(x) for x in p.get('statuses',[])]; rw=[float(x) for x in p.get('rewards',[])]
    if sts!=['DONE','DONE'] or len(c.samples)!=len(CHECKPOINTS) or not all(math.isfinite(x) for x in rw): raise RuntimeError(f'invalid episode {sts} samples={len(c.samples)}')
    return c.samples

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--snapshot-dir',required=True); ap.add_argument('--shard-index',type=int,required=True); ap.add_argument('--num-shards',type=int,default=4); ap.add_argument('--out',required=True); a=ap.parse_args()
    import kaggle_environments
    if str(kaggle_environments.__version__)!=EXPECTED_ENGINE: raise SystemExit('engine mismatch')
    root=Path(a.snapshot_dir); man=json.loads((root/'MANIFEST.json').read_text()); src=list(man['sources']); tm=next(x for x in src if int(x['representative_rank'])==1); teacher=root/tm['path']
    if sha256_bytes(teacher.read_bytes())!=TEACHER_SHA: raise SystemExit('teacher SHA mismatch')
    selected=[x for i,x in enumerate(src) if i%a.num_shards==a.shard_index]; rows=[]; failures=[]
    for k in ('KAGGLE_API_TOKEN','KAGGLE_USERNAME','KAGGLE_KEY'): os.environ.pop(k,None)
    with tempfile.TemporaryDirectory(prefix='v27b-') as td:
      fresh=Path(td)/'main.py'; fresh.write_bytes(teacher.read_bytes())
      for s in selected:
       opp=root/s['path']
       for seed in SEEDS:
        for seat in SEATS:
         key={'source_rank':int(s['representative_rank']),'ref':s['representative_ref'],'main_sha256':s['sha'],'seed':seed,'seat':seat}
         try: rows.append({**key,'samples':run(teacher,fresh,opp,seed,seat)})
         except Exception as e: failures.append({**key,'error':f'{type(e).__name__}: {e}'})
         finally:
          purge_package_modules(teacher.parent); purge_package_modules(fresh.parent); purge_package_modules(opp.parent)
    expected=len(selected)*len(SEEDS)*len(SEATS); mech=not failures and len(rows)==expected
    out={'schema':'kculture-v27b-legal-history-audit-shard-v1','mechanical_pass':mech,'shard_index':a.shard_index,'rows':rows,'failures':failures,'horizons':[str(x) for x in HORIZONS],'checkpoints':list(CHECKPOINTS),'immutable_snapshot_used':True,'automatic_kaggle_submission':False}
    p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('V27B_SHARD_RESULT',json.dumps({'shard':a.shard_index,'mechanical_pass':mech,'episodes':len(rows),'failures':len(failures)},sort_keys=True))
    if not mech: raise SystemExit(2)
if __name__=='__main__': main()
