"""Build deterministic self-contained CR-008 and CR-011 calibration packages.

These archives are for hosted information experiments, not promotion. They embed:
- hash-pinned COK V8;
- frozen R4B terminal liquidation overlay;
- frozen CR-007 pure prediction trees;
- CR-008 append-order or CR-011 early-order response semantics.
"""
from __future__ import annotations

import hashlib, json, shutil, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools import build_kexp050_submission as B

MODEL_PATH=ROOT/'models/cr007_pure_models.json'
EXPECTED_MODEL_BLOB='d4b29e753e2328ac43503f8daa655cc63abdd336'
CR008_BLOB='8e1c26202c3101c19668bf61edf2ae51d4329d5d'
CR011_BLOB='c4f1cb79f3c20b8229ab09e00a6878289cf9648d'
OUT=ROOT/'artifacts/submissions/adaptive_calibration_pair'


def sha(b): return hashlib.sha256(b).hexdigest()

ADAPTIVE_TEMPLATE=r'''

# ---------------------------------------------------------------------------
# Kculture opponent-aware high-confidence sale response.
# Package mode: __MODE__
# ---------------------------------------------------------------------------
import copy as _ka_copy
import json as _ka_json
import math as _ka_math

_ka_base_agent = agent
_KA_MODELS = _ka_json.loads(__MODEL_JSON__)
_KA_PRODUCTS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
_KA_CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
_KA_ANIMALS=("COW","SHEEP","GOOSE")
_KA_SHOPS=("BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET")
_KA_TARGETS={"SELL_CARROT":"CARROT","SELL_STRAWBERRY":"STRAWBERRY"}
_KA_HISTORY={0:{},1:{}}
_KA_LAST={0:-1,1:-1}


def _ka_get(obj,key,default=None):
    try:return obj.get(key,default)
    except AttributeError:
        try:return obj[key]
        except Exception:return default


def _ka_num(d,key):
    try:
        v=float(_ka_get(d,key,0) or 0)
        return v if _ka_math.isfinite(v) else 0.0
    except Exception:return 0.0


def _ka_feature_step(obs):
    try:return float(_ka_get(obs,"step",0) or 0)
    except Exception:return 0.0


def _ka_clock_step(obs):
    raw=_ka_get(obs,"step",None)
    try:
        if raw is not None:return max(0,int(raw))
    except Exception:pass
    try:
        day=max(0,int(_ka_get(obs,"day",0) or 0));hour=max(0,int(_ka_get(obs,"hour",0) or 0))
        return day*24+hour
    except Exception:return 0


def _ka_tile_counts(farm):
    out={}
    for row in _ka_get(farm,"tiles",[]) or []:
        if not isinstance(row,list):continue
        for tile in row:
            if not isinstance(tile,dict):continue
            if tile.get("kind")=="PLANT":
                k=f"crop_{tile.get('crop')}";out[k]=out.get(k,0.0)+1.0
            if tile.get("animal"):
                k=f"animal_{tile.get('animal')}";out[k]=out.get(k,0.0)+1.0
            if tile.get("kind")=="WEED":out["weeds"]=out.get("weeds",0.0)+1.0
            try:out["yield_units"]=out.get("yield_units",0.0)+max(0.0,float(tile.get("yield_units",0) or 0))
            except Exception:pass
    return out


def _ka_farm_public(farm,prefix):
    c=_ka_tile_counts(farm or {})
    out={f"{prefix}money":_ka_num(farm,"money"),f"{prefix}hands":float(len(_ka_get(farm,"hands",[]) or [])),f"{prefix}quads":float(len(_ka_get(farm,"unlocked_quadrants",[]) or [])),f"{prefix}weeds":float(c.get("weeds",0)),f"{prefix}yield_units":float(c.get("yield_units",0))}
    for crop in _KA_CROPS:out[f"{prefix}crop_{crop.lower()}"]=float(c.get(f"crop_{crop}",0))
    for animal in _KA_ANIMALS:out[f"{prefix}animal_{animal.lower()}"]=float(c.get(f"animal_{animal}",0))
    return out


def _ka_public_features(obs,prev,player):
    farms=_ka_get(obs,"farms",[]) or [];pf=_ka_get(prev,"farms",[]) or []
    if len(farms)<2 or len(pf)<2:return {}
    opp=1-player
    own=_ka_farm_public(farms[player],"self_");other=_ka_farm_public(farms[opp],"opp_")
    own0=_ka_farm_public(pf[player],"self_");other0=_ka_farm_public(pf[opp],"opp_")
    market=_ka_get(obs,"market",{}) or {};market0=_ka_get(prev,"market",{}) or {}
    prices=_ka_get(market,"prices",{}) or {};inv=_ka_get(market,"inventory",{}) or {}
    prices0=_ka_get(market0,"prices",{}) or {};inv0=_ka_get(market0,"inventory",{}) or {}
    shops=set(_ka_get(_ka_get(obs,"town",{}) or {},"unlocked_shops",[]) or [])
    st=_ka_feature_step(obs);f={"step":st,"day":st/24.0,"shop_count":float(len(shops))};f.update(own);f.update(other)
    for k,v in own.items():f[f"d{k}"]=v-own0.get(k,0.0)
    for k,v in other.items():f[f"d{k}"]=v-other0.get(k,0.0)
    f["gap_money"]=own["self_money"]-other["opp_money"];f["gap_hands"]=own["self_hands"]-other["opp_hands"];f["gap_quads"]=own["self_quads"]-other["opp_quads"]
    for product in _KA_PRODUCTS:
        lo=product.lower();p=_ka_num(prices,product);q=_ka_num(inv,product)
        f[f"market_price_{lo}"]=p;f[f"market_inventory_{lo}"]=q
        f[f"dmarket_price_{lo}"]=p-_ka_num(prices0,product);f[f"dmarket_inventory_{lo}"]=q-_ka_num(inv0,product)
    for shop in _KA_SHOPS:f[f"shop_{shop.lower()}"]=1.0 if shop in shops else 0.0
    return f


def _ka_tree_prob(model,features,names):
    node=0;left=model["children_left"];right=model["children_right"];feats=model["feature"];th=model["threshold"]
    while left[node]!=-1 and right[node]!=-1:
        idx=feats[node];val=float(features.get(names[idx],0.0));node=left[node] if val<=th[node] else right[node]
    vals=model["value"][node];classes=model["classes"];total=sum(vals)
    if total<=0 or 1 not in classes:return 0.0
    return float(vals[classes.index(1)])/float(total)


def _ka_snapshot(obs):
    return {"step":_ka_get(obs,"step",None),"day":_ka_get(obs,"day",None),"hour":_ka_get(obs,"hour",None),"farms":_ka_copy.deepcopy(_ka_get(obs,"farms",[]) or []),"market":_ka_copy.deepcopy(_ka_get(obs,"market",{}) or {}),"town":_ka_copy.deepcopy(_ka_get(obs,"town",{}) or {})}


def _ka_reset(player,step):
    if step==0 or step<_KA_LAST[player]:_KA_HISTORY[player].clear()
    _KA_LAST[player]=step


def _ka_remember(player,step,obs):
    _KA_HISTORY[player][step]=_ka_snapshot(obs);cutoff=step-30
    for k in list(_KA_HISTORY[player]):
        if k<cutoff:del _KA_HISTORY[player][k]


def _ka_apply(obs,action,player,step):
    prev=_KA_HISTORY[player].get(step-24)
    if prev is None:return action
    feat=_ka_public_features(obs,prev,player)
    if not feat:return action
    names=_KA_MODELS["feature_names"];market=list(action.get("market") or [])
    already={o[1] for o in market if isinstance(o,list) and len(o)>=2 and o[0]=="SELL"}
    shed=_ka_get(_ka_get(obs,"private",{}) or {},"shed",{}) or {};adaptive=[];capacity=max(0,10-len(market))
    for target,item in _KA_TARGETS.items():
        if len(adaptive)>=capacity:break
        if item in already:continue
        try:qty=max(0,int(_ka_get(shed,item,0) or 0))
        except Exception:qty=0
        if qty<=0:continue
        prob=_ka_tree_prob(_KA_MODELS["models"][target],feat,names);threshold=float(_KA_MODELS["thresholds"][target])
        if prob>=threshold:adaptive.append(["SELL",item,qty]);already.add(item)
    if adaptive:
        if __EARLY__:action["market"]=adaptive+market
        else:action["market"]=market+adaptive
    return action


def agent(obs,config=None):
    player=int(_ka_get(obs,"player",0) or 0);step=_ka_clock_step(obs);_ka_reset(player,step)
    action=_ka_base_agent(obs,config);action=_ka_apply(obs,action,player,step);_ka_remember(player,step,obs);return action
'''


