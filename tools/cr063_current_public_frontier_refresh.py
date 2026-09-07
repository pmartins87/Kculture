"""CR063: refresh CURRENT public Kaggriculture frontier packages.

CR060 showed that fixing the seat-1 clock bug is not, by itself, enough to
recover a historically strong package.  This stage therefore stops using old
'best score' as the primary signal and fetches current public notebook outputs.

We preserve exact archive bytes, record hashes, and run a stricter source audit
for direct step access.  No strategy edits and no automatic Kaggle submission.
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
    "rank_latest": {
        "handle": "raykkretzschmar/kaggriculture-rank-your-agent",
        "out": "CR063A_RANK_AGENT_LATEST_PUBLIC_EXACT.tar.gz",
    },
    "replay_v3_latest": {
        "handle": "lynnsakurai/farming-score-v3-replay-revised",
        "out": "CR063B_FARMING_SCORE_V3_LATEST_PUBLIC_EXACT.tar.gz",
    },
    "adaptive_route_v2_latest": {
        "handle": "reyhanksatria/adaptive-route-agent-v2",
        "out": "CR063C_ADAPTIVE_ROUTE_V2_LATEST_PUBLIC_EXACT.tar.gz",
    },
    "shop_guard_latest": {
        "handle": "reyhanksatria/kaggriculture-adaptive-shop-guard",
        "out": "CR063D_ADAPTIVE_SHOP_GUARD_LATEST_PUBLIC_EXACT.tar.gz",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def submission_archives(root: Path):
    found = []
    for p in root.rglob("*"):
        if not p.is_file() or not p.name.lower().endswith((".tar.gz", ".tgz")):
            continue
        try:
            with tarfile.open(p, "r:*") as tf:
                names = sorted(m.name for m in tf.getmembers() if m.isfile())
        except Exception:
            continue
        if "main.py" in names:
            found.append((p, names, sha256_bytes(p.read_bytes())))
    return found


def source_audit(archive: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="cr063-audit-") as td:
        root = Path(td)
        with tarfile.open(archive, "r:*") as tf:
            tf.extractall(root)
        rows = []
        for p in sorted(root.rglob("*.py")):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            rel = p.relative_to(root).as_posix()
            direct_default_zero = (
                'get("step", 0)' in text or "get('step', 0)" in text
                or '_get(obs, "step", 0)' in text or "_get(obs, 'step', 0)" in text
            )
            direct_step = ('"step"' in text or "'step'" in text)
            day_hour = ("day" in text and "hour" in text)
            explicit_clock_formula = (
                day_hour and ("* 24" in text or "*24" in text or "turnsPerDay" in text or "turns_per_day" in text)
            )
            rows.append({
                "file": rel,
                "direct_step_reference": direct_step,
                "direct_step_default_zero": direct_default_zero,
                "day_hour_present": day_hour,
                "clock_formula_candidate": explicit_clock_formula,
            })
        risky = [r["file"] for r in rows if r["direct_step_default_zero"]]
        return {
            "python_files": len(rows),
            "files": rows,
            "direct_default_zero_files": risky,
            "requires_manual_clock_review": bool(risky),
        }


def fetch_one(key: str, spec: dict, outdir: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"cr063-{key}-") as td:
        root = Path(td)
        kagglehub.notebook_output_download(spec["handle"], output_dir=str(root), force_download=True)
        arcs = submission_archives(root)
        if not arcs:
            raise RuntimeError(f"no tar.gz with root main.py for {spec['handle']}")
        uniq = {}
        for row in arcs:
            uniq.setdefault(row[2], row)
        if len(uniq) != 1:
            raise RuntimeError(f"ambiguous submission archives for {spec['handle']}: {sorted(uniq)}")
        src, members, ah = next(iter(uniq.values()))
        outdir.mkdir(parents=True, exist_ok=True)
        dst = outdir / spec["out"]
        shutil.copyfile(src, dst)
        return {
            "handle": spec["handle"],
            "archive": dst.name,
            "archive_sha256": ah,
            "archive_bytes": dst.stat().st_size,
            "members": members,
            "audit": source_audit(dst),
            "status": "PASS",
        }


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", required=True); args = ap.parse_args()
    out = Path(args.output_dir)
    report = {
        "schema_version": "cr063-current-public-frontier-refresh-v1",
        "reason": "CR060 hosted ~1k after seat fix; prioritize current artifacts over historical best scores",
        "automatic_kaggle_submission": False,
        "targets": {},
    }
    for key, spec in TARGETS.items():
        try:
            report["targets"][key] = fetch_one(key, spec, out)
        except Exception as exc:
            report["targets"][key] = {"handle": spec["handle"], "status": "ERROR", "error": repr(exc)}
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not any(v.get("status") == "PASS" for v in report["targets"].values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
