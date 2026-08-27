"""Prepare identity-proven public agents for the CR-002 proxy league.

Downloads each exact historical Kaggle notebook version once, verifies the
frozen submission archive SHA-256 and the exact packaged Python entry SHA-256,
and writes a normalized one-file agent copy into artifacts for downstream
round-robin jobs. Third-party code remains workflow-artifact data only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath

import kagglehub

ROOT = Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member(name: str) -> bool:
    p = PurePosixPath(name.replace("\\", "/"))
    return not p.is_absolute() and ".." not in p.parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/competitive_reset_league_v1.json")
    ap.add_argument("--root", default="artifacts/cr002")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    out_root = ROOT / args.root
    download_root = out_root / "downloads"
    agent_root = out_root / "agents"
    download_root.mkdir(parents=True, exist_ok=True)
    agent_root.mkdir(parents=True, exist_ok=True)

    prepared = []
    for item in cfg["public_agents"]:
        aid = item["id"]
        out = download_root / aid
        out.mkdir(parents=True, exist_ok=True)
        result = kagglehub.notebook_output_download(
            item["handle"], output_dir=str(out), force_download=True
        )

        matches = [p for p in out.rglob(item["archive_name"]) if p.is_file()]
        if len(matches) != 1:
            raise SystemExit(f"{aid}: expected one {item['archive_name']}, found {matches}")
        archive = matches[0]
        archive_bytes = archive.read_bytes()
        actual_archive_sha = sha256(archive_bytes)
        if actual_archive_sha != item["archive_sha256"]:
            raise SystemExit(
                f"{aid}: archive SHA mismatch {actual_archive_sha} != {item['archive_sha256']}"
            )

        with tarfile.open(archive, "r:*") as tf:
            try:
                member = tf.getmember(item["entry_path"])
            except KeyError as exc:
                raise SystemExit(f"{aid}: missing package entry {item['entry_path']}") from exc
            if not member.isfile() or not _safe_member(member.name):
                raise SystemExit(f"{aid}: unsafe/non-file package entry {member.name}")
            fh = tf.extractfile(member)
            data = fh.read() if fh else b""

        actual_entry_sha = sha256(data)
        if actual_entry_sha != item["entry_sha256"]:
            raise SystemExit(
                f"{aid}: entry SHA mismatch {actual_entry_sha} != {item['entry_sha256']}"
            )

        target_dir = agent_root / aid
        target_dir.mkdir(parents=True, exist_ok=True)
        normalized = target_dir / "main.py"
        normalized.write_bytes(data)
        prepared.append({
            "id": aid,
            "historical_score": item["historical_score"],
            "handle": item["handle"],
            "source_archive": str(archive.relative_to(ROOT)),
            "archive_sha256": actual_archive_sha,
            "source_entry_path": item["entry_path"],
            "normalized_path": str(normalized.relative_to(ROOT)),
            "entry_sha256": actual_entry_sha,
            "bytes": len(data),
            "kagglehub_result": str(result),
        })
        print(f"PREPARED {aid} score={item['historical_score']} sha={actual_entry_sha}")

    manifest = {
        "league_id": cfg["league_id"],
        "config": args.config,
        "public_agents": prepared,
        "local_agents": cfg["local_agents"],
        "status": "PASS",
    }
    mp = out_root / "prepared_agents_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
