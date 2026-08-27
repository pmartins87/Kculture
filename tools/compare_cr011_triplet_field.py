"""Paired causal comparison: CR-011 vs CR-008 vs frozen R4B."""
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path

def load(root):
    fs=list(Path(root).glob('*/tournament.json'))
    if len(fs)!=1:raise RuntimeError(f'expected one tournament under {root}: {fs}')
    return json.loads(fs[0].read_text(encoding='utf-8'))
def key(e):return (e['opponent'],int(e['seed']),int(e['candidate_seat']))
def score(e):return 1.0 if e['outcome']=='WIN' else .5 if e['outcome']=='TIE' else 0.0 if e['outcome']=='LOSS' else None
def mean(x):return statistics.mean(x) if x else None

def compare(a,b):
    am={key(e):e for e in a['episodes']};bm={key(e):e for e in b['episodes']};ks=sorted(set(am)&set(bm));rows=[]
    for k in ks:
        x,y=am[k],bm[k]
        if x['money_delta'] is None or y['money_delta'] is None:continue
        rows.append({'opponent':k[0],'seed':k[1],'seat':k[2],'self_gain':float(x['candidate_reward'])-float(y['candidate_reward']),'relative_gain':float(x['money_delta'])-float(y['money_delta']),'score_gain':score(x)-score(y)})
    per={}
    for o in sorted({r['opponent'] for r in rows}):
        xs=[r for r in rows if r['opponent']==o];per[o]={'pairs':len(xs),'mean_self_gain':mean([r['self_gain'] for r in xs]),'mean_relative_gain':mean([r['relative_gain'] for r in xs]),'mean_score_gain':mean([r['score_gain'] for r in xs])}
    return {'complete':set(am)==set(bm) and len(rows)==len(am)==len(bm),'pairs':len(rows),'mean_self_gain':mean([r['self_gain'] for r in rows]),'median_self_gain':statistics.median([r['self_gain'] for r in rows]) if rows else None,'mean_relative_gain':mean([r['relative_gain'] for r in rows]),'mean_score_gain':mean([r['score_gain'] for r in rows]),'positive_self_families':sum((v['mean_self_gain'] or 0)>0 for v in per.values()),'worst_family_score_gain':min((v['mean_score_gain'] for v in per.values()),default=None),'per_opponent':per,'rows':rows}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cr011-root',required=True);ap.add_argument('--cr008-root',required=True);ap.add_argument('--r4b-root',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    j=load(a.cr011_root);e=load(a.cr008_root);b=load(a.r4b_root);jb=compare(j,b);je=compare(j,e)
    gate={'complete_triplet_coverage':jb['complete'] and je['complete'],'zero_errors':j['overall']['errors']==0 and e['overall']['errors']==0 and b['overall']['errors']==0,'vs_r4b_mean_self_positive':(jb['mean_self_gain'] or 0)>0,'vs_r4b_mean_relative_positive':(jb['mean_relative_gain'] or 0)>0,'vs_r4b_positive_self_families_ge_2':jb['positive_self_families']>=2,'vs_r4b_score_not_worse_0_02':(jb['mean_score_gain'] or 0)>=-0.02,'vs_r4b_no_family_score_regression_gt_0_08':jb['worst_family_score_gain'] is not None and jb['worst_family_score_gain']>=-0.08,'vs_cr008_mean_self_positive':(je['mean_self_gain'] or 0)>0,'vs_cr008_mean_relative_positive':(je['mean_relative_gain'] or 0)>0,'vs_cr008_positive_self_families_ge_2':je['positive_self_families']>=2,'vs_cr008_score_not_worse_0_02':(je['mean_score_gain'] or 0)>=-0.02}
    passed=all(gate.values());payload={'experiment':'CR-011','status':'EARLY_ORDER_CAUSAL_PASS' if passed else 'EARLY_ORDER_CAUSAL_FAIL','cr011':j['candidate'],'cr008':e['candidate'],'r4b':b['candidate'],'cr011_overall':j['overall'],'cr008_overall':e['overall'],'r4b_overall':b['overall'],'vs_r4b':jb,'vs_cr008':je,'gate':gate}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps({k:v for k,v in payload.items() if k not in ('vs_r4b','vs_cr008')},indent=2,sort_keys=True));print('vs_r4b',json.dumps({k:v for k,v in jb.items() if k!='rows'},indent=2));print('vs_cr008',json.dumps({k:v for k,v in je.items() if k!='rows'},indent=2))
    if not passed:raise SystemExit(2)
if __name__=='__main__':main()
