"""CR-013: base-selected close-match flip stress for CR-011.

Screen only frozen R4B across fresh seeds/current public opponents. Select close
(opponent, seed, seat) tuples without consulting CR-011, then replay CR-011 on
exactly those tuples. This tests whether CR-011's relative-money improvement can
change outcomes near the win/loss boundary.
"""
from __future__ import annotations
import argparse, importlib.util, json, statistics, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
SEED_PATH=ROOT/'configs/cr013_close_match_seeds_v1.json'
BASE='candidates/r4b_ablation_market_only.py'; CAND='candidates/cr011_adaptive_early_order.py'

def load_agent(path):
    p=Path(path);p=p if p.is_absolute() else ROOT/p
    s=importlib.util.spec_from_file_location(f'cr013_{p.stem}_{time.time_ns()}',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.agent

def play(cpath,opath,seed,seat):
    c=load_agent(cpath);o=load_agent(opath);agents=[c,o] if seat==0 else [o,c]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True);env.run(agents);f=env.toJSON()['steps'][-1]
    st=[f[i].get('status') for i in range(2)];rw=[f[i].get('reward') for i in range(2)];cr=rw[seat];orr=rw[1-seat]
    if st!=['DONE','DONE'] or not isinstance(cr,(int,float)) or not isinstance(orr,(int,float)):return {'error':True,'statuses':st,'rewards':rw}
    d=float(cr)-float(orr);out='WIN' if d>0 else 'LOSS' if d<0 else 'TIE'
    return {'error':False,'reward':float(cr),'opp_reward':float(orr),'delta':d,'outcome':out}

def score(x):return 1.0 if x=='WIN' else .5 if x=='TIE' else 0.0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--opponent',action='append',required=True);ap.add_argument('--target',type=int,default=40);ap.add_argument('--output',required=True);a=ap.parse_args()
    seeds=json.loads(SEED_PATH.read_text())['seeds'];screen=[];errors=0
    for opp in a.opponent:
      for seed in seeds:
       for seat in (0,1):
        r=play(BASE,opp,seed,seat);errors+=int(r.get('error',False));screen.append({'opponent':opp,'seed':seed,'seat':seat,**r})
    valid=[r for r in screen if not r.get('error')]
    p1=[r for r in valid if abs(r['delta'])<=1000]
    p3=[r for r in valid if abs(r['delta'])<=3000]
    if len(p1)>=a.target:selected=sorted(p1,key=lambda r:abs(r['delta']))[:a.target];rule='abs_delta_le_1000'
    elif len(p3)>=a.target:selected=sorted(p3,key=lambda r:abs(r['delta']))[:a.target];rule='abs_delta_le_3000'
    else:selected=sorted(valid,key=lambda r:abs(r['delta']))[:a.target];rule='nearest_abs_delta_fallback'
    rows=[]
    for b in selected:
        c=play(CAND,b['opponent'],b['seed'],b['seat']);errors+=int(c.get('error',False))
        if c.get('error'):continue
        sg=score(c['outcome'])-score(b['outcome'])
        rows.append({'opponent':b['opponent'],'seed':b['seed'],'seat':b['seat'],'base_delta':b['delta'],'candidate_delta':c['delta'],'relative_gain':c['delta']-b['delta'],'self_gain':c['reward']-b['reward'],'base_outcome':b['outcome'],'candidate_outcome':c['outcome'],'score_gain':sg})
    fav=sum(r['score_gain']>0 for r in rows);bad=sum(r['score_gain']<0 for r in rows);mean_score=statistics.mean(r['score_gain'] for r in rows) if rows else None;mean_rel=statistics.mean(r['relative_gain'] for r in rows) if rows else None
    per={}
    for opp in sorted({r['opponent'] for r in rows}):
        xs=[r for r in rows if r['opponent']==opp];per[opp]={'pairs':len(xs),'mean_relative_gain':statistics.mean(r['relative_gain'] for r in xs),'mean_score_gain':statistics.mean(r['score_gain'] for r in xs),'favorable_changes':sum(r['score_gain']>0 for r in xs),'unfavorable_changes':sum(r['score_gain']<0 for r in xs)}
    gate={'zero_errors':errors==0,'selected_pairs_ge_40':len(rows)>=a.target,'mean_relative_gain_positive':mean_rel is not None and mean_rel>0,'mean_score_gain_ge_0_025':mean_score is not None and mean_score>=0.025,'more_favorable_than_unfavorable_changes':fav>bad}
    passed=all(gate.values())
    payload={'experiment':'CR-013','status':'CLOSE_MATCH_FLIP_SIGNAL_SUPPORTED' if passed else 'CLOSE_MATCH_FLIP_SIGNAL_NOT_SUPPORTED','screen_pairs':len(screen),'screen_errors':errors,'close_within_1000':len(p1),'close_within_3000':len(p3),'selection_rule_used':rule,'selected_pairs':len(rows),'summary':{'mean_base_abs_delta':statistics.mean(abs(r['base_delta']) for r in rows) if rows else None,'mean_relative_gain':mean_rel,'mean_self_gain':statistics.mean(r['self_gain'] for r in rows) if rows else None,'mean_score_gain':mean_score,'favorable_outcome_changes':fav,'unfavorable_outcome_changes':bad},'per_opponent':per,'gate':gate,'selected_rows':rows}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True));print(json.dumps({k:v for k,v in payload.items() if k!='selected_rows'},indent=2,sort_keys=True))
    if not passed:raise SystemExit(2)
if __name__=='__main__':main()
