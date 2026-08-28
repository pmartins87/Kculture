"""CR-014C: fast three-arm decomposition on the five actual W/L flips.

Runs frozen R4B, CR-008 and CR-011 on a pre-frozen five-pair diagnostic set.
This answers whether each CR-011 outcome flip came from adaptive selling itself
or specifically from moving the same adaptive sale to the front of the market
queue. Diagnostic only; no thresholds are learned here.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
CFG=ROOT/'configs/cr014c_flip_pairs_v1.json'
ARMS={
    'r4b':ROOT/'candidates/r4b_ablation_market_only.py',
    'cr008':ROOT/'candidates/cr008_adaptive_frontrun.py',
    'cr011':ROOT/'candidates/cr011_adaptive_early_order.py',
}


def load_agent(path:Path):
    spec=importlib.util.spec_from_file_location(f'cr014c_{path.stem}_{time.time_ns()}',path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m.agent


def play(path:Path,opp_path:Path,seed:int,seat:int):
    a=load_agent(path); o=load_agent(opp_path)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run([a,o] if seat==0 else [o,a])
    frame=env.toJSON()['steps'][-1]
    statuses=[frame[i].get('status') for i in range(2)]
    if statuses!=['DONE','DONE']: raise RuntimeError(f'non-DONE {statuses}')
    own=float(frame[seat].get('reward')); other=float(frame[1-seat].get('reward'))
    return {'self':own,'opp':other,'delta':own-other,'score':1.0 if own>other else 0.0 if own<other else 0.5}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--opponent-dir',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
    od=Path(args.opponent_dir); od=od if od.is_absolute() else ROOT/od
    cfg=json.loads(CFG.read_text())
    rows=[]; parity=[]
    for e in cfg['pairs']:
        vals={k:play(p,od/f"{e['opponent']}.py",int(e['seed']),int(e['seat'])) for k,p in ARMS.items()}
        if abs(vals['r4b']['delta']-float(e['r4b_delta']))>1e-9 or abs(vals['cr011']['delta']-float(e['cr011_delta']))>1e-9:
            parity.append({'expected':e,'observed':vals})
        row=dict(e); row['arms']=vals
        row['adaptation_cr008_vs_r4b']={
            'relative':vals['cr008']['delta']-vals['r4b']['delta'],
            'self':vals['cr008']['self']-vals['r4b']['self'],
            'score':vals['cr008']['score']-vals['r4b']['score'],
        }
        row['order_cr011_vs_cr008']={
            'relative':vals['cr011']['delta']-vals['cr008']['delta'],
            'self':vals['cr011']['self']-vals['cr008']['self'],
            'score':vals['cr011']['score']-vals['cr008']['score'],
        }
        if vals['cr008']['score']<vals['r4b']['score']:
            cause='ADAPTATION_ALREADY_FLIPS'
        elif vals['cr011']['score']<vals['cr008']['score']:
            cause='EARLY_ORDER_CROSSES_BOUNDARY'
        elif vals['cr008']['delta']<vals['r4b']['delta'] and vals['cr011']['delta']<vals['cr008']['delta']:
            cause='BOTH_DEGRADE_MARGIN'
        elif vals['cr008']['delta']<vals['r4b']['delta']:
            cause='ADAPTATION_DEGRADES_MARGIN'
        elif vals['cr011']['delta']<vals['cr008']['delta']:
            cause='EARLY_ORDER_DEGRADES_MARGIN'
        else:
            cause='NO_NEGATIVE_COMPONENT'
        row['decomposition']=cause; rows.append(row)
    payload={
        'experiment':'CR-014C','status':'PASS' if not parity else 'PARITY_FAIL','parity_errors':parity,'rows':rows,
        'cause_counts':{c:sum(r['decomposition']==c for r in rows) for c in sorted(set(r['decomposition'] for r in rows))},
        'policy':'Diagnostic only. CR-015 rule selection still requires identity-free state rationale and preregistered fresh validation.'
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in payload.items() if k not in ('rows','parity_errors')}|{'parity_error_count':len(parity),'compact_rows':[{'label':r['label'],'opponent':r['opponent'],'seed':r['seed'],'seat':r['seat'],'deltas':{k:v['delta'] for k,v in r['arms'].items()},'scores':{k:v['score'] for k,v in r['arms'].items()},'cause':r['decomposition']} for r in rows]},indent=2,sort_keys=True))
    if parity: raise SystemExit(2)

if __name__=='__main__': main()
