"""CR045: map recent current-engine lineages for the 2026-09-06 ~3000 teams.

Observational only. Uses the public Georgy Mamarin episode tables to map the
numeric team/submission IDs behind the frozen CR043 official episodes and asks
whether the same submission emits multiple trajectory hashes. This separates
static-tape strength from genuine state-conditioned policy behavior.
"""
from __future__ import annotations

import json
from pathlib import Path

import kagglehub
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET = "georgymamarin/kaggriculture-episodes"
ENGINE = "1.32.7"
SOURCE_EPISODES = {
    "106275171": 1,
    "106277936": 1,
    "106272405": 0,
    "106269624": 0,
    "106262306": 1,
    "106255661": 1,
    "106257899": 0,
    "106254763": 0,
}


def dl(name: str, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(DATASET, path=name, output_dir=str(root), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def main() -> None:
    root = Path("artifacts/cr045/data")
    ep = pd.read_csv(dl("episodes.csv", root))
    ft = pd.read_csv(dl("episode_features.csv", root))
    sh = pd.read_csv(dl("stream_hashes.csv", root))

    seats = pd.concat([
        ep[["episode_id", "end_time", f"sub_{s}", f"team_{s}", f"rating_{s}"]]
        .rename(columns={f"sub_{s}": "submission_id", f"team_{s}": "team_id", f"rating_{s}": "rating"})
        .assign(seat=s)
        for s in (0, 1)
    ], ignore_index=True)
    eng = ft[["episode_id", "seat", "engine_version"]].copy()
    for d in (seats, eng, sh):
        d["episode_id"] = norm(d["episode_id"])
        d["seat"] = pd.to_numeric(d["seat"], errors="coerce").astype("Int64")
    seats["submission_id"] = norm(seats["submission_id"])
    seats["team_id"] = norm(seats["team_id"])
    seats["rating"] = pd.to_numeric(seats["rating"], errors="coerce")
    seats["end_time"] = pd.to_datetime(seats["end_time"], utc=True, errors="coerce")
    eng["engine_version"] = eng["engine_version"].astype(str)

    x = seats.merge(eng, on=["episode_id", "seat"]).merge(sh, on=["episode_id", "seat"], how="left")
    x = x[(x.engine_version == ENGINE) & x.rating.notna() & x.end_time.notna()].copy()
    anchor = x.end_time.max()

    source_rows = []
    for eid, seat in SOURCE_EPISODES.items():
        q = x[(x.episode_id == eid) & (x.seat == seat)]
        if q.empty:
            source_rows.append({"episode_id": eid, "seat": seat, "missing": True})
            continue
        z = q.iloc[0]
        source_rows.append({
            "episode_id": eid,
            "seat": seat,
            "team_id": str(z.team_id),
            "submission_id": str(z.submission_id),
            "rating": float(z.rating),
            "end_time": z.end_time.isoformat(),
            **{c: str(z[c]) for c in ("stream_h24", "stream_h100", "stream_h200", "stream_h400", "stream_h719") if c in z.index and pd.notna(z[c])},
        })

    target_team_ids = sorted({r["team_id"] for r in source_rows if r.get("team_id")})
    window = x[(x.end_time >= anchor - pd.Timedelta(days=7)) & x.team_id.isin(target_team_ids)].copy()
    teams = {}
    for team_id in target_team_ids:
        q = window[window.team_id == team_id].copy()
        subs = []
        for sid, g in q.groupby("submission_id"):
            g = g.sort_values("end_time")
            subs.append({
                "submission_id": str(sid),
                "games": int(len(g)),
                "mean_rating": float(g.rating.mean()),
                "max_rating": float(g.rating.max()),
                "min_rating": float(g.rating.min()),
                "unique_h24": int(g.stream_h24.nunique(dropna=True)) if "stream_h24" in g else None,
                "unique_h100": int(g.stream_h100.nunique(dropna=True)) if "stream_h100" in g else None,
                "unique_h200": int(g.stream_h200.nunique(dropna=True)) if "stream_h200" in g else None,
                "unique_h400": int(g.stream_h400.nunique(dropna=True)) if "stream_h400" in g else None,
                "unique_h719": int(g.stream_h719.nunique(dropna=True)) if "stream_h719" in g else None,
                "latest_end_time": g.end_time.max().isoformat(),
                "representatives": [
                    {
                        "episode_id": str(r.episode_id),
                        "seat": int(r.seat),
                        "rating": float(r.rating),
                        "h24": str(r.stream_h24) if "stream_h24" in r and pd.notna(r.stream_h24) else None,
                        "h200": str(r.stream_h200) if "stream_h200" in r and pd.notna(r.stream_h200) else None,
                        "h719": str(r.stream_h719) if "stream_h719" in r and pd.notna(r.stream_h719) else None,
                    }
                    for _, r in g.sort_values("rating", ascending=False).head(5).iterrows()
                ],
            })
        subs.sort(key=lambda r: (r["max_rating"], r["games"]), reverse=True)
        teams[team_id] = {
            "games_7d": int(len(q)),
            "unique_submissions_7d": int(q.submission_id.nunique()),
            "mean_rating_7d": float(q.rating.mean()) if len(q) else None,
            "max_rating_7d": float(q.rating.max()) if len(q) else None,
            "same_submission_multi_h719": sum(1 for s in subs if (s["unique_h719"] or 0) > 1),
            "same_submission_multi_h200": sum(1 for s in subs if (s["unique_h200"] or 0) > 1),
            "top_submissions": subs[:20],
        }

    out = {
        "experiment": "CR045_TOP3000_LINEAGE_MAP_V1",
        "engine_version": ENGINE,
        "dataset_anchor": anchor.isoformat(),
        "window_days": 7,
        "source_rows": source_rows,
        "target_team_ids": target_team_ids,
        "teams": teams,
        "observational_only": True,
        "runtime_identity_features": False,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    p = Path("artifacts/cr045/report.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    compact = {
        "dataset_anchor": out["dataset_anchor"],
        "source_rows": source_rows,
        "teams": {
            tid: {k: v for k, v in t.items() if k != "top_submissions"}
            | {"top_submissions": [{k: s[k] for k in ("submission_id", "games", "max_rating", "unique_h24", "unique_h200", "unique_h719")} for s in t["top_submissions"][:5]]}
            for tid, t in teams.items()
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
