"""Fetch a pinned public Kaggle notebook output and preserve its full submission package.

This is a research/evaluation helper.  Unlike fetch_frontier_submission_main.py it
keeps sibling modules required by main.py.  Archive extraction is deliberately
strict: regular files/directories only, no links/devices, and no path traversal.
A local wrapper adds the extracted roots to sys.path before executing the original
main.py; the wrapper is for local reproduction only and is never a submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import kagglehub


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_rel(name: str) -> Path:
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        raise RuntimeError(f"unsafe archive member: {name!r}")
    return Path(*p.parts)


def archive_inventory(path: Path) -> list[dict]:
    rows = []
    if path.name.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            for i in zf.infolist():
                if i.is_dir():
                    continue
                rel = safe_rel(i.filename)
                data = zf.read(i)
                rows.append({"name": rel.as_posix(), "bytes": len(data), "sha256": sha(data)})
    else:
        with tarfile.open(path, "r:*") as tf:
            for i in tf.getmembers():
                if i.isdir():
                    continue
                if not i.isfile():
                    raise RuntimeError(f"unsupported archive member type: {i.name!r}")
                rel = safe_rel(i.name)
                fh = tf.extractfile(i)
                data = fh.read() if fh else b""
                rows.append({"name": rel.as_posix(), "bytes": len(data), "sha256": sha(data)})
    return rows


def safe_extract(path: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    root = out.resolve()
    if path.name.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            for i in zf.infolist():
                if i.is_dir():
                    continue
                rel = safe_rel(i.filename)
                dest = (out / rel).resolve()
                if root not in dest.parents:
                    raise RuntimeError(f"path traversal: {i.filename!r}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(i))
    else:
        with tarfile.open(path, "r:*") as tf:
            for i in tf.getmembers():
                if i.isdir():
                    continue
                if not i.isfile():
                    raise RuntimeError(f"unsupported archive member type: {i.name!r}")
                rel = safe_rel(i.name)
                dest = (out / rel).resolve()
                if root not in dest.parents:
                    raise RuntimeError(f"path traversal: {i.name!r}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                fh = tf.extractfile(i)
                dest.write_bytes(fh.read() if fh else b"")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle", required=True)
    ap.add_argument("--package-dir", required=True)
    ap.add_argument("--wrapper", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--allow-no-main", action="store_true")
    args = ap.parse_args()
    if "/versions/" not in args.handle:
        raise ValueError("handle must pin /versions/N")

    receipt = {"handle": args.handle, "status": "DOWNLOAD_NOT_STARTED"}
    with tempfile.TemporaryDirectory(prefix="kculture-frontier-full-") as td:
        root = Path(td)
        try:
            kagglehub.notebook_output_download(args.handle, output_dir=str(root), force_download=True)
        except Exception as exc:
            receipt.update(status="DOWNLOAD_FAILED", error=repr(exc)[:1000])
            Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
            Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
            print(json.dumps(receipt, indent=2, sort_keys=True))
            if args.allow_no_main:
                return
            raise

        loose = sorted(p for p in root.rglob("*") if p.is_file())
        archives = sorted(p for p in loose if p.name.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip")))
        preferred_names = {"submission.tar.gz", "submission.tgz", "submission.tar", "submission.zip"}
        preferred = [p for p in archives if p.name.lower() in preferred_names]
        inventories = []
        candidates = []
        for arc in archives:
            try:
                inv = archive_inventory(arc)
                inventories.append({"archive": arc.name, "sha256": sha(arc.read_bytes()), "members": inv})
                mains = [x for x in inv if PurePosixPath(x["name"]).name == "main.py"]
                for m in mains:
                    candidates.append((arc, m["name"], arc in preferred))
            except Exception as exc:
                inventories.append({"archive": arc.name, "inventory_error": repr(exc)[:500]})

        # Canonical submission archive wins. Otherwise require one unambiguous archive/main.py.
        canonical = [x for x in candidates if x[2]]
        chosen = canonical if canonical else candidates
        if len(chosen) != 1:
            receipt.update(
                status="NO_UNAMBIGUOUS_MAIN",
                loose_files=[str(p.relative_to(root)).replace(os.sep, "/") for p in loose][:300],
                archives=inventories,
                main_candidates=[{"archive": x[0].name, "member": x[1], "canonical": x[2]} for x in candidates],
            )
            Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
            Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
            print(json.dumps(receipt, indent=2, sort_keys=True))
            if args.allow_no_main:
                return
            raise RuntimeError(f"no unambiguous package main.py for {args.handle}")

        arc, member, is_canonical = chosen[0]
        package = Path(args.package_dir)
        safe_extract(arc, package)
        original = (package / Path(*PurePosixPath(member).parts)).resolve()
        package_root = package.resolve()
        if not original.is_file():
            raise RuntimeError(f"extracted main missing: {original}")

        wrapper = Path(args.wrapper)
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        original_text = original.read_text(encoding="utf-8")
        # Execute the original source in the wrapper globals so Kaggle's 'last callable'
        # semantics can still discover the original agent function.
        prefix = (
            "# Local package-aware frontier wrapper; never submit this file.\n"
            "import sys as _kc_sys\n"
            f"_kc_sys.path.insert(0, {str(package_root)!r})\n"
            f"_kc_sys.path.insert(0, {str(original.parent)!r})\n"
            f"__file__ = {str(original)!r}\n"
        )
        wrapper.write_text(prefix + original_text, encoding="utf-8")

        receipt.update(
            status="READY",
            source_archive=arc.name,
            canonical_archive=is_canonical,
            archive_sha256=sha(arc.read_bytes()),
            original_main_member=member,
            original_main_sha256=sha(original.read_bytes()),
            wrapper_sha256=sha(wrapper.read_bytes()),
            member_count=len(archive_inventory(arc)),
            members=archive_inventory(arc),
            loose_output_files=[str(p.relative_to(root)).replace(os.sep, "/") for p in loose][:300],
        )
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({k: v for k, v in receipt.items() if k != "members"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
