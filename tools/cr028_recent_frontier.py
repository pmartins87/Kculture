"""CR028: characterize recent 1.32.7 frontier windows and shared openings."""
from __future__ import annotations
import json
from pathlib import Path
import kagglehub
import pandas as pd

DATASET='georgymamarin/kaggriculture-episodes'; ENGINE='1.32.7'

def dl(n,r):
    r.mkdir(parents=True,exist_ok=True);p=Path(kagglehub.dataset_download(DATASET,path=n,output_dir=str(r),force_download=True))
    if not p.is_file():raise FileNotFoundError(p)
    return p

def norm(s):return s.astype(str).str.replace(r'\.0$','',regex=True)

def main():
    r=Path('artifacts/cr028_recent/data')
    ep=pd.read_csv(dl('episodes.csv',r));ft=pd.read_csv(dl('episode_features.csv',r));sh=pd.read_csv(dl('stream_hashes.csv',r))
    seats=pd.concat([ep[['episode_id','end_time',f'sub_{s}',f'team_{s}',f'rating_{s}']].rename(columns={f'sub_{s}':'submission_id',f'team_{s}':'team',f'rating_{s}':'rating'}).assign(seat=s) for s in (0,1)],ignore_index=True)
    eng=ft[['episode_id','seat','engine_version']].copy()
    for d in (seats,eng,sh):d['episode_id']=norm(d['episode_id']);d['seat']=pd.to_numeric(d['seat'],errors='coerce').astype('Int64')
    seats['submission_id']=norm(seats['submission_id']);seats['rating']=pd.to_numeric(seats['rating'],errors='coerce');seats['end_time']=pd.to_datetime(seats['end_time'],utc=True,errors='coerce');eng['engine_version']=eng['engine_version'].astype(str)
    x=seats.merge(eng,on=['episode_id','seat']).merge(sh,on=['episode_id','seat'],how='left');x=x[(x.engine_version==ENGINE)&x.rating.notna()&x.end_time.notna()].copy()
    anchor=x.end_time.max(); windows={}
    for days in (1,2,3,7,14,21):
        q=x[x.end_time>=anchor-pd.Timedelta(days=days)].copy()
        # One latest/highest representative per submission within the window.
        subs=q.sort_values(['rating','end_time'],ascending=[False,False]).drop_duplicates('submission_id',keep='first')
        top=[]
        for _,z in subs.head(30).iterrows():
            top.append({'episode_id':str(z.episode_id),'seat':int(z.seat),'submission_id':str(z.submission_id),'team':str(z.team),'rating':float(z.rating),'end_time':z.end_time.isoformat(),**{c:str(z[c]) for c in ('stream_h24','stream_h48','stream_h100','stream_h136','stream_h200','stream_h400','stream_h719') if c in z.index and pd.notna(z[c])}})
        lineages={}
        for h in ('stream_h24','stream_h48','stream_h100','stream_h200'):
            if h not in subs.columns:continue
            c=subs.head(100);g=(c[c[h].notna()].groupby(h).agg(submissions=('submission_id','nunique'),teams=('team','nunique'),mean_rating=('rating','mean'),max_rating=('rating','max')).reset_index().sort_values(['submissions','mean_rating'],ascending=False).head(10))
            lineages[h]=[{h:str(a[h]),'submissions':int(a.submissions),'teams':int(a.teams),'mean_rating':float(a.mean_rating),'max_rating':float(a.max_rating)} for _,a in g.iterrows()]
        windows[str(days)]={'seat_games':int(len(q)),'unique_submissions':int(q.submission_id.nunique()),'max_rating':None if q.empty else float(q.rating.max()),'ge2800':int((q.rating>=2800).sum()),'ge2700':int((q.rating>=2700).sum()),'top_submissions':top,'lineages_top100_submissions':lineages}
    out={'experiment':'CR028_RECENT_CURRENT_ENGINE_FRONTIER','engine_version':ENGINE,'dataset_anchor':anchor.isoformat(),'windows_days':windows,'selection_only':True,'runtime_identity_features':False,'held_out_touched':False}
    p=Path('artifacts/cr028_recent/report.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    brief={d:{k:v for k,v in w.items() if k not in ('top_submissions','lineages_top100_submissions')} for d,w in windows.items()}
    print(json.dumps({'anchor':out['dataset_anchor'],'windows':brief},indent=2))
    for d in ('1','3','7'):
        print('WINDOW',d,'TOP',json.dumps(windows[d]['top_submissions'][:10],indent=2));print('WINDOW',d,'H24',json.dumps(windows[d]['lineages_top100_submissions'].get('stream_h24',[])[:5],indent=2));print('WINDOW',d,'H200',json.dumps(windows[d]['lineages_top100_submissions'].get('stream_h200',[])[:5],indent=2))
if __name__=='__main__':main()
