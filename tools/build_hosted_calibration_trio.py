"""Build deterministic hosted calibration trio: R4B / CR-008 / CR-011.

These archives are information instruments, not automatic promotion candidates.
All three share the same hash-pinned COK V8 base and R4B terminal liquidation
semantics. CR-008 appends the frozen adaptive high-confidence sale response;
CR-011 prepends the exact same adaptive orders, isolating market-order position.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_kexp050_submission as B
from tools import build_cr008_cr011_calibration_packages as A

OUT = ROOT / "artifacts" / "submissions" / "hosted_calibration_trio"
R4B_BLOB = "e564125f0c4a1711fd3ea065dc1cb27d4a62ce37"
CR008_BLOB = "8e1c26202c3101c19668bf61edf2ae51d4329d5d"
CR011_BLOB = "c4f1cb79f3c20b8229ab09e00a6878289cf9648d"
MODEL_BLOB = "d4b29e753e2328ac43503f8daa655cc63abdd336"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_common(target: Path, title: str, main_bytes: bytes) -> dict:
    target.mkdir(parents=True, exist_ok=True)
    main = target / "main.py"
    main.write_bytes(main_bytes)
    (target / "LICENSE-APACHE-2.0.txt").write_bytes(B.download(B.LICENSE_URL))
    upstream = B.download(B.NOTICES_URL).decode("utf-8")
    notice = (
        f"Kculture {title}\n"
        "Hosted calibration package; information experiment, not promotion authorization.\n"
        "Derived from COK-ZhangZiliang/Kaggriculture COK V8 under Apache-2.0.\n"
        f"Upstream commit: {B.UPSTREAM_COMMIT}\n"
        f"Upstream main.py SHA-256: {B.EXPECTED_BASE_SHA256}\n"
        f"Frozen R4B blob: {R4B_BLOB}\n"
        f"Frozen CR-008 blob: {CR008_BLOB}\n"
        f"Frozen CR-011 blob: {CR011_BLOB}\n"
        f"Frozen model blob: {MODEL_BLOB}\n\n"
        "----- Upstream THIRD_PARTY_NOTICES.md -----\n\n"
        + upstream
    )
    (target / "THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")
    files = [
        target / "main.py",
        target / "LICENSE-APACHE-2.0.txt",
        target / "THIRD_PARTY_NOTICES.txt",
    ]
    archive = OUT / f"{target.name}.tar.gz"
    B.deterministic_tar_gz(archive, files)
    return {
        "name": target.name,
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": sha256(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "main_sha256": sha256(main.read_bytes()),
    }


def main() -> None:
    base = B.BASE.read_bytes()
    if sha256(base) != B.EXPECTED_BASE_SHA256:
        raise SystemExit("Frozen COK V8 hash mismatch")

    model_path = ROOT / "models" / "cr007_pure_models.json"
    model_text = model_path.read_text(encoding="utf-8")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    packages = []
    packages.append(
        write_common(
            OUT / "Kculture_R4B_fresh_control_v1",
            "R4B fresh control v1",
            base + B.R4B_OVERLAY.encode("utf-8"),
        )
    )

    for name, early in (
        ("Kculture_CR008_adaptive_append_calibration_v1", False),
        ("Kculture_CR011_adaptive_early_calibration_v1", True),
    ):
        overlay = (
            A.ADAPTIVE_TEMPLATE.replace("__MODE__", name)
            .replace("__MODEL_JSON__", repr(model_text))
            .replace("__EARLY__", "True" if early else "False")
        )
        packages.append(
            write_common(
                OUT / name,
                name,
                base + B.R4B_OVERLAY.encode("utf-8") + overlay.encode("utf-8"),
            )
        )

    manifest = {
        "schema_version": "hosted-calibration-trio-v1",
        "purpose": "same-window hosted information experiment",
        "recommended_order": [
            "Kculture_R4B_fresh_control_v1",
            "Kculture_CR008_adaptive_append_calibration_v1",
            "Kculture_CR011_adaptive_early_calibration_v1",
        ],
        "interpretation": {
            "R4B_vs_CR008": "incremental hosted value of adaptive response",
            "CR008_vs_CR011": "incremental hosted value of moving identical adaptive SELL orders earlier",
            "R4B_repeat_optional": "use a fourth slot only if temporal/noise calibration is needed",
        },
        "frozen_blobs": {
            "r4b": R4B_BLOB,
            "cr008": CR008_BLOB,
            "cr011": CR011_BLOB,
            "model": MODEL_BLOB,
        },
        "packages": packages,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
