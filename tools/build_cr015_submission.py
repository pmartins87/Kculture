"""Build a deterministic self-contained CR-015 submission package.

Mechanical preparation only.  Running this builder does not authorize hosted
submission; CR-015 must first pass its preregistered evaluation gates.
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

from tools import build_cr008_cr011_calibration_packages as P
from tools import build_kexp050_submission as B

MODEL_PATH = ROOT / "models/cr007_pure_models.json"
OUT = ROOT / "artifacts/submissions/cr015_liquidation_phase_v1"
CANDIDATE_BLOB = "fabd4bc398e7eadcfd1d44add4d0e593315140e8"
MODEL_BLOB = "d4b29e753e2328ac43503f8daa655cc63abdd336"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def selective_template() -> str:
    old = '''        if __EARLY__:action["market"]=adaptive+market
        else:action["market"]=market+adaptive'''
    new = '''        _ka_first = market[0] if market else None
        _ka_liquidation_phase = isinstance(_ka_first,list) and len(_ka_first)>=2 and _ka_first[0]=="SELL"
        if _ka_liquidation_phase:action["market"]=adaptive+market
        else:action["market"]=market+adaptive'''
    template = P.ADAPTIVE_TEMPLATE
    if old not in template:
        raise RuntimeError("upstream adaptive template placement block changed")
    return template.replace(old, new)


def main() -> None:
    base_bytes = B.BASE.read_bytes()
    if sha(base_bytes) != B.EXPECTED_BASE_SHA256:
        raise SystemExit("COK base hash mismatch")
    model_text = MODEL_PATH.read_text(encoding="utf-8")

    if OUT.exists():
        shutil.rmtree(OUT)
    package_dir = OUT / "Kculture_CR015_liquidation_phase_early_v1"
    package_dir.mkdir(parents=True)

    overlay = (
        selective_template()
        .replace("__MODE__", "CR015_LIQUIDATION_PHASE_EARLY")
        .replace("__MODEL_JSON__", repr(model_text))
        .replace("__EARLY__", "False")  # token no longer controls placement
    )
    main_py = package_dir / "main.py"
    main_py.write_bytes(base_bytes + B.R4B_OVERLAY.encode("utf-8") + overlay.encode("utf-8"))

    (package_dir / "LICENSE-APACHE-2.0.txt").write_bytes(B.download(B.LICENSE_URL))
    notice = (
        "Kculture CR-015 liquidation-phase selective early-order package\n"
        "Derived from COK V8 under Apache-2.0.\n"
        f"Upstream commit: {B.UPSTREAM_COMMIT}\n"
        f"R4B blob: {B.FROZEN_R4B_BLOB}\n"
        f"CR-015 candidate blob: {CANDIDATE_BLOB}\n"
        f"CR-007 model blob: {MODEL_BLOB}\n"
        "Hosted use requires separate experimental authorization.\n\n"
        "----- Upstream notices -----\n"
        + B.download(B.NOTICES_URL).decode("utf-8")
    )
    (package_dir / "THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")

    archive = OUT / "Kculture_CR015_liquidation_phase_early_v1.tar.gz"
    B.deterministic_tar_gz(
        archive,
        [
            main_py,
            package_dir / "LICENSE-APACHE-2.0.txt",
            package_dir / "THIRD_PARTY_NOTICES.txt",
        ],
    )
    manifest = {
        "schema_version": "cr015-package-v1",
        "authorization": "NOT_AUTHORIZED_UNTIL_PREREGISTERED_GATES_PASS",
        "candidate_blob": CANDIDATE_BLOB,
        "model_blob": MODEL_BLOB,
        "r4b_blob": B.FROZEN_R4B_BLOB,
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_py.read_bytes()),
        "placement_rule": "prepend adaptive sales iff frozen R4B base market queue starts with SELL; otherwise append",
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
