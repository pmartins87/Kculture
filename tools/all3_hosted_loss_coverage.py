#!/usr/bin/env python3
"""Offline coverage census: how ALL3 would alter mature O-RW1 hosted replay actions.

No opponent identity is used as a runtime feature. Team names appear only in offline
forensic metadata. This is NOT a counterfactual outcome simulator: it identifies
where/when ALL3 changes the recorded O-RW1 action stream and whether losses were
already economically behind before the first intervention.
"""
from __future__ import annotations
import argparse,json,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.bounded_transaction_oracle_v1 import action_key,canonical_action
from tools.first_party_town_wheat_deferral_causal_gate import eligible as tw_eligible,treated_action as tw_treated_action
from tools.first_party_lq2_canonical_sell_queue import lq2_action

TARGET="Paulo Martins"

def target_seat(d):
    names=list((d.get("info") or {}).get("TeamNames") or [])
    hits=[i for i,x in enumerate(names[:2]) if str(x)==TARGET]
    if len(hits)!=1: return None,None
    s=hits[0]
    return s,str(names[1-s])

def money_delta(obs,seat):
    farms=list(obs.get("farms") or [])
    if len(farms)<2: return None
    try:
        return float((farms[seat] or {}).get("money",0))-float((farms[1-seat] or {}).get("money",0))
    except Exception:
        return None

def result_margin(d,seat):
    rw=list(d.get("rewards") or [])
    if len(rw)<2: return None,None
    m=float(rw[seat])-float(rw[1-seat])
    return ("W" if m>0 else "L" if m<0 else "T"),m

def analyze(path):
    d=json.loads(path.read_text(encoding="utf-8"))
    seat,opp=target_seat(d)
    if seat not in (0,1): return None
    result,margin=result_margin(d,seat)
    config=d.get("configuration") or {}
    tw_used=False
    change_steps=[]; lq2_steps=[]; tw_step=None
    changed_slots=0
    pre336_changes=0
    money_series=[]
    first_change_money=None
    first_lq2_money=None

    for idx,step in enumerate(d.get("steps") or []):
        agent=step[seat]
        obs=agent.get("observation") or {}
        # Step may be omitted from seat-1 replay observations. Restore public replay index.
        if "step" not in obs:
            obs={**obs,"step":idx}
        md=money_delta(obs,seat)
        if md is not None: money_series.append((idx,md))
        recorded=canonical_action(agent.get("action"))
        out=recorded

        if (not tw_used) and tw_eligible(obs,config,recorded):
            out,removed=tw_treated_action(recorded)
            if removed>0:
                tw_used=True; tw_step=idx

        before_lq2=canonical_action(out)
        out=lq2_action(obs,config,before_lq2)
        lq2_changed=action_key(out)!=action_key(before_lq2)

        if action_key(out)!=action_key(recorded):
            change_steps.append(idx)
            if idx<336: pre336_changes+=1
            if first_change_money is None: first_change_money=md
            n=max(len(recorded["market"]),len(out["market"]))
            changed_slots += sum(
                (recorded["market"][i] if i<len(recorded["market"]) else []) !=
                (out["market"][i] if i<len(out["market"]) else [])
                for i in range(n)
            )
        if lq2_changed:
            lq2_steps.append(idx)
            if first_lq2_money is None: first_lq2_money=md

    before336=[v for s,v in money_series if s<336]
    at336=next((v for s,v in money_series if s>=336),None)
    min_pre336=min(before336) if before336 else None
    mean_pre336=statistics.fmean(before336) if before336 else None
    last_pre336=before336[-1] if before336 else None

    return {
      "episode_id":str((d.get("info") or {}).get("EpisodeId") or d.get("id") or path.stem),
      "opponent_team":opp,
      "seat":seat,"result":result,"terminal_margin":margin,
      "all3_changed_turns":len(change_steps),
      "all3_first_change":min(change_steps) if change_steps else None,
      "all3_last_change":max(change_steps) if change_steps else None,
      "tw1_step":tw_step,
      "lq2_changed_turns":len(lq2_steps),
      "lq2_first_change":min(lq2_steps) if lq2_steps else None,
      "changed_market_slots":changed_slots,
      "pre336_changed_turns":pre336_changes,
      "money_delta_at_first_change":first_change_money,
      "money_delta_at_first_lq2":first_lq2_money,
      "money_delta_last_pre336":last_pre336,
      "money_delta_at_or_after336":at336,
      "money_delta_min_pre336":min_pre336,
      "money_delta_mean_pre336":mean_pre336,
    }

