#!/usr/bin/env python3
"""Resolve immutable Kaggle version handles for the already-frozen V13C source SHAs.

Mechanical provenance repair only.  The source population and expected SHAs come from
configs/all3_v13c_current_frontier_representatives.json and cannot be changed here.
"""
from __future__ import annotations
import argparse,json,subprocess,tempfile,time,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main, sha256_bytes

def find_version_value(obj):
    # Prefer exact/common metadata keys.
    preferred=("versionNumber","version_number","currentVersionNumber","current_version_number","version")
    if isinstance(obj,dict):
        for k in preferred:
            v=obj.get(k)
            if isinstance(v,int) and v>=1:
                return v
            if isinstance(v,str) and v.isdigit() and int(v)>=1:
                return int(v)
        # recurse only through metadata-like dict/list values
        for k,v in obj.items():
            if "version" in str(k).lower():
                if isinstance(v,int) and v>=1:return v
                if isinstance(v,str) and v.isdigit() and int(v)>=1:return int(v)
        for v in obj.values():
            hit=find_version_value(v)
            if hit is not None:return hit
    elif isinstance(obj,list):
        for v in obj:
            hit=find_version_value(v)
            if hit is not None:return hit
    return None

def current_version(ref,tmp):
    out=tmp/"meta"
    out.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(["kaggle","kernels","pull",ref,"-m","-p",str(out)],text=True,capture_output=True,check=False)
    if p.returncode!=0:
        raise RuntimeError(f"kaggle kernels pull metadata failed rc={p.returncode}: {(p.stderr or p.stdout)[-1200:]}")
    mp=out/"kernel-metadata.json"
    if not mp.is_file():
        found=list(out.rglob("kernel-metadata.json"))
        if len(found)!=1:
            raise RuntimeError(f"kernel-metadata.json unresolved: {found}")
        mp=found[0]
    meta=json.loads(mp.read_text())
    ver=find_version_value(meta)
    if ver is None:
        raise RuntimeError(f"version number not found; metadata keys={sorted(meta)[:80]}")
    return int(ver),meta

def acquire_hash(handle,tmp,attempts=4):
    last=None
    for a in range(attempts):
        try:
            main,receipt=acquire_public_main(handle,tmp/f"try{a}")
            return sha256_bytes(main.read_bytes()),receipt
        except Exception as exc:
            last=exc
            if a+1<attempts:
                time.sleep(2.0*(a+1))
    raise last

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--max-back",type=int,default=12)
    ap.add_argument("--delay",type=float,default=1.25)
    args=ap.parse_args()

    cfg=json.loads(Path(args.config).read_text())
    reps=list(cfg.get("representatives") or [])
    if len(reps)!=19:
        raise SystemExit(f"expected 19 frozen representatives, got {len(reps)}")

    rows=[];failures=[]
    with tempfile.TemporaryDirectory(prefix="v13c-pin-") as td:
        root=Path(td)
        for i,r in enumerate(reps):
            ref=str(r["ref"]); expected=str(r["main_sha256"]);rank=int(r["rank"])
            try:
                ver,meta=current_version(ref,root/f"r{i:02d}_current")
                tried=[]
                found=None
                lo=max(1,ver-int(args.max_back))
                for v in range(ver,lo-1,-1):
                    handle=f"{ref}/versions/{v}"
                    try:
                        observed,receipt=acquire_hash(handle,root/f"r{i:02d}_v{v}")
                        tried.append({"version":v,"observed_sha256":observed,"status":"OK"})
                        print("V13C_PIN_TRY",json.dumps({"rank":rank,"ref":ref,"version":v,"observed_sha256":observed,"expected_sha256":expected},sort_keys=True),flush=True)
                        if observed==expected:
                            found={"rank":rank,"ref":ref,"main_sha256":expected,
                                   "pinned_handle":handle,"version":v,
                                   "current_version_at_resolution":ver,
                                   "receipt":receipt}
                            break
                    except Exception as exc:
                        tried.append({"version":v,"status":"ERROR","error":f"{type(exc).__name__}: {exc}"})
                    time.sleep(max(0,args.delay))
                if found is None:
                    raise RuntimeError(f"expected SHA not found in versions {ver}..{lo}; tried={tried}")
                rows.append(found)
                print("V13C_PIN_FOUND",json.dumps({k:found[k] for k in ("rank","ref","main_sha256","pinned_handle","version","current_version_at_resolution")},sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"rank":rank,"ref":ref,"expected_sha256":expected,"error":f"{type(exc).__name__}: {exc}"})
                print("V13C_PIN_FAIL",json.dumps(failures[-1],sort_keys=True),flush=True)
            time.sleep(max(0,args.delay))

    mech=(not failures and len(rows)==len(reps))
    result={
      "schema":"kculture-all3-v13c-pinned-frontier-versions-v1",
      "mechanical_pass":mech,
      "source_population_changed":False,
      "strategic_gate_changed":False,
      "input_config":args.config,
      "representatives":rows,
      "failures":failures,
      "automatic_kaggle_submission":False,
      "third_party_code_executed":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V13C_PIN_RESULT",json.dumps({"mechanical_pass":mech,"resolved":len(rows),"failures":failures,
      "pinned":[{"rank":x["rank"],"handle":x["pinned_handle"],"sha":x["main_sha256"]} for x in rows]},sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
