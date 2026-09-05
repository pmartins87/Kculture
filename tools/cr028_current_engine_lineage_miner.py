"""CR028 Phase 0b: mine rating>=3000 lineages on engine 1.32.7 only.

The public population dataset spans multiple Kaggriculture engine versions.  This
script joins per-seat engine_version from episode_features.csv before any lineage
selection so pre-patch high-rating policies cannot contaminate current candidates.
Runtime agents never receive rating/team/hash/version identity features.
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


def norm_id(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    ap.add_argument("--rating-min",type=float,default=3000.0)
    ap.add_argument("--engine",default="1.32.7")
    args=ap.parse_args()

    work=Path("artifacts/cr028_current/data")
    ep=pd.read_csv(download("episodes.csv",work))
    sh=pd.read_csv(download("stream_hashes.csv",work))
    ft=pd.read_csv(download("episode_features.csv",work))

    schema={"episodes":list(ep.columns),"stream_hashes":list(sh.columns),"episode_features":list(ft.columns)}
    required_ep={"episode_id","team_0","team_1","rating_0","rating_1"}
    required_sh={"episode_id","seat","stream_h200"}
    if not required_ep.issubset(ep.columns) or not required_sh.issubset(sh.columns):
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps({"status":"SCHEMA_FAIL","schema":schema},indent=2),encoding="utf-8")
        raise RuntimeError("base dataset schema changed")

    # Georgy's dataset documents engine_version per seat.  Support either a long
    # seat table or a one-row-per-episode wide layout without guessing values.
    if {"episode_id","seat","engine_version"}.issubset(ft.columns):
        eng=ft[["episode_id","seat","engine_version"]].copy()
    elif {"episode_id","engine_version_0","engine_version_1"}.issubset(ft.columns):
        eng=pd.concat([
            ft[["episode_id",f"engine_version_{s}"]].rename(columns={f"engine_version_{s}":"engine_version"}).assign(seat=s)
            for s in (0,1)
        ],ignore_index=True)
    elif {"episode_id","engine_version"}.issubset(ft.columns):
        # Episode-wide engine version is also unambiguous because both seats share engine.
        eng=pd.concat([ft[["episode_id","engine_version"]].assign(seat=s) for s in (0,1)],ignore_index=True)
    else:
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps({"status":"ENGINE_SCHEMA_FAIL","schema":schema},indent=2),encoding="utf-8")
        raise RuntimeError(f"episode_features lacks engine_version key; columns={list(ft.columns)}")

    seats=pd.concat([
        ep[["episode_id",f"team_{s}",f"rating_{s}"]]
          .rename(columns={f"team_{s}":"team",f"rating_{s}":"rating"}).assign(seat=s)
        for s in (0,1)
    ],ignore_index=True)
    for df in (seats,sh,eng):
        df["episode_id"]=norm_id(df["episode_id"])
        df["seat"]=pd.to_numeric(df["seat"],errors="coerce").astype("Int64")
    seats["rating"]=pd.to_numeric(seats["rating"],errors="coerce")
    eng["engine_version"]=eng["engine_version"].astype(str)

    merged=sh.merge(seats,on=["episode_id","seat"],how="inner").merge(eng,on=["episode_id","seat"],how="inner")
    band=merged[(merged["rating"]>=float(args.rating_min)) & (merged["engine_version"]==str(args.engine)) & merged["stream_h200"].notna()].copy()

    base={
        "experiment":"CR028_TOP3000_CURRENT_ENGINE_PHASE0B",
        "dataset":DATASET,
        "rating_min":float(args.rating_min),
        "engine_version":str(args.engine),
        "dataset_rows":{"episodes":int(len(ep)),"stream_hashes":int(len(sh)),"episode_features":int(len(ft)),"merged_seats":int(len(merged)),"filtered_seats":int(len(band))},
        "schema":schema,
        "runtime_identity_features":False,
        "held_out_touched":False,
    }
    if band.empty:
        base.update(status="NO_CURRENT_ENGINE_TOP3000_ROWS",ranked_lineages=[],representatives_for_next_stage=[])
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(base,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(base,indent=2,sort_keys=True));return

    group=(band.groupby("stream_h200")
           .agg(seat_games=("episode_id","size"),unique_teams=("team","nunique"),mean_rating=("rating","mean"),max_rating=("rating","max"))
           .reset_index().sort_values(["seat_games","unique_teams","mean_rating"],ascending=False))
    suffix_cols=[c for c in ("stream_h400","stream_h719") if c in band.columns]
    ranked=[]
    for rank,row in enumerate(group.head(20).itertuples(index=False),start=1):
        lineage=str(row.stream_h200)
        members=band[band["stream_h200"].astype(str)==lineage].copy().sort_values("rating",ascending=False)
        item={
            "rank":rank,"stream_h200":lineage,"seat_games":int(row.seat_games),"unique_teams":int(row.unique_teams),
            "mean_rating":float(row.mean_rating),"max_rating":float(row.max_rating),
            "suffix_diversity":{c:int(members[c].nunique(dropna=True)) for c in suffix_cols},"top_members":[]}
        for _,m in members.head(12).iterrows():
            rec={"episode_id":str(m["episode_id"]),"seat":int(m["seat"]),"team":str(m["team"]),"rating":float(m["rating"]),"engine_version":str(m["engine_version"])}
            for c in ("stream_h24","stream_h100","stream_h200","stream_h400","stream_h719"):
                if c in m.index and pd.notna(m[c]): rec[c]=str(m[c])
            item["top_members"].append(rec)
        ranked.append(item)

    dominant=ranked[0]
    dom=band[band["stream_h200"].astype(str)==dominant["stream_h200"]].sort_values("rating",ascending=False).copy()
    dedupe="stream_h719" if "stream_h719" in dom.columns else ("stream_h400" if "stream_h400" in dom.columns else None)
    if dedupe: dom=dom.drop_duplicates(subset=[dedupe],keep="first")
    reps=[]
    for _,m in dom.head(8).iterrows():
        rec={"episode_id":str(m["episode_id"]),"seat":int(m["seat"]),"team":str(m["team"]),"rating":float(m["rating"]),"engine_version":str(m["engine_version"])}
        for c in ("stream_h24","stream_h100","stream_h200","stream_h400","stream_h719"):
            if c in m.index and pd.notna(m[c]):rec[c]=str(m[c])
        reps.append(rec)

    base.update(
        status="OK",dominant=dominant,dominant_share=float(dominant["seat_games"]/len(band)),
        representatives_for_next_stage=reps,ranked_lineages=ranked,selection_only=True)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(base,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({k:v for k,v in base.items() if k not in ("schema","ranked_lineages")},indent=2,sort_keys=True))


if __name__=="__main__":main()
