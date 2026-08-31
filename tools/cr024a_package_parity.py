"""Exact action-trace parity: research CR024A hybrid vs generated package.

Uses only already-open raw Stage-A seeds.  No raw Stage-B, adaptive-reserved, or
held-out seed is touched by this packaging audit.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
import tempfile
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'configs/cr023_public_tape_preregistered_seeds_v1.json'


def load_module(path: Path, prefix: str):
    spec = importlib.util.spec_from_file_location(f'{prefix}_{time.time_ns()}', path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def canonical_action_trace(env, seat: int):
    steps = env.toJSON()['steps']
    out=[]
    for frame in steps[1:]:
        row=frame[seat]
        action=row.get('action') if isinstance(row,dict) else None
        out.append(json.dumps(action or {}, sort_keys=True, separators=(',',':')))
    return out


def run(agent, opponent_path: Path, seed: int, seat: int):
    opp=load_module(opponent_path,'cr024a_parity_opp').agent
    agents=[agent,opp] if seat==0 else [opp,agent]
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=True)
    env.run(agents)
    final=env.toJSON()['steps'][-1]
    status=[final[i].get('status') for i in range(2)]
    if status != ['DONE','DONE']: raise RuntimeError(status)
    return {
        'trace': canonical_action_trace(env,seat),
        'self': float(final[seat].get('reward')),
        'opp': float(final[1-seat].get('reward')),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',required=True)
    ap.add_argument('--opponent',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()

    cfg=json.loads(CFG.read_text(encoding='utf-8'))
    open_seeds=[int(x) for x in cfg['raw_backbone_stage_a_seeds']]
    # Fixed before package results: first, middle and last raw Stage-A seeds.
    seeds=[open_seeds[0],open_seeds[len(open_seeds)//2],open_seeds[-1]]
    stage_b=set(int(x) for x in cfg['raw_backbone_stage_b_seeds'])
    reserved=set(int(x) for x in cfg['adaptive_overlay_stage_a_seeds_reserved']) | set(int(x) for x in cfg['adaptive_overlay_stage_b_seeds_reserved'])
    if set(seeds)&stage_b or set(seeds)&reserved: raise SystemExit('seed firewall violation')

    opponent=Path(args.opponent)
    if not opponent.is_absolute(): opponent=ROOT/opponent
    rows=[]; errors=[]

    with tempfile.TemporaryDirectory(prefix='cr024a-parity-') as td:
        td=Path(td)
        with tarfile.open(args.archive,'r:gz') as tf:
            info=tf.getmember('main.py'); fh=tf.extractfile(info)
            package_main=td/'main.py'; package_main.write_bytes(fh.read() if fh else b'')

        # Import builder only for transient top19 extraction; import the research
        # shard to instantiate the frozen research hybrid exactly.
        builder=load_module(ROOT/'tools/build_cr024a_submission.py','cr024a_parity_builder')
        research=load_module(ROOT/'tools/cr024a_guarded_stage_b_shard.py','cr024a_parity_research')
        tape,_=builder.extract_top19_tape()

        for seed in seeds:
            for seat in (0,1):
                try:
                    research_agent,_meta=research.make_guarded_agent(tape)
                    package_mod=load_module(package_main,'cr024a_package')
                    package_agent=package_mod.agent
                    a=run(research_agent,opponent,seed,seat)
                    b=run(package_agent,opponent,seed,seat)
                    same_trace=a['trace']==b['trace']
                    same_rewards=(a['self']==b['self'] and a['opp']==b['opp'])
                    first_diff=None
                    if not same_trace:
                        n=min(len(a['trace']),len(b['trace']))
                        first_diff=next((i for i in range(n) if a['trace'][i]!=b['trace'][i]),n if len(a['trace'])!=len(b['trace']) else None)
                    rows.append({'seed':seed,'seat':seat,'same_trace':same_trace,'same_rewards':same_rewards,'first_diff':first_diff,'research_self':a['self'],'package_self':b['self']})
                    if not same_trace or not same_rewards:
                        errors.append({'seed':seed,'seat':seat,'same_trace':same_trace,'same_rewards':same_rewards,'first_diff':first_diff})
                except Exception as exc:
                    errors.append({'seed':seed,'seat':seat,'error':repr(exc)})

    report={
        'experiment':'CR024A_PACKAGE_PARITY',
        'seeds':seeds,
        'seed_class':'RAW_STAGE_A_ALREADY_OPEN_ONLY',
        'rows':rows,
        'row_count':len(rows),
        'error_count':len(errors),
        'errors':errors,
        'decision':'PASS' if len(rows)==len(seeds)*2 and not errors else 'FAIL',
        'stage_b_touched':False,
        'adaptive_reserved_touched':False,
        'held_out_touched':False,
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('decision','seeds','row_count','error_count','errors')},indent=2,sort_keys=True))
    if report['decision']!='PASS': raise SystemExit(3)


if __name__=='__main__': main()
