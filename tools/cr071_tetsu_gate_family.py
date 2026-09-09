from __future__ import annotations

"""Build targeted CR071 Tetsu gate-family variants.

Rationale: expanded CR053-vs-CR070A forensics showed large outcome stratification
by the Tetsu branch actually selected.  These variants alter only the three
prefix-compatible branch gates; route tapes and repair logic remain untouched.
"""

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

YARN = '    (226, "shop_YARN_STORE", 1, YARN),\n'
CARROT = '    (360, "px_CARROT", 42, YARN_CARROT),\n'
MILK = '    (433, "inv_MILK", 10067, MILK_GLUT),\n'

VARIANTS = {
    "PARENT": (),
    "CR071I_NO_YARN_GATE": (YARN,),
    "CR071J_NO_MILK_GLUT_GATE": (MILK,),
    "CR071K_MAIN_ONLY": (YARN, MILK),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def safe_extract(archive: Path, dst: Path) -> None:
    base = dst.resolve()
    with tarfile.open(archive, "r:*") as tf:
        for member in tf.getmembers():
            target = (dst / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name!r}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"links forbidden: {member.name!r}")
        tf.extractall(dst)


def build(base_archive: Path, out_dir: Path, variant: str, needles: tuple[str, ...]) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"{variant.lower()}-") as td:
        root = Path(td)
        safe_extract(base_archive, root)
        main = root / "main.py"
        text = main.read_text(encoding="utf-8")
        patched = text
        removed = []
        for needle in needles:
            if patched.count(needle) != 1:
                raise RuntimeError(f"unexpected gate count for {needle!r}")
            patched = patched.replace(needle, "", 1)
            removed.append(needle.strip())
        compile(patched, f"<{variant}>", "exec")
        main.write_text(patched, encoding="utf-8")
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
        for pyc in root.rglob("*.pyc"):
            pyc.unlink(missing_ok=True)
        dst = out_dir / f"{variant}_SEATSAFE_V1.tar.gz"
        with tarfile.open(dst, "w:gz") as tf:
            for p in sorted(root.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                    tf.add(p, arcname=p.relative_to(root).as_posix())
        return {
            "variant": variant,
            "removed_gates": removed,
            "archive": dst.name,
            "archive_sha256": sha256_file(dst),
            "archive_bytes": dst.stat().st_size,
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    base = Path(args.base)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": "kculture-cr071-tetsu-gate-family-v1",
        "base_archive": base.name,
        "base_archive_sha256": sha256_file(base),
        "policy": "branch-gate-only screen; route tapes and repairs untouched; W/L primary",
        "automatic_kaggle_submission": False,
        "variants": {},
    }
    for variant, needles in VARIANTS.items():
        receipt["variants"][variant] = build(base, out, variant, needles)
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
