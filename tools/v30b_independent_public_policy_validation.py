#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE

FROZEN_SHA='4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01'
FROZEN_REF='arsgorynich/herd-safe-v3-experimental-risk-aware-feed'
SEEDS=(80601,80602,80603,80604); SEATS=(0,1)

def find_main(root:Path, sha:str):
    man=json.loads((root/'MANIFEST.json').read_text())
    for s in man['sources']:
        if str(s['sha'])==sha:
            p=root/s['path']
            if sha256_bytes(p.read_bytes())!=sha: raise RuntimeError('frozen candidate SHA mismatch')
            return p,s
    raise RuntimeError('frozen candidate absent from immutable V30A snapshot')

def run_agent(main,obs,config):
    return call_agent(load_public_agent(main),obs,config)

class All3:
    def __init__(self,base_main):
        purge_package_modules(base_main.parent); self.agent=load_public_agent(base_main); self.host=OptionHostState()
    def __call__(self,obs,config=None):
        a=canonical_action(call_agent(self.agent,obs,config)); return apply_option_host(obs,config,a,self.host,use_rw=True,use_tw=True,use_lq2=True)
class Direct:
    def __init__(self,main): purge_package_modules(main.parent); self.agent=load_public_agent(main)
    def __call__(self,obs,config=None): return call_agent(self.agent,obs,config)

def episode(candidate,opp_main,seed,seat):
    purge_package_modules(opp_main.parent); opp=load_public_agent(opp_main)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False)
    env.run([candidate,opp] if seat==0 else [opp,candidate]); rep=env.toJSON()
    statuses=[str(x) for x in rep.get('statuses',[])]; rewards=[float(x) for x in rep.get('rewards',[])]; steps=len(rep.get('steps') or [])
    if statuses!=['DONE','DONE'] or len(rewards)!=2 or steps<720 or not all(math.isfinite(x) for x in rewards): raise RuntimeError(f'invalid terminal {statuses} {rewards} {steps}')
    mine,other=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0]); margin=mine-other
    return float(score(margin)),float(margin)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--v30a-snapshot',required=True); ap.add_argument('--fresh-snapshot',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,'__version__',''))!=EXPECTED_ENGINE: raise SystemExit('engine mismatch')
    old=Path(a.v30a_snapshot); fresh=Path(a.fresh_snapshot)
    cand_main,cmeta=find_main(old,FROZEN_SHA)
    if str(cmeta.get('representative_ref'))!=FROZEN_REF: raise SystemExit('frozen ref mismatch')
    man=json.loads((fresh/'MANIFEST.json').read_text()); srcs=list(man['sources'])
    if not 8<=len(srcs)<=12: raise SystemExit(f'fresh source count {len(srcs)}')
    base=fresh/man['base']['path']
    if sha256_bytes(base.read_bytes())!=BASE['expected_main_sha256']: raise SystemExit('ALL3 base SHA mismatch')
    opps=[]
    for s in srcs:
        p=fresh/s['path']; sha=str(s['sha'])
        if sha256_bytes(p.read_bytes())!=sha: raise SystemExit(f'fresh source SHA mismatch {sha}')
        opps.append((s,p))
    for k in ('KAGGLE_API_TOKEN','KAGGLE_USERNAME','KAGGLE_KEY'): os.environ.pop(k,None)
    rows=[]; failures=[]
    for s,opp in opps:
      for seed in SEEDS:
       for seat in SEATS:
        vals={}
        for key in ('ALL3','PUBLIC'):
         try:
          purge_package_modules(base.parent); purge_package_modules(cand_main.parent); purge_package_modules(opp.parent)
          ag=All3(base) if key=='ALL3' else Direct(cand_main); sc,mg=episode(ag,opp,seed,seat); vals[key]=(sc,mg)
          rows.append({'candidate':key,'opponent_sha':s['sha'],'opponent_ref':s['representative_ref'],'seed':seed,'seat':seat,'score':sc,'margin':mg})
         except Exception as e: failures.append({'candidate':key,'opponent_sha':s['sha'],'seed':seed,'seat':seat,'error':f'{type(e).__name__}: {e}'})
    expected=len(opps)*len(SEEDS)*len(SEATS)*2; mechanics=(not failures and len(rows)==expected)
    by={(r['opponent_sha'],r['seed'],r['seat'],r['candidate']):r for r in rows}; paired=[]
    if mechanics:
      for s,_ in opps:
       for seed in SEEDS:
        for seat in SEATS:
         b=by[(s['sha'],seed,seat,'ALL3')]; c=by[(s['sha'],seed,seat,'PUBLIC')]
         paired.append({'source':s['sha'],'seed':seed,'seat':seat,'score_delta':c['score']-b['score'],'margin_delta':c['margin']-b['margin']})
    def sr(key):
      z=[r for r in rows if r['candidate']==key]; return sum(r['score'] for r in z)/len(z) if z else None
    bsr=sr('ALL3'); csr=sr('PUBLIC'); md=sum(x['score_delta'] for x in paired)/len(paired) if paired else None
    pos=[x for x in paired if x['score_delta']>0]; neg=[x for x in paired if x['score_delta']<0]
    source_b=len({x['source'] for x in pos}); seed_b=len({x['seed'] for x in pos}); seats=sorted({x['seat'] for x in pos})
    eligible=bool(mechanics and csr>=bsr+0.08 and md>=0.08 and source_b>=4 and seed_b>=3 and len(pos)>len(neg) and seats==[0,1])
    decision='V30B_PUBLIC_PERSISTENT_POLICY_INDEPENDENTLY_VALIDATED' if eligible else ('V30B_PUBLIC_PERSISTENT_POLICY_VALIDATION_FAIL' if mechanics else 'V30B_MECHANICS_INVALID')
    out={'schema':'kculture-v30b-independent-validation-v1','decision':decision,'mechanical_pass':mechanics,'candidate_ref':FROZEN_REF,'candidate_sha':FROZEN_SHA,'fresh_opponents':len(opps),'seeds':list(SEEDS),'seats':list(SEATS),'all3_score_rate':bsr,'candidate_score_rate':csr,'mean_paired_score_delta':md,'mean_paired_margin_delta':(sum(x['margin_delta'] for x in paired)/len(paired) if paired else None),'positive_contexts':len(pos),'negative_contexts':len(neg),'positive_source_breadth':source_b,'positive_seed_breadth':seed_b,'positive_seats':seats,'promotion_eligible':eligible,'failures':failures,'rows':rows}
    p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('V30B_RESULT',json.dumps({k:v for k,v in out.items() if k not in ('rows','failures')},sort_keys=True))
    if not mechanics: raise SystemExit(2)
if __name__=='__main__': main()
