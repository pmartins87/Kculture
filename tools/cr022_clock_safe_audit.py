"""Audit CR022 clock-safe CR008 diagnostic derivative.

1) Normal engine parity: clock-safe must emit exactly the same action sequence and
   terminal rewards as frozen CR008 when `step` is present.
2) Fault injection: take real stored observations, set `step=None`, and show that
   a normalized R4B backbone reproduces the action from the same observation
   with its correct numeric clock, while raw R4B can diverge.

Research/robustness diagnostic only; no hosted-strength claim.
"""
from __future__ import annotations

import argparse, copy, importlib.util, json, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
CR008=ROOT/'candidates/cr008_adaptive_frontrun.py'
SAFE=ROOT/'candidates/cr022_clock_safe_cr008.py'
R4B=ROOT/'candidates/r4b_ablation_market_only.py'
SEEDS=(2026082901,2026082902,2026082903,2026082904,2026082905,2026082906)
CHECKPOINTS=(1,24,96,310,500,718)


def load(path):
    spec=importlib.util.spec_from_file_location(f'audit_{path.stem}_{time.time_ns()}',path);m=importlib.util.module_from_spec(spec);assert spec.loader is not None;spec.loader.exec_module(m);return m


def run(path,seed,seat):
    m=load(path);actions=[]
    def wrapped(obs,config=None):
        a=m.agent(obs,config);actions.append(copy.deepcopy(a));return a
    agents=[wrapped,'starter'] if seat==0 else ['starter',wrapped]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True);env.run(agents);final=env.toJSON()['steps'][-1]
    return {'actions':actions,'reward':float(final[seat]['reward']),'opp_reward':float(final[1-seat]['reward']),'status':final[seat]['status'],'replay':env.toJSON()}


def r4b_action(obs):return load(R4B).agent(copy.deepcopy(obs),None)


def derive(obs):
    out=copy.deepcopy(obs);out['step']=int(out.get('day',0) or 0)*24+int(out.get('hour',0) or 0);return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    parity=[];sample_replay=None
    for seed in SEEDS:
      for seat in (0,1):
        a=run(CR008,seed,seat);b=run(SAFE,seed,seat)
        same=a['actions']==b['actions'] and a['reward']==b['reward'] and a['opp_reward']==b['opp_reward'] and a['status']==b['status']
        parity.append({'seed':seed,'seat':seat,'same':same,'action_mismatches':sum(x!=y for x,y in zip(a['actions'],b['actions']))+abs(len(a['actions'])-len(b['actions'])),'reward_cr008':a['reward'],'reward_safe':b['reward']})
        if sample_replay is None and seat==1:sample_replay=a['replay']
    faults=[]
    steps=(sample_replay or {}).get('steps') or []
    for t in CHECKPOINTS:
        if t>=len(steps)-1:continue
        obs=copy.deepcopy(steps[t][1].get('observation') or {})
        # Stored replay may already omit step for seat1. Construct both variants explicitly.
        numeric=derive(obs);missing=copy.deepcopy(numeric);missing['step']=None;normalized=derive(missing)
        expected=r4b_action(numeric);raw_missing=r4b_action(missing);fixed=r4b_action(normalized)
        faults.append({'t':t,'stored_step':obs.get('step'),'day':obs.get('day'),'hour':obs.get('hour'),'expected_eq_fixed':expected==fixed,'expected_eq_raw_missing':expected==raw_missing,'raw_missing_differs':expected!=raw_missing})
    payload={'experiment':'CR022-clock-safe-audit','normal_parity':{'cases':len(parity),'all_pass':all(r['same'] for r in parity),'rows':parity},'fault_injection':{'cases':len(faults),'all_fixed_match':all(r['expected_eq_fixed'] for r in faults),'raw_divergence_count':sum(r['raw_missing_differs'] for r in faults),'rows':faults}}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps(payload,indent=2,sort_keys=True))
    if not payload['normal_parity']['all_pass'] or not payload['fault_injection']['all_fixed_match']:raise SystemExit(2)

if __name__=='__main__':main()
