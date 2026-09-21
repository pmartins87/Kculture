#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,purge_package_modules
from tools.o_pc1_dev_shard import BASE
from tools.all3_v19c_consensus_fresh_validation import acquire_exact,run_episode,prefire_parity,load_schedule

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True);ap.add_argument("--schedule",required=True)
    ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4)
    ap.add_argument("--out",required=True);args=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    cfg=json.loads(Path(args.config).read_text());all_sources=list(cfg.get("sources") or [])
    seeds=[int(x) for x in cfg.get("seeds") or []];seats=[int(x) for x in cfg.get("seats") or []]
    if len(all_sources)!=10 or seeds!=[78601,78602,78603,78604] or seats!=[0,1]:
        raise SystemExit("frozen V19C population mismatch")
    selected=[s for i,s in enumerate(all_sources) if i%args.num_shards==args.shard_index]
    schedule,schedule_sha=load_schedule(args.schedule)
    rows=[];failures=[];provenance={};started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"v19c-s{args.shard_index}-") as td:
        root=Path(td)
        try:
            base_main,rec=acquire_exact(BASE["handle"],BASE["expected_main_sha256"],root/"base")
            provenance["base"]={"ref":BASE["handle"],"sha":BASE["expected_main_sha256"],"receipt":rec}
        except Exception as exc:
            base_main=None;failures.append({"phase":"base_acquire","error":f"{type(exc).__name__}: {exc}"})
        teachers={}
        if base_main is not None:
            for i,s in enumerate(selected):
                try:
                    main,rec=acquire_exact(str(s["ref"]),str(s["main_sha256"]),root/f"teacher_{i}")
                    teachers[str(s["main_sha256"])]=main
                    provenance[str(s["main_sha256"])]={"ref":s["ref"],"sha":s["main_sha256"],"receipt":rec}
                    time.sleep(1.0)
                except Exception as exc:
                    failures.append({"phase":"teacher_acquire","rank":s["rank"],"ref":s["ref"],"sha":s["main_sha256"],"error":f"{type(exc).__name__}: {exc}"})
        for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"):os.environ.pop(k,None)

        if base_main is not None:
            for s in selected:
                opp=teachers.get(str(s["main_sha256"]))
                if opp is None:continue
                for seed in seeds:
                    for seat in seats:
                        key={"rank":s["rank"],"ref":s["ref"],"main_sha256":s["main_sha256"],"seed":seed,"seat":seat}
                        try:
                            b=run_episode(base_main,opp,seed,seat,False,schedule)
                            t=run_episode(base_main,opp,seed,seat,True,schedule)
                            if not prefire_parity(b,t):raise RuntimeError("pre-fire parity failure")
                            rows.append({**key,
                              "base_score":b["score"],"treatment_score":t["score"],"score_delta":float(t["score"])-float(b["score"]),
                              "base_margin":b["margin"],"treatment_margin":t["margin"],"margin_delta":float(t["margin"])-float(b["margin"]),
                              "fire_count":t["fire_count"],"fire_turns":[int(x["turn"]) for x in t["fire_meta"]]})
                        except Exception as exc:
                            failures.append({**key,"phase":"pair","error":f"{type(exc).__name__}: {exc}"})
                        finally:
                            purge_package_modules(base_main.parent);purge_package_modules(opp.parent)

    expected=len(selected)*len(seeds)*len(seats)
    mech=(not failures and len(rows)==expected)
    out={"schema":"kculture-all3-v19c-consensus-fresh-shard-v1","engine":EXPECTED_ENGINE,
         "schedule_sha256":schedule_sha,"shard_index":args.shard_index,"num_shards":args.num_shards,
         "selected_sources":[s["main_sha256"] for s in selected],"expected_pairs":expected,
         "mechanical_pass":mech,"rows":rows,"failures":failures,"provenance":provenance,
         "seconds":time.perf_counter()-started,"automatic_kaggle_submission":False}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V19C_SHARD_RESULT",json.dumps({"shard":args.shard_index,"mechanical_pass":mech,"pairs":len(rows),"failures":len(failures)},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
