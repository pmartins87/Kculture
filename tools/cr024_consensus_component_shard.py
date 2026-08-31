"""CR024 consensus contingency: causal top11/top19 component decomposition.

Stage-A-only development diagnostic.  Because the two public tapes have an
identical farmer action at all 719 steps and their hands/market disagreements
are disjoint, we can test which component carries performance/harm without
inventing a threshold.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import tempfile
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'configs/cr023_public_tape_preregistered_seeds_v1.json'
CR008=ROOT/'candidates/cr008_adaptive_frontrun.py'
ROUTES=('top11_openloop','top19_openloop')


def load_agent(path:Path,prefix:str):
    spec=importlib.util.spec_from_file_location(f'{prefix}_{time.time_ns()}',path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod.agent


def clock(obs):
    try:
        raw=obs.get('step')
        if raw is not None:return max(0,int(raw))
    except Exception:pass
    try:return max(0,int(obs.get('day') or 0))*24+max(0,int(obs.get('hour') or 0))
    except Exception:return 0


def finite(x):
    y=float(x)
    if not math.isfinite(y):raise RuntimeError(x)
    return y


def score(delta):return 1.0 if delta>0 else 0.0 if delta<0 else 0.5


def download_tape(api,meta,folder):
    eid=int(meta['episode_id']);seat=int(meta['source_seat'])
    api.competition_episode_replay(eid,path=str(folder),quiet=True)
    p=folder/f'episode-{eid}-replay.json'
    replay=json.loads(p.read_text(encoding='utf-8'));steps=replay.get('steps') or []
    if len(steps)<720:raise RuntimeError(f'short replay {eid}')
    return [copy.deepcopy((steps[t+1][seat] or {}).get('action') or {}) for t in range(719)]


def make_tape_agent(tape):
    def agent(obs,config=None):return copy.deepcopy(tape[max(0,min(718,clock(obs)))])
    return agent


def compose(a,b,hands_from,market_from):
    out=[]
    for x,y in zip(a,b):
        # Farmer is asserted identical below; preserve top19 copy as canonical.
        z=copy.deepcopy(y)
        z['hands']=copy.deepcopy((a if hands_from=='top11' else b)[len(out)].get('hands'))
        z['market']=copy.deepcopy((a if market_from=='top11' else b)[len(out)].get('market'))
        out.append(z)
    return out


def play(agent,opp_path,seed,seat):
    opp=load_agent(opp_path,'cr024_comp_opp')
    agents=[agent,opp] if seat==0 else [opp,agent]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run(agents);frame=env.toJSON()['steps'][-1]
    if [frame[i].get('status') for i in range(2)]!=['DONE','DONE']:raise RuntimeError('non-DONE')
    own=finite(frame[seat].get('reward'));other=finite(frame[1-seat].get('reward'));delta=own-other
    return {'self':own,'opp':other,'delta':delta,'score':score(delta)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opponent',required=True);ap.add_argument('--opponent-id',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding='utf-8'))
    seeds=[int(x) for x in cfg['raw_backbone_stage_a_seeds']]
    stage_b=set(int(x) for x in cfg['raw_backbone_stage_b_seeds'])
    if set(seeds)&stage_b:raise SystemExit('seed firewall')
    opp=Path(args.opponent);opp=opp if opp.is_absolute() else ROOT/opp
    api=KaggleApi();api.authenticate();rows=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='cr024-comp-') as td:
        td=Path(td);t11=download_tape(api,cfg['routes']['top11_openloop'],td);t19=download_tape(api,cfg['routes']['top19_openloop'],td)
        for i,(x,y) in enumerate(zip(t11,t19)):
            if json.dumps(x.get('farmer'),sort_keys=True)!=json.dumps(y.get('farmer'),sort_keys=True):raise RuntimeError(f'farmer mismatch at {i}')
            if json.dumps(x.get('hands'),sort_keys=True)!=json.dumps(y.get('hands'),sort_keys=True) and json.dumps(x.get('market'),sort_keys=True)!=json.dumps(y.get('market'),sort_keys=True):raise RuntimeError(f'overlapping hands/market mismatch at {i}')
        arms={
            'top11':t11,
            'top19':t19,
            'h11_m19':compose(t11,t19,'top11','top19'),
            'h19_m11':compose(t11,t19,'top19','top11'),
        }
        for seed in seeds:
            for seat in (0,1):
                row={'seed':seed,'seat':seat,'opponent':args.opponent_id}
                try:row['cr008']=play(load_agent(CR008,'cr024_comp_control'),opp,seed,seat)
                except Exception as exc:errors.append({'seed':seed,'seat':seat,'arm':'cr008','error':repr(exc)});continue
                failed=False
                for name,tape in arms.items():
                    try:row[name]=play(make_tape_agent(tape),opp,seed,seat)
                    except Exception as exc:errors.append({'seed':seed,'seat':seat,'arm':name,'error':repr(exc)});failed=True;break
                if not failed:rows.append(row)
    payload={'experiment':'CR024_CONSENSUS_COMPONENT_DECOMP','stage':'RAW_STAGE_A_ALREADY_OPEN','opponent':args.opponent_id,'expected_rows':len(seeds)*2,'completed_rows':len(rows),'errors':errors,'stage_b_touched':False,'adaptive_reserved_touched':False,'held_out_touched':False,'rows':rows}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'opponent':args.opponent_id,'completed_rows':len(rows),'errors':len(errors)},indent=2))
    if errors or len(rows)!=len(seeds)*2:raise SystemExit(3)

if __name__=='__main__':main()
