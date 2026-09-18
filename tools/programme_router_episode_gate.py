"""Freeze one router using train-only static group selection; fresh end-to-end panel."""
import sys,json,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tools'),str(ROOT/'external/kaggriculture-cppsim')]
import kagsim
from programme_suffix_teacher_v0 import utility
from solver.programme_router import ProgrammeRouter
from solver.programme_actions import decode
D=ROOT/'data/programme_teacher/2026-09-18'
def main():
    z=np.load(D/'PROGRAMME_TEACHER_DATA.npz');res=json.loads((D/'PROGRAMME_SUFFIX_TEACHER.json').read_text())
    choices=[]
    for row in res['group_results']:
        g=row['group_id'];train=z['holdout'][z['group']==g]==0
        u=utility(z[f'group_{g}_margins'][train]);best=float(u.mean(0).max())
        choices.append((best,-row['checkpoint'],-g,row))
    row=max(choices,key=lambda x:x[:3])[-1]
    model=dict(group=row['group_id'],checkpoint=row['checkpoint'],members=row['members'],static_program=row['static_program'],tree=row['tree_model'],selection='highest train-only best-static utility; earliest checkpoint tie break')
    tapes=np.load(sys.argv[1])['tapes'];base=tapes[model['static_program'],:model['checkpoint']]
    assert all(np.array_equal(base,tapes[m,:model['checkpoint']]) for m in model['members'])
    out=[];start=time.perf_counter()
    for opp in [0,38,51,52,54,55,58,59]:
        for seed in [53001,53002]:
            for seat in [0,1]:
                pair={}
                for enabled in [False,True]:
                    agent=ProgrammeRouter(tapes,model,enabled);game=kagsim.Game(seed)
                    for t in range(719):
                        a=agent.act(game.observe(seat));b=decode(tapes[opp,t])
                        game.step(a,b) if seat==0 else game.step(b,a)
                    assert agent.calls==int(enabled)
                    pair['router' if enabled else 'static']=game.reward(seat)-game.reward(1-seat)
                out.append(dict(opponent=opp,seed=seed,seat=seat,**pair))
    wr=lambda k:float(np.mean([int(r[k]>0)+.5*int(r[k]==0) for r in out]))
    result=dict(model=model,episodes=len(out)*2,seconds=time.perf_counter()-start,static_wr=wr('static'),router_wr=wr('router'),rows=out,scope='fresh-seed fixed-tape mechanical/transfer panel; not hosted strength')
    (D/'ROUTER_EPISODE_GATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['rows','model']}));print('SELECTED',model['group'],model['checkpoint'],model['static_program'])
if __name__=='__main__':main()
