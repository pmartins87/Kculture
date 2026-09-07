"""CR058: broad live-agent league after CR029 proxy failure.

This is deliberately NOT a candidate-vs-CR029 gate.  It runs exact hosted/public
packages against each other on common fresh seeds, both seats, so we can compare
non-transitive matchup structure with the hosted ratings we observe.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import shutil
import statistics
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import kagsim

PASS = {"farmer": ["PASS"], "hands": [], "market": []}
MASTER_SEED = 5809072026
SEED_COUNT = 64


def make_seeds() -> list[int]:
    r = random.Random(MASTER_SEED); out = set()
    while len(out) < SEED_COUNT: out.add(r.randint(1, 2147483646))
    return sorted(out)


def extract(archive: Path, root: Path) -> Path:
    dst = root / archive.stem.replace(".tar", "")
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as tf:
        for m in tf.getmembers():
            target = (dst / m.name).resolve()
            if dst.resolve() not in target.parents and target != dst.resolve():
                raise RuntimeError(f"unsafe member {m.name}")
        tf.extractall(dst)
    if not (dst / "main.py").is_file(): raise RuntimeError(f"main.py absent in {archive}")
    return dst


def clear_local_modules(package_dir: Path) -> None:
    p = str(package_dir.resolve())
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if f:
            try:
                if str(Path(f).resolve()).startswith(p): sys.modules.pop(name, None)
            except Exception:
                pass


def load_agent(package_dir: Path):
    clear_local_modules(package_dir)
    sys.path.insert(0, str(package_dir.resolve()))
    try:
        p = package_dir / "main.py"
        spec = importlib.util.spec_from_file_location(f"cr058_{time.time_ns()}", p)
        if spec is None or spec.loader is None: raise RuntimeError(p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        a = getattr(mod, "agent", None)
        if not callable(a): raise RuntimeError("no callable agent")
        return a
    finally:
        try: sys.path.remove(str(package_dir.resolve()))
        except ValueError: pass


def call(agent, obs):
    config = {"episodeSteps": 720}
    try: return agent(obs, config)
    except TypeError: return agent(obs)


def play(a_dir: Path, b_dir: Path, seed: int) -> tuple[float, float]:
    a = load_agent(a_dir); b = load_agent(b_dir); game = kagsim.Game(int(seed))
    while not game.done:
        x = call(a, game.observe(0)) or PASS; y = call(b, game.observe(1)) or PASS
        game.step(x, y)
    r0 = float(game.reward(0)); r1 = float(game.reward(1))
    if not math.isfinite(r0) or not math.isfinite(r1): raise RuntimeError("nonfinite reward")
    return r0, r1


def summarize(margins: list[float]) -> dict:
    w=sum(x>0 for x in margins); l=sum(x<0 for x in margins); t=len(margins)-w-l
    return {"games":len(margins),"wins":w,"losses":l,"ties":t,
            "score_rate":(w+0.5*t)/len(margins) if margins else None,
            "mean_margin":statistics.mean(margins) if margins else None,
            "median_margin":statistics.median(margins) if margins else None}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--a",required=True); ap.add_argument("--b",required=True); ap.add_argument("--a-id",required=True); ap.add_argument("--b-id",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
    if str(getattr(kagsim,"ENGINE_VERSION","")) != "1.32.7": raise RuntimeError("wrong engine")
    seeds=make_seeds(); margins=[]; rows=[]; errors=[]
    with tempfile.TemporaryDirectory(prefix="cr058-league-") as td:
        root=Path(td); a_dir=extract(Path(args.a),root); b_dir=extract(Path(args.b),root)
        start=time.time()
        for i, seed in enumerate(seeds):
            for swap in (False, True):
                try:
                    if not swap:
                        r0,r1=play(a_dir,b_dir,seed); margin=r0-r1
                    else:
                        r0,r1=play(b_dir,a_dir,seed); margin=r1-r0
                    margins.append(float(margin)); rows.append({"seed":seed,"a_seat":1 if swap else 0,"margin":float(margin)})
                except Exception as exc:
                    errors.append({"seed":seed,"swap":swap,"error":repr(exc)[:1000]})
            if (i+1)%16==0: print(json.dumps({"pair":f"{args.a_id}-{args.b_id}","seeds":i+1,"games":len(rows),"errors":len(errors),"elapsed_s":time.time()-start}))
    payload={"experiment":"CR058_BROAD_LIVE_AGENT_LEAGUE_V1","engine":"1.32.7","a":args.a_id,"b":args.b_id,"master_seed":MASTER_SEED,"seed_count":SEED_COUNT,"metrics_a_vs_b":summarize(margins),"errors":errors,"rows":rows}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps({k:v for k,v in payload.items() if k!="rows"},indent=2,sort_keys=True))
    if errors: raise SystemExit(3)

if __name__=="__main__": main()
