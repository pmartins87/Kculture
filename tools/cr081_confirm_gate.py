"""Apply the frozen CR081 promotion gate; no parameter/strategy selection."""
import argparse,json
from pathlib import Path

MASTER_SEED=9120812
SEED_COUNT=32


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    games={}
    for p in a.results.glob('*.json'):
        d=json.loads(p.read_text())
        if 'metrics_a_vs_b' in d:games[d['a'],d['b']]=d
    guards=['CR053','CR061','CR065']
    required=[('CR081','CR071M')]+[(v,o) for o in guards for v in ['CR081','CR071M']]
    missing=[x for x in required if x not in games]
    report={
        'schema_version':'cr081-promotion-gate-v2-runtime-aligned',
        'master_seed':MASTER_SEED,
        'seed_count':SEED_COUNT,
        'invalid_prior_run':34671122716,
        'missing':missing,
        'primary_metric':'seat-balanced W/L',
        'automatic_kaggle_submission':False,
        'retune_on_failure_permitted':False,
    }
    checks={'complete_panel':not missing}
    if not missing:
        checks['all_64_games_32_fresh_seeds']=all(
            games[x]['metrics_a_vs_b']['games']==64 and games[x]['seed_count']==SEED_COUNT and games[x]['master_seed']==MASTER_SEED
            for x in required)
        checks['no_errors_or_non_done']=all(not games[x]['errors'] and games[x]['metrics_a_vs_b']['non_done_games']==0 for x in required)
        rate=lambda v,o:games[v,o]['metrics_a_vs_b']['score_rate']
        delta={o:rate('CR081',o)-rate('CR071M',o) for o in guards}
        checks['direct_at_least_0_5625']=rate('CR081','CR071M')>=.5625
        checks['aggregate_guardrail_delta_nonnegative']=sum(delta.values())>=0
        checks['each_guardrail_delta_at_least_minus_0_0625']=min(delta.values())>=-.0625
        report.update({
            'guardrail_deltas':delta,
            'rows':[{'a':x[0],'b':x[1],**games[x]['metrics_a_vs_b']} for x in required],
        })
    report['checks']=checks
    report['pass']=all(checks.values())
    report['decision']='ELIGIBLE_FOR_ONE_HOSTED_PROBE_AFTER_SLOT_ACCOUNTING' if report['pass'] else 'CLOSE_CR081_BRIDGE_MOVE_TO_STATE_ADAPTIVE_MACRO_POLICY'
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True))
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=='__main__':main()