def avg(xs,key):
    vals=[float(x[key]) for x in xs if x.get(key) is not None]
    return statistics.fmean(vals) if vals else None

def summarize_group(xs):
    return {
      "games":len(xs),
      "mean_terminal_margin":avg(xs,"terminal_margin"),
      "mean_all3_changed_turns":avg(xs,"all3_changed_turns"),
      "mean_lq2_changed_turns":avg(xs,"lq2_changed_turns"),
      "tw1_games":sum(x.get("tw1_step") is not None for x in xs),
      "zero_all3_change_games":sum(x.get("all3_changed_turns",0)==0 for x in xs),
      "mean_first_change_step":avg(xs,"all3_first_change"),
      "mean_money_last_pre336":avg(xs,"money_delta_last_pre336"),
      "mean_money_min_pre336":avg(xs,"money_delta_min_pre336"),
      "behind_at_336":sum((x.get("money_delta_at_or_after336") or 0)<0 for x in xs),
      "ahead_at_336":sum((x.get("money_delta_at_or_after336") or 0)>0 for x in xs),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--replay-root",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.replay_root)
    rows=[]
    failures=[]
    for p in sorted(root.rglob("*.json")):
        try:
            r=analyze(p)
            if r: rows.append(r)
        except Exception as exc:
            failures.append({"file":str(p),"error":f"{type(exc).__name__}: {exc}"})

    losses=[x for x in rows if x["result"]=="L"]
    wins=[x for x in rows if x["result"]=="W"]
    ties=[x for x in rows if x["result"]=="T"]

    # Residual-hard definition is intentionally descriptive, not a causal verdict:
    # loss already behind at step 336 and ALL3's first change is late (>=336).
    residual=[
      x for x in losses
      if (x.get("money_delta_at_or_after336") is not None and x["money_delta_at_or_after336"]<0)
      and (x.get("all3_first_change") is None or x["all3_first_change"]>=336)
    ]
    close_losses=sorted(losses,key=lambda x:abs(x["terminal_margin"]))[:20]
    severe_losses=sorted(losses,key=lambda x:x["terminal_margin"])[:20]

    result={
      "schema":"kculture-all3-hosted-loss-coverage-v1",
      "source":"mature O-RW1 hosted public replays",
      "identity_use":"offline forensic only; prohibited as runtime policy feature",
      "replays":len(rows),"failures":failures,
      "groups":{
        "losses":summarize_group(losses),
        "wins":summarize_group(wins),
        "ties":summarize_group(ties),
        "residual_hard":summarize_group(residual),
      },
      "residual_hard_count":len(residual),
      "residual_hard":sorted(residual,key=lambda x:x["terminal_margin"]),
      "close_losses":close_losses,
      "severe_losses":severe_losses,
      "rows":rows,
      "interpretation_rule":{
        "coverage_only":True,
        "not_counterfactual_outcome":True,
        "next_discovery_priority":"losses already behind by step 336 despite ALL3 changes beginning at/after 336"
      }
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ALL3_HOSTED_LOSS_COVERAGE",json.dumps({
      "replays":len(rows),"failures":len(failures),
      "groups":result["groups"],"residual_hard_count":len(residual),
      "top_residual":[{k:x[k] for k in ("episode_id","opponent_team","seat","terminal_margin","all3_first_change","money_delta_at_or_after336")} for x in result["residual_hard"][:20]]
    },sort_keys=True),flush=True)
    if failures: raise SystemExit(2)

if __name__=="__main__":
    main()
