"""Resume-safe collector for all replays belonging to Kaggle submissions.

Run on a machine where the official Kaggle CLI is already authenticated.
Requires a recent CLI that supports simulation commands (`kaggle competitions
episodes` / `replay`; Kaggle documents these in current releases).

The collector intentionally downloads sequentially with a configurable delay,
skips existing episodes, and stops on the first replay failure so reruns resume
without creating a burst against Kaggle.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def kaggle_version() -> str:
    p = run(["kaggle", "--version"], check=False)
    text = (p.stdout or p.stderr or "").strip()
    if p.returncode != 0:
        raise SystemExit(
            "Kaggle CLI not available/authenticated. Install/upgrade with: "
            "python -m pip install -U kaggle"
        )
    return text


def parse_episode_ids(csv_text: str) -> list[int]:
    # `-v -q` is the documented CSV/quiet combination.  Be tolerant of an
    # informational line before the CSV header and of future column renames.
    lines = [line for line in csv_text.splitlines() if line.strip()]
    for start in range(len(lines)):
        try:
            rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
        except Exception:
            continue
        if not rows:
            continue
        keys = list(rows[0].keys())
        normalized = {str(k).lower().replace("_", ""): k for k in keys if k}
        candidates = []
        for norm, raw in normalized.items():
            if norm in ("id", "episodeid", "episode") or ("episode" in norm and "id" in norm):
                candidates.append(raw)
        for key in candidates:
            vals = []
            ok = True
            for row in rows:
                value = str(row.get(key, "")).strip()
                if not re.fullmatch(r"\d+", value):
                    ok = False
                    break
                vals.append(int(value))
            if ok and vals:
                return sorted(set(vals))
    raise ValueError(
        "Could not identify episode-id column in Kaggle CSV output. "
        "Raw output was preserved for inspection."
    )


def list_episodes(submission_id: int, raw_path: Path) -> list[int]:
    p = run(
        [
            "kaggle",
            "competitions",
            "episodes",
            str(submission_id),
            "-v",
            "-q",
        ],
        check=False,
    )
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        json.dumps(
            {
                "returncode": p.returncode,
                "stdout": p.stdout,
                "stderr": p.stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"episode listing failed for submission {submission_id}: {p.stderr.strip()}"
        )
    return parse_episode_ids(p.stdout)


def existing_for_episode(folder: Path, episode_id: int) -> Path | None:
    token = str(episode_id)
    for p in folder.glob("*.json"):
        if token in p.name:
            return p
    return None


def download_replay(episode_id: int, folder: Path) -> tuple[bool, str]:
    folder.mkdir(parents=True, exist_ok=True)
    existing = existing_for_episode(folder, episode_id)
    if existing:
        return True, str(existing)
    before = {p.resolve() for p in folder.glob("*.json")}
    p = run(
        [
            "kaggle",
            "competitions",
            "replay",
            str(episode_id),
            "-p",
            str(folder),
            "-q",
        ],
        check=False,
    )
    if p.returncode != 0:
        return False, (p.stderr or p.stdout or "unknown replay error").strip()
    after = {x.resolve() for x in folder.glob("*.json")}
    created = sorted(after - before)
    match = existing_for_episode(folder, episode_id)
    if match:
        return True, str(match)
    if len(created) == 1:
        return True, str(created[0])
    return False, "CLI returned success but replay JSON could not be identified"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--submission",
        action="append",
        required=True,
        help="label:submission_id, e.g. r4b:55784381",
    )
    ap.add_argument("--output-dir", default="artifacts/hosted-cli")
    ap.add_argument("--delay-seconds", type=float, default=2.5)
    ap.add_argument(
        "--max-per-submission",
        type=int,
        default=0,
        help="0 means all listed episodes; useful for a small first probe",
    )
    args = ap.parse_args()

    version = kaggle_version()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "hosted-cli-replay-collector-v1",
        "kaggle_cli_version": version,
        "delay_seconds": args.delay_seconds,
        "submissions": {},
    }

    any_failure = False
    for spec in args.submission:
        label, raw_sid = spec.split(":", 1)
        sid = int(raw_sid)
        raw = root / label / "episodes_command.json"
        try:
            ids = list_episodes(sid, raw)
        except Exception as exc:
            report["submissions"][label] = {
                "submission_id": sid,
                "status": "LIST_FAILED",
                "error": repr(exc),
            }
            any_failure = True
            continue

        selected = ids[: args.max_per_submission] if args.max_per_submission > 0 else ids
        replay_dir = root / label / "replays"
        records = []
        stopped = False
        for idx, eid in enumerate(selected):
            ok, detail = download_replay(eid, replay_dir)
            records.append({"episode_id": eid, "ok": ok, "detail": detail})
            if not ok:
                stopped = True
                any_failure = True
                break
            if idx + 1 < len(selected):
                time.sleep(max(0.0, args.delay_seconds))

        report["submissions"][label] = {
            "submission_id": sid,
            "listed_episode_count": len(ids),
            "selected_episode_count": len(selected),
            "downloaded_or_existing": sum(r["ok"] for r in records),
            "stopped_on_failure": stopped,
            "episode_ids": ids,
            "records": records,
            "status": "PASS" if not stopped and len(records) == len(selected) else "PARTIAL",
        }

    (root / "collector_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps({
        "kaggle_cli_version": version,
        "submissions": {
            k: {x: y for x, y in v.items() if x not in ("episode_ids", "records")}
            for k, v in report["submissions"].items()
        },
    }, indent=2, sort_keys=True))
    if any_failure:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
