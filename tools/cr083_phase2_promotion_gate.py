"""Apply the frozen CR083 Phase-2 promotion gate."""
import argparse,json
from pathlib import Path
MASTER=9130832
SEEDS=32

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    games={}
    for p in a.results.rglob('*.json'):
        d=json.loads(p.read_text())
        if 'metrics_a_vs_b' in d: games[(d['a'],d['b'])]=d
    guards=['CR053','CR061','CR065']
    required=[('CR083','CR071M')]+[(v,o) for o in guards for v in ['CR083','CR071M']]
    missing=[list(x) for x in required if x not in games]
    checks={'complete_panel':not missing}
    out={'schema_version':'cr083-phase2-promotion-gate-v1','master_seed':MASTER,'seed_count':SEEDS,'missing':missing}
    if not missing:
        checks['all_64_games_32_fresh_seeds']=all(games[x]['metrics_a_vs_b']['games']==64 and games[x]['seed_count']==SEEDS and games[x]['master_seed']==MASTER for x in required)
        checks['no_errors_or_non_done']=all(not games[x]['errors'] and games[x]['metrics_a_vs_b']['non_done_games']==0 for x in required)
        rate=lambda v,o:games[(v,o)]['metrics_a_vs_b']['score_rate']
        delta={o:rate('CR083',o)-rate('CR071M',o) for o in guards}
        checks['direct_at_least_0_5625']=rate('CR083','CR071M')>=0.5625
        checks['aggregate_guardrail_delta_nonnegative']=sum(delta.values())>=0
        checks['each_guardrail_delta_at_least_minus_0_0625']=min(delta.values())>=-0.0625
        out['guardrail_deltas']=delta
        out['rows']=[{'a':x[0],'b':x[1],**games[x]['metrics_a_vs_b']} for x in required]
    out['checks']=checks;out['pass']=all(checks.values())
    out['decision']='ELIGIBLE_FOR_ONE_HOSTED_PROBE_AFTER_SLOT_ACCOUNTING' if out['pass'] else 'CLOSE_CR083_SEED_DEMAND_CLAMP'
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__':main()
