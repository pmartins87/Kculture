"""CR049: stepwise 1-NN behavior clone of the frozen live king (56064100).

Public replays provide observation -> next-action pairs. For each clock, train on
32 episodes and retrieve the action attached to the nearest public state. The
policy never uses submission/team/opponent identity or the episode seed. Eight
other king episodes measure imitation accuracy; fresh kagsim L1 seasons measure
whether the clone remains functional off the replay manifold.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import json
import math
import random
import statistics
import time
from pathlib import Path

import numpy as np
import requests
import kagsim

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr049_live_king_knn_clone.json"
LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
REPLAY_URL = "https://www.kaggleusercontent.com/episodes/{id}.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}
PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
COUNT_KEYS = ("COW","SHEEP","GOOSE","WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","PASTURE","COOP","WEED","PLANT","SOIL","EMPTY")
MAX_HANDS = 12
MAX_ACTORS = 13


def fetch_json(url: str, *, post=None, tries=5, timeout=180):
    last = None
    for i in range(tries):
        try:
            r = requests.post(url, json=post, timeout=timeout) if post is not None else requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            if i + 1 < tries:
                time.sleep(4 * (i + 1))
    raise last


def fnum(x, default=0.0):
    try:
        if isinstance(x, dict):
            for k in ("value","current","level","price","inventory"):
                if k in x:
                    return fnum(x[k], default)
            return default
        v = float(x)
        return v if math.isfinite(v) else default
    except Exception:
        return default


def getxy(p):
    try:
        return float(p[0]), float(p[1])
    except Exception:
        return -1.0, -1.0


def farm_vec(farm: dict) -> list[float]:
    out = [fnum(farm.get("money"))/10000.0]
    hands = list(farm.get("hands") or [])
    out += [len(hands)/12.0, len(farm.get("unlocked_quadrants") or [])/4.0]
    x,y = getxy(farm.get("farmer") or [-1,-1]); out += [x/6.0,y/6.0]
    for i in range(MAX_HANDS):
        x,y = getxy(hands[i] if i < len(hands) else [-1,-1]); out += [x/6.0,y/6.0]
    counts = {k:0.0 for k in COUNT_KEYS}
    ysum = 0.0
    for row in farm.get("tiles") or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            for key in ("animal","crop","kind"):
                v = tile.get(key)
                if v in counts:
                    counts[v] += 1.0
            ysum += fnum(tile.get("yield_units"))
    out += [counts[k]/20.0 for k in COUNT_KEYS]
    out.append(ysum/100.0)
    return out


def dict_product_vec(d: dict, scale: float) -> list[float]:
    d = d if isinstance(d, dict) else {}
    return [fnum(d.get(p))/scale for p in PRODUCTS]


def signature(obs: dict) -> tuple[np.ndarray, tuple[str,...]]:
    player = int(obs.get("player",0) or 0)
    farms = list(obs.get("farms") or [{},{}])
    while len(farms) < 2:
        farms.append({})
    own = farms[player] if player < len(farms) else {}
    opp = farms[1-player] if len(farms) > 1 else {}
    v = farm_vec(own) + farm_vec(opp)

    private = obs.get("private") or {}
    v += dict_product_vec(private.get("shed") or {}, 100.0)
    v += dict_product_vec(private.get("seeds") or {}, 50.0)
    invs = list(private.get("inventories") or [])
    for i in range(MAX_ACTORS):
        v += dict_product_vec(invs[i] if i < len(invs) else {}, 30.0)

    market = obs.get("market") or {}
    v += dict_product_vec(market.get("prices") or {}, 500.0)
    v += dict_product_vec(market.get("inventory") or market.get("inventories") or {}, 10000.0)
    v += dict_product_vec(market.get("demand") or market.get("demand_levels") or {}, 10.0)

    shops = list(((obs.get("town") or {}).get("unlocked_shops") or []))
    cats = tuple(str(shops[i]) if i < len(shops) else "" for i in range(3))
    weather = obs.get("weather")
    if weather is not None:
        cats += (str(weather),)
    return np.asarray(v, dtype=np.float32), cats


def canon(x) -> str:
    return json.dumps(x if isinstance(x, dict) else {}, sort_keys=True, separators=(",",":"), ensure_ascii=True)


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    lo, hi = int(spec["range_min"]), int(spec["range_max"])
    n = int(spec["count"])
    out = set()
    while len(out) < n:
        out.add(r.randint(lo, hi))
    return sorted(out)


def locate_seat(meta: dict, submission_id: int) -> int:
    for a in meta.get("agents") or []:
        if int(a.get("submissionId") or -1) == submission_id:
            return int(a.get("index") or 0)
    raise RuntimeError("submission absent from episode agents")


def episode_pairs(meta: dict, submission_id: int) -> dict:
    eid = int(meta["id"])
    seat = locate_seat(meta, submission_id)
    rep = fetch_json(REPLAY_URL.format(id=eid))
    steps = rep.get("steps") or []
    if len(steps) < 720:
        raise RuntimeError(f"short replay {eid}: {len(steps)}")
    pairs = []
    for t in range(719):
        obs = (steps[t][seat] or {}).get("observation") or {}
        action = (steps[t+1][seat] or {}).get("action") or PASS
        vec,cats = signature(obs)
        pairs.append((vec,cats,copy.deepcopy(action)))
    return {"episode_id":eid,"seat":seat,"end_time":meta.get("endTime"),"pairs":pairs}


class StepKNN:
    def __init__(self, episodes: list[dict], cat_penalty: float):
        self.cat_penalty = float(cat_penalty)
        self.vecs = []
        self.cats = []
        self.actions = []
        for t in range(719):
            self.vecs.append(np.stack([e["pairs"][t][0] for e in episodes], axis=0))
            self.cats.append([e["pairs"][t][1] for e in episodes])
            self.actions.append([e["pairs"][t][2] for e in episodes])

    def predict(self, obs: dict, t: int) -> tuple[dict,float,int]:
        t = max(0,min(718,int(t)))
        q,c = signature(obs)
        m = self.vecs[t]
        d = np.sum((m - q[None,:]) ** 2, axis=1)
        if self.cat_penalty:
            penalty = np.asarray([sum(a != b for a,b in zip(c,tc)) for tc in self.cats[t]], dtype=np.float32)
            d = d + self.cat_penalty * penalty
        idx = int(np.argmin(d))
        return copy.deepcopy(self.actions[t][idx]), float(d[idx]), idx


def imitation_report(model: StepKNN, holdout: list[dict]) -> dict:
    counts = {"full":0,"farmer":0,"hands":0,"market":0,"total":0}
    distances=[]
    by_episode=[]
    for e in holdout:
        ec={k:0 for k in counts}
        ed=[]
        for t,(vec,cats,target) in enumerate(e["pairs"]):
            # Rebuild a minimal query is impossible from vec alone; holdout stores original
            # signature, so directly score nearest training signature and compare action.
            m=model.vecs[t]
            d=np.sum((m-vec[None,:])**2,axis=1)
            if model.cat_penalty:
                d += model.cat_penalty*np.asarray([sum(a!=b for a,b in zip(cats,tc)) for tc in model.cats[t]],dtype=np.float32)
            idx=int(np.argmin(d)); pred=model.actions[t][idx]
            ec["total"]+=1; counts["total"]+=1
            if canon(pred)==canon(target): ec["full"]+=1; counts["full"]+=1
            for ch in ("farmer","hands","market"):
                if json.dumps(pred.get(ch),sort_keys=True,separators=(",",":"))==json.dumps(target.get(ch),sort_keys=True,separators=(",",":")):
                    ec[ch]+=1; counts[ch]+=1
            ed.append(float(d[idx])); distances.append(float(d[idx]))
        by_episode.append({"episode_id":e["episode_id"],"rates":{k:ec[k]/ec["total"] for k in ("full","farmer","hands","market")},"median_distance":statistics.median(ed)})
    return {"rates":{k:counts[k]/counts["total"] for k in ("full","farmer","hands","market")},"median_distance":statistics.median(distances) if distances else None,"by_episode":by_episode}


def play_knn(model: StepKNN, base_actions: list[dict], seed: int, seat: int) -> tuple[float,float,list[float]]:
    game=kagsim.Game(int(seed)); ds=[]
    while not game.done:
        t=int(game.step_count)
        base=base_actions[t] if t < len(base_actions) else PASS
        if seat==0:
            a0,d,_=model.predict(game.observe(0),t); a1=base
        else:
            a0=base; a1,d,_=model.predict(game.observe(1),t)
        ds.append(d); game.step(a0 or PASS,a1 or PASS)
    return float(game.reward(seat)),float(game.reward(1-seat)),ds


def game_metrics(rows: list[dict]) -> dict:
    ms=[r["margin"] for r in rows]; w=sum(x>0 for x in ms); l=sum(x<0 for x in ms); ti=len(ms)-w-l
    return {"games":len(rows),"wins":w,"losses":l,"ties":ti,"score_rate":(w+0.5*ti)/len(rows) if rows else None,"mean_margin":statistics.mean(ms) if ms else None,"median_margin":statistics.median(ms) if ms else None,"median_knn_distance":statistics.median([r["median_knn_distance"] for r in rows]) if rows else None}


def save_model(path: Path, train: list[dict], source_id: int, cat_penalty: float):
    serial={"source_submission_id":source_id,"cat_penalty":cat_penalty,"episodes":[]}
    for e in train:
        serial["episodes"].append({"episode_id":e["episode_id"],"seat":e["seat"],"end_time":e["end_time"],"samples":[{"v":p[0].tolist(),"c":list(p[1]),"a":p[2]} for p in e["pairs"]]})
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,"wt",encoding="utf-8",compresslevel=9) as f:
        json.dump(serial,f,separators=(",",":"),ensure_ascii=True)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source-bundle",required=True); ap.add_argument("--output",required=True); ap.add_argument("--model-output",required=True); args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8")); sid=int(cfg["source_submission_id"])
    if str(getattr(kagsim,"ENGINE_VERSION","")) != "1.32.7": raise RuntimeError("wrong kagsim engine")
    if tuple(kagsim.run_episode(kagsim.Stream([]),kagsim.Stream([]),seed=11)) != (3000.0,3000.0): raise RuntimeError("kagsim self-check failed")
    eps=fetch_json(LIST_URL,post={"submissionId":sid}).get("episodes") or []
    eps=[e for e in eps if e.get("state")=="COMPLETED" and e.get("endTime")]; eps.sort(key=lambda e:e["endTime"],reverse=True)
    sel=eps[:int(cfg["episode_selection"]["completed_latest_n"])]
    if len(sel)<40: raise RuntimeError(f"only {len(sel)} completed episodes")
    loaded=[]; errors=[]
    for i,e in enumerate(sel):
        try: loaded.append(episode_pairs(e,sid))
        except Exception as exc: errors.append({"episode_id":e.get("id"),"phase":"harvest","error":repr(exc)[:1000]})
        if (i+1)%8==0: print(json.dumps({"harvested":len(loaded),"errors":len(errors)}))
    if errors or len(loaded)!=40: raise RuntimeError(f"harvest incomplete: {errors[:2]}")
    ntrain=int(cfg["episode_selection"]["train_newest_n"]); train=loaded[:ntrain]; hold=loaded[ntrain:]
    model=StepKNN(train,float(cfg["knn"]["categorical_mismatch_penalty"])); imitation=imitation_report(model,hold)
    save_model(Path(args.model_output),train,sid,model.cat_penalty)

    bundle=json.loads(Path(args.source_bundle).read_text(encoding="utf-8")); base=bundle["recent_top"]["tape"]
    seeds=make_seeds(cfg["fresh_seed_generator"]); games=[]
    for i,seed in enumerate(seeds):
        for seat in (0,1):
            try:
                mine,opp,ds=play_knn(model,base,seed,seat); games.append({"seed":seed,"seat":seat,"reward":mine,"opponent_reward":opp,"margin":mine-opp,"median_knn_distance":statistics.median(ds)})
            except Exception as exc: errors.append({"seed":seed,"seat":seat,"phase":"fresh","error":repr(exc)[:1000]})
        if (i+1)%8==0: print(json.dumps({"fresh_seeds":i+1,"games":len(games),"errors":len(errors)}))
    gm=game_metrics(games); gate=cfg["fresh_gate"]
    checks={"complete":len(games)==2*len(seeds) and not errors,"score_rate":gm["score_rate"] is not None and gm["score_rate"]>=float(gate["min_score_rate_vs_cr029"]),"mean_margin":gm["mean_margin"] is not None and gm["mean_margin"]>=float(gate["min_mean_margin"]),"errors":len(errors)<=int(gate["max_errors"])}
    passed=all(checks.values())
    payload={"experiment":cfg["experiment"],"source_submission_id":sid,"source_episode_ids":[e["episode_id"] for e in loaded],"train_episode_ids":[e["episode_id"] for e in train],"holdout_episode_ids":[e["episode_id"] for e in hold],"feature_dim":int(model.vecs[0].shape[1]),"train_samples":len(train)*719,"holdout_samples":len(hold)*719,"imitation":imitation,"fresh_seed_generator":cfg["fresh_seed_generator"],"fresh_vs_cr029":gm,"checks":checks,"errors":errors,"decision":"SHORTLIST_CR049_KNN_CLONE_FOR_PACKAGE_ENGINEERING" if passed else "CR049_KNN_CLONE_NOT_READY","held_out_touched":False,"automatic_kaggle_submission":False}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps(payload,indent=2,sort_keys=True))
    if not checks["complete"]: raise SystemExit(3)


if __name__=="__main__": main()
