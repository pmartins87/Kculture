#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,tarfile
from pathlib import Path
BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
MARKER="_CXD_HOST = [v for v in list(globals().values()) if callable(v)][-1]"
BLOCK=r'''
# V38-A2 MODELPX; Apache-2.0 public tetsutani-lineage mechanism, adapted to V30B.
_MPX_PARENT = [v for v in list(globals().values()) if callable(v)][-1]
_MPX_ITEMS=("MILK","STRAWBERRY","WOOL")
_MPX_HOURS=tuple(range(12,23))
_MPX_REPORT=dict(mpx_fires=0,mpx_units=0,mpx_errors=0)
_MPX_HIST={}
def _mpx_draw_units(item,step):
    return (1 if step%4==0 else 0)+(1 if step%24==0 else 0)
def _mpx_apply(observation,action):
    step=int(observation["step"])
    if step<144 or step>=696 or step%24 not in _MPX_HOURS:return action
    player=int(observation["player"]);market=observation["market"]
    inv_all=market.get("inventory") or {};prices=market.get("prices") or {}
    hist=_MPX_HIST.setdefault(player,{})
    prev=hist.get("prev");inv_now={i:int(inv_all.get(i,0)) for i in _MPX_ITEMS}
    if prev and prev["step"]==step-1:
        for i in _MPX_ITEMS:
            d=inv_now[i]-prev["inv"][i]+_mpx_draw_units(i,step-1)-prev["own"].get(i,0)
            hist.setdefault(i,[]).append(max(0,d))
            if len(hist[i])>12:del hist[i][:6]
    hist["prev"]={"step":step,"inv":inv_now,"own":{}}
    orders=[list(o) for o in (action.get("market") or [])]
    for o in orders:
        if len(o)>=3 and o[0]=="SELL" and o[1] in _MPX_ITEMS:
            hist["prev"]["own"][o[1]]=hist["prev"]["own"].get(o[1],0)+int(o[2])
    already={o[1] for o in orders if len(o)>1 and o[0]=="SELL"}
    native=_IMPL.chassis.players.get(player)
    if not native or native.get("route") not in _IMPL.chassis.routes:return action
    stock=projected_shed(action,FarmView(observation));added=False
    for item in _MPX_ITEMS:
        if item in already or len(orders)>=10:continue
        avail=int(stock.get(item,0))
        if avail<=0 or int(prices.get(item,0))<=1:continue
        rival=hist.get(item) or [];rival_avg=sum(rival[-4:])/len(rival[-4:]) if rival else 0.0
        planned=6
        try:
            inv=int(inv_all.get(item,0));p_cur=float(_r37_market_price(item,inv))
            inv_next=inv+rival_avg+planned-_mpx_draw_units(item,step)
            p_next=float(_r37_market_price(item,max(0,int(inv_next))))
        except Exception:continue
        if p_next<p_cur-0.5:
            take=min(avail,max(1,planned//2))
            if take<=0:continue
            orders.insert(0,["SELL",item,take]);_MPX_REPORT["mpx_fires"]+=1;_MPX_REPORT["mpx_units"]+=take
            hist["prev"]["own"][item]=hist["prev"]["own"].get(item,0)+take;added=True
    return dict(action,market=orders[:10]) if added else action
def _mpx_entry(observation,configuration=None):
    if int(observation.get("step",0))==0:
        _MPX_REPORT.update(mpx_fires=0,mpx_units=0,mpx_errors=0);_MPX_HIST.clear()
    action=_MPX_PARENT(observation,configuration)
    try:return _mpx_apply(observation,action)
    except Exception:
        _MPX_REPORT["mpx_errors"]+=1;return action
_mpx_entry.telemetry=_MPX_REPORT
agent=_mpx_entry
'''
def sha(b):return hashlib.sha256(b).hexdigest()
def pack(path,main):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        i=tarfile.TarInfo("main.py");i.size=len(main);i.mtime=0;i.uid=i.gid=0;i.mode=0o644;tf.addfile(i,io.BytesIO(main))
    with open(path,"wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-package",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    with tarfile.open(a.base_package,"r:*") as tf:base=tf.extractfile("main.py").read()
    if sha(base)!=BASE_MAIN_SHA:raise SystemExit("base sha mismatch")
    src=base.decode("utf-8")
    if "_MPX_ITEMS" in src or src.count(MARKER)!=1:raise SystemExit("integration preflight mismatch")
    src=src.replace(MARKER,BLOCK+"\n"+MARKER,1);compile(src,"v38a2_main.py","exec")
    out=Path(a.output);pack(out,src.encode("utf-8"))
    print({"decision":"V38A2_MPX_BUILT","main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size})
if __name__=="__main__":main()
