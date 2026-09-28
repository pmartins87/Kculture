#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,tarfile
from pathlib import Path

EXPECTED_BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"

BLOCK=r'''# V37-A own economic market controller.
import copy as _v37_copy
_V37A_PARENT = agent
_V37A_PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
_V37A_BASE = {"WHEAT":25,"CARROT":35,"TOMATO":60,"STRAWBERRY":120,"MELON":250,"EGG":50,"MILK":160,"WOOL":200,"FERTILIZER":100}
_V37A_I0 = {k:10000 for k in _V37A_PRODUCTS}
_V37A_STATS = {"calls":0,"sell_turns":0,"late_capex_dropped":0,"errors":0}

def _v37a_tile_pressure(obs,item):
    try:
        other=1-int(obs.get("player",0));farm=obs["farms"][other]
        crop=item if item in ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON") else None
        animal={"EGG":"GOOSE","MILK":"COW","WOOL":"SHEEP"}.get(item);pressure=0
        for row in farm.get("tiles",[]) or []:
            for t in row or []:
                if not isinstance(t,dict):continue
                if crop and t.get("crop")==crop:pressure+=max(1,int(t.get("yield_units",0) or 0))
                elif animal and t.get("animal")==animal:pressure+=max(1,int(t.get("yield_units",0) or 0))
        return pressure
    except Exception:return 0

def _v37a_reserve(obs,item,qty,step):
    if step>=648:return 0
    if item=="WHEAT":
        try:
            me=int(obs.get("player",0));animals=0
            for row in obs["farms"][me].get("tiles",[]) or []:
                for t in row or []:
                    if isinstance(t,dict) and t.get("animal"):animals+=1
            return min(qty,max(6,2*animals))
        except Exception:return min(qty,8)
    if item=="FERTILIZER":return min(qty,4 if step<576 else 0)
    return 0

def _v37a_sale_fraction(obs,item,qty,step,shed_total):
    if qty<=0:return 0.0
    if step>=696:return 1.0
    prices=(obs.get("market") or {}).get("prices") or {}
    inv=(obs.get("market") or {}).get("inventory") or {}
    p=float(prices.get(item,0) or 0);base=float(_V37A_BASE[item])
    mi=float(inv.get(item,_V37A_I0[item]) or _V37A_I0[item]);i0=float(_V37A_I0[item])
    pressure=float(_v37a_tile_pressure(obs,item));score=0.0
    if p>=1.25*base:score+=2.0
    elif p>=1.05*base:score+=1.0
    elif p<=.55*base:score-=1.5
    elif p<=.75*base:score-=.5
    if mi>=i0:score+=min(2.0,(mi-i0)/500.0)
    elif mi<=i0-500:score-=.5
    score+=min(2.0,pressure/12.0)
    if shed_total>=92:score+=3.0
    elif shed_total>=82:score+=1.0
    if step>=624:score+=1.0
    if step>=672:score+=2.0
    if score>=3.0:return 1.0
    if score>=1.5:return .67
    if score>=.5:return .34
    return 0.0

def _v37a_filter_capex(orders,step):
    kept=[]
    for o in orders:
        if not o:continue
        op=o[0];drop=(op=="BUY_LAND" and step>=480) or (op=="BUY_ANIMAL" and step>=528) or (op=="BUY_SEED" and step>=552) or (op=="BUY_PRODUCT" and step>=600) or (op=="HIRE" and step>=624)
        if drop:_V37A_STATS["late_capex_dropped"]+=1
        else:kept.append(list(o))
    return kept

def agent(observation,configuration=None):
    _V37A_STATS["calls"]+=1
    try:
        step=int(observation.get("step",0) or 0);parent=_V37A_PARENT(observation,configuration)
        out={"farmer":_v37_copy.deepcopy(parent.get("farmer",["PASS"])),"hands":_v37_copy.deepcopy(parent.get("hands",[])),"market":[]}
        out["market"]=_v37a_filter_capex([list(o) for o in (parent.get("market") or []) if o and o[0]!="SELL"],step)
        try:stock=projected_shed(out,FarmView(observation))
        except Exception:stock=dict((observation.get("private") or {}).get("shed") or {})
        shed_total=sum(max(0,int(stock.get(k,0) or 0)) for k in _V37A_PRODUCTS);sells=[]
        for item in _V37A_PRODUCTS:
            qty=max(0,int(stock.get(item,0) or 0));reserve=_v37a_reserve(observation,item,qty,step);available=max(0,qty-reserve)
            frac=_v37a_sale_fraction(observation,item,available,step,shed_total);n=min(available,int(round(available*frac)))
            if n>0:
                prices=(observation.get("market") or {}).get("prices") or {}
                priority=float(prices.get(item,0) or 0)*n+_v37a_tile_pressure(observation,item)*float(_V37A_BASE[item])
                sells.append((priority,["SELL",item,n]))
        sells.sort(key=lambda x:x[0],reverse=True);slots=max(0,10-len(out["market"]));out["market"] += [o for _,o in sells[:slots]]
        if sells:_V37A_STATS["sell_turns"]+=1
        return out
    except Exception:
        _V37A_STATS["errors"]+=1
        return _V37A_PARENT(observation,configuration)
agent.telemetry=_V37A_STATS
agent=globals().pop("agent")
'''

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def write_tar(path:Path,main:bytes):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        info=tarfile.TarInfo("main.py");info.size=len(main);info.mtime=0;info.uid=0;info.gid=0;info.mode=0o644
        tf.addfile(info,io.BytesIO(main))
    with path.open("wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-package",required=True);ap.add_argument("--output",required=True);args=ap.parse_args()
    with tarfile.open(args.base_package,"r:*") as tf:
        base=tf.extractfile("main.py").read()
    if sha(base)!=EXPECTED_BASE_MAIN_SHA:raise SystemExit("V37 base main SHA mismatch")
    source=base.decode("utf-8")+"\n\n"+BLOCK+"\n"
    compile(source,"v37a_main.py","exec")
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);write_tar(out,source.encode("utf-8"))
    print({"decision":"V37A_PACKAGE_BUILT","base_main_sha":sha(base),"main_sha":sha(source.encode("utf-8")),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size})

if __name__=="__main__":main()
