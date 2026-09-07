"""CR052: exact public Adaptive Route Agent V2 vs frozen CR029 on kagsim L1."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import time
from pathlib import Path

import kagsim

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr052_public_adaptive_v2_screen.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    out = set()
    while len(out) < int(spec["count"]):
        out.add(r.randint(int(spec["range_min"]), int(spec["range_max"])))
    return sorted(out)


def load_agent(path: Path):
    name = f"cr052_agent_{time.time_ns()}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    agent = getattr(mod, "agent", None)
    if not callable(agent):
        raise RuntimeError("candidate main.py has no callable agent")
    return agent


def call_agent(agent, obs):
    try:
        return agent(obs, None)
    except TypeError:
        return agent(obs)


def play(candidate_path: Path, base_actions: list[dict], seed: int, seat: int) -> tuple[float, float]:
    agent = load_agent(candidate_path)
    game = kagsim.Game(int(seed))
    while not game.done:
        t = int(game.step_count)
        base = base_actions[t] if t < len(base_actions) else PASS
        if seat == 0:
            a0, a1 = call_agent(agent, game.observe(0)), base
        else:
            a0, a1 = base, call_agent(agent, game.observe(1))
        game.step(a0 or PASS, a1 or PASS)
    mine = float(game.reward(seat)); opp = float(game.reward(1-seat))
    if not math.isfinite(mine) or not math.isfinite(opp):
        raise RuntimeError("non-finite reward")
    return mine, opp


def summarize(rows: list[dict]) -> dict:
    ms = [r["margin"] for r in rows]
    w = sum(x > 0 for x in ms); l = sum(x < 0 for x in ms); t = len(ms)-w-l
    return {"games":len(rows),"wins":w,"losses":l,"ties":t,
            "score_rate":(w+0.5*t)/len(rows) if rows else None,
            "mean_margin":statistics.mean(ms) if ms else None,
            "median_margin":statistics.median(ms) if ms else None}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate",required=True); ap.add_argument("--receipt",required=True); ap.add_argument("--source-bundle",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    if str(getattr(kagsim,"ENGINE_VERSION","")) != cfg["engine"]: raise RuntimeError("wrong engine")
    idle=kagsim.Stream([])
    if tuple(kagsim.run_episode(idle,idle,seed=11))!=(3000.0,3000.0): raise RuntimeError("kagsim self-check failed")
    receipt=json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    if receipt.get("handle") != cfg["candidate"]["handle"]: raise RuntimeError("handle mismatch")
    candidate=Path(args.candidate)
    if sha256_file(candidate) != receipt.get("main_sha256"): raise RuntimeError("main hash mismatch")
    bundle=json.loads(Path(args.source_bundle).read_text(encoding="utf-8")); base=bundle["recent_top"]["tape"]
    seeds=make_seeds(cfg["seed_generator"]); rows=[]; errors=[]; start=time.time()
    for i,seed in enumerate(seeds):
        for seat in (0,1):
            try:
                mine,opp=play(candidate,base,seed,seat); rows.append({"seed":seed,"seat":seat,"reward":mine,"opponent_reward":opp,"margin":mine-opp})
            except Exception as exc:
                errors.append({"seed":seed,"seat":seat,"error":repr(exc)[:1000]})
        if (i+1)%32==0: print(json.dumps({"seeds":i+1,"games":len(rows),"errors":len(errors),"elapsed_s":time.time()-start}))
    overall=summarize(rows); gate=cfg["promotion_gate"]; expected=2*len(seeds); er=len(errors)/expected
    checks={"complete":len(rows)==expected and not errors,
            "score_rate":overall["score_rate"] is not None and overall["score_rate"]>=float(gate["min_score_rate_vs_cr029"]),
            "mean_margin":overall["mean_margin"] is not None and overall["mean_margin"]>=float(gate["min_mean_margin"]),
            "error_rate":er<=float(gate["max_error_rate"])}
    payload={"experiment":cfg["experiment"],"engine":cfg["engine"],"candidate":cfg["candidate"],"receipt":receipt,
             "seed_generator":cfg["seed_generator"],"overall":overall,"seat0":summarize([r for r in rows if r["seat"]==0]),
             "seat1":summarize([r for r in rows if r["seat"]==1]),"errors":errors,"checks":checks,
             "decision":"SHORTLIST_CR052_FOR_HOSTED_PACKAGE" if all(checks.values()) else "CR052_DO_NOT_PROMOTE",
             "kaggle_hidden_test_touched":False,"automatic_kaggle_submission":False}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps(payload,indent=2,sort_keys=True))
    if not checks["complete"]: raise SystemExit(3)

if __name__=="__main__": main()
