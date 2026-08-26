"""Discovery-only probe for one exact public Kaggle notebook output.

Unlike fetch_public_kaggle_notebook.py, this helper does not accept an artifact
for benchmarking. It downloads an exact notebook version and records every
output file's path, size, and SHA-256 so a later experiment can pin the exact
file hash fail-closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import kagglehub


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--handle", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--receipt", required=True)
    args = p.parse_args()

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
        files.append({
            "path": str(path.relative_to(out)),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    receipt = {
        "status": "DISCOVERY_ONLY",
        "handle": args.handle,
        "kagglehub_result": str(result),
        "files": files,
    }
    rp = Path(args.receipt)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
