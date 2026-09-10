"""CR077B — W/L-aligned, state-controlled current-meta residual analysis.

One-time methodological repair of CR077, frozen before any 2026-09-10 dataset is
observed. Sep-08 fits state controls, Sep-09 selects at most one action-family /
window mechanism, and Sep-10 is untouched OOT confirmation when public.

Deployment-legal state only: shared farms/market/town plus THIS player's private
shed/seeds/inventories. Opponent private state, team/episode/seed identity are
never model features. Team/episode identity is used only for robustness.
"""
from __future__ import annotations

import argparse, collections, csv, json, math, statistics, tempfile
from pathlib import Path
from typing import Any
import kagglehub
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

WINDOWS=((96,192),(192,360),(360,540),(540,719))
FAMILIES=("HIRE","BUY_LAND","BUY_SEED","BUY_ANIMAL","BUY_PRODUCT","SELL","PASS")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
SHOPS=("BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET")
BOOT=3000; RNG_SEED=20260910

def download(handle:str,filename:str,out:Path)->Path:
    out.mkdir(parents=True,exist_ok=True)
    p=Path(kagglehub.dataset_download(handle,path=filename,output_dir=str(out),force_download=True))
    if not p.is_file(): raise FileNotFoundError(f"missing {handle}:{filename}:{p}")
    return p

def read_csv(path:Path)->list[dict[str,str]]:
    with path.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def fnum(v:Any,default:float=0.0)->float:
    try:
        x=float(v); return x if math.isfinite(x) else default
    except (TypeError,ValueError): return default

def tile_summary(farm:dict,prefix:str)->dict[str,float]:
    c=collections.Counter()
    for row in (farm or {}).get("tiles",[]) or []:
        if not isinstance(row,list): continue
        for tile in row:
            if tile is None: c["empty"]+=1; continue
            if tile=="LOCKED": c["locked"]+=1; continue
            if not isinstance(tile,dict): continue
            kind=str(tile.get("kind") or "")
            if kind=="WEED": c["weeds"]+=1
            elif kind=="PLANT":
                crop=str(tile.get("crop") or ""); c[f"crop_{crop}"]+=1
                c[f"crop_yield_{crop}"]+=fnum(tile.get("yield_units")); c[f"crop_watered_{crop}"]+=1 if tile.get("watered_today") else 0
            elif kind in ("COOP","PASTURE"):
                c[f"structure_{kind}"]+=1; animal=tile.get("animal")
                if animal:
                    animal=str(animal); c[f"animal_{animal}"]+=1; c[f"animal_yield_{animal}"]+=fnum(tile.get("yield_units"))
                    c[f"animal_fed_{animal}"]+=1 if tile.get("fed_today") else 0; c[f"animal_cared_{animal}"]+=1 if tile.get("cared_today") else 0
    out={f"{prefix}money":fnum((farm or {}).get("money")),f"{prefix}hands":float(len((farm or {}).get("hands",[]) or [])),
         f"{prefix}quads":float(len((farm or {}).get("unlocked_quadrants",[]) or [])),f"{prefix}hires_today":fnum((farm or {}).get("hires_today")),
         f"{prefix}weeds":float(c.get("weeds",0)),f"{prefix}empty":float(c.get("empty",0)),f"{prefix}locked":float(c.get("locked",0)),
         f"{prefix}coop":float(c.get("structure_COOP",0)),f"{prefix}pasture":float(c.get("structure_PASTURE",0))}
    farmer=(farm or {}).get("farmer") or []; out[f"{prefix}farmer_x"]=fnum(farmer[0]) if len(farmer)>=2 else -1.; out[f"{prefix}farmer_y"]=fnum(farmer[1]) if len(farmer)>=2 else -1.
    hands=(farm or {}).get("hands",[]) or []; xs=[]; ys=[]
    for h in hands:
        if isinstance(h,(list,tuple)) and len(h)>=2: xs.append(fnum(h[0])); ys.append(fnum(h[1]))
    out[f"{prefix}hand_mean_x"]=statistics.mean(xs) if xs else -1.; out[f"{prefix}hand_mean_y"]=statistics.mean(ys) if ys else -1.
    for crop in CROPS:
        lo=crop.lower(); out[f"{prefix}crop_{lo}"]=float(c.get(f"crop_{crop}",0)); out[f"{prefix}crop_yield_{lo}"]=float(c.get(f"crop_yield_{crop}",0)); out[f"{prefix}crop_watered_{lo}"]=float(c.get(f"crop_watered_{crop}",0))
    for animal in ANIMALS:
        lo=animal.lower(); out[f"{prefix}animal_{lo}"]=float(c.get(f"animal_{animal}",0)); out[f"{prefix}animal_yield_{lo}"]=float(c.get(f"animal_yield_{animal}",0)); out[f"{prefix}animal_fed_{lo}"]=float(c.get(f"animal_fed_{animal}",0)); out[f"{prefix}animal_cared_{lo}"]=float(c.get(f"animal_cared_{animal}",0))
    return out

