"""Reproducible CR080 corpus split, training-only route bank and package."""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cr080_runtime', ROOT / 'candidates/cr080_mengfei_route_bridge.py')
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def split_corpus(corpus):
    cmd = json.loads((corpus/'episodes_command.json').read_text())
    chronology = {int(r['id']): r['createTime'] for r in csv.DictReader(io.StringIO(cmd['stdout']))}
    rows, excluded = [], []
    for path in sorted((corpus/'replays').glob('*.json')):
        with path.open() as f: prefix = f.read(10000)
        names = json.loads(re.search(r'"TeamNames"\s*:\s*(\[[^\]]*\])', prefix)[1])
        eid = int(re.search(r'episode-(\d+)', path.name)[1])
        if names.count('Mengfei Li') != 1:
            excluded.append(eid); continue
        if eid not in chronology: raise ValueError(f'missing chronology {eid}')
        rows.append({'create_time': chronology[eid], 'episode_id': eid, 'file': path.name, 'seat': names.index('Mengfei Li')})
    rows.sort(key=lambda r: (r['create_time'], r['episode_id']))
    n = len(rows)*3//4
    return {'train': rows[:n], 'holdout': rows[n:], 'excluded': excluded}


def extract_route(path, seat):
    replay = json.loads(path.read_bytes())
    frames = replay['steps']
    if len(frames) != 720: raise ValueError('incomplete replay')
    route = {'actions': [], 'positions': [], 'signatures': []}
    for t in range(719):
        obs = frames[t][seat]['observation']
        if rt.clock(obs) != t: raise ValueError('clock alignment')
        action = frames[t+1][seat]['action']
        if not isinstance(action, dict): raise ValueError('invalid source action')
        route['actions'].append(action)
        farm = obs['farms'][seat]
        route['positions'].append([farm['farmer']] + list(farm.get('hands') or []))
        if t % 24 == 0: route['signatures'].append(rt.signature(obs))
    return route


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--corpus', type=Path, required=True); ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    manifest = split_corpus(a.corpus)
    (a.output/'split.json').write_text(json.dumps(manifest, indent=2))
    bank, hashes = [], []
    for i, ref in enumerate(manifest['train']):
        path = a.corpus/'replays'/ref['file']
        bank.append(extract_route(path, ref['seat']))
        hashes.append({'episode_id': ref['episode_id'], 'sha256': digest(path)})
        if (i+1)%16 == 0: print('extracted', i+1, flush=True)
    package = a.output/'package'; package.mkdir(exist_ok=True)
    (package/'main.py').write_bytes((ROOT/'candidates/cr080_mengfei_route_bridge.py').read_bytes())
    raw = json.dumps(bank, sort_keys=True, separators=(',', ':')).encode()
    (package/'routes.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode='w') as tf:
        for name in ('main.py', 'routes.json.gz'):
            data = (package/name).read_bytes(); info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o644; info.mtime = 0
            tf.addfile(info, io.BytesIO(data))
    archive = a.output/'CR080_MENGFEI_DAILY_ROUTE_BRIDGE_V1.tar.gz'
    archive.write_bytes(gzip.compress(out.getvalue(), mtime=0))
    report = {'candidate': 'CR080', 'training_episodes': len(bank), 'holdout_episodes': len(manifest['holdout']),
              'archive': archive.name, 'archive_sha256': digest(archive), 'model_sha256': digest(package/'routes.json.gz'),
              'runtime_sha256': digest(package/'main.py'), 'training_sources': hashes,
              'source_run': 34558022808, 'source_artifact': 10183391523, 'holdout_used_for_build': False,
              'automatic_kaggle_submission': False}
    (a.output/'build_receipt.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='training_sources'}, indent=2), flush=True)


if __name__ == '__main__': main()
