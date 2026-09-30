#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,hashlib,io,json,tarfile
from pathlib import Path

BASE_MAIN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"

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
    if model.get("decision")!="V41_ADAPTIVE_GATE_PASS":raise SystemExit("model did not pass gate")
    rule=model["best_rule"];low=int(rule["low"]);sim=float(rule["sim"]);lead=float(rule["lead"])
    with tarfile.open(a.base_package,"r:*") as tf:base=tf.extractfile("main.py").read()
    if sha(base)!=BASE_MAIN_SHA:raise SystemExit("base main sha mismatch")
    block=f'''
# ===========================================================================
# V41 ADAPTIVE RACE META-CONTROLLER
# Learned on hosted replay counterfactuals with a temporal holdout.
# It does not replace the V30B policy.  It only selects the minimum sale-race
# reservation horizon after step 216, from public opponent evidence observed
# through step 215.  The underlying V9 RACE mechanism remains adaptive and may
# raise the effective horizon further when it observes a rival sale lead.
# ===========================================================================
_V41_PARENT = agent
del agent
_V41_LOW = {low}
_V41_SIM = {sim!r}
_V41_LEAD = {lead!r}
_V41_META_STATE = {{}}
_V41_META_REPORT = dict(meta_decisions=0, meta_low=0, meta_base=0, meta_errors=0)

def _v41_choose(obs):
    player=int(obs["player"])
    race=(_V9_RACE.get(player) or {{}})
    observed_lead=float(race.get("lead",-12) or -12)
    try:
        similarity=float(_r37_similarity(obs))
    except Exception:
        similarity=0.0
    horizon=44 if similarity>=_V41_SIM or observed_lead>=_V41_LEAD else _V41_LOW
    return int(horizon), similarity, observed_lead

def agent(observation,configuration=None):
    player=int(observation["player"]);step=int(observation["step"])
    state=_V41_META_STATE.get(player)
    if state is None or step<=int(state.get("step",-1)):
        state=_V41_META_STATE[player]={{"step":-1,"chosen":None}}
        if step==0:
            V9_RACE_DEFAULT=44
            globals()["V9_RACE_DEFAULT"]=44
            _V41_META_REPORT.update(meta_decisions=0,meta_low=0,meta_base=0,meta_errors=0)
    state["step"]=step
    try:
        if step>=216:
            if state["chosen"] is None:
                h,simv,leadv=_v41_choose(observation)
                state.update(chosen=h,similarity=simv,observed_lead=leadv)
                _V41_META_REPORT["meta_decisions"]+=1
                _V41_META_REPORT["meta_base" if h==44 else "meta_low"]+=1
            globals()["V9_RACE_DEFAULT"]=int(state["chosen"])
        else:
            globals()["V9_RACE_DEFAULT"]=44
    except Exception:
        _V41_META_REPORT["meta_errors"]+=1
        globals()["V9_RACE_DEFAULT"]=44
    return _V41_PARENT(observation,configuration)

import collections as _v41_collections
agent.telemetry=_v41_collections.ChainMap(_V41_META_REPORT,getattr(_V41_PARENT,"telemetry",{{}}))
agent=globals().pop("agent")
'''
    src=base.decode("utf-8")+"\n\n"+block+"\n"
    compile(src,"v41_adaptive_main.py","exec")
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);pack(out,src.encode())
    print(json.dumps({{"decision":"V41_ADAPTIVE_PACKAGE_BUILT","rule":rule,"main_sha":sha(src.encode()),"archive_sha":sha(out.read_bytes()),"bytes":out.stat().st_size}},sort_keys=True))
if __name__=="__main__":main()
