"""Mechanical audit for the self-contained CR024A submission archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import py_compile
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

EXPECTED = {"main.py", "LICENSE-APACHE-2.0.txt", "THIRD_PARTY_NOTICES.txt"}
REQUIRED_TOKENS = (
    '_CR024_GUARD_CLOCK = 192',
    '_CR024_GUARD_FEATURE = "dmarket_price_wool"',
    '_CR024_GUARD_THRESHOLD = 11.5',
    '_cr024_hosted_entrypoint = agent',
)
FORBIDDEN_RUNTIME_TOKENS = (
    'competition_episode_replay(',
    'notebook_output_download(',
    'requests.get(',
    'urllib.request.urlopen(',
)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def safe(name: str) -> bool:
    p = PurePosixPath(name.replace('\\', '/'))
    return not p.is_absolute() and '..' not in p.parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    archive = Path(args.archive)
    errors = []
    with tarfile.open(archive, 'r:gz') as tf:
        members = tf.getmembers()
        names = {m.name for m in members if m.isfile()}
        if names != EXPECTED:
            errors.append(f'member set mismatch: {sorted(names)}')
        for m in members:
            if not safe(m.name): errors.append(f'unsafe member: {m.name}')
            if not m.isfile(): errors.append(f'non-file member: {m.name}')
        main_info = next((m for m in members if m.name == 'main.py'), None)
        if main_info is None:
            errors.append('missing main.py'); main_bytes = b''
        else:
            fh = tf.extractfile(main_info); main_bytes = fh.read() if fh else b''

    text = main_bytes.decode('utf-8') if main_bytes else ''
    for token in REQUIRED_TOKENS:
        if token not in text: errors.append(f'missing frozen token: {token}')
    # Only inspect the generated runtime main.py; builder-side network code is
    # not packaged.  The final runtime must therefore contain no fetch path.
    for token in FORBIDDEN_RUNTIME_TOKENS:
        if token in text: errors.append(f'runtime network token present: {token}')

    with tempfile.TemporaryDirectory(prefix='cr024a-audit-') as td:
        p = Path(td) / 'main.py'; p.write_bytes(main_bytes)
        try: py_compile.compile(str(p), doraise=True)
        except Exception as exc: errors.append(f'compile failed: {exc!r}')

    report = {
        'experiment': 'CR024A',
        'archive': str(archive),
        'archive_sha256': sha(archive.read_bytes()),
        'archive_bytes': archive.stat().st_size,
        'main_sha256': sha(main_bytes),
        'main_bytes': len(main_bytes),
        'members': sorted(EXPECTED),
        'runtime_network_required': False,
        'error_count': len(errors),
        'errors': errors,
        'decision': 'PASS' if not errors else 'FAIL',
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors: raise SystemExit(3)


if __name__ == '__main__': main()
