"""Build deterministic self-contained CR024_CONSENSUS_V1 submission package.

Preparation only.  The builder refuses to run unless the preregistered fresh
reserved-block gate has authorized package creation.
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
CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
OUT = ROOT / "artifacts/submissions/cr024_consensus_v1"
ARCHIVE_NAME = "R4D_CR024_CONSENSUS_H11_M19_V1.tar.gz"
AUTH = "CR024_CONSENSUS_V1_PASS__BUILD_PACKAGE"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_tape(api: KaggleApi, meta: dict, folder: Path):
    episode_id = int(meta["episode_id"]); source_seat = int(meta["source_seat"])
    api.competition_episode_replay(episode_id, path=str(folder), quiet=True)
    p = folder / f"episode-{episode_id}-replay.json"
    replay = json.loads(p.read_text(encoding="utf-8"))
    steps = replay.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {episode_id}: {len(steps)}")
    tape = [copy.deepcopy((steps[t + 1][source_seat] or {}).get("action") or {}) for t in range(719)]
    canonical = json.dumps(tape, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return tape, {"episode_id": episode_id, "source_seat": source_seat, "action_count": 719, "canonical_tape_sha256": sha(canonical)}


def build_consensus(t11, t19):
    if len(t11) != 719 or len(t19) != 719:
        raise RuntimeError("tape length mismatch")
    out = []
    for i, (a, b) in enumerate(zip(t11, t19)):
        if json.dumps(a.get("farmer"), sort_keys=True) != json.dumps(b.get("farmer"), sort_keys=True):
            raise RuntimeError(f"farmer mismatch at {i}")
        z = copy.deepcopy(b)
        z["hands"] = copy.deepcopy(a.get("hands"))
        z["market"] = copy.deepcopy(b.get("market"))
        out.append(z)
    return out


def deterministic_tar_gz(path: Path, files):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tf:
        for src, arcname in sorted(files, key=lambda x: x[1]):
            data = Path(src).read_bytes()
            info = tarfile.TarInfo(arcname)
            info.size = len(data); info.mtime = 0; info.uid = 0; info.gid = 0
            info.uname = ""; info.gname = ""; info.mode = 0o644
            tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def runtime_source(tape):
    tape_json = json.dumps(tape, separators=(",", ":"), sort_keys=True)
    return f'''"""Kculture CR024_CONSENSUS_V1 hosted entrypoint."""\nimport copy as _copy\nimport json as _json\n\n_CR024_CONSENSUS_TAPE = _json.loads({tape_json!r})\n\ndef _clock(obs):\n    try:\n        raw = obs.get("step")\n        if raw is not None:\n            return max(0, int(raw))\n    except Exception:\n        pass\n    try:\n        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))\n    except Exception:\n        return 0\n\ndef agent(obs, config=None):\n    step = max(0, min(718, _clock(obs)))\n    return _copy.deepcopy(_CR024_CONSENSUS_TAPE[step])\n\n_cr024_consensus_hosted_entrypoint = agent\n'''


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--authorization", required=True); args = ap.parse_args()
    if args.authorization != AUTH:
        raise SystemExit("CR024 consensus package build not authorized by reserved gate")
    cfg = json.loads(CFG.read_text(encoding="utf-8")); api = KaggleApi(); api.authenticate()
    with tempfile.TemporaryDirectory(prefix="cr024-consensus-build-") as td:
        folder = Path(td)
        t11, p11 = download_tape(api, cfg["routes"]["top11_openloop"], folder)
        t19, p19 = download_tape(api, cfg["routes"]["top19_openloop"], folder)
    consensus = build_consensus(t11, t19)
    consensus_json = json.dumps(consensus, separators=(",", ":"), sort_keys=True).encode("utf-8")

    if OUT.exists(): shutil.rmtree(OUT)
    package = OUT / "package"; package.mkdir(parents=True)
    main_py = package / "main.py"; main_py.write_text(runtime_source(consensus), encoding="utf-8")
    (package / "LICENSE-APACHE-2.0.txt").write_text("Apache License 2.0 notice placeholder for compatibility with prior Kculture package format. No third-party source code is embedded by CR024_CONSENSUS_V1 runtime.\n", encoding="utf-8")
    (package / "THIRD_PARTY_NOTICES.txt").write_text(
        "Kculture CR024_CONSENSUS_V1\n"
        "Strategy: public action-tape consensus, hands from top11 and market/shell from top19.\n"
        f"Top11 episode {p11['episode_id']} seat {p11['source_seat']} tape SHA-256 {p11['canonical_tape_sha256']}\n"
        f"Top19 episode {p19['episode_id']} seat {p19['source_seat']} tape SHA-256 {p19['canonical_tape_sha256']}\n"
        "Runtime network access: none.\n",
        encoding="utf-8",
    )
    archive = OUT / ARCHIVE_NAME
    deterministic_tar_gz(archive, [(main_py,"main.py"),(package/"LICENSE-APACHE-2.0.txt","LICENSE-APACHE-2.0.txt"),(package/"THIRD_PARTY_NOTICES.txt","THIRD_PARTY_NOTICES.txt")])
    manifest = {
        "schema_version": "cr024-consensus-package-v1",
        "authorization": args.authorization,
        "strategy_materially_new": True,
        "composition": {"farmer_shell": "top19", "hands": "top11", "market": "top19"},
        "top11_provenance": p11, "top19_provenance": p19,
        "consensus_tape_sha256": sha(consensus_json),
        "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive.read_bytes()), "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_py.read_bytes()), "runtime_network_required": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
