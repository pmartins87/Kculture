"""CR-015E: diagnose adaptive placement-mode switching on all 16 CR-014B pairs.

Diagnostic-only, using only pre-CR020 frozen cases. Instruments the frozen CR015
without altering actions. Purpose: test whether allowing a later append->prefix
transition is the trajectory pathology suggested by CR015D.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
CFG=ROOT/'configs/cr014b_affected_pairs_v1.json'
CAND=ROOT/'candidates/cr015_liquidation_phase_early_order.py'


def load(path:Path,tag:str):
    s=importlib.util.spec_from_file_location(f'cr015e_{tag}_{time.time_ns()}',path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m


def instrument(m):
    events=[]; orig=m._selective_adaptive_sales
    def wrapped(obs,action,player,step):
        before=copy.deepcopy(action); out=orig(obs,action,player,step)
        bm=list(before.get('market') or []); am=list(out.get('market') or [])
        if bm!=am:
            rem=[copy.deepcopy(x) for x in bm]; added=[]
            for order in am:
                try: i=rem.index(order)
                except ValueError: added.append(copy.deepcopy(order))
                else: rem.pop(i)
            if added:
                mode='prefix' if am[:len(added)]==added else 'append' if am[-len(added):]==added else 'mixed'
                events.append({'player':int(player),'step':int(step),'mode':mode,'base_market':bm,'added':added})
        return out
    m._selective_adaptive_sales=wrapped
    return events


def run(m,opp_path,seed,seat):
    o=load(opp_path,f'opp_{seed}_{seat}')
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run([m.agent,o.agent] if seat==0 else [o.agent,m.agent]); rep=env.toJSON(); f=rep['steps'][-1]
    st=[f[i].get('status') for i in range(2)]
    if st!=['DONE','DONE']: raise RuntimeError(st)
    own=float(f[seat]['reward']); other=float(f[1-seat]['reward']); d=own-other
    return {'self':own,'opp':other,'delta':d,'score':1.0 if d>0 else 0.0 if d<0 else 0.5}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--opponent-dir',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    od=Path(a.opponent_dir); od=od if od.is_absolute() else ROOT/od
    cfg=json.loads(CFG.read_text())
    rows=[]; errors=[]
    for e in cfg['pairs']:
        seed=int(e['seed']); seat=int(e['seat'])
        try:
            m=load(CAND,f'cand_{seed}_{seat}'); ev=instrument(m); term=run(m,od/f"{e['opponent']}.py",seed,seat)
            own=[x for x in ev if x['player']==seat]
            modes=[x['mode'] for x in own]
            switches=sum(modes[i]!=modes[i-1] for i in range(1,len(modes)))
            rows.append({
              'opponent':e['opponent'],'seed':seed,'seat':seat,
              'frozen_cr014_score_gain':float(e['score_gain']),
              'frozen_cr014_relative_gain':float(e['relative_gain']),
              'terminal':term,'modes':modes,'steps':[x['step'] for x in own],
              'event_count':len(own),'mode_switches':switches,
              'starts_append':bool(modes and modes[0]=='append'),
              'starts_prefix':bool(modes and modes[0]=='prefix'),
              'append_to_prefix':any(modes[i-1]=='append' and modes[i]=='prefix' for i in range(1,len(modes))),
              'events':own,
            })
        except Exception as exc: errors.append({'opponent':e['opponent'],'seed':seed,'seat':seat,'error':repr(exc)})
    def group(pred):
        xs=[r for r in rows if pred(r)]
        return {'n':len(xs),'mean_old_score_gain':sum(r['frozen_cr014_score_gain'] for r in xs)/len(xs) if xs else None,'negative_old_score_gain':sum(r['frozen_cr014_score_gain']<0 for r in xs),'positive_old_score_gain':sum(r['frozen_cr014_score_gain']>0 for r in xs),'mean_old_relative_gain':sum(r['frozen_cr014_relative_gain'] for r in xs)/len(xs) if xs else None}
    payload={'experiment':'CR-015E-mode-switch-diagnostic','validation_status':'DIAGNOSTIC_ONLY_PRE_CR020_DATA','status':'PASS' if not errors and len(rows)==len(cfg['pairs']) else 'FAIL','groups':{
      'append_to_prefix':group(lambda r:r['append_to_prefix']),
      'no_append_to_prefix':group(lambda r:not r['append_to_prefix']),
      'starts_append':group(lambda r:r['starts_append']),
      'starts_prefix':group(lambda r:r['starts_prefix']),
    },'rows':rows,'errors':errors}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    compact={k:v for k,v in payload.items() if k not in ('rows','errors')}; compact['error_count']=len(errors)
    print(json.dumps(compact,indent=2,sort_keys=True))
    if payload['status']!='PASS': raise SystemExit(2)

if __name__=='__main__': main()