def private_summary(private:dict)->dict[str,float]:
    private=private or {}; shed=private.get("shed") or {}; seeds=private.get("seeds") or {}; invs=private.get("inventories") or []; agg=collections.Counter()
    for inv in invs:
        if isinstance(inv,dict):
            for k,v in inv.items(): agg[str(k)]+=fnum(v)
    out={"self_private_inventory_total":float(sum(agg.values())),"self_shed_total":float(sum(fnum(v) for v in shed.values()))}
    for item in PRODUCTS+ANIMALS:
        lo=item.lower(); out[f"self_shed_{lo}"]=fnum(shed.get(item)); out[f"self_carry_{lo}"]=fnum(agg.get(item))
    for crop in CROPS: out[f"self_seed_{crop.lower()}"]=fnum(seeds.get(crop))
    return out

def state_features(obs:dict,player:int)->dict[str,float]:
    farms=(obs or {}).get("farms") or []
    if len(farms)<2 or player not in (0,1): return {}
    opp=1-player; own=tile_summary(farms[player],"self_"); other=tile_summary(farms[opp],"opp_"); out={**own,**other}
    suffixes=sorted(set(k[5:] for k in own if k.startswith("self_")) & set(k[4:] for k in other if k.startswith("opp_")))
    for s in suffixes: out[f"gap_{s}"]=own.get("self_"+s,0.)-other.get("opp_"+s,0.)
    market=(obs or {}).get("market") or {}; prices=market.get("prices") or {}; inv=market.get("inventory") or {}
    for item in PRODUCTS:
        lo=item.lower(); out[f"market_price_{lo}"]=fnum(prices.get(item)); out[f"market_inventory_{lo}"]=fnum(inv.get(item))
    shops=collections.Counter((((obs or {}).get("town") or {}).get("unlocked_shops") or []))
    for shop in SHOPS: out[f"shop_{shop.lower()}"]=float(shops.get(shop,0))
    out["shop_total"]=float(sum(shops.values())); out.update(private_summary((obs or {}).get("private") or {})); return out

def action_intensity(steps:list,player:int,start:int,end:int)->dict[str,float]:
    c=collections.Counter()
    for s in range(start,min(end,len(steps)-1)):
        try: act=steps[s+1][player].get("action")
        except Exception: act=None
        if not isinstance(act,dict): continue
        for order in act.get("market",[]) or []:
            if not (isinstance(order,list) and order): continue
            typ=str(order[0])
            if typ in ("HIRE","BUY_LAND"): c[typ]+=1.
            elif typ in ("BUY_SEED","BUY_ANIMAL","BUY_PRODUCT","SELL"): c[typ]+=max(0.,fnum(order[2],0.) if len(order)>2 else 0.)
        farmer=act.get("farmer")
        if isinstance(farmer,list) and farmer and str(farmer[0])=="PASS": c["PASS"]+=1.
        for hand in act.get("hands",[]) or []:
            if isinstance(hand,list) and hand and str(hand[0])=="PASS": c["PASS"]+=1.
    return {k:float(c.get(k,0.)) for k in FAMILIES}

def rewards(rep:dict)->tuple[float,float]|None:
    try:
        last=rep["steps"][-1]; return float(last[0].get("reward")),float(last[1].get("reward"))
    except Exception: return None

def episode_rows(rep:dict,date:str,eid:str)->list[dict[str,Any]]:
    steps=rep.get("steps") or []; rw=rewards(rep)
    if rw is None or len(steps)<720 or rw[0]==rw[1]: return []
    info=rep.get("info") or {}; teams=info.get("TeamNames") or []; counts={}
    for start,end in WINDOWS:
        counts[(start,end,0)]=action_intensity(steps,0,start,end); counts[(start,end,1)]=action_intensity(steps,1,start,end)
    rows=[]
    for p in (0,1):
        opp=1-p; windows={}
        for start,end in WINDOWS:
            try: obs=steps[start][p].get("observation") or {}
            except Exception: obs={}
            own=counts[(start,end,p)]; other=counts[(start,end,opp)]
            windows[f"{start}-{end}"]={"state":state_features(obs,p),"action_diff":{f:own[f]-other[f] for f in FAMILIES}}
        rows.append({"date":date,"episode_id":eid,"player":p,"self_team":str(teams[p]) if p<len(teams) else f"p{p}","opp_team":str(teams[opp]) if opp<len(teams) else f"p{opp}","win":1 if rw[p]>rw[opp] else 0,"windows":windows})
    return rows

