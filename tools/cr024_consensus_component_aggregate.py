"""Aggregate CR024 Stage-A top11/top19 component decomposition."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

ARMS=('top11','top19','h11_m19','h19_m11')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-glob',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    files=sorted(glob.glob(args.input_glob,recursive=True));rows=[];errors=[]
    for p in files:
        d=json.load(open(p,encoding='utf-8'));errors.extend(d.get('errors') or []);rows.extend(d.get('rows') or [])
    summary={}
    for arm in ARMS:
        fav=unf=unch=0;score=control_score=0.0;margin_gain=[]
        for r in rows:
            c=float(r['cr008']['score']);a=float(r[arm]['score']);score+=a;control_score+=c
            if a>c:fav+=1
            elif a<c:unf+=1
            else:unch+=1
            margin_gain.append(float(r[arm]['delta'])-float(r['cr008']['delta']))
        summary[arm]={
            'favorable':fav,'unfavorable':unf,'unchanged':unch,'net':fav-unf,
            'total_score':score,'control_total_score':control_score,
            'score_gain_vs_cr008':score-control_score,
            'mean_margin_gain_vs_cr008':sum(margin_gain)/max(1,len(margin_gain)),
            'positive_margin_gain_count':sum(x>0 for x in margin_gain),
            'negative_margin_gain_count':sum(x<0 for x in margin_gain),
        }
    # Causal attribution among the two component-splice arms.  This report does
    # not promote a policy; it only identifies which source component carries
    # the top19 margin advantage and which carries harmful conversions.
    pairwise={}
    for a,b in [('h11_m19','top11'),('h11_m19','top19'),('h19_m11','top11'),('h19_m11','top19')]:
        better=worse=same=0;delta_diff=[]
        for r in rows:
            sa=float(r[a]['score']);sb=float(r[b]['score'])
            better+=sa>sb;worse+=sa<sb;same+=sa==sb
            delta_diff.append(float(r[a]['delta'])-float(r[b]['delta']))
        pairwise[f'{a}_vs_{b}']={'better_score':better,'worse_score':worse,'same_score':same,'mean_delta_difference':sum(delta_diff)/max(1,len(delta_diff))}
    mechanical=(len(files)==7 and len(rows)==168 and not errors)
    payload={
        'experiment':'CR024_CONSENSUS_COMPONENT_DECOMP',
        'stage':'RAW_STAGE_A_ALREADY_OPEN',
        'shard_count':len(files),'row_count':len(rows),'error_count':len(errors),'errors':errors,
        'summary':summary,'pairwise':pairwise,
        'stage_b_touched':False,'adaptive_reserved_touched':False,'held_out_touched':False,
        'decision':'DIAGNOSTIC_COMPLETE__FREEZE_NEXT_CONSENSUS_DESIGN' if mechanical else 'MECHANICAL_FAIL',
        'policy':'Do not tune on a future validation set. Use this already-open Stage-A decomposition only to freeze the next consensus/shrinkage candidate before exposing another reserved seed block.',
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'decision':payload['decision'],'row_count':len(rows),'summary':summary,'pairwise':pairwise},indent=2,sort_keys=True))
    if not mechanical:raise SystemExit(3)

if __name__=='__main__':main()
