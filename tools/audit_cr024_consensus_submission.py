"""Mechanical audit for CR024_CONSENSUS_V1 submission archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import py_compile
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

EXPECTED = {"main.py", "LICENSE-APACHE-2.0.txt", "THIRD_PARTY_NOTICES.txt"}
REQUIRED = ("_CR024_CONSENSUS_TAPE =", "_cr024_consensus_hosted_entrypoint = agent")
FORBIDDEN = ("competition_episode_replay(", "notebook_output_download(", "requests.get(", "urllib.request.urlopen(")


def safe(name):
    p = PurePosixPath(name.replace("\\", "/"))
    return not p.is_absolute() and ".." not in p.parts


def sha(data): return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--archive", required=True); ap.add_argument("--output", required=True); args = ap.parse_args()
    archive = Path(args.archive); errors = []
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers(); names = {m.name for m in members if m.isfile()}
        if names != EXPECTED: errors.append(f"member set mismatch: {sorted(names)}")
        for m in members:
            if not safe(m.name): errors.append(f"unsafe member: {m.name}")
            if not m.isfile(): errors.append(f"non-file member: {m.name}")
        info = next((m for m in members if m.name == "main.py"), None)
        fh = tf.extractfile(info) if info is not None else None
        main_bytes = fh.read() if fh else b""
    text = main_bytes.decode("utf-8") if main_bytes else ""
    for token in REQUIRED:
        if token not in text: errors.append(f"missing required token: {token}")
    for token in FORBIDDEN:
        if token in text: errors.append(f"runtime network token: {token}")
    with tempfile.TemporaryDirectory(prefix="cr024-consensus-audit-") as td:
        p = Path(td) / "main.py"; p.write_bytes(main_bytes)
        try: py_compile.compile(str(p), doraise=True)
        except Exception as exc: errors.append(f"compile failed: {exc!r}")
    report = {
        "experiment": "CR024_CONSENSUS_V1_PACKAGE_AUDIT", "archive": str(archive),
        "archive_sha256": sha(archive.read_bytes()), "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_bytes), "main_bytes": len(main_bytes), "members": sorted(EXPECTED),
        "runtime_network_required": False, "error_count": len(errors), "errors": errors,
        "decision": "PASS" if not errors else "FAIL",
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors: raise SystemExit(3)


if __name__ == "__main__": main()