def collect(date:str,top:int,root:Path)->tuple[list[dict],str|None]:
    handle=f"kaggle/kaggriculture-episodes-{date}"
    try: rows=sorted(read_csv(download(handle,"manifest.csv",root/date/"manifest")),key=lambda r:-fnum(r.get("avg_score")))[:top]
    except Exception as exc: return [],repr(exc)
    out=[]
    for row in rows:
        eid=str(row.get("episode_id") or "")
        if not eid: continue
        try:
            p=download(handle,f"{eid}.json",root/date/"episodes"/eid); rep=json.loads(p.read_text(encoding="utf-8")); out.extend(episode_rows(rep,date,eid))
        except Exception: pass
    return out,None

def matrices(rows:list[dict],window:str,family:str,names:list[str]|None=None):
    if names is None: names=sorted({k for r in rows for k in r["windows"][window]["state"]})
    X=np.asarray([[fnum(r["windows"][window]["state"].get(k)) for k in names] for r in rows],float); y=np.asarray([float(r["win"]) for r in rows],float); a=np.asarray([fnum(r["windows"][window]["action_diff"].get(family)) for r in rows],float)
    return X,y,a,names

def win_model()->Any: return make_pipeline(StandardScaler(),LogisticRegression(C=.2,max_iter=5000,solver="lbfgs"))
def action_model()->Any: return make_pipeline(StandardScaler(),Ridge(alpha=20.))
def corr(x:np.ndarray,y:np.ndarray)->float|None:
    if len(x)<8 or float(np.std(x))<1e-9 or float(np.std(y))<1e-9: return None
    return float(np.corrcoef(x,y)[0,1])
def cluster_bootstrap_ci(ra:np.ndarray,ry:np.ndarray,rows:list[dict],seed:int)->tuple[float|None,float|None]:
    clusters=collections.defaultdict(list)
    for i,r in enumerate(rows): clusters[str(r["episode_id"])].append(i)
    keys=sorted(clusters)
    if len(keys)<8: return None,None
    rng=np.random.default_rng(seed); vals=[]
    for _ in range(BOOT):
        chosen=rng.choice(keys,size=len(keys),replace=True); idx=[]
        for k in chosen: idx.extend(clusters[str(k)])
        ii=np.asarray(idx,dtype=int); v=corr(ra[ii],ry[ii])
        if v is not None and math.isfinite(v): vals.append(v)
    if not vals: return None,None
    return float(np.quantile(vals,.10)),float(np.quantile(vals,.90))
def loto_sign_fraction(ra:np.ndarray,ry:np.ndarray,rows:list[dict],sign:float)->tuple[float|None,int]:
    teams=sorted({str(r["self_team"]) for r in rows}|{str(r["opp_team"]) for r in rows}); vals=[]
    for team in teams:
        idx=[i for i,r in enumerate(rows) if str(r["self_team"])!=team and str(r["opp_team"])!=team]
        if len(idx)<16: continue
        ii=np.asarray(idx); v=corr(ra[ii],ry[ii])
        if v is not None: vals.append(v)
    if not vals: return None,0
    return sum(1 for v in vals if v*sign>0)/len(vals),len(vals)
def residual_eval(train:list[dict],test:list[dict],window:str,family:str,seed:int)->dict[str,Any]:
    Xtr,ytr,atr,names=matrices(train,window,family); Xte,yte,ate,_=matrices(test,window,family,names)
    wm=win_model(); am=action_model(); wm.fit(Xtr,ytr); am.fit(Xtr,atr); ry=yte-wm.predict_proba(Xte)[:,1]; ra=ate-am.predict(Xte)
    r=corr(ra,ry); lo,hi=cluster_bootstrap_ci(ra,ry,test,seed); sign=1. if (r is not None and r>=0) else -1.; loto,n_loto=loto_sign_fraction(ra,ry,test,sign)
    return {"window":window,"family":family,"train_rows":len(train),"test_rows":len(test),"test_episodes":len({r0["episode_id"] for r0 in test}),"state_feature_count":len(names),"residual_corr":r,"cluster_bootstrap80":[lo,hi],"leave_one_team_out_sign_fraction":loto,"leave_one_team_out_evaluations":n_loto,"action_diff_std":float(np.std(ate))}
def excludes_zero(rec:dict)->bool:
    r=rec.get("residual_corr"); lo,hi=rec.get("cluster_bootstrap80",[None,None]); return r is not None and lo is not None and hi is not None and ((r>0 and lo>0) or (r<0 and hi<0))
