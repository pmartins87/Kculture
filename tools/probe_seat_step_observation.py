"""Diagnostic: record step/day/hour actually delivered to each Kaggriculture seat.

No strategy evaluation. Runs kaggle-environments 1.32.7 and writes the exact
clock fields seen by two Python agents. This checks the reported seat-1
`observation.step` asymmetry before any candidate is built.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from kaggle_environments import make


def _get(o,k,d=None):
    try:return o.get(k,d)
    except AttributeError:
        try:return o[k]
        except Exception:return d


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--seed',type=int,default=20260829);args=ap.parse_args()
    seen={0:[],1:[]}
    def make_agent(expected_seat):
        def agent(obs,config=None):
            raw=_get(obs,'step','__MISSING__')
            rec={
                'call_index':len(seen[expected_seat]),
                'expected_seat':expected_seat,
                'obs_player':_get(obs,'player',None),
                'step_present':raw!='__MISSING__',
                'step':None if raw=='__MISSING__' else raw,
                'day':_get(obs,'day',None),
                'hour':_get(obs,'hour',None),
            }
            try: rec['derived_step']=int(rec['day'] or 0)*24+int(rec['hour'] or 0)
            except Exception: rec['derived_step']=None
            seen[expected_seat].append(rec)
            return {'farmer':['PASS'],'hands':[],'market':[]}
        return agent
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(args.seed)},debug=True)
    env.run([make_agent(0),make_agent(1)])
    summary={}
    for seat,rows in seen.items():
        nonnull=[r for r in rows if isinstance(r.get('step'),(int,float))]
        nulls=[r for r in rows if r.get('step') is None]
        missing=[r for r in rows if not r.get('step_present')]
        mismatch=[r for r in rows if isinstance(r.get('step'),(int,float)) and r.get('derived_step') is not None and int(r['step'])!=int(r['derived_step'])]
        summary[str(seat)]={
            'calls':len(rows),'numeric_step_calls':len(nonnull),'null_step_calls':len(nulls),'missing_step_calls':len(missing),
            'numeric_step_min':min((int(r['step']) for r in nonnull),default=None),'numeric_step_max':max((int(r['step']) for r in nonnull),default=None),
            'step_vs_dayhour_mismatches':len(mismatch),'first_8':rows[:8],'last_3':rows[-3:],
        }
    payload={'experiment':'seat-step-observation-probe','engine':'kaggle-environments==1.32.7','seed':args.seed,'summary':summary,'observations':seen}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':main()
