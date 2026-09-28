#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,tarfile
from pathlib import Path

EXPECTED_BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
BLOCK=r'''# V37-B own supply-first surplus monetization controller.
import copy as _v37b_copy
_V37B_PARENT=agent
_V37B_FINISHED=("CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL")
_V37B_BASE={"CARROT":35,"TOMATO":60,"STRAWBERRY":120,"MELON":250,"EGG":50,"MILK":160,"WOOL":200}
_V37B_STATS={"calls":0,"changed":0,"units":0,"errors":0}

def _v37b_extra_sales(obs,action):
    step=int(obs.get("step",0) or 0)
    market=[list(o) for o in (action.get("market") or [])]
    if len(market)>=10:return action
    # Never alter/remove/reorder parent orders. Projection is after parent action.
    try:stock=projected_shed(action,FarmView(obs))
    except Exception:stock=dict((obs.get("private") or {}).get("shed") or {})
    total=sum(max(0,int(stock.get(k,0) or 0)) for k in PRODUCTS)
    # Supply-first: only monetize excess when capacity is binding or horizon is short.
    if total<82 and step<624:return action
    prices=(obs.get("market") or {}).get("prices") or {}
    already={o[1] for o in market if len(o)>1 and o[0]=="SELL"}
    candidates=[]
    target=72 if step<672 else 48
    excess=max(0,total-target)
    if step>=696:excess=max(excess,total)
    for item in _V37B_FINISHED:
        if item in already:continue
        have=max(0,int(stock.get(item,0) or 0))
        if have<=0:continue
        price=float(prices.get(item,0) or 0);base=float(_V37B_BASE[item])
        # Never dump premium goods into an already-broken market except terminally.
        floor=(0.55*base if step<696 else 1.0)
        if price<floor:continue
        # Small bounded sale: preserve future town/market value and avoid giant price shock.
        cap=4 if step<624 else 8 if step<696 else 24
        q=min(have,cap,max(1,excess))
        if q>0:candidates.append((price/base,price*q,item,q))
    if not candidates:return action
    candidates.sort(reverse=True)
    out=_v37b_copy.deepcopy(action);slots=10-len(market);added=0
    for _,__,item,q in candidates[:slots]:
        if excess<=0 and step<696:break
        q=min(q,excess if excess>0 else q)
        if q<=0:continue
        out["market"].append(["SELL",item,int(q)])
        added+=int(q);excess=max(0,excess-int(q))
    if added:
        _V37B_STATS["changed"]+=1;_V37B_STATS["units"]+=added
        return out
    return action

def agent(observation,configuration=None):
    _V37B_STATS["calls"]+=1
    base=_V37B_PARENT(observation,configuration)
    try:return _v37b_extra_sales(observation,base)
    except Exception:
        _V37B_STATS["errors"]+=1
        return base
agent.telemetry=_V37B_STATS
agent=globals().pop("agent")
'''
def sha(b):return hashlib.sha256(b).hexdigest()
def tar(path,main):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        i=tarfile.TarInfo("main.py");i.size=len(main);i.mtime=0;i.uid=i.gid=0;i.mode=0o644;tf.addfile(i,io.BytesIO(main))
    with open(path,"wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-package",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    with tarfile.open(a.base_package,"r:*") as tf:base=tf.extractfile("main.py").read()
    if sha(base)!=EXPECTED_BASE_MAIN_SHA:raise SystemExit("base sha mismatch")
    src=base.decode()+"\n\n"+BLOCK+"\n";compile(src,"v37b_main.py","exec");tar(a.output,src.encode())
    out=Path(a.output);print({"decision":"V37B_PACKAGE_BUILT","main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size})
if __name__=="__main__":main()
