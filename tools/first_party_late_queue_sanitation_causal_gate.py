#!/usr/bin/env python3
"""Fresh causal gate for O-LQ1 Late Queue Sanitation."""
from __future__ import annotations
import argparse, json, math, statistics, sys, tempfile, time
from pathlib import Path

from kaggle_environments import make

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import (
    acquire_public_main,load_public_agent,purge_package_modules,sha256_bytes,
)
from tools.bounded_transaction_oracle_v1 import (
    action_key,call_agent,canonical_action,plain,score,
)
from tools.cq2_projected_queue_dev_matrix import cq2_action

EXPECTED_ENGINE="1.32.7"
BASE={
    "key":"v47",
    "handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "expected_main_sha256":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842",
}
V48={
    "key":"v48",
    "handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "expected_main_sha256":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
}
SEEDS=list(range(74301,74309))
MIN_STEP=336
MODE="slot_projected"

def acquire(spec,tmp):
    last=None
    for attempt in range(1,4):
        try:
            main,receipt=acquire_public_main(spec["handle"],tmp/f"attempt-{attempt}")
            observed=sha256_bytes(main.read_bytes())
            if observed!=spec["expected_main_sha256"]:
                raise RuntimeError(f"{spec['key']} identity mismatch {observed}")
            return main,{
                "key":spec["key"],"handle":spec["handle"],
                "observed_main_sha256":observed,
                "acquisition_attempt":attempt,**receipt,
            }
        except Exception as exc:
            last=exc
            if attempt<3:
                time.sleep(2*attempt)
    raise RuntimeError(f"{spec['key']} acquisition failed: {type(last).__name__}: {last}")

class BaseWrap:
    def __init__(self,main):
        self.agent=load_public_agent(main)
        self.trace=[]
    def __call__(self,obs,config=None):
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((int(plain(obs).get("step",len(self.trace))),action_key(b)))
        return b

class LQ1Wrap:
    def __init__(self,main):
        self.agent=load_public_agent(main)
        self.trace=[]
        self.fire_steps=[]
        self.changed_slots=0
        self.cleared_slots=0
        self.qty_down_slots=0
    def __call__(self,obs,config=None):
        step=int(plain(obs).get("step",len(self.trace)))
        b=canonical_action(call_agent(self.agent,obs,config))
        self.trace.append((step,action_key(b)))
        out=cq2_action(obs,config,b,MODE,MIN_STEP)
        out=canonical_action(out)
        if out["farmer"]!=b["farmer"] or out["hands"]!=b["hands"]:
            raise RuntimeError("O-LQ1 changed V47 physical action")
        if action_key(out)!=action_key(b):
            self.fire_steps.append(step)
            n=max(len(b["market"]),len(out["market"]))
            for i in range(n):
                bo=b["market"][i] if i<len(b["market"]) else []
                oo=out["market"][i] if i<len(out["market"]) else []
                if bo==oo:
                    continue
                self.changed_slots+=1
                if bo and not oo:
                    self.cleared_slots+=1
                elif (
                    isinstance(bo,list) and isinstance(oo,list)
                    and len(bo)>=3 and len(oo)>=3
                    and str(bo[0])=="SELL" and str(oo[0])=="SELL"
                    and str(bo[1])==str(oo[1])
                ):
                    try:
                        if float(oo[2])<float(bo[2]):
                            self.qty_down_slots+=1
                    except Exception:
                        pass
        return out

def finish(env,seat):
    p=env.toJSON()
    statuses=[str(x) for x in p.get("statuses",[])]
    rewards=[float(x) for x in p.get("rewards",[])]
    steps=len(p.get("steps") or [])
    if statuses!=["DONE","DONE"] or len(rewards)!=2 or not all(math.isfinite(x) for x in rewards) or steps<720:
        raise RuntimeError(f"invalid episode statuses={statuses} rewards={rewards} steps={steps}")
    mine,opp=(rewards[0],rewards[1]) if seat==0 else (rewards[1],rewards[0])
    margin=mine-opp
    return {"rewards":rewards,"margin":margin,"score":score(margin),"steps":steps}

def run(base_main,v48_main,seed,seat,treatment):
    cand=LQ1Wrap(base_main) if treatment else BaseWrap(base_main)
    opp=load_public_agent(v48_main)
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":int(seed)},debug=False)
    if seat==0: env.run([cand,opp])
    else: env.run([opp,cand])
    out=finish(env,seat)
    out["trace"]=cand.trace
    if treatment:
        out.update({
            "fire_steps":cand.fire_steps,
            "fire_count":len(cand.fire_steps),
            "changed_slots":cand.changed_slots,
            "cleared_slots":cand.cleared_slots,
            "qty_down_slots":cand.qty_down_slots,
        })
    return out

def pretrigger_parity(base,treatment):
    fires=treatment.get("fire_steps",[])
    if not fires:
        return {
            "ok":base["trace"]==treatment["trace"] and base["rewards"]==treatment["rewards"],
            "first_fire":None,
        }
    first=min(fires)
    bt=[x for x in base["trace"] if x[0]<=first]
    tt=[x for x in treatment["trace"] if x[0]<=first]
    return {"ok":bt==tt,"first_fire":first,"base_prefix":len(bt),"treatment_prefix":len(tt)}

