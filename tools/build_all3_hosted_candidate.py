#!/usr/bin/env python3
"""Build hosted-faithful exact V47 + O-RW1 + O-TW1 + O-LQ2 candidate.

The exact public V47 output package is acquired transiently and SHA-pinned.
Only a standalone first-party ALL3 wrapper is appended to main.py.

This tool never submits to Kaggle.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
import tempfile
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from kaggle_environments.agent import get_last_callable
from tools.programme_adaptive_expert_gate import acquire_public_main,sha256_bytes

BASE_HANDLE="ahmedberatozer/kaggriculture-v47-reactive-market-coordination"
BASE_MAIN_SHA256="f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842"
CANDIDATE_NAME="KCULTURE_V47_ALL3_V1"

WRAPPER=r'''
# === Kculture ALL3 wrapper: O-RW1 + O-TW1 + O-LQ2 ===
# Frozen first-party integrated host 2026-09-19.
# Exact pinned V47 hosted entrypoint: _y_agent_shopherd.
import copy as _kc_copy

_KC_ALL3_BASE_AGENT = _y_agent_shopherd
_KC_ALL3_RW_USED = False
_KC_ALL3_TW_USED = False
_KC_ALL3_WHEAT_SHOPS = {
    "BAKERY","PIZZA_SHOP","BRUNCH_SPOT","ICE_CREAM_SHOP","FARMERS_MARKET"
}
_KC_ALL3_ANIMAL_STRUCTURES = {"COW":"PASTURE","SHEEP":"PASTURE","GOOSE":"COOP"}

def _kc_get(obj,key,default=None):
    if isinstance(obj,dict):
        return obj.get(key,default)
    try:
        return obj[key]
    except Exception:
        try:
            return getattr(obj,key)
        except Exception:
            return default

def _kc_plain(x):
    if isinstance(x,dict):
        return {str(k):_kc_plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [_kc_plain(v) for v in x]
    if hasattr(x,"item"):
        try:
            return x.item()
        except Exception:
            pass
    if hasattr(x,"items"):
        try:
            return {str(k):_kc_plain(v) for k,v in x.items()}
        except Exception:
            pass
    return x

def _kc_int(x,default=0):
    try:
        return int(x)
    except Exception:
        return default

def _kc_canon(action):
    a=_kc_plain(action or {"farmer":["PASS"],"hands":[],"market":[]})
    if not isinstance(a,dict):
        return action
    return {
        "farmer":list(a.get("farmer") or ["PASS"]),
        "hands":[list(x) for x in list(a.get("hands") or [])],
        "market":[list(x) for x in list(a.get("market") or [])],
    }

def _kc_step(obs):
    return _kc_int(_kc_get(obs,"step",0),0)

def _kc_own_shed(obs):
    p=_kc_plain(obs)
    private=_kc_get(p,"private",{}) or {}
    shed=_kc_get(private,"shed",{}) or {}
    try:
        items=dict(shed).items()
    except Exception:
        try:
            items=shed.items()
        except Exception:
            items=[]
    return {str(k):max(0,_kc_int(v,0)) for k,v in items}

def _kc_own_item(obs,item):
    return max(0,_kc_int(_kc_own_shed(obs).get(item,0),0))

def _kc_town_wheat_demand(step,obs,config):
    shop_interval=max(1,_kc_int(_kc_get(config or {},"townShopSellInterval",4),4))
    center_interval=max(1,_kc_int(_kc_get(config or {},"townCenterSellInterval",24),24))
    demand=0
    if step % shop_interval == 0:
        p=_kc_plain(obs)
        town=_kc_get(p,"town",{}) or {}
        for shop in list(_kc_get(town,"unlocked_shops",[]) or []):
            if shop in _KC_ALL3_WHEAT_SHOPS:
                demand += 1
    if step % center_interval == 0:
        demand += 1
    return demand

def _kc_wheat_sell_qty(action):
    a=_kc_canon(action)
    total=0
    for order in list(a["market"] or []):
        if isinstance(order,(list,tuple)) and len(order)>=3 and str(order[0])=="SELL" and str(order[1])=="WHEAT":
            total += max(0,_kc_int(order[2],0))
    return total

def _kc_tw_eligible(obs,config,base):
    step=_kc_step(obs)
    if step<0 or step>671:
        return False
    qty=_kc_wheat_sell_qty(base)
    return (
        _kc_town_wheat_demand(step,obs,config)>0
        and qty>0
        and _kc_own_item(obs,"WHEAT")>=qty
    )

def _kc_apply_tw(base):
    a=_kc_canon(base)
    market=[]
    removed=0
    for order in list(a["market"] or []):
        if isinstance(order,(list,tuple)) and len(order)>=3 and str(order[0])=="SELL" and str(order[1])=="WHEAT":
            removed += max(0,_kc_int(order[2],0))
        else:
            market.append(_kc_copy.deepcopy(order))
    if removed<=0:
        return a
    return {"farmer":_kc_copy.deepcopy(a["farmer"]),"hands":_kc_copy.deepcopy(a["hands"]),"market":market}

def _kc_rw_eligible(obs,base):
    step=_kc_step(obs)
    a=_kc_canon(base)
    return 0<=step<=671 and a["market"]==[] and _kc_own_item(obs,"WOOL")>=2

def _kc_apply_rw(base):
    a=_kc_canon(base)
    return {
        "farmer":_kc_copy.deepcopy(a["farmer"]),
        "hands":_kc_copy.deepcopy(a["hands"]),
        "market":[["SELL","WOOL",2]],
    }

def _kc_shed_adjacent(pos,board_size):
    half=board_size//2
    return tuple(pos) in {
        (half-1,half-1),(half,half-1),(half-1,half),(half,half)
    }

def _kc_shed_total(shed):
    return sum(max(0,_kc_int(v,0)) for v in shed.values())

def _kc_project_shed(obs,config,action):
    p=_kc_plain(obs)
    player=_kc_int(_kc_get(p,"player",0),0)
    farms=list(_kc_get(p,"farms",[]) or [])
    if player<0 or player>=len(farms):
        return _kc_own_shed(obs)
    farm=_kc_copy.deepcopy(farms[player])
    private=_kc_copy.deepcopy(_kc_get(p,"private",{}) or {})
    raw_shed=_kc_get(private,"shed",{}) or {}
    try:
        shed={str(k):max(0,_kc_int(v,0)) for k,v in dict(raw_shed).items()}
    except Exception:
        shed={str(k):max(0,_kc_int(v,0)) for k,v in raw_shed.items()}
    inventories=[
        {str(k):max(0,_kc_int(v,0)) for k,v in dict(inv or {}).items()}
        for inv in list(_kc_get(private,"inventories",[]) or [])
    ]
    a=_kc_canon(action)
    unit_actions=[a["farmer"],*a["hands"]]
    tiles=farm.get("tiles") or []
    board_size=max(2,_kc_int(_kc_get(config or {},"boardSize",len(tiles)),10))
    capacity=max(0,_kc_int(_kc_get(config or {},"shedCapacity",100),100))
    farmer_pos=list(farm.get("farmer") or [])
    hand_pos=list(farm.get("hands") or [])
    while len(inventories)<len(unit_actions):
        inventories.append({})

    for idx,ua in enumerate(unit_actions):
        if not isinstance(ua,list) or not ua:
            continue
        pos=farmer_pos if idx==0 else (hand_pos[idx-1] if idx-1<len(hand_pos) else None)
        if not pos or len(pos)<2:
            continue
        x,y=_kc_int(pos[0],-1),_kc_int(pos[1],-1)
        inv=inventories[idx]
        op=str(ua[0])

        if op=="DROP":
            if not _kc_shed_adjacent((x,y),board_size):
                continue
            for item,n0 in list(inv.items()):
                n=max(0,_kc_int(n0,0))
                room=max(0,capacity-_kc_shed_total(shed))
                take=min(n,room)
                if take>0:
                    shed[item]=shed.get(item,0)+take
                    inv[item]-=take
            continue

        if op=="PICKUP":
            if not _kc_shed_adjacent((x,y),board_size) or len(ua)<2:
                continue
            item=str(ua[1])
            n=_kc_int(ua[2],1) if len(ua)>=3 else 1
            n=min(max(0,n),max(0,shed.get(item,0)))
            if n>0:
                shed[item]=shed.get(item,0)-n
                inv[item]=inv.get(item,0)+n
            continue

        if op=="PLACE":
            if len(ua)<2:
                continue
            item=str(ua[1])
            tile=None
            if 0<=y<len(tiles) and 0<=x<len(tiles[y]):
                tile=tiles[y][x]
            if item in _KC_ALL3_ANIMAL_STRUCTURES and isinstance(tile,dict) and str(tile.get("kind"))==_KC_ALL3_ANIMAL_STRUCTURES[item] and "animal" not in tile:
                if inv.get(item,0)>0:
                    inv[item]-=1
                continue
            if not _kc_shed_adjacent((x,y),board_size):
                continue
            n=_kc_int(ua[2],1) if len(ua)>=3 else 1
            n=min(max(0,n),max(0,inv.get(item,0)))
            room=max(0,capacity-_kc_shed_total(shed))
            n=min(n,room)
            if n>0:
                inv[item]=inv.get(item,0)-n
                shed[item]=shed.get(item,0)+n
    return shed

def _kc_is_sell(order):
    return isinstance(order,list) and len(order)>=3 and str(order[0])=="SELL"

def _kc_project_non_sell(order,shed,capacity):
    if not isinstance(order,list) or not order:
        return
    op=str(order[0])
    if op not in ("BUY_PRODUCT","BUY_ANIMAL") or len(order)<2:
        return
    item=str(order[1])
    qty=max(0,_kc_int(order[2],1) if len(order)>=3 else 1)
    room=max(0,capacity-_kc_shed_total(shed))
    take=min(qty,room)
    if take>0:
        shed[item]=shed.get(item,0)+take

def _kc_canonicalize_sell_run(run,shed):
    first_order=[]
    totals={}
    templates={}
    for raw in run:
        order=_kc_copy.deepcopy(list(raw))
        product=str(order[1])
        q=max(0,_kc_int(order[2],0))
        if product not in totals:
            first_order.append(product)
            totals[product]=0
            templates[product]=order
        totals[product]+=q
    emitted=[]
    for product in first_order:
        avail=max(0,_kc_int(shed.get(product,0),0))
        take=min(max(0,totals[product]),avail)
        shed[product]=max(0,avail-take)
        if take<=0:
            continue
        order=_kc_copy.deepcopy(templates[product])
        order[2]=take
        emitted.append(order)
    return emitted + [[] for _ in range(max(0,len(run)-len(emitted)))]

def _kc_apply_lq2(obs,config,action):
    a=_kc_canon(action)
    if _kc_step(obs)<336:
        return a
    shed=_kc_project_shed(obs,config,a)
    capacity=max(0,_kc_int(_kc_get(config or {},"shedCapacity",100),100))
    market=_kc_copy.deepcopy(a["market"])
    out=[]
    i=0
    while i<len(market):
        order=market[i]
        if _kc_is_sell(order):
            j=i
            run=[]
            while j<len(market) and _kc_is_sell(market[j]):
                run.append(market[j])
                j+=1
            out.extend(_kc_canonicalize_sell_run(run,shed))
            i=j
            continue
        out.append(_kc_copy.deepcopy(order))
        _kc_project_non_sell(order,shed,capacity)
        i+=1
    return {"farmer":_kc_copy.deepcopy(a["farmer"]),"hands":_kc_copy.deepcopy(a["hands"]),"market":out}

def _kc_all3_entrypoint(obs,config=None):
    global _KC_ALL3_RW_USED,_KC_ALL3_TW_USED
    step=_kc_step(obs)
    if step<=1:
        _KC_ALL3_RW_USED=False
        _KC_ALL3_TW_USED=False

    base=_kc_canon(_KC_ALL3_BASE_AGENT(obs,config))
    out=base

    if (not _KC_ALL3_TW_USED) and _kc_tw_eligible(obs,config,base):
        out=_kc_apply_tw(base)
        _KC_ALL3_TW_USED=True
    elif (not _KC_ALL3_RW_USED) and _kc_rw_eligible(obs,base):
        out=_kc_apply_rw(base)
        _KC_ALL3_RW_USED=True

    out=_kc_apply_lq2(obs,config,out)
    return out

# IMPORTANT: no callable definitions may appear after _kc_all3_entrypoint.
# === end Kculture ALL3 wrapper ===
'''.lstrip("\n")

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def deterministic_tar_gz(src:Path,dst:Path)->None:
    files=sorted(p for p in src.rglob("*") if p.is_file())
    with dst.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode="w") as tf:
                for p in files:
                    rel=p.relative_to(src).as_posix()
                    data=p.read_bytes()
                    ti=tarfile.TarInfo(rel)
                    ti.size=len(data);ti.mtime=0;ti.uid=0;ti.gid=0;ti.uname="";ti.gname="";ti.mode=0o644
                    tf.addfile(ti,io.BytesIO(data))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out-dir",required=True);args=ap.parse_args()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kculture-all3-package-") as td:
        root=Path(td)
        base_main,acq=acquire_public_main(BASE_HANDLE,root/"upstream")
        observed=sha256_bytes(base_main.read_bytes())
        if observed!=BASE_MAIN_SHA256:
            raise RuntimeError(f"V47 identity mismatch {observed}")
        if acq.get("acquisition")!="output_package":
            raise RuntimeError("ALL3 build requires exact public V47 output package")
        if acq.get("members")!=["main.py"]:
            raise RuntimeError(f"unexpected V47 package members {acq.get('members')}")

        stage=root/"stage";stage.mkdir()
        original=base_main.read_text(encoding="utf-8")
        if "_KC_ALL3_BASE_AGENT" in original:
            raise RuntimeError("upstream already contains ALL3 marker")
        compile(original,"<v47-original>","exec")
        patched=original.rstrip()+"\n\n"+WRAPPER.rstrip()+"\n"
        compile(patched,"<v47-all3>","exec")
        staged=stage/"main.py";staged.write_text(patched,encoding="utf-8")

        base_entry=get_last_callable(original,path=str(base_main.resolve()))
        cand_entry=get_last_callable(patched,path=str(staged.resolve()))
        base_name=getattr(base_entry,"__name__",None)
        cand_name=getattr(cand_entry,"__name__",None)
        if base_name!="_y_agent_shopherd":
            raise RuntimeError(f"unexpected V47 hosted entrypoint {base_name}")
        if cand_name!="_kc_all3_entrypoint":
            raise RuntimeError(f"candidate entrypoint mismatch {cand_name}")

        (stage/"ATTRIBUTION.txt").write_text(
            "Kculture hosted candidate provenance\n"
            "===================================\n"
            f"Candidate: {CANDIDATE_NAME}\n"
            f"Base public Kaggle notebook: {BASE_HANDLE}\n"
            f"Base main.py SHA-256: {BASE_MAIN_SHA256}\n"
            f"Base output archive SHA-256: {acq.get('archive_sha256')}\n"
            "Modification: Kculture first-party O-RW1 + O-TW1 + O-LQ2 wrapper only.\n"
            "No opponent identity, rating, EpisodeId, hidden seed, future state, or opponent-private state is used.\n",
            encoding="utf-8"
        )

        archive=out/f"{CANDIDATE_NAME}.tar.gz"
        deterministic_tar_gz(stage,archive)
        receipt={
            "schema":"kculture-v47-all3-hosted-package-v1",
            "candidate":CANDIDATE_NAME,
            "base_handle":BASE_HANDLE,
            "base_main_sha256":BASE_MAIN_SHA256,
            "base_acquisition":acq,
            "wrapper_sha256":hashlib.sha256(WRAPPER.encode()).hexdigest(),
            "candidate_main_sha256":sha256_file(staged),
            "archive":archive.name,
            "archive_sha256":sha256_file(archive),
            "archive_bytes":archive.stat().st_size,
            "members":["ATTRIBUTION.txt","main.py"],
            "base_hosted_entrypoint":base_name,
            "candidate_hosted_entrypoint":cand_name,
            "automatic_kaggle_submission":False,
        }
        (out/"PACKAGE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        print("ALL3_PACKAGE_RESULT",json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
