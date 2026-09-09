"""Discovery-only causal feature probe for CR071 PRESALE1 at first divergence.
Uses ONLY the original 16-seed screen set. No hosted/promotion decision may use
this output directly. Searches one scalar threshold over legal observable state.
"""
from __future__ import annotations
import argparse, json, multiprocessing as mp, tempfile
from pathlib import Path
from kaggle_exact_runtime import AgentProcess, agent_visible_observation, assert_reference_version, done_status, extract, make_reference_env, make_seeds, norm, reference_config, reference_step

MIN_BRANCH=6
MIN_GAIN=2/32

def score(env, seat):
    rs=[None if env.state[i].reward is None else float(env.state[i].reward) for i in (0,1)]
    st=[str(env.state[i].status) for i in (0,1)]
    if st[seat]=='DONE' and st[1-seat]!='DONE': return 1.0
    if st[seat]!='DONE' and st[1-seat]=='DONE': return 0.0
    if st[seat]!='DONE' or st[1-seat]!='DONE': return 0.5
    m=rs[seat]-rs[1-seat]
    return 1.0 if m>0 else (0.0 if m<0 else 0.5)

def farm_shape(f):
    plants=animals=0
    for row in (f.get('tiles',[]) or []):
        for t in row or []:
            if not isinstance(t,dict): continue
            plants += int(t.get('kind')=='PLANT')
            animals += int(t.get('animal') is not None)
    out={
        'money':float(f.get('money',0) or 0),
        'hands':float(len(f.get('hands',[]) or [])),
        'quadrants':float(len(f.get('unlocked_quadrants',[]) or [])),
        'plants':float(plants),'animals':float(animals),
    }
    for key in ('shed','seeds'):
        v=f.get(key)
        if isinstance(v,dict):
            for k,x in v.items():
                if isinstance(x,(int,float)):
                    out[f'{key}.{k}']=float(x)
    return out

def features(obs, seat):
    out={}
    farms=list(obs.get('farms',[]) or [])
    if len(farms)>=2:
        for pfx,f in (('own',farms[seat]),('opp',farms[1-seat])):
            if isinstance(f,dict):
                for k,v in farm_shape(f).items(): out[f'{pfx}.{k}']=v
    market=obs.get('market') or {}
    for kind in ('prices','inventory'):
        v=market.get(kind) or {}
        if isinstance(v,dict):
            for k,x in v.items():
                if isinstance(x,(int,float)): out[f'market.{kind}.{k}']=float(x)
    return out

def play(cdir,pdir,odir,seed,seat):
    ec,ep=make_reference_env(seed),make_reference_env(seed)
    cc,cp=reference_config(ec),reference_config(ep)
    ctx=mp.get_context('spawn')
    c=AgentProcess(ctx,cdir,f'c{seed}_{seat}'); p=AgentProcess(ctx,pdir,f'p{seed}_{seat}')
    oc=AgentProcess(ctx,odir,f'oc{seed}_{seat}'); op=AgentProcess(ctx,odir,f'op{seed}_{seat}')
    feat=None; divstep=None
    try:
        n=0
        while True:
            dc=all(done_status(s.status) for s in ec.state); dp=all(done_status(s.status) for s in ep.state)
            if dc or dp:
                if dc!=dp: raise RuntimeError('completion mismatch')
                break
            aoc=agent_visible_observation(ec,seat); aop=agent_visible_observation(ep,seat)
            boc=agent_visible_observation(ec,1-seat); bop=agent_visible_observation(ep,1-seat)
            step=int(aoc.get('step',n) or n)
            ac,tc=c.call(aoc,cc); ap,tp=p.call(aop,cp); bc,tbc=oc.call(boc,cc); bp,tbp=op.call(bop,cp)
            if feat is None and norm(ac)!=norm(ap):
                if norm(aoc)!=norm(aop) or norm(boc)!=norm(bop) or norm(bc)!=norm(bp):
                    raise RuntimeError('pre-divergence lockstep violated')
                feat=features(aoc,seat); divstep=step
            if seat==0:
                reference_step(ec,[ac,bc],[tc,tbc]); reference_step(ep,[ap,bp],[tp,tbp])
            else:
                reference_step(ec,[bc,ac],[tbc,tc]); reference_step(ep,[bp,ap],[tbp,tp])
            n+=1
            if n>725: raise RuntimeError('episode too long')
        return {'seed':int(seed),'seat':int(seat),'step':divstep,'features':feat or {},'candidate_score':score(ec,seat),'parent_score':score(ep,seat)}
    finally:
        for x in (c,p,oc,op): x.close()

def stump(rows):
    cand=sum(r['candidate_score'] for r in rows)/len(rows); par=sum(r['parent_score'] for r in rows)/len(rows)
    best=None
    keys=sorted(set.intersection(*(set(r['features']) for r in rows))) if rows else []
    for k in keys:
        vals=sorted(set(r['features'][k] for r in rows))
        for a,b in zip(vals,vals[1:]):
            th=(a+b)/2
            for cand_left in (True,False):
                picks=[(r['features'][k]<=th)==cand_left for r in rows]
                nc=sum(picks); np=len(rows)-nc
                if min(nc,np)<MIN_BRANCH: continue
                s=sum((r['candidate_score'] if pick else r['parent_score']) for r,pick in zip(rows,picks))/len(rows)
                rec={'feature':k,'threshold':th,'candidate_if_le':cand_left,'score':s,'candidate_branch_n':nc,'parent_branch_n':np}
                if best is None or (s, -abs(nc-np), k)>(best['score'],-abs(best['candidate_branch_n']-best['parent_branch_n']),best['feature']): best=rec
    gate=bool(best and best['score']>=cand+MIN_GAIN)
    return {'always_candidate':cand,'always_parent':par,'best_stump':best,'min_branch':MIN_BRANCH,'min_gain_vs_always_candidate':MIN_GAIN,'research_gate_pass':gate,'decision':'BUILD_FRESH_VALIDATION' if gate else 'NO_SIMPLE_STEP110_STUMP'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate',required=True); ap.add_argument('--parent',required=True); ap.add_argument('--cr053',required=True); ap.add_argument('--output',required=True)
    a=ap.parse_args(); assert_reference_version(); rows=[]
    seeds=make_seeds(16,5809072026)
    with tempfile.TemporaryDirectory(prefix='cr071-step110-probe-') as td:
        root=Path(td); c=extract(Path(a.candidate),root,'candidate'); p=extract(Path(a.parent),root,'parent'); o=extract(Path(a.cr053),root,'cr053')
        for seed in seeds:
            for seat in (0,1): rows.append(play(c,p,o,seed,seat))
            print(json.dumps({'completed_games':len(rows),'last_seed':seed}),flush=True)
    result={'schema_version':'kculture-cr071-step110-stump-probe-v1','purpose':'screen_discovery_only','reference_backend':'kaggle-environments==1.32.7','forbidden_features':['seed','identity','final_money_margin'],'rows':rows,'analysis':stump(rows)}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)); print(json.dumps(result['analysis'],indent=2,sort_keys=True))
if __name__=='__main__': main()
