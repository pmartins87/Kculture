"""One-opponent shard for frozen CR-021 Stage A/B evaluation."""
from __future__ import annotations
import argparse, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import tools.cr015_preregistered_evaluation as E

CONFIG=ROOT/'configs/cr021_demand_response_preregistered_seeds_v1.json'
CR008=ROOT/'candidates/cr008_adaptive_frontrun.py'
CR015=ROOT/'candidates/cr015_liquidation_phase_early_order.py'
CR021=ROOT/'candidates/cr021_sparse_tomato_demand.py'

def load_module(path):
    spec=importlib.util.spec_from_file_location(f'cr021_{path.stem}_{time.time_ns()}',path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

def play_candidate(opponent_path,seed,seat):
    own=load_module(CR021); opp=load_module(opponent_path)
    agents=[own.agent,opp.agent] if seat==0 else [opp.agent,own.agent]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True); env.run(agents)
    frame=env.toJSON()['steps'][-1]; statuses=[frame[i].get('status') for i in range(2)]
    if statuses!=['DONE','DONE']: raise RuntimeError(f'non-DONE statuses: {statuses}')
    rewards=[float(frame[i].get('reward')) for i in range(2)]
    st=dict(getattr(own,'_STATE',{}).get(seat,{}) or {})
    metrics={k:int(st.get(k,0) or 0) for k in ('trigger_count','plant_count','harvest_count')}
    return rewards[seat],rewards[1-seat],rewards[seat]-rewards[1-seat],metrics

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opponent',required=True);ap.add_argument('--opponent-id',required=True);ap.add_argument('--stage',choices=('a','b'),required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    opp=Path(a.opponent); opp=opp if opp.is_absolute() else ROOT/opp
    cfg=json.loads(CONFIG.read_text()); seeds=cfg['stage_a' if a.stage=='a' else 'stage_b']
    rows=[];errors=[]
    for seed in seeds:
      for seat in (0,1):
        r={'seed':int(seed),'opponent':a.opponent_id,'seat':seat}
        try:
          for key,path in (('cr008',CR008),('cr015',CR015)):
            s,o,d=E.play(path,opp,seed,seat);r[key]={'self':s,'opp':o,'delta':d,'score':E.score(d)}
          s,o,d,m=play_candidate(opp,seed,seat);r['cr021']={'self':s,'opp':o,'delta':d,'score':E.score(d)};r['cr021_metrics']=m
          rows.append(r)
        except Exception as exc:
          errors.append({'seed':int(seed),'opponent':a.opponent_id,'seat':seat,'error':repr(exc)})
    payload={'experiment':'CR-021','stage':a.stage.upper(),'opponent':a.opponent_id,'seeds':seeds,'expected_pairs':len(seeds)*2,'completed_pairs':len(rows),'errors':errors,'rows':rows}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({'opponent':a.opponent_id,'stage':a.stage.upper(),'pairs':len(rows),'errors':len(errors),'triggers':sum(r['cr021_metrics']['trigger_count'] for r in rows),'plants':sum(r['cr021_metrics']['plant_count'] for r in rows),'harvests':sum(r['cr021_metrics']['harvest_count'] for r in rows)},indent=2))
    if errors or len(rows)!=len(seeds)*2: raise SystemExit(3)
if __name__=='__main__':main()
