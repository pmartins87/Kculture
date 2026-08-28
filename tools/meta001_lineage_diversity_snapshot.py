"""META-001: summarize current Kaggriculture ladder diversity by action lineage.

Evaluation infrastructure only. Downloads three small public metadata tables
from georgymamarin/kaggriculture-episodes instead of the full ~5 GB replay
corpus. Lineage labels are never runtime agent inputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import kagglehub
import pandas as pd

HANDLE = "georgymamarin/kaggriculture-episodes"
FILES = ("episodes.csv", "stream_hashes.csv", "episode_features.csv")


def download(name: str, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return Path(kagglehub.dataset_download(HANDLE, path=name, output_dir=str(root), force_download=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--data-dir", default="artifacts/meta001/data")
    args = ap.parse_args()
    root = Path(args.data_dir)
    paths = {name: download(name, root) for name in FILES}
    ep = pd.read_csv(paths["episodes.csv"])
    sh = pd.read_csv(paths["stream_hashes.csv"])
    ef = pd.read_csv(paths["episode_features.csv"])

    required_ep = {"episode_id", "team_0", "team_1", "rating_0", "rating_1"}
    required_sh = {"episode_id", "seat", "stream_h200"}
    missing = {
        "episodes": sorted(required_ep - set(ep.columns)),
        "stream_hashes": sorted(required_sh - set(sh.columns)),
    }

    report = {
        "experiment": "META-001-lineage-diversity-snapshot",
        "source": HANDLE,
        "files": {k: {"rows": int(len(pd.read_csv(v, nrows=10000000))), "path": str(v)} for k, v in paths.items()},
        "columns": {
            "episodes": list(ep.columns),
            "stream_hashes": list(sh.columns),
            "episode_features": list(ef.columns),
        },
        "missing_required_columns": missing,
    }

    if any(missing.values()):
        report["status"] = "SCHEMA_MISMATCH"
    else:
        seats = pd.concat(
            [
                ep[["episode_id", f"team_{s}", f"rating_{s}"]]
                .set_axis(["episode_id", "team", "rating"], axis=1)
                .assign(seat=s)
                for s in (0, 1)
            ],
            ignore_index=True,
        )
        merged = sh.merge(seats, on=["episode_id", "seat"], how="left")
        # Attach engine version if the public table exposes compatible keys.
        engine_col = next((c for c in ("engine_version", "module_version", "kaggle_environments_version") if c in ef.columns), None)
        if engine_col and {"episode_id", "seat"}.issubset(ef.columns):
            merged = merged.merge(ef[["episode_id", "seat", engine_col]], on=["episode_id", "seat"], how="left")

        top = merged[pd.to_numeric(merged["rating"], errors="coerce") >= 3000].copy()
        top = top[top["stream_h200"].notna() & (top["stream_h200"].astype(str) != "")]
        groups = (
            top.groupby("stream_h200", dropna=False)
            .agg(seat_games=("episode_id", "size"), teams=("team", "nunique"), mean_rating=("rating", "mean"), max_rating=("rating", "max"))
            .reset_index()
            .sort_values(["seat_games", "teams", "max_rating"], ascending=False)
        )
        shared_mask = groups["teams"] >= 2
        shared_hashes = set(groups.loc[shared_mask, "stream_h200"].astype(str))
        seat_shared = top["stream_h200"].astype(str).isin(shared_hashes)

        report.update({
            "status": "PASS",
            "rating_threshold": 3000,
            "top_hashed_seat_games": int(len(top)),
            "top_unique_teams": int(top["team"].nunique()),
            "h200_unique_lineages": int(top["stream_h200"].nunique()),
            "h200_shared_lineages": int(shared_mask.sum()),
            "h200_seat_games_in_shared_lineages": int(seat_shared.sum()),
            "h200_share_in_shared_lineages": float(seat_shared.mean()) if len(top) else None,
            "largest_h200_lineages": groups.head(25).to_dict(orient="records"),
            "engine_version_column": engine_col,
        })
        if engine_col:
            report["top_by_engine_version"] = (
                top.groupby(engine_col, dropna=False)
                .agg(seat_games=("episode_id", "size"), teams=("team", "nunique"), lineages=("stream_h200", "nunique"), mean_rating=("rating", "mean"), max_rating=("rating", "max"))
                .reset_index()
                .to_dict(orient="records")
            )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
