"""Download an exact public Kaggle notebook version and extract packaged main.py.

Used only for reproducible local opponent evaluation. The notebook handle must
include /versions/N. The submission archive is preferred over loose output
files. A provenance receipt records archive/member hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import kagglehub


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--handle",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--receipt",required=True)
    args=ap.parse_args()
    if "/versions/" not in args.handle:
        raise ValueError("handle must pin /versions/N")

    with tempfile.TemporaryDirectory(prefix="kculture-package-main-") as td:
        root=Path(td)
        kagglehub.notebook_output_download(args.handle,output_dir=str(root),force_download=True)
        archives=sorted([p for p in root.rglob("*") if p.is_file() and p.name.lower().endswith((".tar.gz",".tgz",".tar",".zip"))])
        candidates=[]
        for arc in archives:
            raw=arc.read_bytes(); ah=sha(raw)
            if arc.name.lower().endswith(".zip"):
                with zipfile.ZipFile(arc) as z:
                    for info in z.infolist():
                        if not info.is_dir() and PurePosixPath(info.filename).name=="main.py":
                            data=z.read(info); candidates.append((arc,ah,info.filename,data))
            else:
                with tarfile.open(arc,"r:*") as tf:
                    for info in tf.getmembers():
                        if info.isfile() and PurePosixPath(info.name).name=="main.py":
                            f=tf.extractfile(info); data=f.read() if f else b""; candidates.append((arc,ah,info.name,data))
        if not candidates:
            raise RuntimeError(f"no packaged main.py found for {args.handle}")
        shas={sha(x[3]) for x in candidates}
        if len(shas)!=1:
            raise RuntimeError(f"ambiguous packaged main.py hashes: {sorted(shas)}")
        arc,ah,member,data=candidates[0]
        out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
        receipt={
            "handle":args.handle,
            "archive_name":arc.name,
            "archive_sha256":ah,
            "member":member,
            "main_sha256":sha(data),
            "main_bytes":len(data),
            "candidate_count":len(candidates),
        }
        rp=Path(args.receipt); rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(receipt,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__": main()