def build(mode,early,model_text):
    base_bytes=B.BASE.read_bytes()
    if sha(base_bytes)!=B.EXPECTED_BASE_SHA256:raise SystemExit('COK base hash mismatch')
    target=OUT/mode
    if target.exists():shutil.rmtree(target)
    target.mkdir(parents=True)
    overlay=ADAPTIVE_TEMPLATE.replace('__MODE__',mode).replace('__MODEL_JSON__',repr(model_text)).replace('__EARLY__','True' if early else 'False')
    main=target/'main.py';main.write_bytes(base_bytes+B.R4B_OVERLAY.encode('utf-8')+overlay.encode('utf-8'))
    (target/'LICENSE-APACHE-2.0.txt').write_bytes(B.download(B.LICENSE_URL))
    notice=(f"Kculture {mode} hosted calibration package\nDerived from COK V8 under Apache-2.0.\nUpstream commit: {B.UPSTREAM_COMMIT}\nR4B blob: {B.FROZEN_R4B_BLOB}\nCR-008 blob: {CR008_BLOB}\nCR-011 blob: {CR011_BLOB}\nPurpose: hosted information calibration, not promotion.\n\n----- Upstream notices -----\n"+B.download(B.NOTICES_URL).decode('utf-8'))
    (target/'THIRD_PARTY_NOTICES.txt').write_text(notice,encoding='utf-8')
    files=[target/'main.py',target/'LICENSE-APACHE-2.0.txt',target/'THIRD_PARTY_NOTICES.txt']
    archive=OUT/f'{mode}.tar.gz';B.deterministic_tar_gz(archive,files)
    return {'mode':mode,'archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive.read_bytes()),'archive_bytes':archive.stat().st_size,'main_sha256':sha(main.read_bytes())}


def main():
    model_text=MODEL_PATH.read_text(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    reports=[build('Kculture_CR008_adaptive_append_calibration_v1',False,model_text),build('Kculture_CR011_adaptive_early_calibration_v1',True,model_text)]
    (OUT/'manifest.json').write_text(json.dumps({'schema_version':'adaptive-calibration-pair-v1','model_sha256':sha(model_text.encode()),'packages':reports},indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
