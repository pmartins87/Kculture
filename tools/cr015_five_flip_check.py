"""Fast diagnostic: CR-015 on the five CR-014C outcome flips only.

Diagnostic-only.  Fresh preregistered CR-015 Stage A remains the promotion gate.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
CFG=ROOT/'configs/cr014c_flip_pairs_v1.json'
ARMS={
 'cr008':ROOT/'candidates/cr008_adaptive_frontrun.py',
 'cr011':ROOT/'candidates/cr011_adaptive_early_order.py',
 'cr015':ROOT/'candidates/cr015_liquidation_phase_early_order.py',
}

def load(path):
    s=importlib.util.spec_from_file_location(f'ff_{path.stem}_{time.time_ns()}',path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m.agent

def play(path,opp,seed,seat):
    a,o=load(path),load(opp)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run([a,o] if seat==0 else [o,a]); f=env.toJSON()['steps'][-1]
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
        seed=int(e['seed']); seat=int(e['seat']); opp=od/f"{e['opponent']}.py"
        try:
            vals={k:play(p,opp,seed,seat) for k,p in ARMS.items()}
            rows.append({'opponent':e['opponent'],'seed':seed,'seat':seat,'expected_cr011_score_gain':e['score_gain'],'terminal':vals})
        except Exception as exc: errors.append({'opponent':e['opponent'],'seed':seed,'seat':seat,'error':repr(exc)})
    bad=[r for r in rows if float(r['expected_cr011_score_gain'])<0]
    good=[r for r in rows if float(r['expected_cr011_score_gain'])>0]
    recovered=sum(r['terminal']['cr015']['score']==r['terminal']['cr008']['score']==1.0 for r in bad)
    preserved=sum(r['terminal']['cr015']['score']==r['terminal']['cr011']['score']==1.0 for r in good)
    payload={'experiment':'CR-015-five-flip-check','validation_status':'DIAGNOSTIC_ONLY','status':'PASS' if not errors and recovered==len(bad) and preserved==len(good) else 'FAIL','catastrophic_wins_recovered':recovered,'catastrophic_count':len(bad),'favorable_wins_preserved':preserved,'favorable_count':len(good),'errors':errors,'rows':rows}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in payload.items() if k not in ('rows','errors')}|{'error_count':len(errors)},indent=2,sort_keys=True))
    if payload['status']!='PASS': raise SystemExit(2)
if __name__=='__main__': main()
