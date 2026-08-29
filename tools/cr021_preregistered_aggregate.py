"""Aggregate frozen CR-021 shards and apply preregistered gate."""
from __future__ import annotations
import argparse, glob, json, statistics
from pathlib import Path

def score(d): return 1.0 if d>0 else 0.0 if d<0 else 0.5

def contrast(rows,arm,control):
    rel=[r[arm]['delta']-r[control]['delta'] for r in rows]; own=[r[arm]['self']-r[control]['self'] for r in rows]
    sg=[score(r[arm]['delta'])-score(r[control]['delta']) for r in rows]
    return {'pairs':len(rows),'mean_relative_gain':statistics.mean(rel) if rel else 0.0,'median_relative_gain':statistics.median(rel) if rel else 0.0,'mean_self_gain':statistics.mean(own) if own else 0.0,'mean_score_gain':statistics.mean(sg) if sg else 0.0,'favorable_outcome_changes':sum(x>0 for x in sg),'unfavorable_outcome_changes':sum(x<0 for x in sg),'unchanged_outcomes':sum(x==0 for x in sg),'positive_relative_fraction':sum(x>0 for x in rel)/len(rel) if rel else 0.0}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-glob',required=True);ap.add_argument('--stage',choices=('a','b'),required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    files=sorted(glob.glob(a.input_glob,recursive=True));rows=[];errors=[]
    for f in files:
        p=json.load(open(f));rows.extend(p.get('rows',[]));errors.extend(p.get('errors',[]))
    trig=[r for r in rows if int(r.get('cr021_metrics',{}).get('trigger_count',0) or 0)>0]
    planted=[r for r in rows if int(r.get('cr021_metrics',{}).get('plant_count',0) or 0)>0]
    broad8=contrast(rows,'cr021','cr008'); broad15=contrast(rows,'cr021','cr015'); trig8=contrast(trig,'cr021','cr008');trig15=contrast(trig,'cr021','cr015')
    trigger_count=sum(int(r.get('cr021_metrics',{}).get('trigger_count',0) or 0) for r in rows);plant_count=sum(int(r.get('cr021_metrics',{}).get('plant_count',0) or 0) for r in rows);harvest_count=sum(int(r.get('cr021_metrics',{}).get('harvest_count',0) or 0) for r in rows)
    no_harm8=broad8['unfavorable_outcome_changes']<=broad8['favorable_outcome_changes'];no_harm15=broad15['unfavorable_outcome_changes']<=broad15['favorable_outcome_changes']
    supported=(not errors and len(rows)==216 and no_harm8 and no_harm15 and trigger_count>0 and trig8['mean_relative_gain']>0 and broad8['mean_relative_gain']>=-25.0)
    gate={'zero_errors':not errors,'expected_pairs_complete':len(rows)==216,'no_net_unfavorable_vs_cr008':no_harm8,'no_net_unfavorable_vs_cr015':no_harm15,'actual_trigger_present':trigger_count>0,'triggered_mean_relative_vs_cr008_positive':trig8['mean_relative_gain']>0 if trig else False,'broad_mean_relative_vs_cr008_ge_minus25':broad8['mean_relative_gain']>=-25.0,'supported':supported if a.stage=='a' else None}
    payload={'experiment':'CR-021','stage':a.stage.upper(),'files':files,'completed_pairs':len(rows),'error_count':len(errors),'behavior':{'trigger_count':trigger_count,'triggered_pairs':len(trig),'plant_count':plant_count,'planted_pairs':len(planted),'harvest_count':harvest_count},'broad':{'cr021_vs_cr008':broad8,'cr021_vs_cr015':broad15},'triggered':{'cr021_vs_cr008':trig8,'cr021_vs_cr015':trig15},'stage_a_gate':gate,'errors':errors,'rows':rows}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,sort_keys=True));print(json.dumps({k:v for k,v in payload.items() if k not in ('rows','errors','files')},indent=2,sort_keys=True))
    if errors or len(rows)!=216: raise SystemExit(3)
    if a.stage=='a' and not supported: raise SystemExit(2)
if __name__=='__main__':main()
