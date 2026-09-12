"""Frozen CR083 Phase-2 direct Gate A."""
import argparse,json
from pathlib import Path
MASTER=9130831
SEEDS=16

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    d=json.loads(a.result.read_text())
    m=d['metrics_a_vs_b']
    checks={
        'identity':d.get('a')=='CR083' and d.get('b')=='CR071M',
        'exact_32_games_16_seeds':m.get('games')==32 and d.get('seed_count')==SEEDS and d.get('master_seed')==MASTER,
        'no_errors_or_non_done':not (d.get('errors') or []) and m.get('non_done_games')==0,
        'score_rate_at_least_0_5625':m.get('score_rate',0)>=0.5625,
        'mean_margin_positive':m.get('mean_margin_secondary',0)>0,
    }
    out={'schema_version':'cr083-phase2-gate-a-v1','master_seed':MASTER,'seed_count':SEEDS,'checks':checks,
         'metrics':m,'pass':all(checks.values())}
    out['decision']='ELIGIBLE_FOR_FROZEN_PROMOTION_PANEL' if out['pass'] else 'CLOSE_CR083_SEED_DEMAND_CLAMP'
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__':main()