def purge(paths):
    seen=set()
    for p in paths:
        k=str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="artifacts/o-lq1-v48-causal/O_LQ1_V48_CAUSAL.json")
    args=ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments,"__version__",""))!=EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    rows=[]; failures=[]; provenance={}; started=time.perf_counter()
    try:
      with tempfile.TemporaryDirectory(prefix="o-lq1-v48-") as td:
        tmp=Path(td)
        base_main,provenance["base"]=acquire(BASE,tmp/"base")
        v48_main,provenance["v48"]=acquire(V48,tmp/"v48")
        paths=[base_main,v48_main]
        for seed in SEEDS:
          for seat in (0,1):
            try:
                purge(paths); b=run(base_main,v48_main,seed,seat,False)
                purge(paths); t=run(base_main,v48_main,seed,seat,True)
                parity=pretrigger_parity(b,t)
                if not parity["ok"]:
                    raise RuntimeError(f"pretrigger parity failure seed={seed} seat={seat}: {parity}")
                row={
                    "seed":seed,"seat":seat,
                    "base_score":b["score"],"treatment_score":t["score"],
                    "score_delta":t["score"]-b["score"],
                    "base_margin":b["margin"],"treatment_margin":t["margin"],
                    "margin_delta":t["margin"]-b["margin"],
                    "base_rewards":b["rewards"],"treatment_rewards":t["rewards"],
                    "fire_count":t["fire_count"],
                    "first_fire":min(t["fire_steps"]) if t["fire_steps"] else None,
                    "last_fire":max(t["fire_steps"]) if t["fire_steps"] else None,
                    "changed_slots":t["changed_slots"],
                    "cleared_slots":t["cleared_slots"],
                    "qty_down_slots":t["qty_down_slots"],
                    "parity":parity,
                }
                rows.append(row)
                print("O_LQ1_PAIR",json.dumps(row,sort_keys=True),flush=True)
            except Exception as exc:
                failures.append({"seed":seed,"seat":seat,"error":f"{type(exc).__name__}: {exc}"})
            finally:
                purge(paths)
    except Exception as exc:
      failures.append({"phase":"setup","error":f"{type(exc).__name__}: {exc}"})

    mech=not failures and len(rows)==len(SEEDS)*2 and all(r["parity"]["ok"] for r in rows)
    sd=[float(r["score_delta"]) for r in rows]
    md=[float(r["margin_delta"]) for r in rows]
    summary={
        "pairs":len(rows),
        "base_score_rate":statistics.mean(float(r["base_score"]) for r in rows) if rows else None,
        "treatment_score_rate":statistics.mean(float(r["treatment_score"]) for r in rows) if rows else None,
        "mean_score_delta":statistics.mean(sd) if sd else None,
        "mean_margin_delta":statistics.mean(md) if md else None,
        "median_margin_delta":statistics.median(md) if md else None,
        "positive_score_contexts":sum(x>0 for x in sd),
        "negative_score_contexts":sum(x<0 for x in sd),
        "loss_to_tie":sum(r["base_score"]==0.0 and r["treatment_score"]==0.5 for r in rows),
        "loss_to_win":sum(r["base_score"]==0.0 and r["treatment_score"]==1.0 for r in rows),
        "win_to_nonwin":sum(r["base_score"]==1.0 and r["treatment_score"]<1.0 for r in rows),
        "mean_fire_count":statistics.mean(r["fire_count"] for r in rows) if rows else None,
        "total_changed_slots":sum(r["changed_slots"] for r in rows),
        "total_cleared_slots":sum(r["cleared_slots"] for r in rows),
        "total_qty_down_slots":sum(r["qty_down_slots"] for r in rows),
    }
    if (
        mech and summary["mean_score_delta"] is not None
        and summary["mean_score_delta"]>=0.125
        and summary["positive_score_contexts"]>=4
        and summary["negative_score_contexts"]==0
        and summary["mean_margin_delta"]>0
    ):
        decision="O_LQ1_V48_CAUSAL_PASS"
    elif mech and summary["mean_score_delta"] is not None and summary["mean_score_delta"]>0:
        decision="O_LQ1_V48_CAUSAL_WEAK"
    elif mech and summary["mean_margin_delta"] is not None and summary["mean_margin_delta"]>0:
        decision="O_LQ1_V48_CAUSAL_MARGIN_ONLY"
    elif mech:
        decision="O_LQ1_V48_CAUSAL_FAIL"
    else:
        decision="O_LQ1_V48_CAUSAL_MECHANICS_INVALID"

    result={
        "schema":"kculture-o-lq1-v48-causal-v1",
        "engine":EXPECTED_ENGINE,
        "operator":{
            "id":"O-LQ1","mode":MODE,"min_step":MIN_STEP,
            "rule":"from step 336, projected own-inventory sequential SELL clamp/clear on exact V47 market",
            "runtime_uses_v48_code":False,
        },
        "seeds":SEEDS,"mechanical_pass":mech,
        "summary":summary,"decision":decision,
        "rows":rows,"failures":failures,"provenance":provenance,
        "seconds":time.perf_counter()-started,
        "automatic_kaggle_submission":False,
    }
    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("O_LQ1_V48_CAUSAL_RESULT",json.dumps({
        "decision":decision,"mechanical_pass":mech,"summary":summary,
        "failures":len(failures),"seconds":result["seconds"]
    },sort_keys=True),flush=True)
    if not mech:
        raise SystemExit(2)

if __name__=="__main__":
    main()
