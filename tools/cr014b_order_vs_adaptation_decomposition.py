"""CR-014B: decompose adaptive-sale effect from market-order-position effect.

Uses only the 16 CR-014 pairs that were already known to be affected.  This is
mechanistic diagnosis, never validation.  For every pair it runs frozen R4B,
CR-008 (same adaptive sale appended) and CR-011 (same adaptive sale prefixed),
checks R4B/CR-011 parity against the frozen CR-014 terminal outcomes, then asks:

  1. did CR-008 already create the bad/good terminal effect?
  2. what additional effect came solely from moving the same order earlier?
  3. at the first CR-008/CR-011 action difference, are observations identical
     and are market-order multisets identical (only sequence changed)?
  4. how do money, shed, and public market state differ immediately afterward?

The report deliberately avoids opponent-identity gates; names are reporting keys.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CFG = ROOT / "configs/cr014b_affected_pairs_v1.json"
ARMS = {
    "r4b": ROOT / "candidates/r4b_ablation_market_only.py",
    "cr008": ROOT / "candidates/cr008_adaptive_frontrun.py",
    "cr011": ROOT / "candidates/cr011_adaptive_early_order.py",
}


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(f"cr014b_{path.stem}_{time.time_ns()}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.agent


def play(path: Path, opponent: Path, seed: int, seat: int):
    a = load_agent(path); o = load_agent(opponent)
    env = make("kaggriculture", configuration={"episodeSteps":720,"seed":int(seed)}, debug=True)
    env.run([a,o] if seat == 0 else [o,a])
    return env.toJSON()


def final(rep, seat: int):
    frame=rep["steps"][-1]
    if [frame[i].get("status") for i in range(2)] != ["DONE","DONE"]:
        raise RuntimeError("non-DONE")
    own=float(frame[seat].get("reward")); opp=float(frame[1-seat].get("reward"))
    return own,opp,own-opp


def action(rep,seat,t):
    if t+1 >= len(rep["steps"]): return {}
    x=rep["steps"][t+1][seat].get("action")
    return x if isinstance(x,dict) else {}


def obs(rep,seat,t):
    if t < 0 or t >= len(rep["steps"]): return {}
    x=rep["steps"][t][seat].get("observation")
    return x if isinstance(x,dict) else {}


def get(obj,key,default=None):
    try:return obj.get(key,default)
    except Exception:return default


def farm_money(o,seat):
    fs=get(o,"farms",[]) or []
    try:return float(get(fs[seat],"money",0) or 0)
    except Exception:return None


def shed_qty(o,item):
    try:return float(get(get(get(o,"private",{}) or {},"shed",{}) or {},item,0) or 0)
    except Exception:return None


def market_value(o,section,item):
    try:return float(get(get(get(o,"market",{}) or {},section,{}) or {},item,0) or 0)
    except Exception:return None


def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"))

def mcounter(a): return collections.Counter(canon(x) for x in (a.get("market") or []))


def compact_state(o,seat):
    return {
        "money":farm_money(o,seat),
        "strawberry_shed":shed_qty(o,"STRAWBERRY"),
        "strawberry_price":market_value(o,"prices","STRAWBERRY"),
        "strawberry_inventory":market_value(o,"inventory","STRAWBERRY"),
    }


def diff_state(a,b):
    aa=compact_state(a[0],a[1]); bb=compact_state(b[0],b[1])
    out={}
    for k in aa:
        av=aa[k]; bv=bb[k]
        out[k]={"a":av,"b":bv,"a_minus_b":(av-bv if av is not None and bv is not None else None)}
    return out


def score(d): return 1.0 if d>0 else 0.0 if d<0 else 0.5


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--opponent-dir",required=True); ap.add_argument("--output",required=True)
    args=ap.parse_args()
    od=Path(args.opponent_dir); od=od if od.is_absolute() else ROOT/od
    cfg=json.loads(CFG.read_text())
    rows=[]; parity=[]
    for e in cfg["pairs"]:
        opp=od/f"{e['opponent']}.py"; seat=int(e["seat"]); seed=int(e["seed"])
        reps={k:play(p,opp,seed,seat) for k,p in ARMS.items()}
        vals={}
        for k,r in reps.items():
            own,other,delta=final(r,seat); vals[k]={"self":own,"opp":other,"delta":delta,"score":score(delta)}
        if abs(vals["r4b"]["delta"]-float(e["base_delta"]))>1e-9 or abs(vals["cr011"]["delta"]-float(e["candidate_delta"]))>1e-9:
            parity.append({"opponent":e["opponent"],"seed":seed,"seat":seat,"observed":vals,"expected":e})

        first=None
        for t in range(min(len(reps["cr008"]["steps"]),len(reps["cr011"]["steps"]))-1):
            a8=action(reps["cr008"],seat,t); a11=action(reps["cr011"],seat,t)
            if a8 != a11:
                o8=obs(reps["cr008"],seat,t); o11=obs(reps["cr011"],seat,t)
                n8=obs(reps["cr008"],seat,t+1); n11=obs(reps["cr011"],seat,t+1)
                first={
                    "step":t,
                    "observations_identical":canon(o8)==canon(o11),
                    "market_multiset_identical":mcounter(a8)==mcounter(a11),
                    "cr008_action":a8,
                    "cr011_action":a11,
                    "before_cr008":compact_state(o8,seat),
                    "before_cr011":compact_state(o11,seat),
                    "after_state_cr011_minus_cr008":diff_state((n11,seat),(n8,seat)),
                }
                break
        row={
            "opponent":e["opponent"],"seed":seed,"seat":seat,"cr014_score_gain":e["score_gain"],
            "terminal":vals,
            "adaptation_vs_r4b":{
                "relative":vals["cr008"]["delta"]-vals["r4b"]["delta"],
                "self":vals["cr008"]["self"]-vals["r4b"]["self"],
                "score":vals["cr008"]["score"]-vals["r4b"]["score"],
            },
            "order_position_cr011_vs_cr008":{
                "relative":vals["cr011"]["delta"]-vals["cr008"]["delta"],
                "self":vals["cr011"]["self"]-vals["cr008"]["self"],
                "score":vals["cr011"]["score"]-vals["cr008"]["score"],
            },
            "first_cr008_cr011_difference":first,
        }
        rows.append(row)

    def agg(field):
        xs=[r[field] for r in rows]
        return {k:statistics.mean(x[k] for x in xs) for k in ("relative","self","score")}
    cats=[r for r in rows if r["cr014_score_gain"]<0]
    good=[r for r in rows if r["cr014_score_gain"]>0]
    def group(xs):
        if not xs:return {}
        return {
            "n":len(xs),
            "adaptation_vs_r4b":{k:statistics.mean(r["adaptation_vs_r4b"][k] for r in xs) for k in ("relative","self","score")},
            "order_position_cr011_vs_cr008":{k:statistics.mean(r["order_position_cr011_vs_cr008"][k] for r in xs) for k in ("relative","self","score")},
            "first_difference_steps":sorted(set(r["first_cr008_cr011_difference"]["step"] for r in xs if r["first_cr008_cr011_difference"])),
        }
    payload={
        "experiment":"CR-014B",
        "status":"PASS" if not parity else "PARITY_FAIL",
        "pairs":len(rows),"parity_errors":parity,
        "all":{"adaptation_vs_r4b":agg("adaptation_vs_r4b"),"order_position_cr011_vs_cr008":agg("order_position_cr011_vs_cr008")},
        "catastrophic_cr014_group":group(cats),
        "favorable_cr014_group":group(good),
        "rows":rows,
        "interpretation":"Separate whether CR-014 damage originates in taking the adaptive sale at all or specifically in executing that same sale before base market orders. This diagnostic may motivate CR-015 but is not validation."
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in payload.items() if k not in ("rows","parity_errors")}|{"parity_error_count":len(parity)},indent=2,sort_keys=True))
    if parity: raise SystemExit(2)

if __name__=="__main__": main()
