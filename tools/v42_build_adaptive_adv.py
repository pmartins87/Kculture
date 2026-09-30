#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,json,tarfile
from pathlib import Path
BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
ADV_ITEMS=("STRAWBERRY","WOOL","EGG","MILK","MELON","CARROT","TOMATO")

def sha(b):return hashlib.sha256(b).hexdigest()
def pack(path,main):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        i=tarfile.TarInfo("main.py");i.size=len(main);i.mtime=0;i.uid=i.gid=0;i.mode=0o644;tf.addfile(i,io.BytesIO(main))
    with open(path,"wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--base-package",required=True);ap.add_argument("--model",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    model=json.loads(Path(a.model).read_text())
    if model.get("decision")!="V42_ADAPTIVE_ADV_GATE_PASS":raise SystemExit("V42 model did not pass")
    look=int(model["chosen_look"]);sim=float(model["gate"]["similarity"]);lead=float(model["gate"]["lead"])
    with tarfile.open(a.base_package,"r:*") as tf:base=tf.extractfile("main.py").read()
    if sha(base)!=BASE_MAIN_SHA:raise SystemExit("base sha mismatch")
    block=f'''
# ===========================================================================
# V42 ONLINE-GATED ADV
# Public-observation adaptation on top of exact V30B.
# The base agent runs unchanged through step 216. Thereafter future tape sales
# may be advanced only if the opponent looks like the same family or has
# already demonstrated an observed sale lead. The physical policy is untouched.
# ===========================================================================
_V42_PARENT=agent
del agent
_V42_LOOK={look}
_V42_SIM={sim!r}
_V42_LEAD={lead!r}
_V42_ITEMS={ADV_ITEMS!r}
_V42_STATE={{}}
_V42_REPORT=dict(adv_decisions=0,adv_active_games=0,adv_turns=0,adv_units=0,adv_errors=0)

def _v42_gate(obs):
    p=int(obs["player"]);race=(_V9_RACE.get(p) or {{}})
    try:s=float(_r37_similarity(obs))
    except Exception:s=0.0
    l=float(race.get("lead",-12) or -12)
    return bool(s>=_V42_SIM or l>=_V42_LEAD),s,l

def _v42_future(player,step):
    native=_IMPL.chassis.players.get(player)
    if not native or native.get("route") not in _IMPL.chassis.routes:return [],None
    route=native["route"];plan=[];first=None
    for off in range(1,_V42_LOOK+1):
        t=step+off
        if t>718:break
        tape=_IMPL.chassis.routes[2 if t>=648 else route]
        for o in (tape[t].get("market") or []):
            if not o or len(o)<3:continue
            if first is None:first=o
            if o[0]=="SELL" and o[1] in _V42_ITEMS:
                try:q=max(0,int(o[2]))
                except Exception:q=0
                if q>0:plan.append((t,o[1],q))
    protected=first[1] if first is not None and first[0]=="SELL" else None
    if protected is not None:plan=[x for x in plan if x[1]!=protected]
    return plan,protected

def _v42_apply(obs,action):
    step=int(obs["step"]);player=int(obs["player"])
    if step<216 or step>=718 or step%24==23:return action
    plan,_=_v42_future(player,step)
    if not plan:return action
    market=[list(o) for o in (action.get("market") or [])]
    if any(len(o)>1 and o[0]=="BUY_PRODUCT" for o in market):return action
    stock=projected_shed(action,FarmView(obs))
    selling={{}}
    for o in market:
        if len(o)>=3 and o[0]=="SELL":
            selling[o[1]]=selling.get(o[1],0)+max(0,int(o[2]))
    commands=[action.get("farmer") or ["PASS"],*(action.get("hands") or [])]
    picked={{c[1] for c in commands if len(c)>1 and c[0]=="PICKUP"}}
    prices=obs["market"]["prices"];extra=[];added=0
    for item in sorted({{it for _,it,_ in plan}},key=lambda it:-int(prices.get(it,0))):
        if item in picked or int(prices.get(item,0))<2:continue
        avail=int(stock.get(item,0))-selling.get(item,0)
        if avail<1:continue
        hit=next((o for o in market if len(o)>=3 and o[0]=="SELL" and o[1]==item),None)
        if hit is None and len(market)+len(extra)>=10:continue
        n=0
        for t,it,q in plan:
            if it!=item or avail<=0:continue
            take=min(q,avail);n+=take;avail-=take
        if n<1:continue
        if hit is not None:hit[2]=int(hit[2])+n
        else:extra.append(["SELL",item,n])
        added+=n
    if not added:return action
    _V42_REPORT["adv_turns"]+=1;_V42_REPORT["adv_units"]+=added
    return dict(action,market=(extra+market)[:10])

def agent(observation,configuration=None):
    player=int(observation["player"]);step=int(observation["step"])
    state=_V42_STATE.get(player)
    if state is None or step<=int(state.get("step",-1)):
        state=_V42_STATE[player]={{"step":-1,"decided":False,"active":False}}
        if step==0:_V42_REPORT.update(adv_decisions=0,adv_active_games=0,adv_turns=0,adv_units=0,adv_errors=0)
    state["step"]=step
    action=_V42_PARENT(observation,configuration)
    try:
        if step==216 and not state["decided"]:
            active,s,l=_v42_gate(observation);state.update(decided=True,active=active,similarity=s,lead=l)
            _V42_REPORT["adv_decisions"]+=1
            if active:_V42_REPORT["adv_active_games"]+=1
        if state["active"]:action=_v42_apply(observation,action)
    except Exception:_V42_REPORT["adv_errors"]+=1
    return action

import collections as _v42_collections
agent.telemetry=_v42_collections.ChainMap(_V42_REPORT,getattr(_V42_PARENT,"telemetry",{{}}))
agent=globals().pop("agent")
'''
    src=base.decode("utf-8")+"\n\n"+block+"\n";compile(src,"v42_main.py","exec")
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);pack(out,src.encode())
    print(json.dumps({"decision":"V42_PACKAGE_BUILT","look":look,"sim":sim,"lead":lead,"main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size},sort_keys=True))
if __name__=="__main__":main()
