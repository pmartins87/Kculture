#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,os,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.kaggle_meta_scout_cli import csv_rows,normkey
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes

TOP_N=100;MAX_NEW=40;SMOKE_SEED=80900

def ref_value(row):
    for k,v in row.items():
        if normkey(k)=="ref" and str(v).strip():return str(v).strip()
    for _k,v in row.items():
        s=str(v or "").strip()
        if "/" in s and " " not in s:return s
    return None

def list_refs():
    cmd=["kaggle","kernels","list","--competition","kaggriculture","--sort-by","scoreDescending","--page-size","100","-v"]
    p=subprocess.run(cmd,text=True,capture_output=True,check=False)
    if p.returncode!=0:raise RuntimeError(p.stderr[-4000:])
    refs=[];seen=set()
    for row in csv_rows(p.stdout):
        ref=ref_value(row)
        if ref and ref not in seen:
            seen.add(ref);refs.append(ref)
        if len(refs)>=TOP_N:break
    if len(refs)<80:raise RuntimeError(f"expected broad list >=80 refs, got {len(refs)}")
    return refs,p.stdout

def acquire_retry(ref,target,attempts=6):
    last=None
    for i in range(attempts):
        try:
            main,receipt=acquire_public_main(ref,target/f"a{i}")
            return main,sha256_bytes(main.read_bytes()),receipt
        except Exception as e:
            last=e
            if i+1<attempts:time.sleep(min(30,3*(2**i)))
    raise last

def smoke(main,seat):
    purge_package_modules(main.parent);ag=load_public_agent(main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":SMOKE_SEED},debug=False)
    env.run([ag,"starter"] if seat==0 else ["starter",ag])
    rep=env.toJSON();st=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
    return st==["DONE","DONE"] and len(rw)==2 and steps>=720 and all(math.isfinite(x) for x in rw)

def known_shas(*roots):
    s=set()
    for rr in roots:
        p=Path(rr)/"MANIFEST.json"
        if not p.exists():continue
        m=json.loads(p.read_text())
        s.update(str(x["sha"]) for x in m.get("sources",[]))
    return s

def snap(src,dest):
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(src.parent,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    p=dest/"main.py"
    if not p.exists():p.write_bytes(src.read_bytes())
    return p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v30a",required=True);ap.add_argument("--v32a",required=True)
    ap.add_argument("--snapshot",required=True);ap.add_argument("--out",required=True);ap.add_argument("--raw",required=True)
    a=ap.parse_args()
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:raise SystemExit("engine mismatch")
    known=known_shas(a.v30a,a.v32a)
    refs,raw=list_refs();Path(a.raw).parent.mkdir(parents=True,exist_ok=True);Path(a.raw).write_text(raw)
    root=Path(a.snapshot);root.mkdir(parents=True,exist_ok=True)
    acq=[];unique={};fail=[]
    with tempfile.TemporaryDirectory(prefix="v33a-") as td:
      td=Path(td)
      for rank,ref in enumerate(refs,start=1):
        try:
          main,sha,receipt=acquire_retry(ref,td/f"r{rank:03d}")
          acq.append({"rank":rank,"ref":ref,"sha":sha,"status":"ACQUIRED"})
          if sha not in unique:unique[sha]={"main":main,"rank":rank,"ref":ref,"refs":[ref]}
          else:unique[sha]["refs"].append(ref)
        except Exception as e:
          fail.append({"rank":rank,"ref":ref,"error":f"{type(e).__name__}: {e}"})
      eligible=[]
      for sha,m in sorted(unique.items(),key=lambda kv:(kv[1]["rank"],kv[0])):
        if sha in known:continue
        oks=[]
        for seat in (0,1):
          try:oks.append(smoke(m["main"],seat))
          except Exception:oks.append(False)
          finally:purge_package_modules(m["main"].parent)
        if all(oks):
          eligible.append({"sha":sha,"representative_rank":m["rank"],"representative_ref":m["ref"],"main":m["main"]})
      selected=eligible[:MAX_NEW]
      srcs=[]
      for x in selected:
        p=snap(x["main"],root/"sources"/x["sha"])
        if sha256_bytes(p.read_bytes())!=x["sha"]:raise RuntimeError("snapshot SHA mismatch")
        srcs.append({"sha":x["sha"],"representative_rank":x["representative_rank"],"representative_ref":x["representative_ref"],"path":f"sources/{x['sha']}/main.py"})
      (root/"MANIFEST.json").write_text(json.dumps({"schema":"kculture-v33a-expanded-public-snapshot-v1","sources":srcs},indent=2,sort_keys=True)+"
")
    mech=len(refs)>=80
    out={"schema":"kculture-v33a-expanded-public-census-v1","mechanical_pass":mech,"listed_refs":len(refs),"acquired_unique":len(unique),
         "known_sha_count":len(known),"new_executable_unique":len(eligible),"selected_count":len(srcs),"sources":srcs,"failures":fail}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"
")
    print("V33A_CENSUS",json.dumps({k:v for k,v in out.items() if k not in ("sources","failures")},sort_keys=True))
    if not mech:raise SystemExit(2)
if __name__=="__main__":main()
