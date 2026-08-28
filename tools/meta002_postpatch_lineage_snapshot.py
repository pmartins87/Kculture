"""META-002: characterize the actually relevant Kaggriculture 1.32.7 ladder regime.

Evaluation-only. Uses public metadata from georgymamarin/kaggriculture-episodes.
No lineage or team identity is ever an agent runtime feature.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import kagglehub
import pandas as pd

HANDLE = "georgymamarin/kaggriculture-episodes"
ENGINE = "1.32.7"


def dl(name: str, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return Path(kagglehub.dataset_download(HANDLE, path=name, output_dir=str(root), force_download=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='artifacts/meta002/data')
    ap.add_argument('--output', required=True)
    ap.add_argument('--top-seat-games', type=int, default=100)
    a=ap.parse_args()
    root=Path(a.data_dir)
    ep=pd.read_csv(dl('episodes.csv',root))
    sh=pd.read_csv(dl('stream_hashes.csv',root))
    ef=pd.read_csv(dl('episode_features.csv',root), usecols=['episode_id','seat','engine_version'])

    seats=pd.concat([
        ep[['episode_id',f'team_{s}',f'rating_{s}',f'sub_{s}','create_time','end_time']]
          .rename(columns={f'team_{s}':'team',f'rating_{s}':'rating',f'sub_{s}':'submission_id'})
          .assign(seat=s)
        for s in (0,1)
    ],ignore_index=True)
    x=sh.merge(seats,on=['episode_id','seat'],how='left').merge(ef,on=['episode_id','seat'],how='left')
    x=x[x['engine_version'].astype(str)==ENGINE].copy()
    x['rating']=pd.to_numeric(x['rating'],errors='coerce')
    x=x[x['rating'].notna() & x['stream_h200'].notna()].copy()
    x=x.sort_values(['rating','end_time','episode_id'],ascending=[False,False,False])

    top=x.head(min(a.top_seat_games,len(x))).copy()
    groups=(top.groupby('stream_h200')
        .agg(seat_games=('episode_id','size'),teams=('team','nunique'),submissions=('submission_id','nunique'),mean_rating=('rating','mean'),max_rating=('rating','max'))
        .reset_index().sort_values(['seat_games','max_rating'],ascending=False))

    # One highest-rated public representative per lineage for future evaluation corpus construction.
    reps=(top.sort_values(['rating','end_time'],ascending=[False,False])
          .drop_duplicates('stream_h200')
          [['stream_h200','team','submission_id','episode_id','seat','rating','create_time','end_time']])

    quantiles={str(q):float(x['rating'].quantile(q)) for q in (0.5,0.75,0.9,0.95,0.99)} if len(x) else {}
    report={
        'experiment':'META-002-postpatch-lineage-snapshot',
        'source':HANDLE,
        'engine_version':ENGINE,
        'status':'PASS' if len(x) else 'NO_POSTPATCH_ROWS',
        'postpatch_hashed_seat_games':int(len(x)),
        'postpatch_unique_teams':int(x['team'].nunique()),
        'postpatch_unique_submissions':int(x['submission_id'].nunique()),
        'postpatch_unique_h200_lineages':int(x['stream_h200'].nunique()),
        'rating_max':float(x['rating'].max()) if len(x) else None,
        'rating_quantiles':quantiles,
        'top_window_seat_games':int(len(top)),
        'top_window_unique_teams':int(top['team'].nunique()),
        'top_window_unique_submissions':int(top['submission_id'].nunique()),
        'top_window_unique_h200_lineages':int(top['stream_h200'].nunique()),
        'top_window_largest_lineages':groups.head(30).to_dict(orient='records'),
        'top_window_representatives':reps.head(50).to_dict(orient='records'),
    }
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,default=str),encoding='utf-8')
    print(json.dumps(report,indent=2,sort_keys=True,default=str))
    if report['status']!='PASS': raise SystemExit(2)

if __name__=='__main__': main()
