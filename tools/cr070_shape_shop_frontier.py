from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, sys, tarfile, tempfile
from pathlib import Path
import kagglehub

TARGETS={
 'tetsu':('tetsutani/shape-the-shop-work-the-pasture-kaggriculture','R4D_CR070A_TETSU_SHAPE_SHOP_SEATSAFE_V1.tar.gz'),
 'indar':('indarkarhana/shape-the-shop-work-the-pasture-top-10','R4D_CR070B_INDAR_SHAPE_SHOP_SEATSAFE_V1.tar.gz'),
}
WRAPPER='''\n\n# CR070 mechanical seat-clock compatibility shim; policy logic unchanged.\ndef _cr070_clock_safe_obs(obs):\n    try: raw=obs.get("step")\n    except Exception: raw=getattr(obs,"step",None)\n    if raw is not None: return obs\n    try: p=dict(obs)\n    except Exception: p={}\n    try: day=p.get("day",getattr(obs,"day",0))\n    except Exception: day=0\n    try: hour=p.get("hour",getattr(obs,"hour",0))\n    except Exception: hour=0\n    p["step"]=int(day or 0)*24+int(hour or 0)\n    return p\ntry:\n    _CR070_ORIGINAL_AGENT=agent\nexcept NameError:\n    _CR070_ORIGINAL_AGENT=kaggriculture_agent\ndef _cr070_agent(obs,configuration=None):\n    fixed=_cr070_clock_safe_obs(obs)\n    try: return _CR070_ORIGINAL_AGENT(fixed,configuration)\n    except TypeError: return _CR070_ORIGINAL_AGENT(fixed)\nagent=_cr070_agent\n'''
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def find_archives(root):
 out=[]
 for p in root.rglob('*'):
  if not p.is_file() or not p.name.lower().endswith(('.tar.gz','.tgz')): continue
  try:
   with tarfile.open(p,'r:*') as tf:names=[m.name for m in tf.getmembers() if m.isfile()]
  except Exception:continue
  if 'main.py' in names: out.append((p,names))
 return out
def verify(root):
 sys.path.insert(0,str(root))
 try:
  spec=importlib.util.spec_from_file_location('cr070_verify',root/'main.py')
  if spec is None or spec.loader is None:raise RuntimeError('cannot load main')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  if not callable(getattr(mod,'agent',None)):raise RuntimeError('no callable agent after shim')
  q=mod._cr070_clock_safe_obs({'player':1,'day':3,'hour':11})
  if int(q.get('step',-1))!=83:raise RuntimeError('clock probe failed')
 finally:
  try:sys.path.remove(str(root))
  except ValueError:pass
def build(key,handle,outname,outdir):
 with tempfile.TemporaryDirectory(prefix=f'cr070-{key}-') as td:
  root=Path(td);kagglehub.notebook_output_download(handle,output_dir=str(root),force_download=True)
  arcs=find_archives(root)
  if not arcs:return {'handle':handle,'status':'NO_SUBMISSION_ARCHIVE','files':[p.name for p in root.rglob('*') if p.is_file()][:80]}
  conventional=[x for x in arcs if x[0].name in ('submission.tar.gz','submission.tgz')]
  if conventional:src,names=conventional[0]
  else:
   uniq={sha(p):(p,n) for p,n in arcs}
   if len(uniq)!=1:return {'handle':handle,'status':'AMBIGUOUS','archives':[p.name for p,_ in arcs]}
   src,names=next(iter(uniq.values()))
  unpack=root/'unpack';unpack.mkdir()
  with tarfile.open(src,'r:*') as tf:tf.extractall(unpack)
  main=unpack/'main.py';orig=hashlib.sha256(main.read_bytes()).hexdigest();text=main.read_text(encoding='utf-8')
  main.write_text(text.rstrip()+WRAPPER+'\n',encoding='utf-8');verify(unpack)
  for c in unpack.rglob('__pycache__'):shutil.rmtree(c,ignore_errors=True)
  dst=outdir/outname;outdir.mkdir(parents=True,exist_ok=True)
  with tarfile.open(dst,'w:gz') as tf:
   for p in sorted(unpack.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':tf.add(p,arcname=p.relative_to(unpack).as_posix())
  return {'handle':handle,'status':'PASS','source_archive':src.name,'source_main_sha256':orig,'archive':dst.name,'archive_sha256':sha(dst),'archive_bytes':dst.stat().st_size,'members':names,'seat1_clock_probe':83}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);a=ap.parse_args();out=Path(a.output_dir)
 r={'schema_version':'cr070-v1','automatic_kaggle_submission':False,'targets':{}}
 for k,(h,n) in TARGETS.items():
  try:r['targets'][k]=build(k,h,n,out)
  except Exception as e:r['targets'][k]={'handle':h,'status':'ERROR','error':repr(e)}
 (out/'report.json').write_text(json.dumps(r,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps(r,indent=2,sort_keys=True))
 if not any(v.get('status')=='PASS' for v in r['targets'].values()):raise SystemExit(2)
if __name__=='__main__':main()
