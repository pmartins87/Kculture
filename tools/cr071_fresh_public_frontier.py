"""CR071: freeze the *current* public Kaggriculture frontier for benchmarking.

This tool is research infrastructure only.  It does not submit anything to Kaggle.
It downloads current public notebook outputs, selects the runnable submission archive,
adds only the already-proven missing-step/seat clock compatibility shim, verifies the
entrypoint, and records exact hashes so later experiments cannot silently drift when a
public notebook publishes a new version.

Public agents are controls / component research sources.  A final Kculture submission
must be our own evidence-backed derivative and comply with the competition rules.
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

import kagglehub

TARGETS = {
    "tetsu_current": (
        "tetsutani/shape-the-shop-work-the-pasture-kaggriculture",
        "R4D_CR071F1_TETSU_CURRENT_SEATSAFE_V1.tar.gz",
    ),
    "farming_v3_current": (
        "lynnsakurai/farming-score-v3-replay-revised",
        "R4D_CR071F2_FARMING_V3_CURRENT_SEATSAFE_V1.tar.gz",
    ),
    "adaptive_v2_current": (
        "reyhanksatria/adaptive-route-agent-v2",
        "R4D_CR071F3_ADAPTIVE_V2_CURRENT_SEATSAFE_V1.tar.gz",
    ),
    "indar_current": (
        "indarkarhana/shape-the-shop-work-the-pasture-top-10",
        "R4D_CR071F4_INDAR_CURRENT_SEATSAFE_V1.tar.gz",
    ),
}

CLOCK_SHIM = r'''

# CR071 research-only mechanical seat-clock compatibility shim; policy unchanged.
def _cr071_clock_safe_obs(obs):
    try:
        raw = obs.get("step")
    except Exception:
        raw = getattr(obs, "step", None)
    if raw is not None:
        return obs
    try:
        p = dict(obs)
    except Exception:
        p = {}
    try:
        day = p.get("day", getattr(obs, "day", 0))
    except Exception:
        day = 0
    try:
        hour = p.get("hour", getattr(obs, "hour", 0))
    except Exception:
        hour = 0
    p["step"] = int(day or 0) * 24 + int(hour or 0)
    return p
try:
    _CR071_PUBLIC_ORIGINAL_AGENT = agent
except NameError:
    _CR071_PUBLIC_ORIGINAL_AGENT = kaggriculture_agent
def _cr071_public_agent(obs, configuration=None):
    fixed = _cr071_clock_safe_obs(obs)
    try:
        return _CR071_PUBLIC_ORIGINAL_AGENT(fixed, configuration)
    except TypeError:
        return _CR071_PUBLIC_ORIGINAL_AGENT(fixed)
agent = _cr071_public_agent
'''


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_extract(archive: Path, dst: Path) -> None:
    with tarfile.open(archive, "r:*") as tf:
        base = dst.resolve()
        for member in tf.getmembers():
            target = (dst / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe tar member: {member.name}")
        tf.extractall(dst)


def candidate_archives(root: Path) -> list[tuple[Path, list[str]]]:
    found = []
    for p in root.rglob("*"):
        if not p.is_file() or not p.name.lower().endswith((".tar.gz", ".tgz")):
            continue
        try:
            with tarfile.open(p, "r:*") as tf:
                names = [m.name for m in tf.getmembers() if m.isfile()]
        except Exception:
            continue
        if "main.py" in names:
            found.append((p, names))
    return found


def choose_archive(root: Path) -> tuple[Path, list[str], dict]:
    arcs = candidate_archives(root)
    if not arcs:
        raise RuntimeError("no runnable tar.gz/tgz containing main.py in notebook output")

    # Prefer the conventional Kaggle output name.  If several copies are byte-identical,
    # collapse them by hash.  Never guess between genuinely different runnable archives.
    conventional = [x for x in arcs if x[0].name.lower() in {"submission.tar.gz", "submission.tgz"}]
    pool = conventional or arcs
    by_hash: dict[str, tuple[Path, list[str]]] = {}
    for p, names in pool:
        by_hash.setdefault(sha256(p), (p, names))
    if len(by_hash) != 1:
        raise RuntimeError(
            "ambiguous runnable archives: "
            + json.dumps([{"path": str(p.relative_to(root)), "sha256": sha256(p)} for p, _ in pool])
        )
    src, names = next(iter(by_hash.values()))
    inventory = {
        "all_runnable_archives": [
            {"path": str(p.relative_to(root)), "sha256": sha256(p), "bytes": p.stat().st_size}
            for p, _ in arcs
        ],
        "selected_from_conventional_name": bool(conventional),
    }
    return src, names, inventory


def verify(root: Path) -> None:
    sys.path.insert(0, str(root))
    try:
        spec = importlib.util.spec_from_file_location("cr071_public_verify", root / "main.py")
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import packaged main.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not callable(getattr(mod, "agent", None)):
            raise RuntimeError("no callable agent")
        q = mod._cr071_clock_safe_obs({"player": 1, "day": 3, "hour": 11})
        if int(q.get("step", -1)) != 83:
            raise RuntimeError("seat clock probe failed")
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass


def pack(root: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dst, "w:gz") as tf:
        for p in sorted(root.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            tf.add(p, arcname=p.relative_to(root).as_posix())


def build(key: str, handle: str, outname: str, outdir: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"cr071-fresh-{key}-") as td:
        download_root = Path(td) / "download"
        download_root.mkdir(parents=True)
        kagglehub.notebook_output_download(handle, output_dir=str(download_root), force_download=True)
        src, members, inventory = choose_archive(download_root)

        unpack = Path(td) / "unpack"
        unpack.mkdir()
        safe_extract(src, unpack)
        main = unpack / "main.py"
        source_main_hash = sha256(main)
        source_archive_hash = sha256(src)
        text = main.read_text(encoding="utf-8")
        main.write_text(text.rstrip() + CLOCK_SHIM + "\n", encoding="utf-8")
        verify(unpack)
        for cache in list(unpack.rglob("__pycache__")):
            shutil.rmtree(cache, ignore_errors=True)

        dst = outdir / outname
        pack(unpack, dst)
        return {
            "key": key,
            "handle": handle,
            "status": "PASS",
            "source_archive_path": str(src.relative_to(download_root)),
            "source_archive_sha256": source_archive_hash,
            "source_main_sha256": source_main_hash,
            "packaged_main_sha256": sha256(main),
            "archive": dst.name,
            "archive_sha256": sha256(dst),
            "archive_bytes": dst.stat().st_size,
            "members": members,
            "notebook_output_inventory": inventory,
            "seat1_clock_probe": 83,
            "automatic_kaggle_submission": False,
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "kculture-cr071-fresh-public-frontier-v1",
        "purpose": "benchmark_controls_only",
        "automatic_kaggle_submission": False,
        "targets": {},
    }
    for key, (handle, outname) in TARGETS.items():
        try:
            report["targets"][key] = build(key, handle, outname, out)
        except Exception as exc:
            report["targets"][key] = {
                "key": key,
                "handle": handle,
                "status": "ERROR",
                "error": repr(exc),
            }
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not any(v.get("status") == "PASS" for v in report["targets"].values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