def discovery_ok(rec:dict)->bool:
    return bool(rec.get("residual_corr") is not None and abs(rec["residual_corr"])>=.20 and rec.get("action_diff_std",0)>=.5 and excludes_zero(rec) and rec.get("leave_one_team_out_sign_fraction") is not None and rec["leave_one_team_out_sign_fraction"]>=.75 and rec.get("leave_one_team_out_evaluations",0)>=3)
def oot_ok(selected:dict,rec:dict)->bool:
    a=selected.get("residual_corr"); b=rec.get("residual_corr"); return bool(a is not None and b is not None and a*b>0 and abs(b)>=.15 and excludes_zero(rec) and rec.get("leave_one_team_out_sign_fraction") is not None and rec["leave_one_team_out_sign_fraction"]>=.65 and rec.get("leave_one_team_out_evaluations",0)>=3)
def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--top",type=int,default=60); ap.add_argument("--output",required=True); args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="kculture-cr077b-") as tmp:
        root=Path(tmp); d8,e8=collect("2026-09-08",args.top,root); d9,e9=collect("2026-09-09",args.top,root); d10,e10=collect("2026-09-10",args.top,root)
    if len(d8)<40 or len(d9)<40: raise SystemExit(f"insufficient discovery rows d8={len(d8)} d9={len(d9)} errors={e8,e9}")
    grid=[]; i=0
    for start,end in WINDOWS:
        window=f"{start}-{end}"
        for fam in FAMILIES: grid.append(residual_eval(d8,d9,window,fam,RNG_SEED+i)); i+=1
    eligible=[r for r in grid if discovery_ok(r)]; eligible.sort(key=lambda r:(-abs(r["residual_corr"]),r["window"],r["family"])); selected=eligible[0] if eligible else None
    validation=None; confirmed=False
    if selected and len(d10)>=40:
        validation=residual_eval(d8,d10,selected["window"],selected["family"],RNG_SEED+999); confirmed=oot_ok(selected,validation)
    if not selected: decision="NO_WL_RESIDUAL_MECHANISM_DISCOVERED"
    elif len(d10)<40: decision="WAIT_FOR_2026_09_10_OOT"
    elif confirmed: decision="BUILD_CR078_CAUSAL_ABLATION"
    else: decision="WL_RESIDUAL_MECHANISM_FAILED_OOT"
    payload={"schema_version":"kculture-cr077b-wl-residual-v1","purpose":"one_time_method_repair_before_sep10_oot","method_frozen_before_sep10_observation":True,"datasets":{"2026-09-08":len(d8),"2026-09-09":len(d9),"2026-09-10":len(d10)},"dataset_errors":{"2026-09-08":e8,"2026-09-09":e9,"2026-09-10":e10},"target":"binary W/L; ties excluded","fixed_windows":[f"{a}-{b}" for a,b in WINDOWS],"fixed_families":list(FAMILIES),"action_intensity_definition":{"HIRE":"event count","BUY_LAND":"event count","BUY_SEED":"units","BUY_ANIMAL":"units","BUY_PRODUCT":"units","SELL":"units","PASS":"explicit farmer/hand PASS count"},"state_policy":"shared self/opponent farm summaries + shared market + per-shop counts + THIS player's private shed/seeds/carry only","forbidden_model_features":["team identity","episode id","seed","opponent private shed/seeds/inventory"],"robustness":"episode-cluster bootstrap + leave-one-team-out sign stability; team identity never enters model","discovery_gate":"Sep09 |residual corr|>=0.20, action-diff std>=0.5, episode-cluster bootstrap80 excludes zero, LOTO sign fraction>=0.75 with >=3 evaluations; select exactly one","fresh_oot_gate":"Sep10 same sign, |residual corr|>=0.15, episode-cluster bootstrap80 excludes zero, LOTO sign fraction>=0.65 with >=3 evaluations; Sep08 controls remain frozen","discovery_grid":grid,"selected_mechanism":selected,"fresh_oot_validation":validation,"decision":decision,"next_if_confirmed":"CR078 one-mechanism causal ablation; no direct strategy promotion from residual association","next_if_failed":"close this shortlist; do not choose runner-up post hoc","automatic_strategy_promotion":False,"automatic_kaggle_submission":False}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    md=["# CR077B W/L-aligned current-meta residual analysis","",f"Sep08 rows: **{len(d8)}**",f"Sep09 rows: **{len(d9)}**",f"Sep10 rows: **{len(d10)}**",f"Eligible mechanisms: **{len(eligible)}**",f"Selected: **{(selected or {}).get('window','none')} / {(selected or {}).get('family','none')}**",f"Fresh OOT confirmed: **{confirmed}**","",f"Decision: **{decision}**"]
    out.with_suffix(".md").write_text("\n".join(md)+"\n",encoding="utf-8"); print("\n".join(md))
if __name__=="__main__": main()
