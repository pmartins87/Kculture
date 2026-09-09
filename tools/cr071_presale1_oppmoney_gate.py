from __future__ import annotations
import argparse, hashlib, json, shutil, tarfile, tempfile
from pathlib import Path

VARIANT='CR071O_CR053_PRESALE1_OPPMONEY190'
THRESHOLD=190.0

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def safe_extract(archive: Path, dst: Path):
    base=dst.resolve()
    with tarfile.open(archive,'r:*') as tf:
        for m in tf.getmembers():
            t=(dst/m.name).resolve()
            if t!=base and base not in t.parents: raise RuntimeError(f'unsafe member {m.name}')
            if m.issym() or m.islnk(): raise RuntimeError('links forbidden')
        tf.extractall(dst)

def patch_source(src: str) -> str:
    init='        self._fs_for = None\n        self._cr053_like = False\n'
    if src.count(init)!=1: raise RuntimeError(f'init marker mismatch: {src.count(init)}')
    src=src.replace(init, init+'        self._cr053_step110_gate = None\n',1)

    counter='    def _cr053_counter_market(self, step, market, proj):\n        if not self._cr053_like:\n            return market\n'
    replacement='    def _cr053_counter_market(self, step, market, proj):\n        if not self._cr053_like:\n            return market\n        # CR071O discovery-only stump frozen before fresh validation:\n        # once step 110 is reached, retain counterplay only when the public\n        # opponent money is > 190.0; otherwise behave as the parent thereafter.\n        if step >= 110 and self._cr053_step110_gate is not True:\n            return market\n'
    if src.count(counter)!=1: raise RuntimeError(f'counter marker mismatch: {src.count(counter)}')
    src=src.replace(counter,replacement,1)

    act='        self._cr053_update_detector(obs, step, me)\n'
    gate=(
        '        self._cr053_update_detector(obs, step, me)\n'
        '        if step == 110:\n'
        '            farms_gate = list(obs.get("farms", []) or [])\n'
        '            opp_money_gate = (float(farms_gate[1 - me].get("money", 0) or 0)\n'
        '                              if len(farms_gate) >= 2 and isinstance(farms_gate[1 - me], dict) else 0.0)\n'
        '            self._cr053_step110_gate = bool(self._cr053_like and opp_money_gate > 190.0)\n'
    )
    if src.count(act)!=1: raise RuntimeError(f'act marker mismatch: {src.count(act)}')
    src=src.replace(act,gate,1)
    compile(src,'<cr071o>','exec')
    return src

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--presale1',required=True); ap.add_argument('--output-dir',required=True)
    a=ap.parse_args(); src_archive=Path(a.presale1); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cr071o-') as td:
        root=Path(td); safe_extract(src_archive,root)
        main=root/'main.py'; original=main.read_text(encoding='utf-8'); patched=patch_source(original)
        main.write_text(patched,encoding='utf-8')
        for c in root.rglob('__pycache__'): shutil.rmtree(c,ignore_errors=True)
        for p in root.rglob('*.pyc'): p.unlink(missing_ok=True)
        dst=out/f'{VARIANT}_SEATSAFE_V1.tar.gz'
        with tarfile.open(dst,'w:gz') as tf:
            for p in sorted(root.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc': tf.add(p,arcname=p.relative_to(root).as_posix())
    rec={
      'schema_version':'kculture-cr071o-presale1-oppmoney190-v1',
      'variant':VARIANT,
      'source_presale1_sha256':sha256_file(src_archive),
      'archive':dst.name,'sha256':sha256_file(dst),
      'selector':{'decision_step':110,'feature':'public opponent money','operator':'>','threshold':THRESHOLD,'candidate_if_true':'PRESALE1','candidate_if_false':'PARENT'},
      'provenance':'frozen from discovery-only run 34351223145; fresh validation must not tune threshold',
      'automatic_kaggle_submission':False,
    }
    (out/'receipt_cr071o.json').write_text(json.dumps(rec,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps(rec,indent=2,sort_keys=True))
if __name__=='__main__': main()
