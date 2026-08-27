"""Verify CR-008 deployed public feature encoder matches frozen CR-004 encoder."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.cr004_adaptation_signal import TEST_DATE, download, read_csv, public_features


def load_candidate():
    path=ROOT/"candidates/cr008_adaptive_frontrun.py"
    spec=importlib.util.spec_from_file_location("cr008_feature_audit_candidate",path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--top",type=int,default=5); ap.add_argument("--output",required=True); args=ap.parse_args()
    cand=load_candidate()
    comparisons=0; max_err=0.0; key_mismatches=0; value_mismatches=0; examples=[]
    with tempfile.TemporaryDirectory(prefix="kculture-cr008-feature-parity-") as tmp:
        root=Path(tmp); handle=f"kaggle/kaggriculture-episodes-{TEST_DATE}"
        manifest=sorted(read_csv(download(handle,"manifest.csv",root/"manifest")),key=lambda r:-float(r.get("avg_score") or 0))[:args.top]
        for mr in manifest:
            eid=str(mr["episode_id"]); rep=json.loads(download(handle,f"{eid}.json",root/"episodes"/eid).read_text(encoding="utf-8")); steps=rep.get("steps") or []
            for p in (0,1):
                for t in range(96,min(696,len(steps))):
                    obs=steps[t][p].get("observation") or {}; prev=steps[t-24][p].get("observation") or {}
                    a=public_features(obs,prev,p); b=cand._public_features(obs,prev,p); comparisons+=1
                    if set(a)!=set(b):
                        key_mismatches+=1
                        if len(examples)<5: examples.append({"episode":eid,"player":p,"step":t,"type":"keys","only_ref":sorted(set(a)-set(b)),"only_candidate":sorted(set(b)-set(a))})
                        continue
                    local=0.0
                    for k in a:
                        try: e=abs(float(a[k])-float(b[k]))
                        except Exception: e=math.inf
                        local=max(local,e)
                    max_err=max(max_err,local)
                    if local>1e-12:
                        value_mismatches+=1
                        if len(examples)<5: examples.append({"episode":eid,"player":p,"step":t,"type":"values","max_error":local})
    gate={"comparisons_ge_1000":comparisons>=1000,"zero_key_mismatches":key_mismatches==0,"max_abs_error_le_1e_12":max_err<=1e-12,"zero_value_mismatches":value_mismatches==0}
    passed=all(gate.values())
    payload={"experiment":"CR-008-feature-parity","status":"FEATURE_PARITY_PASS" if passed else "FEATURE_PARITY_FAIL","comparisons":comparisons,"max_abs_error":max_err,"key_mismatches":key_mismatches,"value_mismatches":value_mismatches,"examples":examples,"gate":gate}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps(payload,indent=2,sort_keys=True))
    if not passed: raise SystemExit(2)

if __name__=="__main__": main()
