"""Aggregate frozen CR028 Stage-A variant reports and select diagnostics shortlist."""
from __future__ import annotations
import argparse, glob, json
from pathlib import Path

def key(r):
    q=r.get('reactive') or {}
    return (float(q.get('score_gain') or -999), -int(q.get('regressions') or 999), float(r.get('direct_score') or -999), float(q.get('mean_delta_gain') or -1e18), float(r.get('direct_mean_delta') or -1e18))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-glob',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    files=sorted(glob.glob(a.input_glob,recursive=True));reports=[json.load(open(p,encoding='utf-8')) for p in files]
    ids=[r['variant']['id'] for r in reports]
    expected={'full_recent_top','prefix24_then_cr024','prefix48_then_cr024','prefix100_then_cr024','prefix136_then_cr024','prefix200_then_cr024'}
    mechanical=len(reports)==len(expected) and set(ids)==expected and all((r.get('checks') or {}).get('mechanical') for r in reports)
    ranked=sorted(reports,key=key,reverse=True)
    passes=[r for r in ranked if r.get('screen_pass')]
    compact=[]
    for i,r in enumerate(ranked,1):
        compact.append({'rank':i,'variant':r['variant']['id'],'prefix_turns':r['variant']['recent_prefix_turns'],'screen_pass':bool(r.get('screen_pass')),'direct_score':r.get('direct_score'),'direct_mean_delta':r.get('direct_mean_delta'),'reactive':r.get('reactive'),'per_opponent':r.get('per_opponent'),'errors':r.get('errors')})
    decision='SHORTLIST_FOR_FRESH_HOSTED_CALIBRATION' if mechanical and passes else ('NO_CR028_STAGEA_VARIANT_PASSED' if mechanical else 'MECHANICAL_INCOMPLETE')
    payload={'experiment':'CR028_RECENT_TOP_SPLICE_STAGE_A','mechanical_complete':mechanical,'decision':decision,'passing_variants':[r['variant']['id'] for r in passes],'selected_for_next_stage':passes[0]['variant']['id'] if passes else None,'ranking':compact,'selection_rule':'reactive score gain, fewer regressions, direct score, reactive mean margin, direct mean margin; no threshold rescue','held_out_touched':False,'automatic_kaggle_submission':False}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps(payload,indent=2,sort_keys=True))
    if not mechanical:raise SystemExit(3)
if __name__=='__main__':main()
