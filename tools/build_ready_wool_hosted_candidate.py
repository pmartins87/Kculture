#!/usr/bin/env python3
"""Build the frozen V47 + O-RW1 hosted candidate without persisting upstream source.

The exact public V47 output package is downloaded transiently, source identity is
SHA-pinned, and a minimal one-shot O-RW1 wrapper is appended to main.py.

No Kaggle submission is performed by this tool.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main, sha256_bytes
from kaggle_environments.agent import get_last_callable

BASE_HANDLE = "ahmedberatozer/kaggriculture-v47-reactive-market-coordination"
BASE_MAIN_SHA256 = "f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"
CANDIDATE_NAME = "KCULTURE_V47_ORW1_ONESHOT_V1"

WRAPPER = r'''

# === Kculture O-RW1 one-shot wrapper — frozen 2026-09-18 ===
# Exact pinned V47 hosted entrypoint is _y_agent_shopherd.
_KC_ORW1_BASE_AGENT = _y_agent_shopherd
_KC_ORW1_USED = False

def _kc_orw1_get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except Exception:
        try:
            return obj[key]
        except Exception:
            try:
                return getattr(obj, key)
            except Exception:
                return default

def _kc_orw1_step(obs):
    try:
        return int(_kc_orw1_get(obs, "step", 0) or 0)
    except Exception:
        return 0

def _kc_orw1_wool(obs):
    private = _kc_orw1_get(obs, "private", {}) or {}
    shed = _kc_orw1_get(private, "shed", {}) or {}
    try:
        return max(0, int(_kc_orw1_get(shed, "WOOL", 0) or 0))
    except Exception:
        return 0

def _kc_orw1_entrypoint(obs, config=None):
    global _KC_ORW1_USED
    step = _kc_orw1_step(obs)
    if step <= 1:
        _KC_ORW1_USED = False

    base = _KC_ORW1_BASE_AGENT(obs, config)
    if not isinstance(base, dict):
        return base

    market = list(base.get("market") or [])
    if (not _KC_ORW1_USED
            and step <= 671
            and not market
            and _kc_orw1_wool(obs) >= 2):
        out = dict(base)
        out["market"] = [["SELL", "WOOL", 2]]
        _KC_ORW1_USED = True
        return out
    return base

# IMPORTANT: no callable definitions may appear after _kc_orw1_entrypoint.
# === end Kculture O-RW1 wrapper ===
'''.lstrip("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def deterministic_tar_gz(src: Path, dst: Path) -> None:
    files = sorted(p for p in src.rglob("*") if p.is_file())
    with dst.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tf:
                for p in files:
                    rel = p.relative_to(src).as_posix()
                    data = p.read_bytes()
                    ti = tarfile.TarInfo(rel)
                    ti.size = len(data)
                    ti.mtime = 0
                    ti.uid = 0
                    ti.gid = 0
                    ti.uname = ""
                    ti.gname = ""
                    ti.mode = 0o644
                    tf.addfile(ti, io.BytesIO(data))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kculture-orw1-package-") as td:
        root = Path(td)
        base_main, acquisition = acquire_public_main(BASE_HANDLE, root / "upstream")
        observed = sha256_bytes(base_main.read_bytes())
        if observed != BASE_MAIN_SHA256:
            raise RuntimeError(
                f"V47 source identity mismatch {observed} != {BASE_MAIN_SHA256}"
            )
        if acquisition.get("acquisition") != "output_package":
            raise RuntimeError(
                "Hosted candidate build requires the exact public V47 output package"
            )
        members = acquisition.get("members") or []
        if members != ["main.py"]:
            raise RuntimeError(f"unexpected V47 package members: {members}")

        stage = root / "stage"
        stage.mkdir()
        original = base_main.read_text(encoding="utf-8")
        if "_KC_ORW1_BASE_AGENT" in original:
            raise RuntimeError("upstream source unexpectedly already contains O-RW1 marker")
        compile(original, "<v47-original>", "exec")
        patched = original.rstrip() + "\n\n" + WRAPPER.rstrip() + "\n"
        compile(patched, "<v47-orw1>", "exec")
        staged_main = stage / "main.py"
        staged_main.write_text(patched, encoding="utf-8")

        base_entry = get_last_callable(original, path=str(base_main.resolve()))
        cand_entry = get_last_callable(patched, path=str(staged_main.resolve()))
        base_entry_name = getattr(base_entry, "__name__", None)
        cand_entry_name = getattr(cand_entry, "__name__", None)
        if base_entry_name != "_y_agent_shopherd":
            raise RuntimeError(f"unexpected exact V47 hosted entrypoint: {base_entry_name}")
        if cand_entry_name != "_kc_orw1_entrypoint":
            raise RuntimeError(f"candidate staged hosted entrypoint mismatch: {cand_entry_name}")

        attribution = (
            "Kculture hosted candidate provenance\n"
            "===================================\n"
            f"Candidate: {CANDIDATE_NAME}\n"
            f"Base public Kaggle notebook: {BASE_HANDLE}\n"
            f"Base main.py SHA-256: {BASE_MAIN_SHA256}\n"
            f"Base output archive SHA-256: {acquisition.get('archive_sha256')}\n"
            "Modification: Kculture O-RW1 one-shot wrapper only.\n"
            "O-RW1: when base market is empty, own current shed has >=2 WOOL, and "
            "step<=671, SELL WOOL 2 once per episode.\n"
            "The original source comments/notices are retained verbatim in main.py.\n"
            "Consult the original Kaggle notebook for upstream license terms before "
            "redistribution or hosted submission.\n"
        )
        (stage / "ATTRIBUTION.txt").write_text(attribution, encoding="utf-8")

        archive = out / f"{CANDIDATE_NAME}.tar.gz"
        deterministic_tar_gz(stage, archive)

        receipt = {
            "schema": "kculture-v47-orw1-hosted-package-v1",
            "candidate": CANDIDATE_NAME,
            "base_handle": BASE_HANDLE,
            "base_main_sha256": BASE_MAIN_SHA256,
            "base_acquisition": acquisition,
            "wrapper_sha256": hashlib.sha256(WRAPPER.encode("utf-8")).hexdigest(),
            "candidate_main_sha256": sha256_file(staged_main),
            "archive": archive.name,
            "archive_sha256": sha256_file(archive),
            "archive_bytes": archive.stat().st_size,
            "members": ["ATTRIBUTION.txt", "main.py"],
            "base_hosted_entrypoint": base_entry_name,
            "candidate_hosted_entrypoint": cand_entry_name,
            "automatic_kaggle_submission": False,
            "license_note": (
                "Upstream source provenance is pinned. Exact upstream license must be "
                "confirmed from the source notebook before hosted submission."
            ),
        }
        (out / "PACKAGE_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("ORW1_PACKAGE_RESULT", json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
