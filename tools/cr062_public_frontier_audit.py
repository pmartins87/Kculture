"""CR062: harvest strong public Kaggriculture notebook versions and audit seat-clock safety.

We intentionally pin historically best notebook versions rather than trusting the
latest rerun score.  This stage copies exact submission archives and statically
reports whether source code references obs['step'] without an obvious day/hour
fallback.  No strategic edits and no automatic Kaggle submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

import kagglehub

TARGETS = {
    "rank_v11": {
        "handle": "raykkretzschmar/kaggriculture-rank-your-agent/versions/11",
        "public_score_context": 2990.4,
        "out": "CR062A_RANK_AGENT_V11_PUBLIC_EXACT.tar.gz",
    },
    "math_v4": {
        "handle": "lynnsakurai/farming-score-a-mathematical-approach/versions/4",
        "public_score_context": 2733.3,
        "out": "CR062B_MATH_V4_PUBLIC_EXACT.tar.gz",
    },
    "multiroute_v59": {
        "handle": "flexonafft/kaggriculture-adaptive-replay-agent/versions/59",
        "public_score_context": 2767.3,
        "out": "CR062C_MULTI_ROUTE_V59_PUBLIC_EXACT.tar.gz",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_members(path: Path) -> list[str]:
    with tarfile.open(path, "r:*") as tf:
        return sorted(m.name for m in tf.getmembers() if m.isfile())


def audit_source(root: Path) -> dict:
    py = sorted(root.rglob("*.py"))
    refs = []
    safe_hits = []
    for p in py:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = p.relative_to(root).as_posix()
        if '"step"' in text or "'step'" in text:
            refs.append(rel)
        if ("day" in text and "hour" in text and "step" in text) and ("24" in text or "turnsPerDay" in text or "turns_per_day" in text):
            safe_hits.append(rel)
    return {
        "python_files": len(py),
        "step_reference_files": refs,
        "clock_fallback_candidate_files": safe_hits,
        "static_seat_clock_risk": bool(refs and not safe_hits),
    }


def fetch_one(key: str, spec: dict, outdir: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"cr062-{key}-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(spec["handle"], output_dir=str(root), force_download=True)
        archives = []
        for p in root.rglob("*"):
            if p.is_file() and p.name.lower().endswith((".tar.gz", ".tgz")):
                try:
                    members = archive_members(p)
                except Exception:
                    continue
                if "main.py" in members:
                    archives.append((p, members))
        if not archives:
            raise RuntimeError(f"no root-main submission archive for {spec['handle']}")
        unique = {}
        for p, members in archives:
            unique.setdefault(sha(p.read_bytes()), (p, members))
        if len(unique) != 1:
            raise RuntimeError(f"ambiguous archives for {spec['handle']}: {list(unique)}")
        ah, (src, members) = next(iter(unique.items()))
        dst = outdir / spec["out"]
        outdir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        unpack = root / "audit_unpack"
        unpack.mkdir()
        with tarfile.open(src, "r:gz") as tf:
            tf.extractall(unpack)
        source_audit = audit_source(unpack)
        return {
            "handle": spec["handle"],
            "public_score_context": spec["public_score_context"],
            "archive": dst.name,
            "archive_sha256": ah,
            "archive_bytes": dst.stat().st_size,
            "members": members,
            "audit": source_audit,
        }


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", required=True); args = ap.parse_args()
    out = Path(args.output_dir)
    report = {"schema_version":"cr062-public-frontier-audit-v1", "automatic_kaggle_submission":False, "targets":{}}
    for key, spec in TARGETS.items():
        try:
            report["targets"][key] = fetch_one(key, spec, out)
            report["targets"][key]["status"] = "PASS"
        except Exception as exc:
            report["targets"][key] = {"handle":spec["handle"], "status":"ERROR", "error":repr(exc), "public_score_context":spec["public_score_context"]}
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not any(v.get("status") == "PASS" for v in report["targets"].values()):
        raise SystemExit(2)


if __name__ == "__main__": main()
