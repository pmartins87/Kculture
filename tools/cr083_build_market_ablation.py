"""Build a deterministic CR071M market-family deletion for CR083 Phase 1.

Architecture research only: the source policy is unchanged except that one frozen
market operation family is removed from the *final* queue immediately before return.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ALLOWED = {"SELL", "BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def patch_source(source: str, op: str) -> str:
    if op not in ALLOWED:
        raise ValueError(op)
    anchor = (
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": (market + extra)[:MAX_ORDERS]}\n'
    )
    if source.count(anchor) != 1:
        raise RuntimeError("CR071M final-market return anchor mismatch")
    repl = (
        '        # CR083 Phase-1 causal deletion: remove exactly one market family\n'
        '        # after all inherited CR071M queue construction/safety logic.\n'
        '        _cr083_market = (market + extra)[:MAX_ORDERS]\n'
        f'        _cr083_market = [o for o in _cr083_market if not (o and o[0] == {op!r})]\n'
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": _cr083_market}\n'
    )
    out = source.replace(anchor, repl, 1)
    compile(out, "main.py", "exec")
    return out


def write_deterministic_tar_gz(path: Path, main_text: str) -> None:
    data = main_text.encode("utf-8")
    ti = tarfile.TarInfo("main.py")
    ti.size = len(data)
    ti.mode = 0o644
    ti.mtime = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(ti, io.BytesIO(data))
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--op", required=True, choices=sorted(ALLOWED))
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    base_bytes = a.base.read_bytes()
    source = extract_main(a.base)
    patched = patch_source(source, a.op)
    write_deterministic_tar_gz(a.output, patched)
    out_bytes = a.output.read_bytes()

    manifest = {
        "schema_version": "cr083-phase1-market-ablation-v1",
        "base": "CR071M",
        "ablated_market_op": a.op,
        "filter_position": "after final CR071M market queue construction and MAX_ORDERS truncation",
        "farmer_hands_unchanged": True,
        "all_nonablated_market_ops_unchanged": True,
        "architecture_research_only": True,
        "base_sha256": sha256_bytes(base_bytes),
        "candidate_sha256": sha256_bytes(out_bytes),
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
