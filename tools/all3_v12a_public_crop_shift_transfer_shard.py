#!/usr/bin/env python3
"""V12A exact-ALL3 public crop-shift regime transfer census shard."""
from __future__ import annotations
import argparse,collections,json,math,sys,tempfile,time
from pathlib import Path
from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE,BASE,V2_OPPONENTS,acquire
from tools.programme_adaptive_expert_gate import load_public_agent,purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent,canonical_action,plain,score
from tools.first_party_option_host_v1 import OptionHostState,apply_option_host
from tools.cr087_top_macro_profile import public_counts

SEEDS=[77001,77002,77003,77004,77005,77006,77007,77008]
CHECKPOINTS=(456,480,504,552,600)
ALLOWED={x["key"] for x in V2_OPPONENTS}
CROPS=("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")

def farm_snapshot(obs,seat):
    p=plain(obs)
    farms=p.get("farms") or []
    if len(farms)!=2:
        raise RuntimeError(f"expected two public farms, got {len(farms)}")
    own=farms[int(seat)]; opp=farms[1-int(seat)]
    oc=public_counts(own); pc=public_counts(opp)
    row={
      "own_money":float(own.get("money",0) or 0),
      "opp_money":float(opp.get("money",0) or 0),
    }
    for x in CROPS:
        row[f"own_{x}"]=int(oc.get(f"crop_{x}",0))
        row[f"opp_{x}"]=int(pc.get(f"crop_{x}",0))
        row[f"gap_{x}"]=row[f"own_{x}"]-row[f"opp_{x}"]
    row["opp_carrot_adv"]=row["opp_CARROT"]>row["own_CARROT"]
    row["strict"]=(
      row["opp_CARROT"]-row["own_CARROT"]>=4
      and row["own_WHEAT"]-row["opp_WHEAT"]>=4
    )
    return row

class All3Census:
    def __init__(self,main,seat):
        self.agent=load_public_agent(main)
        self.state=OptionHostState()
        self.seat=int(seat)
        self.turn=0
        self.snapshots={}
    def __call__(self,obs,config=None):
        turn=self.turn; self.turn+=1
        base=canonical_action(call_agent(self.agent,obs,config))
        all3=apply_option_host(obs,config,base,self.state,use_rw=True,use_tw=True,use_lq2=True)
        if turn in CHECKPOINTS:
            self.snapshots[str(turn)]=farm_snapshot(obs,self.seat)
        return all3

def finish(env,seat,cand):
    p=env.toJSON()
    st=[str(x) for x in p.get("statuses",[])]
    rw=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if st!=["DONE","DONE"] or len(rw)!=2 or not all(math.isfinite(x) for x in rw) or steps<720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine,opp=(rw[0],rw[1]) if int(seat)==0 else (rw[1],rw[0])
    margin=mine-opp
    if set(cand.snapshots)!=set(str(x) for x in CHECKPOINTS):
        raise RuntimeError(f"missing checkpoints {set(map(str,CHECKPOINTS))-set(cand.snapshots)}")
    signal_steps=[int(k) for k,v in cand.snapshots.items() if v["opp_carrot_adv"]]
    strict_steps=[int(k) for k,v in cand.snapshots.items() if v["strict"]]
    return {
      "rewards":rw,"margin":margin,"score":score(margin),
      "result":"W" if margin>0 else ("L" if margin<0 else "T"),
      "snapshots":cand.snapshots,
      "opp_carrot_adv_any":bool(signal_steps),
      "signal_steps":sorted(signal_steps),
      "first_signal_step":min(signal_steps) if signal_steps else None,
      "strict_any":bool(strict_steps),
      "strict_steps":sorted(strict_steps),
      "first_strict_step":min(strict_steps) if strict_steps else None,
    }

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen:continue
        seen.add(k);purge_package_modules(p.parent)

def summarize(rows):
    if not rows:return {}
    sig=[r for r in rows if r["opp_carrot_adv_any"]]
    strict=[r for r in rows if r["strict_any"]]
    nonsig=[r for r in rows if not r["opp_carrot_adv_any"]]
    def ss(rr):
        if not rr:return {"support":0}
        return {
          "support":len(rr),
          "wins":sum(r["result"]=="W" for r in rr),
          "losses":sum(r["result"]=="L" for r in rr),
          "ties":sum(r["result"]=="T" for r in rr),
          "score_rate":sum(float(r["score"]) for r in rr)/len(rr),
          "loss_rate":sum(r["result"]=="L" for r in rr)/len(rr),
          "mean_margin":sum(float(r["margin"]) for r in rr)/len(rr),
        }
    return {"all":ss(rows),"signal":ss(sig),"strict":ss(strict),"non_signal":ss(nonsig)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--opponent",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    if args.opponent not in ALLOWED:raise SystemExit("bad opponent")
    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    spec=next(x for x in V2_OPPONENTS if x["key"]==args.opponent)
    rows=[];failures=[];prov={};started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix=f"v12a-{args.opponent}-") as td:
        tmp=Path(td)
        base_main,prov["base"]=acquire(BASE,tmp/"base")
        if spec["expected_main_sha256"]==BASE["expected_main_sha256"]:
            opp_main=base_main
            prov["opponent"]={**prov["base"],"key":spec["key"],"family":spec["family"],"reused_exact_base_bytes":True}
        else:
            opp_main,rec=acquire(spec,tmp/"opp")
            prov["opponent"]={**rec,"family":spec["family"]}
        paths=[base_main,opp_main]

        for seed in SEEDS:
          for seat in (0,1):
            key={"opponent":args.opponent,"family":spec["family"],"seed":seed,"seat":seat}
            try:
                purge(paths)
                cand=All3Census(base_main,seat)
                opp=load_public_agent(opp_main)
                env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
                if seat==0:env.run([cand,opp])
                else:env.run([opp,cand])
                res=finish(env,seat,cand)
                row={**key,**res}
                rows.append(row)
                print("V12A_EPISODE",json.dumps({
                  **key,"result":row["result"],"margin":row["margin"],"score":row["score"],
                  "opp_carrot_adv_any":row["opp_carrot_adv_any"],"first_signal_step":row["first_signal_step"],
                  "strict_any":row["strict_any"],"first_strict_step":row["first_strict_step"]
                },sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({**key,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==len(SEEDS)*2
    result={
      "schema":"kculture-v12a-public-crop-shift-transfer-shard-v1",
      "engine":EXPECTED_ENGINE,"mechanical_pass":mech,
      "opponent":args.opponent,"family":spec["family"],"seeds":SEEDS,
      "checkpoints":list(CHECKPOINTS),"rows":rows,"summary":summarize(rows),
      "failures":failures,"provenance":prov,
      "seconds":time.perf_counter()-started,
      "automatic_kaggle_submission":False,
      "runtime_identity_feature_allowed":False,
    }
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V12A_SHARD_RESULT",json.dumps({
      "opponent":args.opponent,"family":spec["family"],"mechanical_pass":mech,
      "summary":result["summary"],"failures":len(failures)
    },sort_keys=True),flush=True)
    if not mech:raise SystemExit(2)

if __name__=="__main__":main()
