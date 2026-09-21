#!/usr/bin/env python3
"""Dormant V21B untouched fresh validation shard."""
from __future__ import annotations
import argparse,hashlib,json,os,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,purge_package_modules
from tools.o_pc1_dev_shard import BASE
from tools.all3_v19c_consensus_fresh_validation import load_schedule
from tools.all3_v21a_semantic_decomposition_shard import (
    MODE_CATS,acquire_exact,build_category_map,run_episode,
)

def load_v21a(path):
    p=Path(path)
    if p.is_dir():
        files=sorted(p.rglob("*.json"))
        if len(files)!=1:raise RuntimeError(f"expected one V21A JSON, found {len(files)}")
        p=files[0]
    raw=p.read_bytes();d=json.loads(raw)
    if d.get("decision")!="V21A_SEMANTIC_WL_HEADROOM":raise RuntimeError("V21A did not authorize V21B")
    mode=str(d.get("selected_mode") or "")
    if mode not in MODE_CATS or mode=="BASE":raise RuntimeError(f"invalid selected mode {mode}")
    return d,mode,hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True);ap.add_argument("--schedule",required=True);ap.add_argument("--v21a",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=5)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());sources=list(cfg["sources"])
    seeds=[int(x) for x in cfg["validation_seeds"]];seats=[int(x) for x in cfg["seats"]]
    if len(sources)!=10 or seeds!=[78901,78902,78903,78904] or seats!=[0,1]:raise SystemExit("frozen V21B population mismatch")
    selected=[s for i,s in enumerate(sources) if i%args.num_shards==args.shard_index]
    schedule,schedule_sha=load_schedule(args.schedule)
    if schedule_sha!=str(cfg["schedule_sha256"]):raise SystemExit("schedule SHA mismatch")
    cats,counts=build_category_map(schedule)
    if counts!={k:int(v) for k,v in cfg["expected_category_counts"].items()}:raise SystemExit("semantic category drift")
    _,mode,v21a_sha=load_v21a(args.v21a)

    rows=[];failures=[];prov={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v21b-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            prov["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            for i,s in enumerate(selected):
                try:
                    main,rec=acquire_exact(str(s["ref"]),str(s["main_sha256"]),root/f"teacher_{i}")
                    teachers[str(s["main_sha256"])]=main;prov[str(s["main_sha256"])]={"ref":s["ref"],"sha":s["main_sha256"],"receipt":rec};time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","ref":s["ref"],"sha":s["main_sha256"],"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)
        if base_main is not None:
            for s in selected:
                opp=teachers.get(str(s["main_sha256"]))
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        key={"rank":s["rank"],"ref":s["ref"],"main_sha256":s["main_sha256"],"seed":seed,"seat":seat}
                        try:
                            b=run_episode(base_main,opp,seed,seat,"BASE",schedule,cats)
                            t=run_episode(base_main,opp,seed,seat,mode,schedule,cats)
                            if [x for x in b["trace"] if int(x[0])<=463] != [x for x in t["trace"] if int(x[0])<=463]:
                                raise RuntimeError("pre-scope trace mismatch")
                            rows.append({**key,"selected_mode":mode,
                                "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                                "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                                "fire_count":t["fire_count"],"fire_turns":t["fire_turns"],"fire_categories":t["fire_categories"]})
                        except Exception as exc:
                            failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(base_main.parent);purge_package_modules(opp.parent)
    expected=len(selected)*len(seeds)*len(seats)
    mech=(not failures and len(rows)==expected and all(r["selected_mode"]==mode for r in rows))
    out={"schema":"kculture-all3-v21b-semantic-fresh-shard-v1","engine":EXPECTED_ENGINE,
         "schedule_sha256":schedule_sha,"v21a_sha256":v21a_sha,"selected_mode":mode,"category_counts":counts,
         "shard_index":args.shard_index,"num_shards":args.num_shards,"expected_pairs":expected,
         "mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":prov,
         "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V21B_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mode":mode,"mechanical_pass":mech,"pairs":len(rows),"fires":sum(int(r["fire_count"])>0 for r in rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
