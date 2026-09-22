#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from pathlib import Path
H=('0','1','2','4','8','16','32','64','128','256','512','FULL')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--input-dir',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
 docs=[]
 for p in Path(a.input_dir).rglob('*.json'):
  try:d=json.loads(p.read_text())
  except:continue
  if d.get('schema')=='kculture-v27b-legal-history-audit-shard-v1': docs.append(d)
 rows=[r for d in docs for r in d.get('rows',[])]; fails=[x for d in docs for x in d.get('failures',[])]
 shard_counts={int(d.get('num_shards',-1)) for d in docs}; shard_ids={int(d.get('shard_index',-1)) for d in docs}; expected_shards=next(iter(shard_counts)) if len(shard_counts)==1 else -1\n mech=expected_shards>0 and len(docs)==expected_shards and shard_ids==set(range(expected_shards)) and all(d.get('mechanical_pass') for d in docs) and not fails and len(rows)==72
 metrics={}
 for h in H:
  vals=[]
  for r in rows:
   for s in r['samples']: vals.append((r,s,s['horizons'][h]))
  def rate(k,xx=vals): return statistics.fmean(float(z[2][k]) for z in xx) if xx else None
  src=[]
  for sha in sorted({r['main_sha256'] for r in rows}):
   x=[z for z in vals if z[0]['main_sha256']==sha]; src.append(rate('full_equal',x))
  cp=[]
  for step in sorted({s['step'] for r in rows for s in r['samples']}):
   x=[z for z in vals if z[1]['step']==step]; cp.append(rate('full_equal',x))
  metrics[h]={'complete_action_parity':rate('full_equal'),'market_parity':rate('market_equal'),'farmer_parity':rate('farmer_equal'),'hands_parity':rate('hands_equal'),'minimum_source_complete_action_parity':min(src),'minimum_checkpoint_complete_action_parity':min(cp)}
 def finite_pass(m): return m['complete_action_parity']>=.99 and m['market_parity']>=.99 and m['farmer_parity']>=.995 and m['hands_parity']>=.99 and m['minimum_source_complete_action_parity']>=.95 and m['minimum_checkpoint_complete_action_parity']>=.90
 selected=next((h for h in H[:-1] if finite_pass(metrics[h])),None)
 fullpass=metrics['FULL']['complete_action_parity']>=.995
 if not mech: dec='V27B_MECHANICS_INVALID'
 elif selected is not None: dec='V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE'
 elif fullpass: dec='V27B_FULL_LEGAL_HISTORY_DISTILLATION_REQUIRED'
 else: dec='V27B_TEACHER_HISTORY_NOT_RECONSTRUCTIBLE'
 out={'schema':'kculture-v27b-legal-history-audit-v1','mechanical_pass':mech,'decision':dec,'episodes':len(rows),'selected_horizon':selected,'full_history_pass':fullpass,'metrics':metrics,'failures':fails,'automatic_kaggle_submission':False}
 p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('V27B_RESULT',json.dumps({'decision':dec,'mechanical_pass':mech,'episodes':len(rows),'selected_horizon':selected,'full_history_parity':metrics['FULL']['complete_action_parity'],'h0_parity':metrics['0']['complete_action_parity'],'failures':len(fails)},sort_keys=True))
 if not mech: raise SystemExit(2)
if __name__=='__main__':main()
