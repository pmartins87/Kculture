"""Fetch a pinned public Kaggle notebook output and preserve its runnable package.

Research/evaluation helper.  It prefers a canonical submission archive containing
main.py and preserves sibling modules.  Some high-scoring public notebooks emit a
submission archive containing submission.py *plus* a loose main.py beside it; in
that case the unique loose main.py is the real Kaggle entrypoint and all ordinary
loose output files are copied beside it for exact local reproduction.

Extraction is deliberately strict: regular files/directories only, no links or
devices, and no path traversal.  The local wrapper is never a submission.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
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


def copy_loose_outputs(root: Path, loose: list[Path], out: Path) -> list[str]:
    """Copy ordinary notebook output files, excluding cache/control debris."""
    copied = []
    out.mkdir(parents=True, exist_ok=True)
    for src in loose:
        rel = src.relative_to(root)
        parts = set(rel.parts)
        if ".complete" in parts or "__pycache__" in parts or src.suffix == ".pyc":
            continue
        if src.name.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip", ".archive")):
            continue
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        copied.append(rel.as_posix())
    return copied


def wrapper_source(original_text: str, package_root: Path, original: Path) -> str:
    """Inject local sys.path setup *after* a module docstring and __future__ imports.

    Python requires future imports to precede ordinary executable statements.  We
    use the AST only to locate the legal insertion point; the original source is
    otherwise byte-for-byte preserved as text.
    """
    tree = ast.parse(original_text)
    insert_after = 0
    body = list(tree.body)
    i = 0
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
        insert_after = int(body[0].end_lineno or body[0].lineno)
        i = 1
    while i < len(body) and isinstance(body[i], ast.ImportFrom) and body[i].module == "__future__":
        insert_after = int(body[i].end_lineno or body[i].lineno)
        i += 1
    prefix = (
        "# Local package-aware frontier wrapper; never submit this file.\n"
        "import sys as _kc_sys\n"
        f"_kc_sys.path.insert(0, {str(package_root)!r})\n"
        f"_kc_sys.path.insert(0, {str(original.parent)!r})\n"
        f"__file__ = {str(original)!r}\n"
    )
    lines = original_text.splitlines(keepends=True)
    pos = max(0, min(len(lines), insert_after))
    return "".join(lines[:pos]) + prefix + "".join(lines[pos:])


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

        package = Path(args.package_dir)
        canonical = [x for x in candidates if x[2]]
        chosen = canonical if canonical else candidates
        source_mode = None
        archive_meta = {}
        copied_loose = []

        if len(chosen) == 1:
            arc, member, is_canonical = chosen[0]
            safe_extract(arc, package)
            original = (package / Path(*PurePosixPath(member).parts)).resolve()
            source_mode = "archive_main"
            archive_meta = {
                "source_archive": arc.name,
                "canonical_archive": is_canonical,
                "archive_sha256": sha(arc.read_bytes()),
                "member_count": len(archive_inventory(arc)),
                "members": archive_inventory(arc),
            }
        else:
            loose_mains = [p for p in loose if p.name == "main.py" and ".complete" not in p.parts and "__pycache__" not in p.parts]
            if len(loose_mains) == 1:
                copied_loose = copy_loose_outputs(root, loose, package)
                rel = loose_mains[0].relative_to(root)
                original = (package / rel).resolve()
                source_mode = "loose_output_main"
                archive_meta = {"archives": inventories}
            else:
                receipt.update(
                    status="NO_UNAMBIGUOUS_MAIN",
                    loose_files=[str(p.relative_to(root)).replace(os.sep, "/") for p in loose][:300],
                    archives=inventories,
                    main_candidates=[{"archive": x[0].name, "member": x[1], "canonical": x[2]} for x in candidates],
                    loose_main_candidates=[str(p.relative_to(root)).replace(os.sep, "/") for p in loose_mains],
                )
                Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
                Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
                print(json.dumps(receipt, indent=2, sort_keys=True))
                if args.allow_no_main:
                    return
                raise RuntimeError(f"no unambiguous package/loose main.py for {args.handle}")

        package_root = package.resolve()
        if not original.is_file():
            raise RuntimeError(f"entrypoint missing after preservation: {original}")

        wrapper = Path(args.wrapper)
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        original_text = original.read_text(encoding="utf-8")
        wrapper.write_text(wrapper_source(original_text, package_root, original), encoding="utf-8")

        receipt.update(
            status="READY",
            source_mode=source_mode,
            original_main_member=str(original.relative_to(package_root)).replace(os.sep, "/"),
            original_main_sha256=sha(original.read_bytes()),
            wrapper_sha256=sha(wrapper.read_bytes()),
            copied_loose_outputs=copied_loose,
            loose_output_files=[str(p.relative_to(root)).replace(os.sep, "/") for p in loose][:300],
            **archive_meta,
        )
        rp = Path(args.receipt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({k: v for k, v in receipt.items() if k not in ("members", "archives")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
