"""CR060/CR061: repair the current Kaggriculture seat-1 missing-step bug.

The public runtime in kaggle-environments 1.32.7 leaves obs['step'] unset for
player index 1 while day/hour remain synchronized.  CR055 and CR056 both key
large step-indexed schedules off obs['step']; that makes their seat-1 policy
behave as turn 0 for the whole season.

This builder makes the narrowest possible derived packages:
  * CR060 = CR055 Preempt H6 exact package + day/hour clock fallback.
  * CR061 = CR056 Indar TOP10 exact package + root-level step injection so all
    nested modules receive a correct synthetic step when seat 1 lacks it.

No strategic actions or thresholds are otherwise changed.
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(src, "r:gz") as tf:
        tf.extractall(dst)


def pack(src_dir: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w:gz") as tf:
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                tf.add(p, arcname=p.relative_to(src_dir).as_posix())


def patch_cr055(root: Path) -> dict:
    p = root / "main.py"
    text = p.read_text(encoding="utf-8")
    anchor = '''def agent(obs):\n    try:\n        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)\n'''
    replacement = '''def _clock(obs):\n    raw = _get(obs, "step", None)\n    if raw is None:\n        raw = int(_get(obs, "day", 0) or 0) * 24 + int(_get(obs, "hour", 0) or 0)\n    return max(0, int(raw or 0))\n\n\ndef agent(obs):\n    try:\n        step = min(_clock(obs), len(_ACTIONS) - 1)\n'''
    if text.count(anchor) != 1:
        raise RuntimeError("CR055 patch anchor mismatch")
    text = text.replace(anchor, replacement, 1)
    p.write_text(text, encoding="utf-8")
    return {"clock_fallback": "day*24+hour", "patch_scope": "main.py::_clock only"}


def patch_cr056(root: Path) -> dict:
    p = root / "main.py"
    text = p.read_text(encoding="utf-8")
    anchor = '''# Kaggle's raw loader selects the final callable in insertion order.\ndef kaggriculture_e776_agent(obs, configuration=None):\n    return _policy(obs, configuration)\n'''
    replacement = '''def _clock_safe_obs(obs):\n    try:\n        raw = obs.get("step")\n    except Exception:\n        raw = None\n    if raw is not None:\n        return obs\n    try:\n        patched = dict(obs)\n        patched["step"] = int(patched.get("day", 0) or 0) * 24 + int(patched.get("hour", 0) or 0)\n        return patched\n    except Exception:\n        return obs\n\n\n# Kaggle's raw loader selects the final callable in insertion order.\ndef kaggriculture_e776_agent(obs, configuration=None):\n    return _policy(_clock_safe_obs(obs), configuration)\n'''
    if text.count(anchor) != 1:
        raise RuntimeError("CR056 patch anchor mismatch")
    text = text.replace(anchor, replacement, 1)
    p.write_text(text, encoding="utf-8")
    return {"clock_fallback": "inject day*24+hour at root", "patch_scope": "main.py wrapper only"}


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify_cr055(root: Path) -> dict:
    mod = import_module(root / "main.py", "cr060_verify")
    assert mod._clock({"player": 1, "day": 3, "hour": 11}) == 83
    assert mod._clock({"player": 0, "step": 83, "day": 0, "hour": 0}) == 83
    return {"seat1_missing_step_clock": 83, "seat0_explicit_step_clock": 83}


def verify_cr056(root: Path) -> dict:
    sys.path.insert(0, str(root))
    try:
        mod = import_module(root / "main.py", "cr061_verify")
        patched = mod._clock_safe_obs({"player": 1, "day": 3, "hour": 11})
        assert int(patched["step"]) == 83
        original = {"player": 0, "step": 83, "day": 0, "hour": 0}
        assert mod._clock_safe_obs(original) is original
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    return {"seat1_missing_step_injected": 83, "seat0_explicit_step_preserved": True}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cr055", required=True)
    ap.add_argument("--cr056", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    specs = [
        ("cr060", Path(args.cr055), "R4D_CR060_PREEMPT_H6_SEATSAFE_V1.tar.gz", patch_cr055, verify_cr055),
        ("cr061", Path(args.cr056), "R4D_CR061_INDAR_TOP10_SEATSAFE_V1.tar.gz", patch_cr056, verify_cr056),
    ]
    report = {
        "schema_version": "cr060-cr061-seat1-clock-fix-v1",
        "automatic_kaggle_submission": False,
        "cause": "seat 1 has no obs.step; day/hour are synchronized",
        "candidates": {},
    }
    for key, src, name, patcher, verifier in specs:
        with tempfile.TemporaryDirectory(prefix=f"{key}-") as td:
            root = Path(td) / "pkg"
            extract(src, root)
            before_main = hashlib.sha256((root / "main.py").read_bytes()).hexdigest()
            patch = patcher(root)
            verification = verifier(root)
            target = out / name
            pack(root, target)
            report["candidates"][key] = {
                "source_archive": src.name,
                "source_archive_sha256": sha256(src),
                "source_main_sha256": before_main,
                "archive": target.name,
                "archive_sha256": sha256(target),
                "archive_bytes": target.stat().st_size,
                "patch": patch,
                "verification": verification,
                "decision": "READY_FOR_HOSTED_SEAT_BUG_CALIBRATION",
            }
    (out / "receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
