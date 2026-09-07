"""CR064-CR066: current public frontier, seat-safe wrappers only.

Hosted evidence is the calibration target. CR060 showed the seat-1 missing-step
bug is real but not sufficient to explain the historical/public-score gap.
These candidates therefore use CURRENT public package bytes from CR063 and make
only one mechanical compatibility change: if obs.step is absent, synthesize it
from synchronized day/hour before the original policy sees the observation.

CR064 = current Adaptive Shop Guard.
CR065 = current Farming Score V3 Replay Revised.
CR066 = current Rank Your Agent.

No strategy thresholds/actions are edited. No Kaggle submission is automatic.
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
    "cr064": ("CR063D_ADAPTIVE_SHOP_GUARD_LATEST_PUBLIC_EXACT.tar.gz", "R4D_CR064_ADAPTIVE_SHOP_GUARD_SEATSAFE_V1.tar.gz"),
    "cr065": ("CR063B_FARMING_SCORE_V3_LATEST_PUBLIC_EXACT.tar.gz", "R4D_CR065_FARMING_SCORE_V3_SEATSAFE_V1.tar.gz"),
    "cr066": ("CR063A_RANK_AGENT_LATEST_PUBLIC_EXACT.tar.gz", "R4D_CR066_RANK_AGENT_LATEST_SEATSAFE_V1.tar.gz"),
}

WRAPPER = r'''

# CR06X mechanical compatibility shim: kaggle-environments 1.32.7 can omit
# obs["step"] for one seat while day/hour remain synchronized. Strategy below
# is unchanged; only the missing clock field is reconstructed.
def _cr06x_clock_safe_obs(obs):
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

_CR06X_ORIGINAL_AGENT = agent

def kaggriculture_cr06x_seatsafe(obs, configuration=None):
    fixed = _cr06x_clock_safe_obs(obs)
    try:
        return _CR06X_ORIGINAL_AGENT(fixed, configuration)
    except TypeError:
        return _CR06X_ORIGINAL_AGENT(fixed)

agent = kaggriculture_cr06x_seatsafe
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
        original_main = hashlib.sha256(main.read_bytes()).hexdigest()
        text = main.read_text(encoding="utf-8")
        if "_cr06x_clock_safe_obs" in text:
            raise RuntimeError(f"{key} source already patched")
        # Appending preserves every original byte before the compatibility shim.
        main.write_text(text.rstrip() + WRAPPER + "\n", encoding="utf-8")
        mod = import_main(root, f"{key}_verify")
        a = mod._cr06x_clock_safe_obs({"player": 1, "day": 3, "hour": 11})
        if int(a["step"]) != 83:
            raise RuntimeError(f"{key} fallback verification failed: {a}")
        original = {"player": 0, "step": 83, "day": 0, "hour": 0}
        if mod._cr06x_clock_safe_obs(original) is not original:
            raise RuntimeError(f"{key} explicit-step observation not preserved")
        # Remove verifier bytecode before packaging.
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
        pack(root, out)
        with tarfile.open(out, "r:gz") as tf:
            members = sorted(m.name for m in tf.getmembers() if m.isfile())
        if "main.py" not in members or any("__pycache__" in m or m.endswith(".pyc") for m in members):
            raise RuntimeError(f"{key} package audit failed")
        return {
            "source_archive": src.name,
            "source_archive_sha256": sha(src),
            "source_main_sha256": original_main,
            "archive": out.name,
            "archive_sha256": sha(out),
            "archive_bytes": out.stat().st_size,
            "members": members,
            "verification": {"seat1_day3_hour11_step": 83, "explicit_step_identity_preserved": True},
            "patch_scope": "append-only root observation clock shim",
            "strategy_changed": False,
            "decision": "READY_FOR_MECHANICAL_SMOKE",
        }


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--source-dir", required=True); ap.add_argument("--output-dir", required=True); args = ap.parse_args()
    srcdir, outdir = Path(args.source_dir), Path(args.output_dir)
    report = {"schema_version":"cr064-cr066-current-frontier-seatsafe-v1", "automatic_kaggle_submission":False, "candidates":{}}
    for key, (srcname, outname) in SPECS.items():
        src = srcdir / srcname
        if not src.exists(): raise FileNotFoundError(src)
        report["candidates"][key] = build_one(key, src, outdir / outname)
    (outdir / "receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
