"""Fetch hash-pinned public Kaggriculture opponent artifacts.

Downloaded files live under ignored `artifacts/public_opponents/`; provenance
remains checked into `configs/public_opponents.json`.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs" / "public_opponents.json"
OUTPUT = ROOT / "artifacts" / "public_opponents"


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fetched = []

    for item in manifest["artifacts"]:
        destination = OUTPUT / item["local_filename"]
        with urllib.request.urlopen(item["download_url"], timeout=30) as response:
            payload = response.read()

        digest = hashlib.sha256(payload).hexdigest()
        if digest != item["sha256"]:
            raise RuntimeError(
                f"SHA256 mismatch for {item['id']}: expected {item['sha256']}, got {digest}"
            )

        destination.write_bytes(payload)
        fetched.append(
            {
                "id": item["id"],
                "path": str(destination.relative_to(ROOT)),
                "sha256": digest,
                "bytes": len(payload),
                "source_commit": item["commit"],
                "license": item["license"],
            }
        )

    receipt = {"result": "PASS", "artifacts": fetched}
    (OUTPUT / "fetch_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
