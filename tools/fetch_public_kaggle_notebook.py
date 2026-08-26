"""Fetch one exact public Kaggle notebook output through KaggleHub.

This helper is deliberately fail-closed: the requested output file is accepted
only if its SHA-256 equals the caller-supplied expected digest.  It is intended
for public competition artifacts whose notebook/version/license provenance has
already been recorded separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import kagglehub


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    expected = args.sha256.lower()
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise SystemExit("--sha256 must be a lowercase/uppercase 64-digit SHA-256 hex digest")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    result = kagglehub.notebook_output_download(
        args.handle,
        output_dir=str(out),
        force_download=True,
    )

    files = []
    for path in sorted(out.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        files.append(
            {
                "path": str(path.relative_to(out)),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    exact_name = [row for row in files if row["path"] == args.filename]
    if len(exact_name) != 1:
        raise SystemExit(
            f"Expected exactly one output path {args.filename!r}; found {exact_name}; all={files}"
        )
    if exact_name[0]["sha256"] != expected:
        raise SystemExit(
            f"SHA-256 mismatch for {args.filename}: expected {expected}, got {exact_name[0]['sha256']}"
        )

    receipt = {
        "status": "PASS",
        "handle": args.handle,
        "requested_filename": args.filename,
        "expected_sha256": expected,
        "matched": exact_name[0],
        "all_files": files,
        "kagglehub_result": str(result),
    }
    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
