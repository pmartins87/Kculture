#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math,os,sys
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from tools.programme_adaptive_expert_gate import EXPECTED_ENGINE,load_public_agent,purge_package_modules,sha256_bytes
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.o_pc1_dev_shard import BASE
WINDOWS={"BASE":None,"EARLY":(0,191),"PRE_MID":(192,383),"LATE":(480,719)}
class Hybrid:
 def __init__(self,base_main,teacher_main,mode):
  purge_package_modules(base_main.parent);purge_package_modules(teacher_main.parent)
  self.base=load_public_agent(base_main);purge_package_modules(teacher_main.parent)
  self.teacher=None if mode=="BASE" else load_public_agent(teacher_main);self.host=OptionHostState();self.mode=mode
 def __call__(self,obs,config=None):
  exact=canonical_action(call_agent(self.base,obs,config));all3=apply_option_host(obs,config,exact,self.host,use_rw=True,use_tw=True,use_lq2=True)
  if self.mode=="BASE": return all3
  shadow=canonical_action(call_agent(self.teacher,obs,config));step=int((obs or {}).get("step",-1));lo,hi=WINDOWS[self.mode]
  if not(lo<=step<=hi): return all3
  out=copy.deepcopy(all3);out["farmer"]=copy.deepcopy(shadow["farmer"]);out["hands"]=copy.deepcopy(shadow["hands"]);return out
def run_one(base,teacher,seed,seat,mode):
 purge_package_modules(base.parent);purge_package_modules(teacher.parent);cand=Hybrid(base,teacher,mode);purge_package_modules(teacher.parent);opp=load_public_agent(teacher)
 env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False);env.run([cand,opp] if int(seat)==0 else [opp,cand]);rep=env.toJSON();sts=[str(x) for x in rep.get("statuses",[])];rw=[float(x) for x in rep.get("rewards",[])];steps=len(rep.get("steps") or [])
 if sts!=["DONE","DONE"] or len(rw)!=2 or steps<720 or not all(math.isfinite(x) for x in rw): raise RuntimeError(f"invalid {mode} {sts} {rw} steps={steps}")
 mine,other=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0]);margin=mine-other;return float(score(margin)),float(margin)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--snapshot-dir",required=True);ap.add_argument("--v28f",required=True);ap.add_argument("--shard-index",type=int,required=True);ap.add_argument("--num-shards",type=int,default=4);ap.add_argument("--out",required=True);a=ap.parse_args()
 import kaggle_environments
 if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE: raise SystemExit("engine mismatch")
 root=Path(a.snapshot_dir);man=json.loads((root/"MANIFEST.json").read_text());f=json.loads(Path(a.v28f).read_text());base=root/man["base"]["path"]
 if sha256_bytes(base.read_bytes())!=BASE["expected_main_sha256"]: raise SystemExit("base SHA mismatch")
 paths={};meta={}
 for s in man["sources"]:
  p=root/s["path"];sha=str(s["sha"])
  if sha256_bytes(p.read_bytes())!=sha: raise SystemExit("source SHA mismatch")
  paths[sha]=p;meta[sha]=s
 hard=sorted([r for r in f["rows"] if r["candidate"]=="ALL3" and float(r["score"])==0.0],key=lambda r:(int(r["source_rank"]),str(r["main_sha256"]),int(r["seed"]),int(r["seat"])))
 if len(hard)!=66: raise SystemExit(f"expected 66 losses got {len(hard)}")
 selected=[r for i,r in enumerate(hard) if i%a.num_shards==a.shard_index];rows=[];fails=[]
 for k in ("KAGGLE_API_TOKEN","KAGGLE_USERNAME","KAGGLE_KEY"): os.environ.pop(k,None)
 for ctx in selected:
  sha=str(ctx["main_sha256"]);bs=bm=None
  for mode in WINDOWS:
   try:
    ts,tm=run_one(base,paths[sha],ctx["seed"],ctx["seat"],mode)
    if mode=="BASE":
     if ts!=float(ctx["score"]) or tm!=float(ctx["margin"]): raise RuntimeError(f"BASE parity mismatch {(ts,tm)} != {(ctx['score'],ctx['margin'])}")
     bs,bm=ts,tm
    rows.append({"main_sha256":sha,"representative_ref":meta[sha]["representative_ref"],"source_rank":int(meta[sha]["representative_rank"]),"seed":int(ctx["seed"]),"seat":int(ctx["seat"]),"mode":mode,"base_score":bs,"base_margin":bm,"treatment_score":ts,"treatment_margin":tm,"score_delta":ts-bs,"margin_delta":tm-bm})
   except Exception as e: fails.append({"sha":sha,"seed":ctx["seed"],"seat":ctx["seat"],"mode":mode,"error":f"{type(e).__name__}: {e}"})
   finally: purge_package_modules(base.parent);purge_package_modules(paths[sha].parent)
 mech=not fails and len(rows)==len(selected)*len(WINDOWS);out={"schema":"kculture-v28l-physical-temporal-localization-shard-v1","mechanical_pass":mech,"shard_index":a.shard_index,"num_shards":a.num_shards,"windows":WINDOWS,"rows":rows,"failures":fails,"automatic_kaggle_submission":False}
 p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("V28L_SHARD_RESULT",json.dumps({"shard":a.shard_index,"mechanical_pass":mech,"contexts":len(selected),"rows":len(rows),"failures":len(fails)},sort_keys=True));
 if not mech: raise SystemExit(2)
if __name__=="__main__":main()
