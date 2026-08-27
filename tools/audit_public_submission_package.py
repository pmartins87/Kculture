"""CR-001: audit exact public Kaggle notebook outputs and submission archives.

Discovery/forensics only. Third-party code is not written into the repository.
The tool downloads one exact public notebook version, hashes every output file,
inspects supported archives in-memory, hashes every member, and compares any
packaged main.py with the top-level notebook-output main.py.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

import kagglehub


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_member_name(name: str) -> bool:
    p = PurePosixPath(name.replace("\\", "/"))
    return not p.is_absolute() and ".." not in p.parts


def inspect_tar(path: Path) -> dict:
    members = []
    mains = []
    try:
        with tarfile.open(path, "r:*") as tf:
            for info in tf.getmembers():
                row = {
                    "path": info.name,
                    "type": "file" if info.isfile() else "other",
                    "bytes": info.size if info.isfile() else None,
                    "safe_path": safe_member_name(info.name),
                }
                if info.isfile():
                    fh = tf.extractfile(info)
                    data = fh.read() if fh else b""
                    row["sha256"] = sha256(data)
                    if PurePosixPath(info.name).name == "main.py":
                        mains.append({
                            "path": info.name,
                            "bytes": len(data),
                            "sha256": row["sha256"],
                        })
                members.append(row)
        return {"format": "tar", "status": "OK", "members": members, "main_candidates": mains}
    except Exception as exc:
        return {"format": "tar", "status": "ERROR", "error": repr(exc), "members": [], "main_candidates": []}


def inspect_zip(path: Path) -> dict:
    members = []
    mains = []
    try:
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                row = {
                    "path": info.filename,
                    "type": "other" if info.is_dir() else "file",
                    "bytes": None if info.is_dir() else info.file_size,
                    "safe_path": safe_member_name(info.filename),
                }
                if not info.is_dir():
                    data = zf.read(info)
                    row["sha256"] = sha256(data)
                    if PurePosixPath(info.filename).name == "main.py":
                        mains.append({
                            "path": info.filename,
                            "bytes": len(data),
                            "sha256": row["sha256"],
                        })
                members.append(row)
        return {"format": "zip", "status": "OK", "members": members, "main_candidates": mains}
    except Exception as exc:
        return {"format": "zip", "status": "ERROR", "error": repr(exc), "members": [], "main_candidates": []}


def is_archive(path: Path) -> bool:
    n = path.name.lower()
    return n.endswith((".tar.gz", ".tgz", ".tar", ".zip"))


def inspect_archive(path: Path) -> dict:
    lower = path.name.lower()
    detail = inspect_zip(path) if lower.endswith(".zip") else inspect_tar(path)
    detail.update({
        "output_path": str(path),
        "archive_bytes": path.stat().st_size,
        "archive_sha256": sha256(path.read_bytes()),
    })
    return detail


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--handle", required=True)
    p.add_argument("--target-id", required=True)
    p.add_argument("--reported-score", type=float, required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--manifest", required=True)
    args = p.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    kaggle_result = kagglehub.notebook_output_download(
        args.handle,
        output_dir=str(out),
        force_download=True,
    )

    output_files = []
    top_level_mains = []
    archives = []
    for path in sorted(out.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        rel = str(path.relative_to(out))
        row = {"path": rel, "bytes": len(data), "sha256": sha256(data)}
        output_files.append(row)
        if path.name == "main.py" and len(path.relative_to(out).parts) == 1:
            top_level_mains.append(row)
        if is_archive(path):
            detail = inspect_archive(path)
            detail["output_path"] = rel
            archives.append(detail)

    packaged_mains = []
    for archive in archives:
        for m in archive.get("main_candidates", []):
            packaged_mains.append({
                "archive_path": archive["output_path"],
                **m,
            })

    top_shas = {m["sha256"] for m in top_level_mains}
    package_shas = {m["sha256"] for m in packaged_mains}
    if top_shas and package_shas:
        identity = "IDENTITY_MATCH" if top_shas & package_shas else "BENCHMARK_IDENTITY_MISMATCH"
    elif package_shas:
        identity = "NO_TOP_LEVEL_MAIN"
    elif archives:
        identity = "NO_COMPARABLE_PACKAGE_MAIN"
    else:
        identity = "NO_SUBMISSION_ARCHIVE_FOUND"

    # Surface likely support files without interpreting third-party code.
    package_python_files = []
    for archive in archives:
        for row in archive.get("members", []):
            if row.get("type") == "file" and str(row.get("path", "")).endswith(".py"):
                package_python_files.append({
                    "archive_path": archive["output_path"],
                    "path": row["path"],
                    "bytes": row.get("bytes"),
                    "sha256": row.get("sha256"),
                })

    manifest = {
        "status": "PASS",
        "experiment": "CR-001",
        "target_id": args.target_id,
        "handle": args.handle,
        "reported_historical_score": args.reported_score,
        "kagglehub_result": str(kaggle_result),
        "output_files": output_files,
        "top_level_main_candidates": top_level_mains,
        "archives": archives,
        "packaged_main_candidates": packaged_mains,
        "packaged_python_files": package_python_files,
        "identity_classification": identity,
        "benchmark_warning": (
            "Old local benchmark identity is invalid until exact package entry point is proved."
            if identity != "IDENTITY_MATCH"
            else "Byte identity established for at least one output-main/package-main pair; dependency layout still requires parity proof."
        ),
    }

    mp = Path(args.manifest)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "target_id": args.target_id,
        "reported_historical_score": args.reported_score,
        "identity_classification": identity,
        "top_level_mains": top_level_mains,
        "packaged_mains": packaged_mains,
        "archive_summaries": [
            {
                "output_path": a["output_path"],
                "format": a["format"],
                "status": a["status"],
                "archive_sha256": a["archive_sha256"],
                "member_count": len(a.get("members", [])),
                "main_count": len(a.get("main_candidates", [])),
            }
            for a in archives
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
