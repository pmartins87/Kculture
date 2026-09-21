#!/usr/bin/env python3
"""Build deterministic hosted V47 + ALL3 + frozen O-TM1 package. Never submits."""
from __future__ import annotations
import argparse,copy,hashlib,json,tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from kaggle_environments.agent import get_last_callable
from tools.programme_adaptive_expert_gate import acquire_public_main,sha256_bytes
from tools.build_all3_hosted_candidate import (
    BASE_HANDLE,BASE_MAIN_SHA256,WRAPPER as ALL3_WRAPPER,
    deterministic_tar_gz,sha256_file,
)

CANDIDATE_NAME="KCULTURE_V47_ALL3_TM1_V1"
BINDING_SCHEDULE_SHA="c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22"

TM1_TEMPLATE=r'''
# === Kculture O-TM1 wrapper: frozen P2 cross-source consensus schedule ===
_KC_TM1_SCHEDULE = __KC_TM1_SCHEDULE_LITERAL__

def _kc_tm1_own_available(obs):
    p=_kc_plain(obs)
    private=_kc_get(p,"private",{}) or {}
    shed=_kc_get(private,"shed",{}) or {}
    carried={}
    for bag in list(_kc_get(private,"inventories",[]) or []):
        if isinstance(bag,dict):
            for k,v in bag.items():
                carried[str(k)]=carried.get(str(k),0)+max(0,_kc_int(v,0))
    out={}
    keys=set()
    try: keys.update(dict(shed).keys())
    except Exception:
        try: keys.update(shed.keys())
        except Exception: pass
    keys.update(carried.keys())
    for k in keys:
        try: sv=max(0,_kc_int(_kc_get(shed,k,0),0))
        except Exception: sv=0
        out[str(k)]=max(0,sv+max(0,_kc_int(carried.get(str(k),0),0)))
    return out

def _kc_tm1_project_sells(schedule_market,obs):
    m=_kc_copy.deepcopy(list(schedule_market or []))
    avail=_kc_tm1_own_available(obs)
    by_product={}
    for i,o in enumerate(m):
        if isinstance(o,list) and len(o)>=3 and str(o[0])=="SELL":
            p=str(o[1]);q=max(0,_kc_int(o[2],0))
            by_product.setdefault(p,[]).append((i,q))
    for product,items in by_product.items():
        remaining=max(0,_kc_int(avail.get(product,0),0))
        for i,q in items:
            take=min(max(0,q),remaining)
            remaining-=take
            if take<=0:
                m[i]=[]
            else:
                m[i]=["SELL",product,take]
    return m

def _kc_tm1_apply(obs,base,turn):
    b=_kc_canon(base)
    t=_kc_int(turn,0)
    if t<464 or t>591:
        return b
    entry=_KC_TM1_SCHEDULE.get(str(t))
    if entry is None:
        return b
    market=entry.get("market") if isinstance(entry,dict) else entry
    projected=_kc_tm1_project_sells(market,obs)
    return {
        "farmer":_kc_copy.deepcopy(b["farmer"]),
        "hands":_kc_copy.deepcopy(b["hands"]),
        "market":projected,
    }

def _kc_tm1_entrypoint(obs,config=None):
    base=_kc_all3_entrypoint(obs,config)
    return _kc_tm1_apply(obs,base,_kc_step(obs))
# === end Kculture O-TM1 wrapper ===
'''.lstrip("\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schedule",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    schedule_path=Path(args.schedule)
    raw=schedule_path.read_bytes()
    observed_schedule_sha=hashlib.sha256(raw).hexdigest()
    if observed_schedule_sha!=BINDING_SCHEDULE_SHA:
        raise RuntimeError(f"binding schedule SHA mismatch {observed_schedule_sha}")
    sd=json.loads(raw)
    if sd.get("decision")!="V19A_CONSENSUS_SCHEDULE_READY":
        raise RuntimeError("schedule artifact not READY")
    schedule=sd.get("schedule") or {}
    if len(schedule)!=102:
        raise RuntimeError(f"unexpected schedule size {len(schedule)}")
    tm1=TM1_TEMPLATE.replace("__KC_TM1_SCHEDULE_LITERAL__",json.dumps(schedule,sort_keys=True,separators=(",",":")))

    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kculture-all3-tm1-package-") as td:
        root=Path(td)
        base_main,acq=acquire_public_main(BASE_HANDLE,root/"upstream")
        if sha256_bytes(base_main.read_bytes())!=BASE_MAIN_SHA256:
            raise RuntimeError("V47 identity mismatch")
        if acq.get("acquisition")!="output_package" or acq.get("members")!=["main.py"]:
            raise RuntimeError(f"unexpected V47 acquisition {acq}")

        original=base_main.read_text(encoding="utf-8")
        compile(original,"<v47-original>","exec")
        patched=original.rstrip()+"\n\n"+ALL3_WRAPPER.rstrip()+"\n\n"+tm1.rstrip()+"\n"
        compile(patched,"<v47-all3-tm1>","exec")

        stage=root/"stage";stage.mkdir()
        main_py=stage/"main.py";main_py.write_text(patched,encoding="utf-8")
        entry=get_last_callable(patched,path=str(main_py.resolve()))
        entry_name=getattr(entry,"__name__",None)
        if entry_name!="_kc_tm1_entrypoint":
            raise RuntimeError(f"candidate entrypoint mismatch {entry_name}")

        (stage/"ATTRIBUTION.txt").write_text(
            "Kculture hosted candidate provenance\n"
            "===================================\n"
            f"Candidate: {CANDIDATE_NAME}\n"
            f"Base public Kaggle notebook: {BASE_HANDLE}\n"
            f"Base main.py SHA-256: {BASE_MAIN_SHA256}\n"
            f"V19A schedule SHA-256: {BINDING_SCHEDULE_SHA}\n"
            "Modification: first-party ALL3 (O-RW1 + O-TW1 + O-LQ2) plus frozen O-TM1 P2 consensus schedule.\n"
            "No opponent identity, rating, EpisodeId, hidden seed, seat, context id, future state, or outcome feature is used.\n",
            encoding="utf-8"
        )
        archive=out/f"{CANDIDATE_NAME}.tar.gz"
        deterministic_tar_gz(stage,archive)
        receipt={
          "schema":"kculture-v47-all3-tm1-hosted-package-v1",
          "candidate":CANDIDATE_NAME,
          "base_handle":BASE_HANDLE,"base_main_sha256":BASE_MAIN_SHA256,
          "base_acquisition":acq,
          "schedule_sha256":BINDING_SCHEDULE_SHA,
          "scheduled_turns":len(schedule),
          "all3_wrapper_sha256":hashlib.sha256(ALL3_WRAPPER.encode()).hexdigest(),
          "tm1_wrapper_sha256":hashlib.sha256(tm1.encode()).hexdigest(),
          "candidate_main_sha256":sha256_file(main_py),
          "archive":archive.name,"archive_sha256":sha256_file(archive),"archive_bytes":archive.stat().st_size,
          "members":["ATTRIBUTION.txt","main.py"],
          "candidate_hosted_entrypoint":entry_name,
          "automatic_kaggle_submission":False,
        }
        (out/"PACKAGE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        print("V19D_PACKAGE_RESULT",json.dumps(receipt,sort_keys=True),flush=True)

if __name__=="__main__":main()
