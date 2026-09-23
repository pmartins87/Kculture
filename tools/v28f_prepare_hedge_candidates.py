#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,math,shutil,sys,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules,sha256_bytes

CR053_ARCHIVE="R4D_CR053_ROUTE106309334_V1.tar.gz"
CR053_ARCHIVE_SHA="095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15"
CR053_MAIN_SHA="6e5d298797117bc72ad43c06b1d6a37634ad33a16a5c371c8c7e1a0aa5fc4519"
CR029_ARCHIVE="R4D_CR029_FULL_RECENT_TOP_V1.tar.gz"
CR029_TAPE_SHA="6c56840b9510e0688da2fbec47e8f89583c63a0124fa4c8801fa5d93c197226b"
SMOKE_SEED=80400

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def safe_extract(archive,dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive,"r:gz") as tf:
        for m in tf.getmembers():
            p=Path(m.name)
            if p.is_absolute() or ".." in p.parts:
                raise RuntimeError(f"unsafe tar member {m.name}")
        tf.extractall(dest)
    hits=list(dest.rglob("main.py"))
    if len(hits)!=1: raise RuntimeError(f"expected one main.py in {archive}, got {len(hits)}")
    return hits[0]

def smoke(main_py,seat):
    purge_package_modules(main_py.parent)
    agent=load_public_agent(main_py)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":SMOKE_SEED},debug=False)
    env.run([agent,"starter"] if seat==0 else ["starter",agent])
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    purge_package_modules(main_py.parent)
    return {"seat":seat,"ok":statuses==["DONE","DONE"] and len(rewards)==2 and steps>=720 and all(math.isfinite(x) for x in rewards),"statuses":statuses,"rewards":rewards,"steps":steps}

def freeze_package(src_main,dest):
    src_root=src_main.parent
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src_root,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    main=dest/"main.py"
    if not main.exists(): raise RuntimeError("frozen main missing")
    return main

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir",required=True)
    ap.add_argument("--cr053-root",required=True)
    ap.add_argument("--cr029-root",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    snap=Path(a.snapshot_dir);snap.mkdir(parents=True,exist_ok=True)

    cr053_hits=list(Path(a.cr053_root).rglob(CR053_ARCHIVE))
    if len(cr053_hits)!=1: raise SystemExit(f"CR053 archive count {len(cr053_hits)}")
    cr053_archive=cr053_hits[0]
    if sha(cr053_archive)!=CR053_ARCHIVE_SHA: raise SystemExit("CR053 archive SHA mismatch")

    cr029_hits=list(Path(a.cr029_root).rglob(CR029_ARCHIVE))
    manifests=list(Path(a.cr029_root).rglob("manifest.json"))
    if len(cr029_hits)!=1 or len(manifests)!=1: raise SystemExit(f"CR029 archive/manifest counts {len(cr029_hits)}/{len(manifests)}")
    cr029_archive=cr029_hits[0]
    cr029_manifest=json.loads(manifests[0].read_text())
    if cr029_manifest.get("tape_sha256")!=CR029_TAPE_SHA: raise SystemExit("CR029 tape SHA mismatch")
    if cr029_manifest.get("archive_sha256")!=sha(cr029_archive): raise SystemExit("CR029 archive manifest mismatch")

    with tempfile.TemporaryDirectory(prefix="v28f-extract-") as td:
        td=Path(td)
        c53=safe_extract(cr053_archive,td/"cr053")
        c29=safe_extract(cr029_archive,td/"cr029")
        if sha256_bytes(c53.read_bytes())!=CR053_MAIN_SHA: raise SystemExit("CR053 main SHA mismatch")
        if cr029_manifest.get("main_sha256")!=sha256_bytes(c29.read_bytes()): raise SystemExit("CR029 main manifest mismatch")
        c53f=freeze_package(c53,snap/"candidates"/"CR053")
        c29f=freeze_package(c29,snap/"candidates"/"CR029")

    smokes={
      "CR053":[smoke(c53f,0),smoke(c53f,1)],
      "CR029":[smoke(c29f,0),smoke(c29f,1)],
    }
    smoke_pass=all(all(x["ok"] for x in xs) for xs in smokes.values())
    manifest={
      "schema":"kculture-v28f-hedge-candidate-snapshot-v1",
      "candidates":{
        "CR053":{"path":"candidates/CR053/main.py","main_sha256":sha(c53f),"archive_sha256":CR053_ARCHIVE_SHA},
        "CR029":{"path":"candidates/CR029/main.py","main_sha256":sha(c29f),"archive_sha256":sha(cr029_archive),"tape_sha256":CR029_TAPE_SHA},
      },
      "smokes":smokes,
      "mechanical_pass":smoke_pass,
      "automatic_kaggle_submission":False,
    }
    (snap/"HEDGE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("V28F_PREP",json.dumps({"mechanical_pass":smoke_pass,"candidates":manifest["candidates"],"smokes":smokes},sort_keys=True),flush=True)
    if not smoke_pass: raise SystemExit(2)

if __name__=="__main__": main()
