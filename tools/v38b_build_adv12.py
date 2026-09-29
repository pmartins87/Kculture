#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,tarfile
from pathlib import Path

BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
CXD_MARKER="_CXD_HOST = [v for v in list(globals().values()) if callable(v)][-1]"

ADV_BLOCK=r'''
# ===========================================================================
# V38-B / ADV12: bounded sale-advance race layer.
# Derived from public Apache-2.0 Kaggriculture work (Ahmed Berat Ozer /
# Dmitrii Gluzdov lineage); adapted to exact V30B host. Existing upstream
# notices are retained. Only public/current state plus native route plan used.
# ===========================================================================
_ADV_PARENT=[v for v in list(globals().values()) if callable(v)][-1]
_ADV_LOOK=12
_ADV_FROM=144
_ADV_TO=718
_ADV_PROTECT=True
_ADV_FRONT=True
_ADV_BOOK=False
_ADV_SUBTRACT_DEBTS=False
_ADV_ITEMS=('STRAWBERRY','WOOL','EGG','MILK','MELON','CARROT','TOMATO')
_ADV_REPORT=dict(adv_turns=0,adv_units=0,adv_errors=0)

def _adv_future(player,t):
    native=_IMPL.chassis.players[player]
    return _IMPL.chassis.routes[2 if t>=648 else native['route']][t].get('market',[]) or []

def _adv_apply(obs,action):
    step=int(obs['step']);player=int(obs['player'])
    if step%24==23 or not _ADV_FROM<=step<_ADV_TO:return action
    native=_IMPL.chassis.players[player]
    debts=native['sell_state'].setdefault('r36_debts',{})
    plan=[];first=None
    for off in range(1,_ADV_LOOK+1):
        t=step+off
        if t>718:break
        for o in _adv_future(player,t):
            if not o or len(o)<3:continue
            if first is None:first=o
            if o[0]=='SELL' and o[1] in _ADV_ITEMS:
                try:q=max(0,int(o[2]))
                except Exception:q=0
                if _ADV_SUBTRACT_DEBTS:q-=debts.get(t,{}).get(o[1],0)
                if q>0:plan.append((t,o[1],q))
    protected=first[1] if _ADV_PROTECT and first is not None and first[0]=='SELL' else None
    plan=[(t,item,q) for t,item,q in plan if item!=protected]
    if not plan:return action
    market=[list(o) for o in (action.get('market') or [])]
    if any(len(o)>1 and o[0]=='BUY_PRODUCT' for o in market):return action
    stock=projected_shed(action,FarmView(obs))
    selling={}
    for o in market:
        if len(o)>=3 and o[0]=='SELL':
            try:selling[o[1]]=selling.get(o[1],0)+max(0,int(o[2]))
            except Exception:return action
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    picked={c[1] for c in commands if len(c)>1 and c[0]=='PICKUP'}
    prices=obs['market']['prices'];added=0;extra=[];booked=[]
    for item in sorted({it for _,it,_ in plan},key=lambda it:-int(prices.get(it,0))):
        if item in picked or int(prices.get(item,0))<2:continue
        avail=int(stock.get(item,0))-selling.get(item,0)
        if avail<1:continue
        hit=next((o for o in market if len(o)>=3 and o[0]=='SELL' and o[1]==item),None)
        if hit is None and len(market)+len(extra)>=10:continue
        n=0
        for t,it,q in plan:
            if it!=item or avail<=0:continue
            take=min(q,avail);booked.append((t,item,take));n+=take;avail-=take
        if n<1:continue
        if hit is not None:hit[2]=int(hit[2])+n
        else:extra.append(['SELL',item,n])
        added+=n
    if not added:return action
    for t,item,take in (booked if _ADV_BOOK else []):
        d=debts.setdefault(t,{});d[item]=d.get(item,0)+take
    _ADV_REPORT['adv_turns']+=1;_ADV_REPORT['adv_units']+=added
    return dict(action,market=extra+market)

def _adv_frontload(obs,action):
    market=[list(o) for o in (action.get('market') or []) if o]
    if len(market)<2 or int(obs['step'])<_ADV_FROM:return action
    buys={o[1] for o in market if len(o)>1 and o[0]=='BUY_PRODUCT'}
    front=[o for o in market if len(o)>=3 and o[0]=='SELL' and o[1] not in buys]
    mid=[o for o in market if (len(o)>=3 and o[0]=='BUY_PRODUCT') or
         (len(o)>=3 and o[0]=='SELL' and o[1] in buys)]
    rest=[o for o in market if o not in front and o not in mid]
    new=front+mid+rest
    if new==market:return action
    _ADV_REPORT['front_turns']=_ADV_REPORT.get('front_turns',0)+1
    return dict(action,market=new)

def _adv_entry(observation,configuration=None):
    action=_ADV_PARENT(observation,configuration)
    try:
        if int(observation['step'])==0:
            _ADV_REPORT.clear();_ADV_REPORT.update(adv_turns=0,adv_units=0,adv_errors=0)
        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [
            ('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)])
        if standard:action=_adv_apply(observation,action)
        if standard and _ADV_FRONT:action=_adv_frontload(observation,action)
        st=_RACE_STATE.get(int(observation['player']))
        if st is not None and st.get('prev_action') is not None and st.get('step')==int(observation['step']):
            st['prev_action']=action
    except Exception:
        _ADV_REPORT['adv_errors']=_ADV_REPORT.get('adv_errors',0)+1
    return action

_adv_entry.telemetry=_ADV_REPORT
agent=_adv_entry

'''

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def pack(path:Path,main:bytes):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        i=tarfile.TarInfo("main.py");i.size=len(main);i.mtime=0;i.uid=i.gid=0;i.mode=0o644
        tf.addfile(i,io.BytesIO(main))
    with path.open("wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-package",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    with tarfile.open(a.base_package,"r:*") as tf:base=tf.extractfile("main.py").read()
    if sha(base)!=BASE_MAIN_SHA:raise SystemExit("V30B main SHA mismatch")
    src=base.decode("utf-8")
    for dep in ("_RACE_STATE","r36_debts","projected_shed","class FarmView","_IMPL"):
        if dep not in src:raise SystemExit(f"missing dependency {dep}")
    if "_ADV_LOOK" in src:raise SystemExit("base already has ADV")
    if src.count(CXD_MARKER)!=1:raise SystemExit("CXD host marker mismatch")
    src=src.replace(CXD_MARKER,ADV_BLOCK+"\n"+CXD_MARKER,1)
    compile(src,"v38b_main.py","exec")
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);pack(out,src.encode("utf-8"))
    print({"decision":"V38B_ADV12_BUILT","base_main_sha":sha(base),"main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size})

if __name__=="__main__":main()
