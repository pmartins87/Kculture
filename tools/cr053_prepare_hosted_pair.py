"""Prepare two materially distinct hosted candidates after CR051/CR052.

CR052: copy the exact public Apache-2.0 Adaptive Route Agent V2 submission
archive, pinned by handle and expected archive SHA.

CR053: package the exact 719-action route from live-king episode 106309334,
which CR051 selected as the training-best static route and validated at 58.0%
against CR029. Re-check it on a fresh 1024-seed both-seat panel before package.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import random
import shutil
import statistics
import tarfile
import tempfile
from pathlib import Path

import kagglehub
import kagsim

import cr049_live_king_knn_clone as c49

ROOT = Path(__file__).resolve().parents[1]
PASS = {"farmer": ["PASS"], "hands": [], "market": []}
CR052_HANDLE = "reyhanksatria/adaptive-route-agent-v2/versions/2"
CR052_EXPECTED_ARCHIVE_SHA = "b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d"
CR053_EPISODE_ID = 106309334
CR053_SOURCE_SUBMISSION_ID = 56064100
CR053_MASTER_SEED = 5309072026
CR053_SEED_COUNT = 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_tape_sha(tape: list[dict]) -> str:
    return sha(json.dumps(tape, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def deterministic_tar_gz(path: Path, files: list[tuple[bytes, str]]) -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tf:
        for data, arcname in sorted(files, key=lambda x: x[1]):
            info = tarfile.TarInfo(arcname)
            info.size = len(data); info.mtime = 0; info.uid = 0; info.gid = 0
            info.uname = ""; info.gname = ""; info.mode = 0o644
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def runtime_source(tape: list[dict]) -> bytes:
    tape_json = json.dumps(tape, separators=(",", ":"), sort_keys=True)
    src = f'''"""CR053 static route 106309334. Public replay-derived coherent policy."""\nimport copy as _copy\nimport json as _json\n_TAPE = _json.loads({tape_json!r})\n\ndef _clock(obs):\n    try:\n        raw = obs.get("step")\n        if raw is not None:\n            return max(0, int(raw))\n    except Exception:\n        pass\n    try:\n        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))\n    except Exception:\n        return 0\n\ndef agent(obs, config=None):\n    return _copy.deepcopy(_TAPE[max(0, min(718, _clock(obs)))])\n'''
    return src.encode("utf-8")


def find_exact_cr052_archive() -> tuple[bytes, str]:
    with tempfile.TemporaryDirectory(prefix="cr052-exact-archive-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(CR052_HANDLE, output_dir=str(root), force_download=True)
        arcs = sorted(p for p in root.rglob("*") if p.is_file() and p.name.lower().endswith((".tar.gz", ".tgz", ".tar")))
        matches = []
        for p in arcs:
            data = p.read_bytes()
            if sha(data) == CR052_EXPECTED_ARCHIVE_SHA:
                matches.append((data, p.name))
        if len(matches) != 1:
            raise RuntimeError(f"expected one CR052 archive hash match, got {len(matches)}")
        data, name = matches[0]
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            names = {m.name for m in tf.getmembers() if m.isfile()}
        if "main.py" not in names or "agent.so" not in names:
            raise RuntimeError(f"CR052 archive missing runtime members: {sorted(names)}")
        return data, name


def fetch_cr053_tape() -> tuple[list[dict], int]:
    eps = c49.fetch_json(c49.LIST_URL, post={"submissionId": CR053_SOURCE_SUBMISSION_ID}).get("episodes") or []
    meta = next((e for e in eps if int(e.get("id") or -1) == CR053_EPISODE_ID), None)
    if meta is None:
        raise RuntimeError("CR053 episode absent from frozen submission episode list")
    loaded = c49.episode_pairs(meta, CR053_SOURCE_SUBMISSION_ID)
    tape = [copy.deepcopy(p[2]) for p in loaded["pairs"]]
    if len(tape) != 719:
        raise RuntimeError(f"CR053 tape len {len(tape)}")
    return tape, int(loaded["seat"])


def make_seeds() -> list[int]:
    r = random.Random(CR053_MASTER_SEED); out = set()
    while len(out) < CR053_SEED_COUNT:
        out.add(r.randint(1, 2147483646))
    return sorted(out)


def validate_static(tape: list[dict], base: list[dict]) -> dict:
    s = kagsim.Stream(tape); b = kagsim.Stream(base)
    jobs = []; meta = []
    for seed in make_seeds():
        jobs.append((s, b, seed)); meta.append(0)
        jobs.append((b, s, seed)); meta.append(1)
    results = kagsim.run_many(jobs)
    margins = []
    for (a, bb), seat in zip(results, meta):
        margins.append(float(a - bb) if seat == 0 else float(bb - a))
    w = sum(x > 0 for x in margins); l = sum(x < 0 for x in margins); t = len(margins)-w-l
    return {
        "games": len(margins), "wins": w, "losses": l, "ties": t,
        "score_rate": (w + 0.5*t)/len(margins),
        "mean_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "master_seed": CR053_MASTER_SEED,
        "seed_count": CR053_SEED_COUNT,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source-bundle", required=True); ap.add_argument("--output-dir", required=True); args = ap.parse_args()
    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7": raise RuntimeError("wrong engine")
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8")); base = bundle["recent_top"]["tape"]

    cr052_data, source_name = find_exact_cr052_archive()
    cr052_path = out / "R4D_CR052_ADAPTIVE_ROUTE_V2_PUBLIC_EXACT.tar.gz"
    cr052_path.write_bytes(cr052_data)

    tape, source_seat = fetch_cr053_tape()
    cr053_validation = validate_static(tape, base)
    cr053_pass = cr053_validation["score_rate"] >= 0.54 and cr053_validation["mean_margin"] >= 0.0
    main_py = runtime_source(tape)
    notice = (
        "Kculture CR053 static route candidate.\n"
        f"Public Kaggriculture replay episode: {CR053_EPISODE_ID}; source seat: {source_seat}.\n"
        f"Source submission id for provenance only: {CR053_SOURCE_SUBMISSION_ID}.\n"
        f"Canonical action tape SHA-256: {canonical_tape_sha(tape)}.\n"
        "No runtime network, opponent identity, seed identity, or submission identity is used.\n"
    ).encode("utf-8")
    cr053_path = out / "R4D_CR053_ROUTE106309334_V1.tar.gz"
    deterministic_tar_gz(cr053_path, [(main_py, "main.py"), (notice, "PROVENANCE.txt")])

    receipt = {
        "engine": "1.32.7",
        "automatic_kaggle_submission": False,
        "cr052": {
            "handle": CR052_HANDLE,
            "source_archive_name": source_name,
            "archive": cr052_path.name,
            "archive_sha256": sha(cr052_path.read_bytes()),
            "archive_bytes": cr052_path.stat().st_size,
            "local_screen": {"games":512,"wins":130,"ties":328,"losses":54,"score_rate":0.57421875,"mean_margin":109.791015625},
            "decision": "READY_FOR_HOSTED_SUBMISSION"
        },
        "cr053": {
            "source_episode_id": CR053_EPISODE_ID,
            "source_seat": source_seat,
            "tape_sha256": canonical_tape_sha(tape),
            "archive": cr053_path.name,
            "archive_sha256": sha(cr053_path.read_bytes()),
            "archive_bytes": cr053_path.stat().st_size,
            "fresh_static_validation": cr053_validation,
            "decision": "READY_FOR_HOSTED_SUBMISSION" if cr053_pass else "DO_NOT_SUBMIT"
        }
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if not cr053_pass:
        raise SystemExit(4)

if __name__ == "__main__": main()
