"""Resilient authenticated Kaggle hosted-replay collector.

Compared with v1, transient replay failures are retried with exponential backoff
and an exhausted episode does not prevent later episodes from being collected.
The final report records every attempt/failure and exits non-zero only after the
full requested corpus has been attempted.

Selection policy is explicit. When a capped sample is requested, callers may use
--selection oldest or --selection newest. This prevents accidentally treating the
oldest episodes of a long-lived submission as the current meta.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import time
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def kaggle_version() -> str:
    p = run(["kaggle", "--version"])
    text = (p.stdout or p.stderr or "").strip()
    if p.returncode != 0:
        raise SystemExit("Kaggle CLI unavailable/authentication setup failed")
    return text


def parse_episode_ids(csv_text: str) -> list[int]:
    lines = [line for line in csv_text.splitlines() if line.strip()]
    for start in range(len(lines)):
        rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
        if not rows:
            continue
        normalized = {str(k).lower().replace("_", ""): k for k in rows[0] if k}
        for norm, key in normalized.items():
            if norm not in ("id", "episodeid", "episode") and not ("episode" in norm and "id" in norm):
                continue
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
    raise ValueError("Could not identify episode-id column")


def list_episodes(submission_id: int, raw_path: Path) -> list[int]:
    p = run(["kaggle", "competitions", "episodes", str(submission_id), "-v", "-q"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps({"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}, indent=2), encoding="utf-8")
    if p.returncode != 0:
        raise RuntimeError(f"episode listing failed: {(p.stderr or p.stdout).strip()}")
    return parse_episode_ids(p.stdout)


def existing_for_episode(folder: Path, episode_id: int) -> Path | None:
    token = str(episode_id)
    return next((p for p in folder.glob("*.json") if token in p.name), None)


def replay_once(episode_id: int, folder: Path) -> tuple[bool, str]:
    folder.mkdir(parents=True, exist_ok=True)
    existing = existing_for_episode(folder, episode_id)
    if existing:
        return True, str(existing)
    before = {p.resolve() for p in folder.glob("*.json")}
    p = run(["kaggle", "competitions", "replay", str(episode_id), "-p", str(folder), "-q"])
    if p.returncode != 0:
        return False, (p.stderr or p.stdout or "unknown replay error").strip()
    after = {x.resolve() for x in folder.glob("*.json")}
    match = existing_for_episode(folder, episode_id)
    if match:
        return True, str(match)
    created = sorted(after - before)
    if len(created) == 1:
        return True, str(created[0])
    return False, "CLI returned success but replay JSON could not be identified"


def download_with_retries(episode_id: int, folder: Path, retries: int, backoff: float) -> tuple[bool, str, list[dict]]:
    attempts = []
    for attempt in range(1, retries + 1):
        ok, detail = replay_once(episode_id, folder)
        attempts.append({"attempt": attempt, "ok": ok, "detail": detail})
        if ok:
            return True, detail, attempts
        if attempt < retries:
            time.sleep(backoff * (2 ** (attempt - 1)))
    return False, attempts[-1]["detail"], attempts


def select_episode_ids(ids: list[int], max_count: int, selection: str) -> list[int]:
    if max_count <= 0 or max_count >= len(ids):
        return list(ids)
    if selection == "newest":
        # Episode ids increase monotonically enough for Kaggriculture public
        # episodes to serve as a robust recency ordering. Keep ascending order
        # inside the selected window for deterministic processing.
        return ids[-max_count:]
    if selection == "oldest":
        return ids[:max_count]
    raise ValueError(f"unknown selection policy: {selection}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", action="append", required=True, help="label:submission_id")
    ap.add_argument("--output-dir", default="artifacts/hosted-authenticated-v2")
    ap.add_argument("--delay-seconds", type=float, default=0.5)
    ap.add_argument("--max-per-submission", type=int, default=0)
    ap.add_argument("--selection", choices=("oldest", "newest"), default="oldest")
    ap.add_argument("--retries", type=int, default=6)
    ap.add_argument("--retry-backoff-seconds", type=float, default=1.0)
    args = ap.parse_args()

    version = kaggle_version()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "hosted-cli-replay-collector-v2",
        "kaggle_cli_version": version,
        "selection": args.selection,
        "submissions": {},
    }
    total_failures = 0

    for spec in args.submission:
        label, raw_sid = spec.split(":", 1)
        sid = int(raw_sid)
        try:
            ids = list_episodes(sid, root / label / "episodes_command.json")
        except Exception as exc:
            report["submissions"][label] = {"submission_id": sid, "status": "LIST_FAILED", "error": repr(exc)}
            total_failures += 1
            continue
        selected = select_episode_ids(ids, args.max_per_submission, args.selection)
        replay_dir = root / label / "replays"
        records = []
        for idx, eid in enumerate(selected):
            ok, detail, attempts = download_with_retries(eid, replay_dir, max(1, args.retries), max(0.0, args.retry_backoff_seconds))
            records.append({"episode_id": eid, "ok": ok, "detail": detail, "attempts": attempts})
            if not ok:
                total_failures += 1
            if idx + 1 < len(selected):
                time.sleep(max(0.0, args.delay_seconds))
            if (idx + 1) % 20 == 0 or idx + 1 == len(selected):
                print(json.dumps({"label": label, "attempted": idx + 1, "total": len(selected), "ok": sum(r["ok"] for r in records), "failed": sum(not r["ok"] for r in records)}), flush=True)
        report["submissions"][label] = {
            "submission_id": sid,
            "listed_episode_count": len(ids),
            "selected_episode_count": len(selected),
            "selected_min_episode_id": min(selected) if selected else None,
            "selected_max_episode_id": max(selected) if selected else None,
            "selection": args.selection,
            "downloaded_or_existing": sum(r["ok"] for r in records),
            "failed_episode_count": sum(not r["ok"] for r in records),
            "episode_ids": ids,
            "selected_episode_ids": selected,
            "records": records,
            "status": "PASS" if all(r["ok"] for r in records) and len(records) == len(selected) else "PARTIAL",
        }

    (root / "collector_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: {x: y for x, y in v.items() if x not in ("episode_ids", "selected_episode_ids", "records")} for k, v in report["submissions"].items()}, indent=2, sort_keys=True))
    if total_failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
