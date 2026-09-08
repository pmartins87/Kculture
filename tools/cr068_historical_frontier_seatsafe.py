"""CR068: mechanical seat-safe wrappers for two historically strong public agents.

Purpose: test materially different architectures without assuming that historical
Kaggle scores transfer to the current pool.  We take exact public packages from
CR062 and make only one compatibility edit: if obs.step is absent, synthesize it
from synchronized day/hour before the original policy sees the observation.

Candidates:
  * CR068A = Rank Your Agent V11 (historical public context ~2990.4)
  * CR068B = Farming Score Mathematical Approach V4 (~2733.3)

No strategic thresholds/actions are changed. No automatic Kaggle submission.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

SPECS = {
    "cr068a": ("CR062A_RANK_AGENT_V11_PUBLIC_EXACT.tar.gz", "R4D_CR068A_RANK_V11_SEATSAFE_V1.tar.gz"),
    "cr068b": ("CR062B_MATH_V4_PUBLIC_EXACT.tar.gz", "R4D_CR068B_MATH_V4_SEATSAFE_V1.tar.gz"),
}

WRAPPER = r'''

# CR068 mechanical compatibility shim only.
def _cr068_clock_safe_obs(obs):
    try:
        raw = obs.get("step")
    except Exception:
        try:
            raw = getattr(obs, "step")
        except Exception:
            raw = None
    if raw is not None:
        return obs
    try:
        patched = dict(obs)
    except Exception:
        patched = {}
        try:
            patched.update(obs)
        except Exception:
            pass
    try:
        day = patched.get("day", getattr(obs, "day", 0))
    except Exception:
        day = 0
    try:
        hour = patched.get("hour", getattr(obs, "hour", 0))
    except Exception:
        hour = 0
    patched["step"] = int(day or 0) * 24 + int(hour or 0)
    return patched

_CR068_ORIGINAL_AGENT = agent

def kaggriculture_cr068_seatsafe(obs, configuration=None):
    fixed = _cr068_clock_safe_obs(obs)
    try:
        return _CR068_ORIGINAL_AGENT(fixed, configuration)
    except TypeError:
        return _CR068_ORIGINAL_AGENT(fixed)

agent = kaggriculture_cr068_seatsafe
'''


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def extract(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(src, "r:gz") as tf:
        tf.extractall(dst)


def pack(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dst, "w:gz") as tf:
        for p in sorted(src.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                tf.add(p, arcname=p.relative_to(src).as_posix())


def import_main(root: Path, name: str):
    sys.path.insert(0, str(root))
    try:
        spec = importlib.util.spec_from_file_location(name, root / "main.py")
        if spec is None or spec.loader is None:
            raise RuntimeError(root / "main.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)


def build_one(key: str, src: Path, out: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"{key}-") as td:
        root = Path(td) / "pkg"
        extract(src, root)
        main = root / "main.py"
        before = hashlib.sha256(main.read_bytes()).hexdigest()
        text = main.read_text(encoding="utf-8")
        if "_cr068_clock_safe_obs" in text:
            raise RuntimeError(f"{key} already patched")
        main.write_text(text.rstrip() + WRAPPER + "\n", encoding="utf-8")
        mod = import_main(root, f"{key}_verify")
        patched = mod._cr068_clock_safe_obs({"player":1,"day":3,"hour":11})
        assert int(patched["step"]) == 83
        original = {"player":0,"step":83,"day":0,"hour":0}
        assert mod._cr068_clock_safe_obs(original) is original
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
        pack(root, out)
        return {
            "source_archive": src.name,
            "source_archive_sha256": sha(src),
            "source_main_sha256": before,
            "archive": out.name,
            "archive_sha256": sha(out),
            "archive_bytes": out.stat().st_size,
            "strategy_changed": False,
            "verification": {"seat1_day3_hour11_step":83,"explicit_step_identity_preserved":True},
            "decision":"READY_FOR_SMOKE",
        }


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--source-dir",required=True); ap.add_argument("--output-dir",required=True); args=ap.parse_args()
    srcdir,outdir=Path(args.source_dir),Path(args.output_dir)
    report={"schema_version":"cr068-historical-frontier-seatsafe-v1","automatic_kaggle_submission":False,"candidates":{}}
    for key,(srcname,outname) in SPECS.items():
        report["candidates"][key]=build_one(key,srcdir/srcname,outdir/outname)
    (outdir/"receipt.json").write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__ == "__main__": main()
