"""CR043: independent probe of current ~3000 official winners vs CR029.

This is deliberately outside the CR039/rank5 line. It freezes eight public
2026-09-06 official top-episode representatives, verifies replay provenance,
measures how far their complete action trajectories differ from CR029, and
plays CR029 against each winner tape on the original environment/seed in both
seats. Diagnostic only: no candidate is promoted from this probe alone.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import math
import statistics
import tempfile
from pathlib import Path

import kagglehub
from kaggle_environments import make

import cr035_public_regime_selector_shard as core

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr043_latest_top3000_probe.json"
PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
WINDOWS = ((0,23),(24,167),(168,287),(288,431),(432,575),(576,647),(648,695),(696,718))


def _download(handle: str, name: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = Path(kagglehub.dataset_download(handle, path=name, output_dir=str(out), force_download=True))
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def _actions(rep: dict, seat: int) -> list[dict]:
    steps = rep.get("steps") or []
    return [copy.deepcopy((steps[t][seat] or {}).get("action") or {}) for t in range(1, len(steps))]


def _canon(x) -> str:
    return json.dumps(x if isinstance(x,dict) else {}, sort_keys=True, separators=(",",":"), ensure_ascii=True)


def _sha(tape: list[dict]) -> str:
    return hashlib.sha256(_canon(tape).encode("utf-8")).hexdigest()


def _farm_comp(farm: dict) -> dict:
    c = collections.Counter()
    for row in farm.get("tiles",[]) or []:
        for tile in row or []:
            if not isinstance(tile,dict):
                continue
            if tile.get("animal"):
                c[str(tile["animal"])] += 1
            elif tile.get("kind") == "PLANT" and tile.get("crop"):
                c[str(tile["crop"])] += 1
            elif tile.get("kind") == "WEED":
                c["WEED"] += 1
    return dict(c)


def _state_profile(obs: dict, player: int) -> dict:
    farms = obs.get("farms") or []
    if len(farms) < 2 or player >= len(farms):
        return {}
    f = farms[player]
    o = farms[1-player]
    comp = _farm_comp(f)
    opp = _farm_comp(o)
    return {
        "money": float(f.get("money",0) or 0),
        "opp_money": float(o.get("money",0) or 0),
        "money_gap": float(f.get("money",0) or 0)-float(o.get("money",0) or 0),
        "hands": len(f.get("hands",[]) or []),
        "quads": len(f.get("unlocked_quadrants",[]) or []),
        "herd": sum(int(comp.get(x,0) or 0) for x in ("COW","SHEEP","GOOSE")),
        "opp_herd": sum(int(opp.get(x,0) or 0) for x in ("COW","SHEEP","GOOSE")),
        "comp": comp,
    }


def _probe_agent(tape: list[dict], seat: int, checkpoints: set[int], probe: dict[int,dict]):
    def agent(obs, config=None):
        s=max(0,min(718,core._clock(obs)))
        if s in checkpoints and s not in probe:
            probe[s]=_state_profile(obs,seat)
        return copy.deepcopy(tape[s])
    return agent


def _plain_agent(tape: list[dict]):
    def agent(obs, config=None):
        s=max(0,min(718,core._clock(obs)))
        return copy.deepcopy(tape[s])
    return agent


def _final(rep: dict) -> tuple[list[float],list[str]]:
    st=rep.get("steps") or []
    if len(st)!=720:
        raise RuntimeError(f"steps={len(st)}")
    statuses=[st[-1][i].get("status") for i in (0,1)]
    if statuses != ["DONE","DONE"]:
        raise RuntimeError(f"statuses={statuses}")
    rewards=[float(st[-1][i].get("reward")) for i in (0,1)]
    if not all(math.isfinite(x) for x in rewards):
        raise RuntimeError("nonfinite reward")
    return rewards,statuses


def _play(candidate: list[dict], opponent: list[dict], conf: dict, seed: int, seat: int, checkpoints: list[int]) -> dict:
    own_probe={}; opp_probe={}
    own=_probe_agent(candidate,seat,set(checkpoints),own_probe)
    opp=_probe_agent(opponent,1-seat,set(checkpoints),opp_probe)
    cc=copy.deepcopy(conf);cc["episodeSteps"]=720;cc["seed"]=int(seed)
    env=make("kaggriculture",configuration=cc,debug=True)
    env.run([own,opp] if seat==0 else [opp,own])
    rep=env.toJSON();rewards,_=_final(rep)
    delta=rewards[seat]-rewards[1-seat]
    return {"score":core._wl(delta),"delta":delta,"self_reward":rewards[seat],"opp_reward":rewards[1-seat],"candidate_checkpoints":own_probe,"opponent_checkpoints":opp_probe}


def _replay_pair(t0: list[dict], t1: list[dict], conf: dict, seed: int) -> dict:
    cc=copy.deepcopy(conf);cc["episodeSteps"]=720;cc["seed"]=int(seed)
    env=make("kaggriculture",configuration=cc,debug=True)
    env.run([_plain_agent(t0),_plain_agent(t1)])
    rewards,_=_final(env.toJSON())
    return {"rewards":rewards}


def _agreement(a: list[dict], b: list[dict]) -> dict:
    out={}
    for lo,hi in WINDOWS:
        vals=[_canon(a[t])==_canon(b[t]) for t in range(lo,hi+1)]
        out[f"{lo}_{hi}"]={"exact_matches":sum(vals),"steps":len(vals),"rate":sum(vals)/len(vals)}
    return out


def _market_totals(tape: list[dict]) -> dict:
    q=collections.Counter()
    for a in tape:
        for row in a.get("market",[]) or []:
            if not (isinstance(row,list) and row):
                continue
            op=str(row[0]); item=str(row[1]) if len(row)>1 else ""
            try: qty=int(row[2]) if len(row)>2 else 1
            except Exception: qty=1
            q[f"{op}:{item}"] += qty
    return dict(q)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-bundle",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    bundle=json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base=bundle["recent_top"]["tape"]
    if len(base)!=719 or core._tape_sha(base)!=bundle["recent_top"]["tape_sha256"]:
        raise RuntimeError("CR029 source-bundle mismatch")
    checkpoints=[int(x) for x in cfg["checkpoints"] if int(x)<=718]
    rows=[]; episodes=[]; errors=[]
    with tempfile.TemporaryDirectory(prefix="cr043-") as td0:
        td=Path(td0)
        for meta in cfg["episodes"]:
            eid=int(meta["episode_id"])
            try:
                p=_download(cfg["day_handle"],f"{eid}.json",td/str(eid))
                rep=json.loads(p.read_text(encoding="utf-8")); steps=rep.get("steps") or []
                if len(steps)!=720: raise RuntimeError(f"episode {eid} steps={len(steps)}")
                info=rep.get("info") or {}; names=info.get("TeamNames") or ["p0","p1"]
                rewards=[float(steps[-1][i].get("reward")) for i in (0,1)]
                win=0 if rewards[0]>=rewards[1] else 1
                if win!=int(meta["expected_winner_seat"]): raise RuntimeError(f"winner seat {win}")
                if str(names[win])!=str(meta["expected_winner_team"]): raise RuntimeError(f"winner team {names[win]}")
                seed=int(info.get("seed")); conf=rep.get("configuration") if isinstance(rep.get("configuration"),dict) else {}
                tapes=[_actions(rep,0),_actions(rep,1)]
                if any(len(t)!=719 for t in tapes): raise RuntimeError("bad tape length")
                reproduced=_replay_pair(tapes[0],tapes[1],conf,seed)
                reproduce_exact=all(abs(reproduced["rewards"][i]-rewards[i])<1e-9 for i in (0,1))
                wt=tapes[win]
                ep={
                    "episode_id":eid,"avg_score":float(meta["expected_avg_score"]),"winner_seat":win,"winner_team":str(names[win]),"seed":seed,
                    "original_rewards":rewards,"replayed_rewards":reproduced["rewards"],"replay_exact":reproduce_exact,
                    "winner_tape_sha256":core._tape_sha(wt),"agreement_vs_cr029":_agreement(wt,base),
                    "winner_market_totals":_market_totals(wt),"cr029_market_totals":_market_totals(base),
                }
                episodes.append(ep)
                for seat in (0,1):
                    r=_play(base,wt,conf,seed,seat,checkpoints)
                    rows.append({"episode_id":eid,"winner_team":str(names[win]),"avg_score":float(meta["expected_avg_score"]),"seed":seed,"seat":seat,**r})
            except Exception as exc:
                errors.append({"episode_id":eid,"error":repr(exc)[:1000]})
    scores=[float(r["score"]) for r in rows]; deltas=[float(r["delta"]) for r in rows]
    by_team={}
    for team in sorted(set(r["winner_team"] for r in rows)):
        rr=[r for r in rows if r["winner_team"]==team]; ss=[x["score"] for x in rr]; dd=[x["delta"] for x in rr]
        by_team[team]={"games":len(rr),"wins":sum(x==1 for x in ss),"losses":sum(x==0 for x in ss),"ties":sum(x==0.5 for x in ss),"score_total":sum(ss),"mean_delta":statistics.mean(dd) if dd else None}
    out={
        "experiment":cfg["experiment"],"source_date":cfg["source_date"],"mechanical_complete":not errors and len(rows)==2*len(cfg["episodes"]),"errors":errors,
        "cr029_vs_top3000":{"games":len(rows),"wins":sum(x==1 for x in scores),"losses":sum(x==0 for x in scores),"ties":sum(x==0.5 for x in scores),"score_total":sum(scores),"score_rate":sum(scores)/len(scores) if scores else None,"mean_delta":statistics.mean(deltas) if deltas else None,"median_delta":statistics.median(deltas) if deltas else None},
        "by_winner_team":by_team,"episodes":episodes,"rows":rows,
        "diagnostic_only":True,"runtime_identity_features":False,"fresh_validation_touched":False,"held_out_touched":False,"automatic_kaggle_submission":False,
    }
    op=Path(args.output);op.parent.mkdir(parents=True,exist_ok=True);op.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k not in ("rows","episodes")},indent=2,sort_keys=True,ensure_ascii=False))
    if errors: raise SystemExit(3)

if __name__=="__main__": main()
