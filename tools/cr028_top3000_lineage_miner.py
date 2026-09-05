"""CR028 Phase 0: identify dominant public action-stream lineages in rating>=3000.

Research/evaluation only.  Runtime agents never receive team/rating/lineage identity.
The public Kaggriculture Episodes dataset already contains canonical stream hashes;
we use them only to choose development backbones before any candidate is frozen.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import kagglehub
import pandas as pd

DATASET = "georgymamarin/kaggriculture-episodes"


def download(filename: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(DATASET, path=filename, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(f"missing {DATASET}:{filename}: {p}")
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--rating-min", type=float, default=3000.0)
    args = ap.parse_args()

    work = Path("artifacts/cr028_lineage/data")
    ep_path = download("episodes.csv", work)
    sh_path = download("stream_hashes.csv", work)
    ep = pd.read_csv(ep_path)
    sh = pd.read_csv(sh_path)

    required_ep = {"episode_id", "team_0", "team_1", "rating_0", "rating_1"}
    required_sh = {"episode_id", "seat", "stream_h200"}
    if not required_ep.issubset(ep.columns):
        raise RuntimeError(f"episodes.csv missing {sorted(required_ep-set(ep.columns))}; columns={list(ep.columns)}")
    if not required_sh.issubset(sh.columns):
        raise RuntimeError(f"stream_hashes.csv missing {sorted(required_sh-set(sh.columns))}; columns={list(sh.columns)}")

    seats = pd.concat([
        ep[["episode_id", f"team_{s}", f"rating_{s}"]]
          .rename(columns={f"team_{s}": "team", f"rating_{s}": "rating"})
          .assign(seat=s)
        for s in (0, 1)
    ], ignore_index=True)
    seats["episode_id"] = seats["episode_id"].astype(str)
    sh["episode_id"] = sh["episode_id"].astype(str)
    sh["seat"] = pd.to_numeric(sh["seat"], errors="coerce").astype("Int64")
    seats["seat"] = seats["seat"].astype("Int64")
    seats["rating"] = pd.to_numeric(seats["rating"], errors="coerce")

    top = sh.merge(seats, on=["episode_id", "seat"], how="inner")
    top = top[top["rating"] >= float(args.rating_min)].copy()
    top = top[top["stream_h200"].notna()].copy()
    if top.empty:
        raise RuntimeError("no rating-band rows after merge")

    group = (top.groupby("stream_h200", dropna=False)
             .agg(seat_games=("episode_id", "size"),
                  unique_teams=("team", "nunique"),
                  mean_rating=("rating", "mean"),
                  max_rating=("rating", "max"))
             .reset_index()
             .sort_values(["seat_games", "unique_teams", "mean_rating"], ascending=False))

    ranked = []
    representatives = []
    suffix_cols = [c for c in ("stream_h400", "stream_h719") if c in top.columns]
    for rank, row in enumerate(group.head(20).itertuples(index=False), start=1):
        lineage = str(row.stream_h200)
        members = top[top["stream_h200"].astype(str) == lineage].copy().sort_values("rating", ascending=False)
        item = {
            "rank": rank,
            "stream_h200": lineage,
            "seat_games": int(row.seat_games),
            "unique_teams": int(row.unique_teams),
            "mean_rating": float(row.mean_rating),
            "max_rating": float(row.max_rating),
            "suffix_diversity": {c: int(members[c].nunique(dropna=True)) for c in suffix_cols},
            "top_members": [],
        }
        for _, m in members.head(12).iterrows():
            rec = {
                "episode_id": str(m["episode_id"]),
                "seat": int(m["seat"]),
                "team": str(m["team"]),
                "rating": float(m["rating"]),
            }
            for c in ("stream_h24", "stream_h100", "stream_h200", "stream_h400", "stream_h719"):
                if c in m.index and pd.notna(m[c]):
                    rec[c] = str(m[c])
            item["top_members"].append(rec)
        ranked.append(item)

    dominant = ranked[0]
    dom = top[top["stream_h200"].astype(str) == dominant["stream_h200"]].copy()
    # Choose representatives by distinct full/suffix lineage where available, highest rating first.
    dedupe_col = "stream_h719" if "stream_h719" in dom.columns else ("stream_h400" if "stream_h400" in dom.columns else None)
    dom = dom.sort_values("rating", ascending=False)
    if dedupe_col:
        dom = dom.drop_duplicates(subset=[dedupe_col], keep="first")
    for _, m in dom.head(8).iterrows():
        rec = {"episode_id": str(m["episode_id"]), "seat": int(m["seat"]), "team": str(m["team"]), "rating": float(m["rating"])}
        for c in ("stream_h24", "stream_h100", "stream_h200", "stream_h400", "stream_h719"):
            if c in m.index and pd.notna(m[c]):
                rec[c] = str(m[c])
        representatives.append(rec)

    shared_rows = int(sum(x["seat_games"] for x in ranked if x["unique_teams"] >= 2))
    result = {
        "experiment": "CR028_TOP3000_LINEAGE_PHASE0",
        "dataset": DATASET,
        "rating_min": float(args.rating_min),
        "dataset_rows": {"episodes": int(len(ep)), "stream_hashes": int(len(sh)), "rating_band_hashed_seats": int(len(top))},
        "dominant": dominant,
        "dominant_share": float(dominant["seat_games"] / len(top)),
        "top20_shared_lineage_rows": shared_rows,
        "representatives_for_next_stage": representatives,
        "ranked_lineages": ranked,
        "selection_only": True,
        "runtime_identity_features": False,
        "held_out_touched": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "ranked_lineages"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
