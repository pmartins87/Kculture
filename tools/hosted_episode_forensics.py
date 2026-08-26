"""Prize-first hosted ladder forensics for Kaggriculture.

Uses the official public Episodes Index/day dataset through kagglehub. The goal
is to understand what metadata is available for locating our hosted games and
to preserve enough sanitized episode metadata to reconcile live behavior with
our exact submitted package.

This is observational only. It never touches validation or held-out seeds.
"""
from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path

import kagglehub

INDEX_HANDLE = "kaggle/kaggriculture-episodes-index"


def download(handle: str, filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {handle}:{filename}: {p}")
    return p


def rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def safe_metadata(rep: dict) -> dict:
    info = rep.get("info") if isinstance(rep.get("info"), dict) else {}
    cfg = rep.get("configuration") if isinstance(rep.get("configuration"), dict) else {}
    steps = rep.get("steps") if isinstance(rep.get("steps"), list) else []
    first = steps[0][0] if steps and isinstance(steps[0], list) and steps[0] else {}
    obs0 = first.get("observation") if isinstance(first, dict) and isinstance(first.get("observation"), dict) else {}

    # Capture only small scalar/list metadata. Public episodes may expose agent,
    # submission or seed identifiers under different keys across versions.
    interesting = {
        "episodeId", "episode_id", "seed", "randomSeed", "submissionId",
        "submission_id", "TeamNames", "teamNames", "agentIds", "agents",
    }
    def filt(d: dict) -> dict:
        out = {}
        for k, v in d.items():
            if k in interesting or any(tok in str(k).lower() for tok in ("seed", "team", "agent", "submission")):
                if isinstance(v, (str, int, float, bool, type(None))):
                    out[str(k)] = v
                elif isinstance(v, list) and len(v) <= 20:
                    out[str(k)] = v
        return out

    return {
        "top_level_keys": sorted(map(str, rep.keys())),
        "info": filt(info),
        "configuration": filt(cfg),
        "initial_observation": filt(obs0),
        "team_names": info.get("TeamNames") or info.get("teamNames"),
        "step_count": len(steps),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--sample", type=int, default=3)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kculture-hosted-forensics-") as tmp:
        root = Path(tmp)
        idx = sorted(rows(download(INDEX_HANDLE, "manifest.csv", root / "index")), key=lambda r: r["date"])
        if not idx:
            raise RuntimeError("episodes index empty")
        date = args.date or idx[-1]["date"]
        idx_row = next(r for r in idx if r["date"] == date)
        day_handle = f"kaggle/kaggriculture-episodes-{date}"
        day_rows = rows(download(day_handle, "manifest.csv", root / "day"))
        if not day_rows:
            raise RuntimeError("day manifest empty")

        # Select highest-Elo episodes only for metadata probing. No strategic
        # conclusion is drawn from this small sample.
        selected = sorted(day_rows, key=lambda r: -float(r.get("avg_score") or 0))[: max(1, args.sample)]
        episodes = []
        for r in selected:
            eid = str(r["episode_id"])
            p = download(day_handle, f"{eid}.json", root / "episodes" / eid)
            rep = json.loads(p.read_text(encoding="utf-8"))
            episodes.append({
                "manifest_row": r,
                "metadata": safe_metadata(rep),
            })

        report = {
            "schema_version": "hosted-episode-forensics-v1",
            "date": date,
            "index_row": idx_row,
            "day_manifest_columns": sorted(day_rows[0].keys()),
            "day_manifest_count": len(day_rows),
            "sampled_episodes": episodes,
            "locatability": {
                "manifest_has_identity_fields": [k for k in day_rows[0].keys() if any(t in k.lower() for t in ("team", "agent", "submission"))],
                "note": "If identity fields are absent from the manifest, locate our episodes using submission/team metadata from episode JSON or user-provided Episodes link/ID.",
            },
        }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
