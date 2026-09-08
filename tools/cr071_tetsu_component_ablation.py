from __future__ import annotations

"""Build one-component CR071 ablations from the exact CR070A/Tetsu package.

The experiment is deliberately conservative: every candidate starts from the exact
CR070A archive and removes exactly one public branch/repair component.  Long route
tapes, all untouched components, and the mechanical seat-clock shim remain byte-for-
byte equivalent except for the explicit source edit recorded in receipt.json.
"""

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


VARIANTS = {
    "PARENT": "parent",
    "CR071A_NO_YARN_GATE": "no_yarn_gate",
    "CR071B_NO_CARROT_GATE": "no_carrot_gate",
    "CR071C_NO_MILK_GLUT_GATE": "no_milk_glut_gate",
    "CR071D_NO_WEED_DIG": "no_weed_dig",
    "CR071E_NO_ROOM_GUARD": "no_room_guard",
    "CR071F_NO_CLAMP_SELLS": "no_clamp_sells",
    "CR071G_NO_DEAD_STOCK": "no_dead_stock",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def remove_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"start marker absent: {start_marker}")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise RuntimeError(f"end marker absent: {end_marker}")
    return text[:start] + replacement + text[end:]


def patch_source(text: str, mode: str) -> str:
    if mode == "parent":
        return text
    if mode == "no_yarn_gate":
        needle = '    (226, "shop_YARN_STORE", 1, YARN),\n'
        if text.count(needle) != 1:
            raise RuntimeError("unexpected YARN gate count")
        return text.replace(needle, "", 1)
    if mode == "no_carrot_gate":
        needle = '    (360, "px_CARROT", 42, YARN_CARROT),\n'
        if text.count(needle) != 1:
            raise RuntimeError("unexpected CARROT gate count")
        return text.replace(needle, "", 1)
    if mode == "no_milk_glut_gate":
        needle = '    (433, "inv_MILK", 10067, MILK_GLUT),\n'
        if text.count(needle) != 1:
            raise RuntimeError("unexpected MILK_GLUT gate count")
        return text.replace(needle, "", 1)
    if mode == "no_weed_dig":
        return remove_between(
            text,
            "        # ---- weed_dig:",
            "        # ---- projected shed:",
            "        # ---- weed_dig ablated by CR071 screen ----\n\n",
        )
    if mode == "no_room_guard":
        return remove_between(
            text,
            "        # ---- room_guard:",
            "        # ---- clamp_sells:",
            "        # ---- room_guard ablated by CR071 screen ----\n\n",
        )
    if mode == "no_clamp_sells":
        return remove_between(
            text,
            "        # ---- clamp_sells:",
            "        # ---- dead_stock:",
            "        # ---- clamp_sells ablated by CR071 screen ----\n\n",
        )
    if mode == "no_dead_stock":
        return remove_between(
            text,
            "        # ---- dead_stock:",
            '        return {"farmer": acts[0], "hands": acts[1:],',
            "        # ---- dead_stock ablated by CR071 screen ----\n        extra = []\n\n",
        )
    raise ValueError(mode)


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


def build_one(base_archive: Path, out_dir: Path, variant: str, mode: str) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"cr071-{variant.lower()}-") as td:
        root = Path(td)
        safe_extract(base_archive, root)
        main = root / "main.py"
        if not main.is_file():
            raise RuntimeError("base archive has no root main.py")
        original = main.read_text(encoding="utf-8")
        patched = patch_source(original, mode)
        if mode == "parent" and patched != original:
            raise RuntimeError("parent unexpectedly changed")
        if mode != "parent" and patched == original:
            raise RuntimeError(f"variant {variant} made no source change")
        compile(patched, f"<{variant}>", "exec")
        main.write_text(patched, encoding="utf-8")
        for cache in root.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
        for pyc in root.rglob("*.pyc"):
            pyc.unlink(missing_ok=True)
        filename = f"{variant}_SEATSAFE_V1.tar.gz"
        dst = out_dir / filename
        with tarfile.open(dst, "w:gz") as tf:
            for p in sorted(root.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                    tf.add(p, arcname=p.relative_to(root).as_posix())
        return {
            "variant": variant,
            "mode": mode,
            "archive": filename,
            "archive_sha256": sha256_file(dst),
            "archive_bytes": dst.stat().st_size,
            "main_sha256": sha256_bytes(patched.encode("utf-8")),
            "source_changed": patched != original,
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
        "schema_version": "kculture-cr071-tetsu-component-ablation-v1",
        "base_archive": base.name,
        "base_archive_sha256": sha256_file(base),
        "policy": "one-component-removal screen; W/L primary; no automatic Kaggle submission",
        "automatic_kaggle_submission": False,
        "variants": {},
    }
    for variant, mode in VARIANTS.items():
        receipt["variants"][variant] = build_one(base, out, variant, mode)
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
