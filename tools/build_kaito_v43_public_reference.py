"""Build an attributed deterministic submission archive for Kaito V43 public reference.

The strategic code is not modified. The exact Apache-2.0 Kaggle notebook output
is renamed to main.py and packaged with license/provenance files. This package
exists solely as a public-reference calibration arm; any future Kculture-derived
candidate must preserve attribution for reused code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools import build_kexp050_submission as B

EXPECTED_MAIN_SHA256='69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3'
SOURCE_URL='https://www.kaggle.com/code/kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid'
SOURCE_HANDLE='kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid/versions/13'


def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--output-dir',default='artifacts/submissions/kaito_v43_public_reference');args=ap.parse_args()
    src=Path(args.source);data=src.read_bytes()
    if sha(data)!=EXPECTED_MAIN_SHA256:raise SystemExit(f'Kaito V43 source SHA mismatch: {sha(data)}')
    out=Path(args.output_dir); shutil.rmtree(out,ignore_errors=True);pkg=out/'Kculture_PUBLIC_REFERENCE_Kaito_V43_v13';pkg.mkdir(parents=True)
    main_py=pkg/'main.py';main_py.write_bytes(data)
    license_path=pkg/'LICENSE-APACHE-2.0.txt';license_path.write_bytes(B.download(B.LICENSE_URL))
    notice=(
        'Kculture public-reference calibration package\n\n'
        'Strategic agent source: Kaito Fukami, "103/128 Fresh Public | v43 Sparse Shop Hybrid", Kaggle Version 13.\n'
        f'Source: {SOURCE_URL}\n'
        f'Kaggle handle: {SOURCE_HANDLE}\n'
        'Source notebook license: Apache License 2.0.\n'
        f'Exact main.py SHA-256: {EXPECTED_MAIN_SHA256}\n\n'
        'This archive does not claim authorship of the strategic source. It is an attributed, byte-identical public-reference arm used to calibrate Kculture experiments against a contemporary publicly shared agent.\n'
    )
    (pkg/'THIRD_PARTY_NOTICES.txt').write_text(notice,encoding='utf-8')
    archive=out/'Kculture_PUBLIC_REFERENCE_Kaito_V43_v13.tar.gz'
    B.deterministic_tar_gz(archive,[main_py,license_path,pkg/'THIRD_PARTY_NOTICES.txt'])
    manifest={'schema_version':'public-reference-package-v1','source_url':SOURCE_URL,'source_handle':SOURCE_HANDLE,'license':'Apache-2.0','main_sha256':sha(main_py.read_bytes()),'archive_sha256':sha(archive.read_bytes()),'archive_bytes':archive.stat().st_size,'strategic_modifications':False,'purpose':'hosted calibration reference, not automatic promotion'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf-8');print(json.dumps(manifest,indent=2,sort_keys=True))

if __name__=='__main__':main()
