"""CR055/CR056: prepare two exact public hosted calibration candidates.

These candidates are intentionally promoted for HOSTED calibration even when
CR029 head-to-head disagrees with their public ladder history.  The purpose is
to falsify our local proxy, not to tune another CR029 derivative.

CR055 = exact Kaggriculture Preempt H6 V1 archive.
CR056 = exact Shape the Shop Work the Pasture TOP10 V1 archive.

No archive contents are edited.  We copy the exact submission archive bytes
emitted by the pinned public notebook version and record hashes/members.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import kagglehub

CANDIDATES = {
    "cr055": {
        "handle": "koushikrudra/kaggriculture-preempt-h6/versions/1",
        "output_name": "R4D_CR055_PREEMPT_H6_PUBLIC_EXACT.tar.gz",
        "expected_archive_sha256": "9c632b48239e96a23d2763a8f29081f46eb652b0bd2a6a455c6331fe57b81333",
        "public_score_context": 2882.2,
    },
    "cr056": {
        "handle": "indarkarhana/shape-the-shop-work-the-pasture-top-10/versions/1",
        "output_name": "R4D_CR056_INDAR_TOP10_PUBLIC_EXACT.tar.gz",
        "expected_archive_sha256": None,
        "public_score_context": 2680.8,
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def members(path: Path) -> list[dict]:
    out = []
    low = path.name.lower()
    if low.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                data = z.read(info)
                out.append({"member": info.filename, "bytes": len(data), "sha256": sha(data)})
    else:
        with tarfile.open(path, "r:*") as tf:
            for info in tf.getmembers():
                if not info.isfile():
                    continue
                f = tf.extractfile(info); data = f.read() if f else b""
                out.append({"member": info.name, "bytes": len(data), "sha256": sha(data)})
    return sorted(out, key=lambda x: x["member"])


def is_submission_archive(path: Path) -> tuple[bool, list[dict]]:
    try:
        mm = members(path)
    except Exception:
        return False, []
    mains = [m for m in mm if PurePosixPath(m["member"]).name == "main.py"]
    return bool(mains), mm


def fetch_one(spec: dict, outdir: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="kculture-external-hosted-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(spec["handle"], output_dir=str(root), force_download=True)
        arcs = sorted(
            p for p in root.rglob("*")
            if p.is_file() and p.name.lower().endswith((".tar.gz", ".tgz", ".tar", ".zip"))
        )
        candidates = []
        for p in arcs:
            ok, mm = is_submission_archive(p)
            if ok:
                candidates.append((p, mm, sha(p.read_bytes())))
        if not candidates:
            raise RuntimeError(f"no submission archive containing main.py: {spec['handle']}")

        expected = spec.get("expected_archive_sha256")
        if expected:
            matches = [x for x in candidates if x[2] == expected]
            if len(matches) != 1:
                raise RuntimeError(f"expected hash {expected} matches={len(matches)} for {spec['handle']}")
            chosen = matches[0]
        else:
            # Ambiguity is not silently resolved. Multiple notebook artifacts with
            # different packaged agents require an explicitly pinned receipt.
            hashes = sorted({x[2] for x in candidates})
            if len(hashes) != 1:
                raise RuntimeError(f"ambiguous submission archive hashes for {spec['handle']}: {hashes}")
            chosen = candidates[0]

        src, mm, ah = chosen
        # Kaggle submissions here are expected to be tar.gz. Do not repackage a
        # ZIP while calling it exact.
        if not src.name.lower().endswith((".tar.gz", ".tgz")):
            raise RuntimeError(f"exact source archive is not tar.gz: {src.name}")
        out = outdir / spec["output_name"]
        outdir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, out)
        if sha(out.read_bytes()) != ah:
            raise RuntimeError("copy changed archive bytes")
        root_main = any(m["member"] == "main.py" for m in mm)
        if not root_main:
            raise RuntimeError(f"main.py not at archive root for {spec['handle']}")
        return {
            "handle": spec["handle"],
            "source_archive_name": src.name,
            "archive": out.name,
            "archive_sha256": ah,
            "archive_bytes": out.stat().st_size,
            "members": mm,
            "public_score_context": spec.get("public_score_context"),
            "exact_source_bytes": True,
            "decision": "READY_FOR_HOSTED_CALIBRATION",
        }


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", required=True); args = ap.parse_args()
    out = Path(args.output_dir)
    report = {
        "schema_version": "cr055-cr056-exact-public-hosted-pair-v1",
        "purpose": "hosted calibration after CR029 H2H proxy contradiction",
        "automatic_kaggle_submission": False,
        "candidates": {},
    }
    for key, spec in CANDIDATES.items():
        report["candidates"][key] = fetch_one(spec, out)
    (out / "receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
