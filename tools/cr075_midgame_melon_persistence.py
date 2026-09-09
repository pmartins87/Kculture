from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_extract(archive: Path, dst: Path) -> None:
    base = dst.resolve()
    with tarfile.open(archive, "r:*") as tf:
        for member in tf.getmembers():
            target = (dst / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError("links forbidden")
        tf.extractall(dst)


INJECT = r'''
        # ---- CR075 midgame melon persistence ----
        # Frozen hosted-meta hypothesis from CR074 (2026-09-06..08): winners
        # repeatedly retain/sell more MELON in the midgame while the parent route
        # exhausts its planned MELON sales in phase 1.  Keep the intervention
        # deliberately small and prefix-compatible across every parent route.
        if step == 264:
            for o in market:
                if o and len(o) >= 3 and o[0] == "BUY_SEED" and o[1] == "CARROT" and int(o[2]) == 1:
                    o[1] = "MELON"
                    o[2] = 3
                    break
        melon_replants = {275: 1, 277: 2}.get(step, 0)
        if melon_replants:
            changed = 0
            for a in acts:
                if changed >= melon_replants:
                    break
                if a and len(a) >= 2 and a[0] == "PLANT" and a[1] == "WHEAT":
                    a[1] = "MELON"
                    changed += 1
'''


def patch_source(src: str) -> str:
    marker = '        positions = [tuple(farm["farmer"])] + [tuple(p) for p in farm["hands"]]\n'
    if src.count(marker) != 1:
        raise RuntimeError("CR075 positions marker mismatch")
    patched = src.replace(marker, marker + "\n" + INJECT + "\n", 1)
    compile(patched, "<cr075-midgame-melon>", "exec")
    return patched


def package_dir(root: Path, dst: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for pyc in root.rglob("*.pyc"):
        pyc.unlink(missing_ok=True)
    with tarfile.open(dst, "w:gz") as tf:
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                tf.add(p, arcname=p.relative_to(root).as_posix())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    base = Path(args.base)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cr075-build-") as td:
        root = Path(td)
        safe_extract(base, root)
        main_py = root / "main.py"
        original = main_py.read_text(encoding="utf-8")
        patched = patch_source(original)
        main_py.write_text(patched, encoding="utf-8")
        dst = out / "CR075_MIDGAME_MELON_PERSISTENCE_SEATSAFE_V1.tar.gz"
        package_dir(root, dst)

    receipt = {
        "schema_version": "kculture-cr075-midgame-melon-persistence-v1",
        "base_sha256": sha256_file(base),
        "candidate_sha256": sha256_file(dst),
        "candidate": dst.name,
        "hypothesis": "small midgame MELON persistence intervention derived from a 3-date hosted winner-vs-loser signal",
        "frozen_changes": [
            "step264 BUY_SEED CARROT 1 -> BUY_SEED MELON 3",
            "step275 first PLANT WHEAT -> PLANT MELON",
            "step277 first two PLANT WHEAT -> PLANT MELON",
        ],
        "unchanged": [
            "all route-selection thresholds",
            "all hires",
            "all animal purchases and placements",
            "all STRAWBERRY actions",
            "all market logic except the single seed-order substitution",
            "room_guard, clamp_sells and dead_stock logic",
        ],
        "automatic_kaggle_submission": False,
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
