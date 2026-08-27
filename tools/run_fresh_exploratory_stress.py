"""KEXP-052 fresh exploratory stress test.

Generate deterministic environmental seeds that are disjoint from frozen
 development/validation/held-out partitions and from the previously used
 exploratory live-meta pool. Run candidate vs frozen R4B in both seats.

This is exploratory development evidence only. It never reads individual
validation/held-out outcomes and never tunes against those partitions.
"""
from __future__ import annotations
import argparse, json, random, statistics, sys
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.run_episode import resolve_agent
BASE="file:candidates/r4b_ablation_market_only.py:agent"
MASTER=202608270052


def walk_seeds(v,out):
    if isinstance(v,dict):
        for x in v.values(): walk_seeds(x,out)
    elif isinstance(v,list):
        for x in v: walk_seeds(x,out)
    elif isinstance(v,int): out.add(v)


def excluded():
    out=set()
    parts=json.loads((ROOT/'configs/seed_partitions.json').read_text(encoding='utf-8'))
    for key in ('development','validation','held_out'):
        out.update(int(x) for x in parts.get(key,[]))
    p=ROOT/'configs/exploratory_live_meta_seeds_20260825.json'
    if p.exists(): walk_seeds(json.loads(p.read_text(encoding='utf-8')),out)
    return out


def fresh_seeds(n):
    rng=random.Random(MASTER); used=excluded(); out=[]
    while len(out)<n:
        x=rng.randint(1,2147483646)
        if x not in used:
            used.add(x);out.append(x)
    return out


def run_game(candidate,seed,seat):
    c=resolve_agent(candidate);o=resolve_agent(BASE)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run([c,o] if seat==0 else [o,c]);rep=env.toJSON();f=rep['steps'][-1]
    cr=f[seat].get('reward');orr=f[1-seat].get('reward');cs=f[seat].get('status');os=f[1-seat].get('status')
    if cs!='DONE' or os!='DONE' or not isinstance(cr,(int,float)) or not isinstance(orr,(int,float)):
        return {'seed':seed,'candidate_seat':seat,'outcome':'ERROR','terminal_delta':None,'candidate_reward':cr,'opponent_reward':orr,'candidate_status':cs,'opponent_status':os}
    d=float(cr)-float(orr); outcome='WIN' if d>0 else 'LOSS' if d<0 else 'TIE'
    return {'seed':seed,'candidate_seat':seat,'outcome':outcome,'terminal_delta':d,'candidate_reward':cr,'opponent_reward':orr,'candidate_status':cs,'opponent_status':os}


def block(rows):
    v=[r for r in rows if r['outcome']!='ERROR'];w=sum(r['outcome']=='WIN' for r in v);l=sum(r['outcome']=='LOSS' for r in v);t=sum(r['outcome']=='TIE' for r in v)
    return {'games':len(rows),'valid':len(v),'errors':len(rows)-len(v),'wins':w,'losses':l,'ties':t,'score_rate_tie_half':(w+.5*t)/len(v) if v else None,'mean_terminal_delta':statistics.mean(r['terminal_delta'] for r in v) if v else None}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);ap.add_argument('--count',type=int,default=96);ap.add_argument('--output',required=True);args=ap.parse_args()
    seeds=fresh_seeds(args.count);rows=[]
    for seed in seeds:
        for seat in (0,1): rows.append(run_game(args.candidate,seed,seat))
    overall=block(rows);s0=block([r for r in rows if r['candidate_seat']==0]);s1=block([r for r in rows if r['candidate_seat']==1])
    gate={'zero_errors':overall['errors']==0,'overall_score_ge_053':overall['score_rate_tie_half'] is not None and overall['score_rate_tie_half']>=.53,'mean_delta_positive':overall['mean_terminal_delta'] is not None and overall['mean_terminal_delta']>0,'both_seats_ge_048':s0['score_rate_tie_half'] is not None and s1['score_rate_tie_half'] is not None and min(s0['score_rate_tie_half'],s1['score_rate_tie_half'])>=.48}
    gate['pass']=all(gate.values())
    payload={'schema_version':'fresh-exploratory-stress-v1','master_seed':MASTER,'seed_count':len(seeds),'seeds':seeds,'candidate':args.candidate,'baseline':BASE,'summary':{'overall':overall,'seat0':s0,'seat1':s1},'predeclared_gate':gate,'rows':rows}
    out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({'summary':payload['summary'],'gate':gate},indent=2,sort_keys=True))
if __name__=='__main__':main()
