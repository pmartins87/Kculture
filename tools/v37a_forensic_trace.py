#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,tarfile,tempfile
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

def load(pkg,root):
    with tarfile.open(pkg,"r:*") as tf: tf.extractall(root)
    p=Path(root)/"main.py"
    return get_last_callable(p.read_text(encoding="utf-8"),path=str(p.resolve()))

def one(pkg_a,pkg_b,seed,seat,label):
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        A=load(pkg_a,a); B=load(pkg_b,b)
        env=make("kaggriculture",configuration={"episodeSteps":720,"seed":seed},debug=False)
        env.run([A,B] if seat==0 else [B,A])
        rep=env.toJSON()
        steps=rep.get("steps") or []
        rew=[float(x) for x in rep.get("rewards",[])]
        mine=rew[0] if seat==0 else rew[1]; other=rew[1] if seat==0 else rew[0]
        checkpoints=[]
        for t in [0,24,48,96,192,288,384,480,576,624,672,696,719]:
            if t>=len(steps): continue
            row=steps[t][seat]
            obs=row.get("observation") or {}
            farm=(obs.get("farms") or [{}])[seat] if len(obs.get("farms") or [])>seat else {}
            priv=obs.get("private") or {}
            shed=priv.get("shed") or {}
            action=(steps[t+1][seat].get("action") if t+1<len(steps) else None)
            checkpoints.append({
                "step":t,
                "money":farm.get("money"),
                "hands":len(farm.get("hands") or []),
                "hires_today":farm.get("hires_today"),
                "shed_total":sum(int(v or 0) for v in shed.values() if isinstance(v,(int,float))),
                "shed":shed,
                "action":action,
            })
        final=steps[-1][seat].get("observation") or {}
        ff=(final.get("farms") or [{}])[seat] if len(final.get("farms") or [])>seat else {}
        return {"label":label,"seed":seed,"seat":seat,"reward":mine,"opp_reward":other,"margin":mine-other,
                "final_money":ff.get("money"),"checkpoints":checkpoints}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--v37",required=True);ap.add_argument("--base",required=True);ap.add_argument("--opp",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    rows=[]
    for seed in [81201,81202]:
      for seat in [0,1]:
        rows.append(one(a.v37,a.opp,seed,seat,"V37A_vs_AHMED"))
        rows.append(one(a.base,a.opp,seed,seat,"V30B_vs_AHMED"))
    Path(a.out).write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
    for r in rows:
      print("V37_FORENSIC",json.dumps({k:v for k,v in r.items() if k!="checkpoints"},sort_keys=True))
if __name__=="__main__":main()
