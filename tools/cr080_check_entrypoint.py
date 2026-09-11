"""Real official-loader contract tests; invalid returned actions cannot be scored."""
import argparse,json,multiprocessing as mp,tempfile
from pathlib import Path
from kaggle_exact_runtime import AgentProcess,make_reference_env,reference_config,agent_visible_observation


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    env=make_reference_env(86357557);cfg=reference_config(env);ctx=mp.get_context('spawn');checks=[]
    with tempfile.TemporaryDirectory() as td:
        for label,code,should_fail in [('raised_exception','def agent(obs):\n    raise ValueError("CR080_CONTRACT_SENTINEL")\n',True),('invalid_action','def agent(obs):\n    return ["PASS"]\n',True),('legal_pass','def agent(obs):\n    return {"farmer":["PASS"],"hands":[],"market":[]}\n',False)]:
            p=Path(td)/label;p.mkdir();(p/'main.py').write_text(code);proc=AgentProcess(ctx,p,label)
            try:
                try:out,_=proc.call(agent_visible_observation(env,0),cfg);failed=False;detail=out
                except RuntimeError as e:failed=True;detail=str(e)
                checks.append({'check':label,'pass':failed==should_fail,'detail':detail})
            finally:proc.close()
    for seat in [0,1]:
        proc=AgentProcess(ctx,a.package.resolve(),'cr080_actual')
        try:
            out,dt=proc.call(agent_visible_observation(env,seat),cfg)
            # This validates actual compiled source and external model loading.
            ok=out.get('market')==[['BUY_PRODUCT','WHEAT',13]] and out.get('farmer')==['PASS']
            checks.append({'check':f'actual_loader_seat_{seat}','pass':ok,'duration':dt,'action':out})
        finally:proc.close()
    report={'checks':checks,'pass':all(c['pass'] for c in checks)}
    a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    if not report['pass']:raise SystemExit(2)

if __name__=='__main__':main()
