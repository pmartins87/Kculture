"""Download one pinned public Kaggle notebook output and extract its exact submission archive.

Unlike fetch_exact_package_main.py, this preserves runtime companions such as
agent.so. Extraction is path-safe and a receipt hashes every extracted file.
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


def safe_rel(name: str) -> Path:
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        raise RuntimeError(f"unsafe archive member: {name!r}")
    return Path(*p.parts)


def archive_members(path: Path):
    if path.name.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                yield info.filename, z.read(info)
    else:
        with tarfile.open(path, "r:*") as tf:
            for info in tf.getmembers():
                if not info.isfile():
                    continue
                f = tf.extractfile(info)
                yield info.name, (f.read() if f else b"")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()
    if "/versions/" not in args.handle:
        raise ValueError("handle must pin /versions/N")

    with tempfile.TemporaryDirectory(prefix="kculture-package-dir-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(args.handle, output_dir=str(root), force_download=True)
        archives = sorted(
            p for p in root.rglob("*")
            if p.is_file() and p.name.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip"))
        )
        candidates = []
        for arc in archives:
            members = list(archive_members(arc))
            mains = [(n, d) for n, d in members if PurePosixPath(n).name == "main.py"]
            if mains:
                candidates.append((arc, members, mains))
        if not candidates:
            raise RuntimeError(f"no submission archive containing main.py for {args.handle}")

        main_hashes = {sha(d) for _, _, mains in candidates for _, d in mains}
        if len(main_hashes) != 1:
            raise RuntimeError(f"ambiguous main.py hashes: {sorted(main_hashes)}")
        arc, members, mains = candidates[0]
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        manifest = []
        for name, data in members:
            rel = safe_rel(name)
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            manifest.append({"member": name, "sha256": sha(data), "bytes": len(data)})

        main_name, main_data = mains[0]
        receipt = {
            "handle": args.handle,
            "archive_name": arc.name,
            "archive_sha256": sha(arc.read_bytes()),
            "main_member": main_name,
            "main_sha256": sha(main_data),
            "member_count": len(manifest),
            "members": sorted(manifest, key=lambda x: x["member"]),
        }
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
