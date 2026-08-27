"""Fetch exact user-supplied Kaggriculture hosted episode IDs from official daily datasets.

This is provenance/forensics only. It searches a bounded date window for the
known episode IDs, downloads the exact public replay JSONs, and records any
submission/team/agent identifiers exposed by the replay metadata.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

import kagglehub


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def identity_bits(rep: dict) -> dict:
    interesting_tokens = ("submission", "team", "agent", "seed", "episode")

    def filt(d):
        out = {}
        if not isinstance(d, dict):
            return out
        for k, v in d.items():
            kl = str(k).lower()
            if any(tok in kl for tok in interesting_tokens):
                if isinstance(v, (str, int, float, bool, type(None))):
                    out[str(k)] = v
                elif isinstance(v, list) and len(v) <= 50:
                    out[str(k)] = v
        return out

    steps = rep.get("steps") or []
    first_obs = {}
    if steps and isinstance(steps[0], list) and steps[0]:
        fr = steps[0][0]
        if isinstance(fr, dict) and isinstance(fr.get("observation"), dict):
            first_obs = fr["observation"]
    return {
        "top_level": filt(rep),
        "info": filt(rep.get("info")),
        "configuration": filt(rep.get("configuration")),
        "first_observation": filt(first_obs),
        "team_names": (rep.get("info") or {}).get("TeamNames") or (rep.get("info") or {}).get("teamNames"),
        "top_level_keys": sorted(map(str, rep.keys())),
        "info_keys": sorted(map(str, (rep.get("info") or {}).keys())) if isinstance(rep.get("info"), dict) else [],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", action="append", required=True, help="label:episode_id")
    ap.add_argument("--end-date", default="2026-08-27")
    ap.add_argument("--lookback-days", type=int, default=4)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    targets = {}
    for spec in args.episode:
        label, eid = spec.split(":", 1)
        targets[eid] = label

    root = Path(args.output_dir)
    end = date.fromisoformat(args.end_date)
    found = {}
    searched = []
    for offset in range(args.lookback_days):
        d = (end - timedelta(days=offset)).isoformat()
        handle = f"kaggle/kaggriculture-episodes-{d}"
        try:
            manifest_path = download(handle, "manifest.csv", root / "downloads" / d / "manifest")
            rows = read_csv(manifest_path)
        except Exception as exc:
            searched.append({"date": d, "status": "unavailable", "error": repr(exc)})
            continue
        ids = {str(r.get("episode_id")): r for r in rows}
        matched = []
        for eid, label in targets.items():
            if eid in ids and eid not in found:
                p = download(handle, f"{eid}.json", root / "downloads" / d / eid)
                rep = json.loads(p.read_text(encoding="utf-8"))
                out = root / "replays" / f"{label}_{eid}.json"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(rep), encoding="utf-8")
                found[eid] = {
                    "label": label,
                    "episode_id": eid,
                    "date": d,
                    "manifest_row": ids[eid],
                    "replay_path": str(out),
                    "identity": identity_bits(rep),
                    "step_count": len(rep.get("steps") or []),
                }
                matched.append(eid)
        searched.append({"date": d, "status": "ok", "manifest_count": len(rows), "matched": matched})
        if len(found) == len(targets):
            break

    missing = [eid for eid in targets if eid not in found]
    report = {
        "schema_version": "known-hosted-replay-fetch-v1",
        "targets": targets,
        "found": found,
        "missing": missing,
        "searched": searched,
        "status": "PASS" if not missing else "PARTIAL",
    }
    (root / "fetch_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if missing:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
