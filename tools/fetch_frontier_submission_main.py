"""Fetch the exact ladder submission main.py from a pinned public Kaggle notebook.

Unlike fetch_exact_package_main.py, this helper resolves notebooks that publish
multiple experimental archives by preferring the canonical `submission.tar.gz`
(or submission.tgz/submission.zip) produced by that exact notebook version.
If no canonical archive exists, exactly one archive/main.py candidate or one
loose main.py is accepted. Ambiguity is a hard failure.
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


def archive_main(path: Path):
    raw = path.read_bytes()
    ah = sha(raw)
    rows = []
    if path.name.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if not info.is_dir() and PurePosixPath(info.filename).name == "main.py":
                    rows.append((info.filename, zf.read(info)))
    else:
        with tarfile.open(path, "r:*") as tf:
            for info in tf.getmembers():
                if info.isfile() and PurePosixPath(info.name).name == "main.py":
                    fh = tf.extractfile(info)
                    rows.append((info.name, fh.read() if fh else b""))
    return ah, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()
    if "/versions/" not in args.handle:
        raise ValueError("handle must pin /versions/N")

    with tempfile.TemporaryDirectory(prefix="kculture-frontier-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(args.handle, output_dir=str(root), force_download=True)
        archives = sorted(p for p in root.rglob("*") if p.is_file() and p.name.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip")))
        preferred_names = {"submission.tar.gz", "submission.tgz", "submission.tar", "submission.zip"}
        preferred = [p for p in archives if p.name.lower() in preferred_names]

        candidates = []
        source_kind = None
        scan = preferred if preferred else archives
        for arc in scan:
            ah, mains = archive_main(arc)
            for member, data in mains:
                candidates.append((arc, ah, member, data))
        if preferred:
            source_kind = "canonical_submission_archive"

        if not candidates and not preferred:
            loose = sorted(p for p in root.rglob("main.py") if p.is_file())
            if len(loose) == 1:
                p = loose[0]
                data = p.read_bytes()
                candidates = [(p, None, p.name, data)]
                source_kind = "loose_main"

        if not candidates:
            raise RuntimeError(f"no submission main.py found for {args.handle}")
        unique = {sha(x[3]) for x in candidates}
        if len(unique) != 1:
            detail = [(x[0].name, x[2], sha(x[3])) for x in candidates]
            raise RuntimeError(f"ambiguous frontier main.py: {detail}")

        arc, ah, member, data = candidates[0]
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        receipt = {
            "handle": args.handle,
            "source_kind": source_kind or "single_archive_candidate",
            "source_name": arc.name,
            "archive_sha256": ah,
            "member": member,
            "main_sha256": sha(data),
            "main_bytes": len(data),
            "candidate_count": len(candidates),
        }
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
