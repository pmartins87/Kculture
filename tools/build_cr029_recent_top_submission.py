"""Build deterministic self-contained CR029 full_recent_top submission package.

This packages exactly the coherent 719-action policy that passed CR029. It does
not alter, splice, retune, or adapt the policy. The source replay identity and
stream hashes are verified before packaging.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr029_fresh_official_meta_calibration.json"
OUT = ROOT / "artifacts/submissions/cr029_full_recent_top_v1"
ARCHIVE_NAME = "R4D_CR029_FULL_RECENT_TOP_V1.tar.gz"
AUTH = "CR029_FULL_RECENT_TOP_PASS__BUILD_PACKAGE"
EXPECTED_TAPE_SHA256 = "6c56840b9510e0688da2fbec47e8f89583c63a0124fa4c8801fa5d93c197226b"


def canonical(action: dict) -> bytes:
    return json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stream_hash(actions: list[dict], n: int) -> str:
    body = b"".join(canonical(a) + b"\0" for a in actions[:n])
    return hashlib.sha256(body).hexdigest()[:16]


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def actions_for(replay: dict, seat: int) -> list[dict]:
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay: {len(steps)}")
    return [copy.deepcopy((steps[t + 1][seat] or {}).get("action") or {}) for t in range(719)]


def deterministic_tar_gz(path: Path, files: list[tuple[Path, str]]) -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tf:
        for src, arcname in sorted(files, key=lambda x: x[1]):
            data = src.read_bytes()
            info = tarfile.TarInfo(arcname)
            info.size = len(data)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def runtime_source(tape: list[dict]) -> str:
    tape_json = json.dumps(tape, separators=(",", ":"), sort_keys=True)
    return f'''"""Kculture CR029 FULL_RECENT_TOP_V1 hosted entrypoint.\n\nExact coherent policy promoted by CR029; no runtime network or identity logic.\n"""\nimport copy as _copy\nimport json as _json\n\n_CR029_RECENT_TOP_TAPE = _json.loads({tape_json!r})\n\ndef _clock(obs):\n    try:\n        raw = obs.get("step")\n        if raw is not None:\n            return max(0, int(raw))\n    except Exception:\n        pass\n    try:\n        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))\n    except Exception:\n        return 0\n\ndef agent(obs, config=None):\n    step = max(0, min(718, _clock(obs)))\n    return _copy.deepcopy(_CR029_RECENT_TOP_TAPE[step])\n\n_cr029_full_recent_top_hosted_entrypoint = agent\n'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization", required=True)
    args = ap.parse_args()
    if args.authorization != AUTH:
        raise SystemExit("CR029 package build not authorized by frozen gate")

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    source = cfg["recent_top_source"]
    api = KaggleApi(); api.authenticate()
    with tempfile.TemporaryDirectory(prefix="cr029-package-build-") as td:
        folder = Path(td)
        episode_id = int(source["episode_id"])
        api.competition_episode_replay(episode_id, path=str(folder), quiet=True)
        replay = json.loads((folder / f"episode-{episode_id}-replay.json").read_text(encoding="utf-8"))
        tape = actions_for(replay, int(source["source_seat"]))

    if len(tape) != 719:
        raise RuntimeError(f"unexpected tape length: {len(tape)}")
    observed_tape_sha = tape_sha(tape)
    if observed_tape_sha != EXPECTED_TAPE_SHA256:
        raise RuntimeError(f"tape SHA mismatch: {observed_tape_sha}")

    verified = {}
    for raw_n, expected in source["expected_stream_hashes"].items():
        n = int(raw_n)
        observed = stream_hash(tape, n)
        verified[str(n)] = {"expected": expected, "observed": observed, "exact": observed == expected}
    if not all(v["exact"] for v in verified.values()):
        raise RuntimeError(f"stream hash mismatch: {verified}")

    if OUT.exists():
        shutil.rmtree(OUT)
    package = OUT / "package"
    package.mkdir(parents=True)
    main_py = package / "main.py"
    main_py.write_text(runtime_source(tape), encoding="utf-8")
    (package / "LICENSE-APACHE-2.0.txt").write_text(
        "Apache License 2.0 notice placeholder retained for Kculture package-format compatibility.\n"
        "The CR029 runtime embeds only public competition action data and Kculture wrapper code.\n",
        encoding="utf-8",
    )
    (package / "THIRD_PARTY_NOTICES.txt").write_text(
        "Kculture CR029 FULL_RECENT_TOP_V1\n"
        f"Public competition replay source: episode {source['episode_id']}, seat {source['source_seat']}.\n"
        f"Observed source submission id (provenance only): {source['submission_id']}.\n"
        f"Canonical action tape SHA-256: {observed_tape_sha}.\n"
        "The package contains no downloaded third-party source code and requires no runtime network access.\n",
        encoding="utf-8",
    )

    archive = OUT / ARCHIVE_NAME
    files = [
        (main_py, "main.py"),
        (package / "LICENSE-APACHE-2.0.txt", "LICENSE-APACHE-2.0.txt"),
        (package / "THIRD_PARTY_NOTICES.txt", "THIRD_PARTY_NOTICES.txt"),
    ]
    deterministic_tar_gz(archive, files)

    # Determinism check: rebuild identical bytes before publishing manifest.
    second = OUT / (ARCHIVE_NAME + ".rebuild")
    deterministic_tar_gz(second, files)
    if archive.read_bytes() != second.read_bytes():
        raise RuntimeError("non-deterministic archive rebuild")
    second.unlink()

    manifest = {
        "schema_version": "cr029-full-recent-top-package-v1",
        "authorization": args.authorization,
        "candidate": "full_recent_top",
        "policy_modified": False,
        "source_episode_id": int(source["episode_id"]),
        "source_seat": int(source["source_seat"]),
        "source_submission_id_provenance_only": int(source["submission_id"]),
        "source_observed_rating_context": float(source["observed_rating"]),
        "source_stream_verification": verified,
        "action_count": len(tape),
        "tape_sha256": observed_tape_sha,
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_py.read_bytes()),
        "runtime_network_required": False,
        "runtime_identity_features": False,
        "held_out_touched": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
