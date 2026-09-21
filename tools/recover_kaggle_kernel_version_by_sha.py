#!/usr/bin/env python3
"""Recover an exact historical Kaggle kernel version by frozen main.py SHA.

Mechanical recovery only. It never accepts a non-matching source hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def find_code_file(root: Path) -> Path | None:
    # Prefer main.py because Kaggriculture agents are packaged that way.
    candidates = list(root.rglob("main.py"))
    if candidates:
        return candidates[0]
    py = [p for p in root.rglob("*.py") if p.is_file()]
    return py[0] if len(py) == 1 else None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--expected-sha", required=True)
    ap.add_argument("--min-version", type=int, default=1)
    ap.add_argument("--max-version", type=int, default=60)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--result", required=True)
    args=ap.parse_args()

    attempts=[]
    found=None
    with tempfile.TemporaryDirectory(prefix="kaggle-historical-sha-") as td:
        td=Path(td)
        for version in range(args.min_version,args.max_version+1):
            dest=td/f"v{version}"
            dest.mkdir(parents=True,exist_ok=True)
            cmd=["kaggle","kernels","pull",f"{args.ref}/{version}","-p",str(dest),"-m"]
            p=subprocess.run(cmd,capture_output=True,text=True)
            rec={"version":version,"returncode":p.returncode}
            if p.returncode != 0:
                rec["error"]=(p.stderr or p.stdout)[-1000:]
                attempts.append(rec)
                # Missing versions above the current version are normal; keep scanning
                # only through the frozen bounded range.
                time.sleep(0.5)
                continue
            code=find_code_file(dest)
            if code is None:
                rec["error"]="no unique python code file found"
                attempts.append(rec)
                continue
            got=sha256(code)
            rec["sha256"]=got
            rec["code_file"]=code.name
            attempts.append(rec)
            print("HIST_VERSION",json.dumps(rec,sort_keys=True),flush=True)
            if got == args.expected_sha:
                out=Path(args.out_dir)
                out.mkdir(parents=True,exist_ok=True)
                target=out/"main.py"
                target.write_bytes(code.read_bytes())
                found={
                    "ref":args.ref,
                    "version":version,
                    "expected_sha":args.expected_sha,
                    "recovered_sha":got,
                    "file":"main.py",
                }
                break
            time.sleep(0.5)

    result={
        "schema":"kculture-kaggle-historical-kernel-sha-recovery-v1",
        "ref":args.ref,
        "expected_sha":args.expected_sha,
        "found":found,
        "attempts":attempts,
        "automatic_kaggle_submission":False,
    }
    rp=Path(args.result); rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("HIST_RECOVERY_RESULT",json.dumps({
        "found":bool(found),
        "version":None if not found else found["version"],
        "attempts":len(attempts),
    },sort_keys=True),flush=True)
    if not found:
        raise SystemExit(2)

if __name__=="__main__":
    main()
