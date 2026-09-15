#!/usr/bin/env python3
"""Build deterministic modular FP001 physical packages for CR089 H2H."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = (
    "candidates/fp001_e5_elite_mixed_animal.py",
    "candidates/fp001_e3_single_hand_crop_density.py",
    "candidates/fp001_e2_dedicated_strawberry_hand.py",
    "candidates/fp001_h10_cow_scale_module.py",
    "candidates/fp001_h10_cow_scale_care_wrapper.py",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_tar(path, members):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name, data in sorted(members.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-id", required=True)
    ap.add_argument("--composition", required=True)
    ap.add_argument("--strawberries", type=int, default=1)
    ap.add_argument("--melons", type=int, default=6)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    species = tuple(x.strip().upper() for x in args.composition.split(",") if x.strip())
    if len(species) != 5 or any(x not in {"COW", "SHEEP"} for x in species):
        raise ValueError(species)
    if args.strawberries < 0 or args.melons < 0 or args.strawberries + args.melons > 8:
        raise ValueError((args.strawberries, args.melons))

    wrapper = (
        "from candidates.fp001_e5_elite_mixed_animal import make_agent as _make_agent\n"
        f"agent = _make_agent({species!r}, 'DAILY', {args.strawberries}, {args.melons})\n"
    ).encode()
    compile(wrapper.decode(), "main.py", "exec")

    members = {"main.py": wrapper}
    source_hashes = {}
    for rel in DEPENDENCIES:
        path = ROOT / rel
        data = path.read_bytes()
        if rel.endswith(".py"):
            compile(data.decode("utf-8"), rel, "exec")
        members[rel] = data
        source_hashes[rel] = sha256(data)
    provenance = {
        "schema": "cr089-fp001-physical-package-v1",
        "candidate_id": args.candidate_id,
        "composition": species,
        "care_mode": "DAILY",
        "crop_block": {"MELON": args.melons, "STRAWBERRY": args.strawberries},
        "runtime_identity_features": False,
        "runtime_rating_or_episode_features": False,
        "runtime_hidden_seed_or_future": False,
        "runtime_opponent_private_features": False,
        "source_hashes": source_hashes,
    }
    members["CR089_PROVENANCE.json"] = json.dumps(provenance, indent=2, sort_keys=True).encode()

    output = Path(args.output)
    write_tar(output, members)
    first = output.read_bytes()
    rebuild = output.with_suffix(output.suffix + ".rebuild")
    write_tar(rebuild, members)
    if first != rebuild.read_bytes():
        raise RuntimeError("non-deterministic package")
    rebuild.unlink()

    provenance["archive_sha256"] = sha256(first)
    provenance["archive_size"] = len(first)
    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(provenance, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
