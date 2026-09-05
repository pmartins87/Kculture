"""CR028: characterize the public rating frontier on Kaggriculture engine 1.32.7.

This avoids comparing post-patch agents to historical pre-patch 3000+ ratings.
Research metadata only; no team/rating/hash identity is exposed to runtime agents.
"""
from __future__ import annotations

import json
from pathlib import Path

import kagglehub
import pandas as pd

DATASET = "georgymamarin/kaggriculture-episodes"
ENGINE = "1.32.7"


def dl(name: str, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(DATASET, path=name, output_dir=str(root), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def norm_id(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True)


def main() -> None:
    root=Path("artifacts/cr028_frontier/data")
    ep=pd.read_csv(dl("episodes.csv",root))
    sh=pd.read_csv(dl("stream_hashes.csv",root))
    ft=pd.read_csv(dl("episode_features.csv",root))

    seats=pd.concat([
        ep[["episode_id",f"sub_{s}",f"team_{s}",f"rating_{s}","end_time"]]
          .rename(columns={f"sub_{s}":"submission_id",f"team_{s}":"team",f"rating_{s}":"rating"})
          .assign(seat=s)
        for s in (0,1)
    ],ignore_index=True)
    eng=ft[["episode_id","seat","engine_version"]].copy()
    for d in (seats,sh,eng):
        d["episode_id"]=norm_id(d["episode_id"])
        d["seat"]=pd.to_numeric(d["seat"],errors="coerce").astype("Int64")
    seats["rating"]=pd.to_numeric(seats["rating"],errors="coerce")
    seats["submission_id"]=norm_id(seats["submission_id"])
    eng["engine_version"]=eng["engine_version"].astype(str)

    x=seats.merge(eng,on=["episode_id","seat"],how="inner").merge(sh,on=["episode_id","seat"],how="left")
    x=x[(x["engine_version"]==ENGINE)&x["rating"].notna()].copy()
    if x.empty: raise RuntimeError("no current-engine rated seats")
    x=x.sort_values(["rating","end_time"],ascending=[False,False])

    thresholds={str(t):int((x["rating"]>=t).sum()) for t in (3000,2950,2900,2850,2800,2750,2700,2600,2500)}
    qs={str(q):float(x["rating"].quantile(q)) for q in (0.90,0.95,0.975,0.99,0.995,0.999)}

    # One representative per submission prevents a single prolific submission
    # from occupying the entire frontier table.
    subs=x.drop_duplicates("submission_id",keep="first").copy()
    top_subs=[]
    for _,r in subs.head(50).iterrows():
        top_subs.append({
            "episode_id":str(r["episode_id"]),"seat":int(r["seat"]),"submission_id":str(r["submission_id"]),
            "team":str(r["team"]),"rating":float(r["rating"]),"end_time":str(r["end_time"]),
            **{c:str(r[c]) for c in ("stream_h24","stream_h48","stream_h100","stream_h136","stream_h200","stream_h300","stream_h400","stream_h719") if c in r.index and pd.notna(r[c])}
        })

    # Analyze lineages within robust frontier cohorts.  Prefer top unique
    # submissions rather than arbitrary historical threshold when population is sparse.
    lineage_views={}
    for k in (20,50,100,250):
        cohort=subs.head(k)
        if cohort.empty: continue
        for hcol in ("stream_h24","stream_h100","stream_h200"):
            if hcol not in cohort.columns: continue
            g=(cohort[cohort[hcol].notna()].groupby(hcol)
               .agg(submissions=("submission_id","nunique"),teams=("team","nunique"),mean_rating=("rating","mean"),max_rating=("rating","max"))
               .reset_index().sort_values(["submissions","mean_rating"],ascending=False).head(10))
            lineage_views[f"top{k}_{hcol}"]=[{
                hcol:str(r[hcol]),"submissions":int(r["submissions"]),"teams":int(r["teams"]),
                "mean_rating":float(r["mean_rating"]),"max_rating":float(r["max_rating"])} for _,r in g.iterrows()]

    # Current/latest observation per submission, separately from peak observation.
    latest=(x.sort_values("end_time",ascending=False).drop_duplicates("submission_id",keep="first")
            .sort_values("rating",ascending=False))
    top_latest=[]
    for _,r in latest.head(30).iterrows():
        top_latest.append({"episode_id":str(r["episode_id"]),"seat":int(r["seat"]),"submission_id":str(r["submission_id"]),"team":str(r["team"]),"rating":float(r["rating"]),"end_time":str(r["end_time"]),
            **{c:str(r[c]) for c in ("stream_h24","stream_h100","stream_h200","stream_h400","stream_h719") if c in r.index and pd.notna(r[c])}})

    out={
        "experiment":"CR028_CURRENT_ENGINE_FRONTIER_DISTRIBUTION",
        "engine_version":ENGINE,"rated_seat_games":int(len(x)),"unique_submissions":int(x["submission_id"].nunique()),
        "max_observed_rating":float(x["rating"].max()),"threshold_counts":thresholds,"rating_quantiles":qs,
        "top_peak_submissions":top_subs,"top_latest_submissions":top_latest,"lineage_views":lineage_views,
        "selection_only":True,"runtime_identity_features":False,"held_out_touched":False,
    }
    p=Path("artifacts/cr028_frontier/report.json");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k not in ("top_peak_submissions","top_latest_submissions","lineage_views")},indent=2,sort_keys=True))
    print("TOP_PEAK",json.dumps(top_subs[:10],indent=2))
    print("TOP_LATEST",json.dumps(top_latest[:10],indent=2))
    print("LINEAGES_TOP50_H200",json.dumps(lineage_views.get("top50_stream_h200",[])[:10],indent=2))


if __name__=="__main__":main()
