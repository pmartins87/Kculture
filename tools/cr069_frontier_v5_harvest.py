from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, sys, tarfile, tempfile
from pathlib import Path
import kagglehub

TARGETS={
 'v5':('lynnsakurai/farming-score-v5-timing-optimized','R4D_CR069A_FARMING_SCORE_V5_SEATSAFE_V2.tar.gz'),
 'island':('destbreso/island-ga-an-owned-schedule-is-a-moat','R4D_CR069B_ISLAND_GA_SEATSAFE_V2.tar.gz'),
}
WRAPPER='''\n\n# CR069 mechanical seat-clock compatibility shim. Strategy unchanged.\ndef _cr069_clock_safe_obs(obs):\n    try: raw=obs.get("step")\n    except Exception: raw=getattr(obs,"step",None)\n    if raw is not None: return obs\n    try: p=dict(obs)\n    except Exception: p={}\n    try: day=p.get("day",getattr(obs,"day",0))\n    except Exception: day=0\n    try: hour=p.get("hour",getattr(obs,"hour",0))\n    except Exception: hour=0\n    p["step"]=int(day or 0)*24+int(hour or 0)\n    return p\ntry:\n    _CR069_ORIGINAL_AGENT=agent\nexcept NameError:\n    _CR069_ORIGINAL_AGENT=kaggriculture_agent\ndef _cr069_agent(obs,configuration=None):\n    fixed=_cr069_clock_safe_obs(obs)\n    try: return _CR069_ORIGINAL_AGENT(fixed,configuration)\n    except TypeError: return _CR069_ORIGINAL_AGENT(fixed)\nagent=_cr069_agent\n'''
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def root_main_archives(root):
 out=[]
 for p in root.rglob('*'):
  if not p.is_file() or not p.name.lower().endswith(('.tar.gz','.tgz')): continue
  try:
   with tarfile.open(p,'r:*') as tf: names=[m.name for m in tf.getmembers() if m.isfile()]
  except Exception: continue
  if 'main.py' in names: out.append((p,names))
 return out
def verify_import(root):
 sys.path.insert(0,str(root))
 try:
  spec=importlib.util.spec_from_file_location('cr069_verify',root/'main.py')
  if spec is None or spec.loader is None: raise RuntimeError('cannot load patched main')
  mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
  if not callable(getattr(mod,'agent',None)): raise RuntimeError('patched agent not callable')
  probe=mod._cr069_clock_safe_obs({'player':1,'day':3,'hour':11})
  if int(probe.get('step',-1))!=83: raise RuntimeError(f'clock probe failed: {probe}')
 finally:
  try: sys.path.remove(str(root))
  except ValueError: pass
def build(handle,outname,outdir):
 with tempfile.TemporaryDirectory(prefix='cr069-') as td:
  root=Path(td); kagglehub.notebook_output_download(handle,output_dir=str(root),force_download=True)
  arcs=root_main_archives(root)
  if not arcs: return {'handle':handle,'status':'NO_SUBMISSION_ARCHIVE','files':[p.name for p in root.rglob('*') if p.is_file()][:100]}
  chosen=None
  for p,n in arcs:
   if p.name=='submission.tar.gz': chosen=(p,n); break
  if chosen is None:
   uniq={sha(p):(p,n) for p,n in arcs}
   if len(uniq)!=1: return {'handle':handle,'status':'AMBIGUOUS','archives':[p.name for p,_ in arcs]}
   chosen=next(iter(uniq.values()))
  src,names=chosen; unpack=root/'unpack'; unpack.mkdir()
  with tarfile.open(src,'r:*') as tf: tf.extractall(unpack)
  main=unpack/'main.py'; text=main.read_text(encoding='utf-8')
  source_hash=hashlib.sha256(main.read_bytes()).hexdigest()
  if '_cr069_clock_safe_obs' not in text: main.write_text(text.rstrip()+WRAPPER+'\n',encoding='utf-8')
  verify_import(unpack)
  for c in unpack.rglob('__pycache__'): shutil.rmtree(c,ignore_errors=True)
  dst=outdir/outname; outdir.mkdir(parents=True,exist_ok=True)
  with tarfile.open(dst,'w:gz') as tf:
   for p in sorted(unpack.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc': tf.add(p,arcname=p.relative_to(unpack).as_posix())
  return {'handle':handle,'status':'PASS','source_archive':src.name,'source_main_sha256':source_hash,'archive':dst.name,'archive_sha256':sha(dst),'archive_bytes':dst.stat().st_size,'seat1_clock_probe':83}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',required=True); a=ap.parse_args(); out=Path(a.output_dir)
 r={'schema_version':'cr069-v2','automatic_kaggle_submission':False,'targets':{}}
 for k,(h,n) in TARGETS.items():
  try:r['targets'][k]=build(h,n,out)
  except Exception as e:r['targets'][k]={'handle':h,'status':'ERROR','error':repr(e)}
 (out/'report.json').write_text(json.dumps(r,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps(r,indent=2,sort_keys=True))
 if r['targets']['v5'].get('status')!='PASS': raise SystemExit(2)
if __name__=='__main__': main()
