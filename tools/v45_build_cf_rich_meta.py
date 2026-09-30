#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,json,tarfile
from pathlib import Path

BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
ITEMS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
ANIMALS=("COW","SHEEP","GOOSE")
ADV_ITEMS=("STRAWBERRY","WOOL","EGG","MILK","MELON","CARROT","TOMATO")

def sha(b): return hashlib.sha256(b).hexdigest()
def pack(path,main):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w") as tf:
        i=tarfile.TarInfo("main.py");i.size=len(main);i.mtime=0;i.uid=i.gid=0;i.mode=0o644
        tf.addfile(i,io.BytesIO(main))
    with open(path,"wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0) as gz:gz.write(raw.getvalue())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-package",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    model=json.loads(Path(a.model).read_text())
    if model.get("decision")!="V45_CF_RICH_TREE_GATE_PASS":
        raise SystemExit("V45 model did not pass")
    names=model["feature_names"];tree=model["model"]["tree"]
    with tarfile.open(a.base_package,"r:*") as tf: base=tf.extractfile("main.py").read()
    if sha(base)!=BASE_MAIN_SHA: raise SystemExit("base main SHA mismatch")

    block=f'''
# ===========================================================================
# V45 COUNTERFACTUAL-RICH PUBLIC-STATE META CONTROLLER
# Trained on exact V30B counterfactual trajectories. The exact final V30B
# entrypoint runs first. Public state is observed passively; at step 216 a
# shallow tree chooses ADV lookahead 0/4/8/12. Physical policy is untouched.
# ===========================================================================
_V45_PARENT=[v for v in list(globals().values()) if callable(v)][-1]
_V45_NAMES={names!r}
_V45_TREE={tree!r}
_V45_ITEMS={ITEMS!r}
_V45_CROPS={CROPS!r}
_V45_ANIMALS={ANIMALS!r}
_V45_ADV_ITEMS={ADV_ITEMS!r}
_V45_STATE={{}}
_V45_HISTORY={{}}
_V45_REPORT=dict(meta_decisions=0,look0=0,look4=0,look8=0,look12=0,
                 adv_turns=0,adv_units=0,errors=0)

def _v45_counts(farm):
    c={{k:0 for k in _V45_CROPS}};a={{k:0 for k in _V45_ANIMALS}};kinds={{}}
    for row in (farm.get("tiles") or []):
        for t in row:
            if not isinstance(t,dict):continue
            x=t.get("crop");y=t.get("animal");z=t.get("kind")
            if x in c:c[x]+=1
            if y in a:a[y]+=1
            if z:kinds[z]=kinds.get(z,0)+1
    return c,a,kinds

def _v45_snapshot(obs):
    market=obs.get("market") or {{}};inv=market.get("inventory") or {{}};pr=market.get("prices") or {{}}
    return {{"inv":{{i:float(inv.get(i,10000) or 0) for i in _V45_ITEMS}},
             "price":{{i:float(pr.get(i,0) or 0) for i in _V45_ITEMS}}}}

def _v45_features(obs):
    p=int(obs["player"]);q=1-p;farms=obs.get("farms") or [{{}},{{}}]
    own=farms[p];opp=farms[q]
    oc,oa,ok=_v45_counts(own);qc,qa,qk=_v45_counts(opp)
    race=(_V9_RACE.get(p) or {{}})
    try:sim=float(_r37_similarity(obs))
    except Exception:sim=0.0
    vals={{"similarity":sim,"lead":float(race.get("lead",-12) or -12),"seat":float(p),
          "own_money":float(own.get("money",0) or 0),"opp_money":float(opp.get("money",0) or 0),
          "money_diff":float(own.get("money",0) or 0)-float(opp.get("money",0) or 0),
          "own_hands":float(len(own.get("hands") or [])),"opp_hands":float(len(opp.get("hands") or [])),
          "hands_diff":float(len(own.get("hands") or []))-float(len(opp.get("hands") or [])),
          "own_quads":float(len(own.get("unlocked_quadrants") or [])),
          "opp_quads":float(len(opp.get("unlocked_quadrants") or []))}}
    for k in _V45_CROPS:
        vals["own_crop_"+k]=float(oc[k]);vals["opp_crop_"+k]=float(qc[k]);vals["crop_diff_"+k]=float(oc[k]-qc[k])
    for k in _V45_ANIMALS:
        vals["own_animal_"+k]=float(oa[k]);vals["opp_animal_"+k]=float(qa[k]);vals["animal_diff_"+k]=float(oa[k]-qa[k])
    for kind in ("PLANT","PASTURE","COOP"):
        vals["own_kind_"+kind]=float(ok.get(kind,0));vals["opp_kind_"+kind]=float(qk.get(kind,0))
    h=_V45_HISTORY[p]
    now=h[216]
    for lag in (0,24,48):
        s=now if lag==0 else h[216-lag]
        for it in _V45_ITEMS:
            vals[f"inv_{{it}}_lag{{lag}}"]=s["inv"][it]
            vals[f"price_{{it}}_lag{{lag}}"]=s["price"][it]
    for it in _V45_ITEMS:
        vals[f"inv_delta24_{{it}}"]=vals[f"inv_{{it}}_lag0"]-vals[f"inv_{{it}}_lag24"]
        vals[f"inv_delta48_{{it}}"]=vals[f"inv_{{it}}_lag0"]-vals[f"inv_{{it}}_lag48"]
        vals[f"price_delta24_{{it}}"]=vals[f"price_{{it}}_lag0"]-vals[f"price_{{it}}_lag24"]
    return vals

def _v45_predict(vals):
    t=_V45_TREE;node=0
    while True:
        fi=int(t["feature"][node])
        if fi<0:
            counts=t["value"][node];idx=max(range(len(counts)),key=lambda i:counts[i])
            return int(t["classes"][idx])
        name=_V45_NAMES[fi];thr=float(t["threshold"][node])
        node=int(t["children_left"][node] if float(vals.get(name,0.0))<=thr else t["children_right"][node])

def _v45_future(player,step,look):
    native=_IMPL.chassis.players.get(player)
    if not native or native.get("route") not in _IMPL.chassis.routes:return []
    route=native["route"];out=[];first=None
    for off in range(1,look+1):
        t=step+off
        if t>718:break
        tape=_IMPL.chassis.routes[2 if t>=648 else route]
        for o in (tape[t].get("market") or []):
            if not o or len(o)<3:continue
            if first is None:first=o
            if o[0]=="SELL" and o[1] in _V45_ADV_ITEMS:
                try:q=max(0,int(o[2]))
                except Exception:q=0
                if q>0:out.append((t,o[1],q))
    protected=first[1] if first is not None and first[0]=="SELL" else None
    return [(t,i,q) for t,i,q in out if i!=protected]

def _v45_apply(obs,action,look):
    step=int(obs["step"]);player=int(obs["player"])
    if look<=0 or step<216 or step>=718 or step%24==23:return action
    plan=_v45_future(player,step,look)
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
    _V45_REPORT["adv_turns"]+=1;_V45_REPORT["adv_units"]+=added
    return dict(action,market=(extra+market)[:10])

def v45_adaptive_agent(observation,configuration=None):
    p=int(observation["player"]);step=int(observation["step"])
    st=_V45_STATE.get(p)
    if st is None or step<int(st.get("step",-1)):
        st=_V45_STATE[p]={{"step":-1,"decided":False,"look":0,"active":False}}
        _V45_HISTORY[p]={{}}
        if step==0:
            _V45_REPORT.update(meta_decisions=0,look0=0,look4=0,look8=0,look12=0,
                               adv_turns=0,adv_units=0,errors=0)
    st["step"]=step

    # Exactly as in the counterfactual feature collector: parent first.
    action=_V45_PARENT(observation,configuration)
    try:
        _V45_HISTORY[p][step]=_v45_snapshot(observation)
        if step==216 and not st["decided"]:
            vals=_v45_features(observation)
            look=_v45_predict(vals)
            active=bool(float(vals.get("similarity",0.0))>=0.95 or float(vals.get("lead",-12.0))>=4.0)
            st.update(decided=True,look=int(look),active=active)
            _V45_REPORT["meta_decisions"]+=1
            _V45_REPORT["look"+str(int(look))]+=1
        if st["active"] and st["look"]>0:
            action=_v45_apply(observation,action,st["look"])
    except Exception:
        _V45_REPORT["errors"]+=1
    return action

import collections as _v45_collections
v45_adaptive_agent.telemetry=_v45_collections.ChainMap(_V45_REPORT,getattr(_V45_PARENT,"telemetry",{{}}))
'''
    src=base.decode("utf-8")+"\n\n"+block+"\n"
    compile(src,"v45_main.py","exec")
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);pack(out,src.encode())
    print(json.dumps({{"decision":"V45_PACKAGE_BUILT","main_sha":sha(src.encode()),
          "archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size}},sort_keys=True))

if __name__=="__main__": main()
