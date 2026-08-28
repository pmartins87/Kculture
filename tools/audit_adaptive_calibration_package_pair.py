"""Parity gate for self-contained CR-008/CR-011 calibration archives.

Uses official Aug-26 top replay observation streams where adaptive triggers are
known to occur. Each packaged agent must reproduce its frozen source candidate
exactly. In addition, packaged CR-008 and CR-011 must exhibit at least one
market-sequence difference with identical order multiset, proving the A/B axis is
active rather than vacuous.
"""
from __future__ import annotations
import collections, importlib.util, json, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.cr004_adaptation_signal import download, read_csv

DATE='2026-08-26';TOP=20
PAIRS=[
 ('cr008','candidates/cr008_adaptive_frontrun.py','artifacts/submissions/adaptive_calibration_pair/Kculture_CR008_adaptive_append_calibration_v1/main.py'),
 ('cr011','candidates/cr011_adaptive_early_order.py','artifacts/submissions/adaptive_calibration_pair/Kculture_CR011_adaptive_early_calibration_v1/main.py'),
]

def load(path):
 p=ROOT/path;spec=importlib.util.spec_from_file_location(f'pkgpar_{p.stem}_{time.time_ns()}',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def mc(a):return collections.Counter(canon(x) for x in (a.get('market') or []))

def main():
 reports={k:{'states':0,'mismatches':0,'examples':[]} for k,_,_ in PAIRS};seq_changes=0;seq_bad=0;episodes=0
 with tempfile.TemporaryDirectory(prefix='kculture-adaptive-pkg-parity-') as tmp:
  root=Path(tmp);handle=f'kaggle/kaggriculture-episodes-{DATE}'
  manifest=sorted(read_csv(download(handle,'manifest.csv',root/'manifest')),key=lambda r:-float(r.get('avg_score') or 0))[:TOP]
  for row in manifest:
   eid=str(row['episode_id']);rep=json.loads(download(handle,f'{eid}.json',root/'episodes'/eid).read_text());steps=rep.get('steps') or []
   if len(steps)<720:continue
   episodes+=1
   for player in (0,1):
    mods={k:(load(src),load(pkg)) for k,src,pkg in PAIRS}
    abmods={k:load(pkg) for k,_,pkg in PAIRS}
    for t in range(min(719,len(steps))):
     obs=steps[t][player].get('observation') if isinstance(steps[t][player],dict) else None
     if not isinstance(obs,dict):continue
     for k,(s,p) in mods.items():
      sa=s.agent(obs,None);pa=p.agent(obs,None);reports[k]['states']+=1
      if sa!=pa:
       reports[k]['mismatches']+=1
       if len(reports[k]['examples'])<10:reports[k]['examples'].append({'episode':eid,'state':t,'player':player,'source':sa,'package':pa})
     a=abmods['cr008'].agent(obs,None);b=abmods['cr011'].agent(obs,None)
     if (a.get('market') or [])!=(b.get('market') or []):
      if mc(a)==mc(b):seq_changes+=1
      else:seq_bad+=1
 payload={'schema_version':'adaptive-calibration-package-parity-v1','source_date':DATE,'episodes':episodes,'reports':reports,'ab_sequence_changes':seq_changes,'ab_multiset_mismatches':seq_bad}
 payload['passed']=episodes>=10 and all(v['states']>=10000 and v['mismatches']==0 for v in reports.values()) and seq_changes>0 and seq_bad==0
 out=ROOT/'artifacts/submissions/adaptive_calibration_pair/parity.json';out.write_text(json.dumps(payload,indent=2,sort_keys=True));print(json.dumps({**payload,'reports':{k:{x:y for x,y in v.items() if x!='examples'} for k,v in reports.items()}},indent=2))
 if not payload['passed']:raise SystemExit(2)
if __name__=='__main__':main()
