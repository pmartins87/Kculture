#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,tarfile
from pathlib import Path

EXPECTED_BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
BLOCK=r'''# V37-C own late-day idle-harvest rescue.
import copy as _v37c_copy
_V37C_PARENT=agent
_V37C_STATS={"calls":0,"harvests":0,"units":0,"errors":0}

def _v37c_inventory_total(private):
    shed=sum(max(0,int(v or 0)) for v in (private.get("shed") or {}).values())
    carried=sum(sum(max(0,int(v or 0)) for v in (inv or {}).values()) for inv in (private.get("inventories") or []))
    return shed+carried

def _v37c_rescue(obs,action):
    step=int(obs.get("step",0) or 0)
    hour=step%24
    if hour<20 or step>=696:return action
    seat=int(obs.get("player",0) or 0)
    farms=obs.get("farms") or []
    if seat>=len(farms):return action
    farm=farms[seat];private=obs.get("private") or {}
    positions=[farm.get("farmer")]+list(farm.get("hands") or [])
    commands=[action.get("farmer") or ["PASS"]]+list(action.get("hands") or [])
    commands += [["PASS"] for _ in range(max(0,len(positions)-len(commands)))]
    capacity_left=max(0,96-_v37c_inventory_total(private))
    if capacity_left<=0:return action
    changed=False;rescued=0
    for i,(pos,cmd) in enumerate(zip(positions,commands)):
        if capacity_left<=0:break
        if cmd!=["PASS"] or not isinstance(pos,(list,tuple)) or len(pos)<2:continue
        try:tile=farm["tiles"][int(pos[1])][int(pos[0])]
        except Exception:continue
        if not isinstance(tile,dict) or int(tile.get("yield_units",0) or 0)<=0:continue
        # Harvest only real yield; this never replaces a planned non-PASS action.
        units=max(1,int(tile.get("yield_units",0) or 0))
        if units>capacity_left:continue
        commands[i]=["HARVEST"];capacity_left-=units;rescued+=units;changed=True
        _V37C_STATS["harvests"]+=1;_V37C_STATS["units"]+=units
    if not changed:return action
    out=_v37c_copy.deepcopy(action);out["farmer"]=commands[0];out["hands"]=commands[1:len(positions)]
    return out

def agent(observation,configuration=None):
    _V37C_STATS["calls"]+=1
    base=_V37C_PARENT(observation,configuration)
    try:return _v37c_rescue(observation,base)
    except Exception:
        _V37C_STATS["errors"]+=1
        return base
agent.telemetry=_V37C_STATS
agent=globals().pop("agent")
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
    if sha(base)!=EXPECTED_BASE_MAIN_SHA:raise SystemExit("base sha mismatch")
    src=base.decode()+"\n\n"+BLOCK+"\n";compile(src,"v37c_main.py","exec");pack(a.output,src.encode())
    out=Path(a.output);print({"decision":"V37C_PACKAGE_BUILT","main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size})
if __name__=="__main__":main()
