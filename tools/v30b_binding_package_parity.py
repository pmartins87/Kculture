#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,shutil,tarfile,gzip,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,score

FROZEN_SHA="4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01"
FROZEN_REF="arsgorynich/herd-safe-v3-experimental-risk-aware-feed"
PARITY_SEEDS=(80509,80510)
SEATS=(0,1)

def find_candidate(root:Path):
    man=json.loads((root/"MANIFEST.json").read_text())
    for s in man["sources"]:
        if str(s["sha"])==FROZEN_SHA:
            p=root/s["path"]
            if sha256_bytes(p.read_bytes())!=FROZEN_SHA: raise RuntimeError("candidate SHA mismatch")
            if str(s.get("representative_ref"))!=FROZEN_REF: raise RuntimeError("candidate ref mismatch")
            return p,s,man
    raise RuntimeError("candidate absent")

def deterministic_tar(src:Path,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    with open(out,"wb") as raw:
      with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as gz:
       with tarfile.open(fileobj=gz,mode="w") as tf:
        for p in sorted(src.rglob("*"),key=lambda x:x.as_posix()):
            rel=p.relative_to(src).as_posix()
            info=tf.gettarinfo(str(p),arcname=rel)
            info.uid=0;info.gid=0;info.uname="";info.gname="";info.mtime=0
            if p.is_file():
                with open(p,"rb") as f: tf.addfile(info,f)
            else: tf.addfile(info)
    return hashlib.sha256(out.read_bytes()).hexdigest()

def episode(agent_main:Path,opp_main:Path,seed:int,seat:int):
    purge_package_modules(agent_main.parent);purge_package_modules(opp_main.parent)
    ag=load_public_agent(agent_main);opp=load_public_agent(opp_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    env.run([ag,opp] if seat==0 else [opp,ag])
    rep=env.toJSON();st=[str(x) for x in rep.get("statuses",[])]
    rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw):
        raise RuntimeError(f"invalid terminal {st} {rw} {steps}")
    mine,other=(rw[0],rw[1]) if seat==0 else (rw[1],rw[0])
    return {"rewards":rw,"score":float(score(mine-other)),"margin":float(mine-other),"steps":steps}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v30a-snapshot",required=True);ap.add_argument("--package-dir",required=True);ap.add_argument("--archive",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")

    root=Path(a.v30a_snapshot);cand,cmeta,man=find_candidate(root)
    pkg=Path(a.package_dir)
    if pkg.exists(): shutil.rmtree(pkg)
    shutil.copytree(cand.parent,pkg)
    packaged_main=pkg/cand.name
    if packaged_main.name!="main.py":
        target=pkg/"main.py"
        if target.exists(): raise RuntimeError("package main.py collision")
        packaged_main.rename(target);packaged_main=target
    packaged_sha=sha256_bytes(packaged_main.read_bytes())
    if packaged_sha!=FROZEN_SHA: raise RuntimeError("packaged main SHA mismatch")

    archive_sha=deterministic_tar(pkg,Path(a.archive))
    file_manifest=[]
    for p in sorted(pkg.rglob("*"),key=lambda x:x.as_posix()):
        if p.is_file():
            file_manifest.append({"path":p.relative_to(pkg).as_posix(),"sha256":sha256_bytes(p.read_bytes()),"size":p.stat().st_size})

    srcs=sorted(man["sources"],key=lambda s:(int(s["representative_rank"]),str(s["sha"])))
    opps=[]
    for s in srcs:
        p=root/s["path"]
        if str(s["sha"])==FROZEN_SHA: continue
        if sha256_bytes(p.read_bytes())!=str(s["sha"]): raise RuntimeError("opponent SHA mismatch")
        opps.append((s,p))
        if len(opps)==2: break
    if len(opps)!=2: raise RuntimeError("need two parity opponents")

    rows=[];fails=[]
    for s,opp in opps:
      for seed in PARITY_SEEDS:
       for seat in SEATS:
        try:
          d=episode(cand,opp,seed,seat)
          p=episode(packaged_main,opp,seed,seat)
          ok=(d["rewards"]==p["rewards"] and d["score"]==p["score"] and d["margin"]==p["margin"])
          rows.append({"opponent_sha":s["sha"],"opponent_ref":s["representative_ref"],"seed":seed,"seat":seat,
                       "direct":d,"packaged":p,"exact_parity":ok})
          if not ok: fails.append({"opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":"parity mismatch"})
        except Exception as e:
          fails.append({"opponent_sha":s["sha"],"seed":seed,"seat":seat,"error":f"{type(e).__name__}: {e}"})
        finally:
          purge_package_modules(cand.parent);purge_package_modules(packaged_main.parent);purge_package_modules(opp.parent)

    pass_count=sum(bool(r["exact_parity"]) for r in rows)
    mech=(not fails and len(rows)==8 and pass_count==8)
    out={"schema":"kculture-v30b-binding-package-parity-v1","mechanical_pass":mech,
         "candidate_ref":FROZEN_REF,"candidate_sha":FROZEN_SHA,"packaged_main_sha":packaged_sha,
         "archive_sha256":archive_sha,"package_files":file_manifest,"parity_pass":mech,
         "parity_contexts":len(rows),"parity_exact":pass_count,"rows":rows,"failures":fails}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V30B_BINDING_PARITY",json.dumps({k:v for k,v in out.items() if k not in ("rows","package_files","failures")},sort_keys=True))
    if not mech: raise SystemExit(2)
if __name__=="__main__": main()
