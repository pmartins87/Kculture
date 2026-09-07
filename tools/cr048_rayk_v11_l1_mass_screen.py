"""CR048: exact Rayk V11 adaptive agent vs frozen CR029 on kagsim L1.

The candidate is loaded from the exact public V11 packaged main.py and receives
bit-exact 1.32.7 observations turn by turn. CR029 stays the frozen fixed stream.
Every seed is played in both seats. No Kaggle submission is made.
"""
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
CFG = ROOT / "configs/cr048_rayk_v11_l1_mass_screen.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    lo, hi = int(spec["range_min"]), int(spec["range_max"])
    n = int(spec["count"])
    out = set()
    while len(out) < n:
        out.add(r.randint(lo, hi))
    return sorted(out)


def load_agent(path: Path):
    name = f"cr048_rayk_{time.time_ns()}"
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
    agent = load_agent(candidate_path)  # reset all module-level adaptive state per episode
    game = kagsim.Game(int(seed))
    while not game.done:
        t = int(game.step_count)
        base = base_actions[t] if t < len(base_actions) else PASS
        if seat == 0:
            a0 = call_agent(agent, game.observe(0))
            a1 = base
        else:
            a0 = base
            a1 = call_agent(agent, game.observe(1))
        game.step(a0 or PASS, a1 or PASS)
    mine = float(game.reward(seat))
    opp = float(game.reward(1 - seat))
    if not math.isfinite(mine) or not math.isfinite(opp):
        raise RuntimeError("non-finite reward")
    return mine, opp


def summarize(rows: list[dict]) -> dict:
    margins = [r["margin"] for r in rows]
    ordered = sorted(margins)
    wins = sum(x > 0 for x in margins)
    losses = sum(x < 0 for x in margins)
    ties = len(margins) - wins - losses
    return {
        "games": len(rows),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "score_total": wins + 0.5 * ties,
        "score_rate": (wins + 0.5 * ties) / len(rows) if rows else None,
        "mean_margin": statistics.mean(margins) if margins else None,
        "median_margin": statistics.median(margins) if margins else None,
        "p05_margin": ordered[max(0, int(0.05 * (len(ordered)-1)))] if ordered else None,
        "p95_margin": ordered[min(len(ordered)-1, int(0.95 * (len(ordered)-1)))] if ordered else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    if str(getattr(kagsim, "ENGINE_VERSION", "")) != str(cfg["engine"]):
        raise RuntimeError(f"wrong kagsim engine {getattr(kagsim, 'ENGINE_VERSION', None)}")
    idle = kagsim.Stream([])
    if tuple(kagsim.run_episode(idle, idle, seed=11)) != (3000.0, 3000.0):
        raise RuntimeError("kagsim self-check failed")

    candidate = Path(args.candidate)
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    expected = cfg["candidate"]
    if receipt.get("handle") != expected["handle"]:
        raise RuntimeError("candidate handle mismatch")
    if receipt.get("archive_sha256") != expected["archive_sha256"]:
        raise RuntimeError("candidate archive hash mismatch")
    if sha256_file(candidate) != expected["main_sha256"] or receipt.get("main_sha256") != expected["main_sha256"]:
        raise RuntimeError("candidate main hash mismatch")

    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base_actions = bundle["recent_top"]["tape"]
    if len(base_actions) != 719:
        raise RuntimeError("CR029 tape length mismatch")

    seeds = make_seeds(cfg["seed_generator"])
    rows = []
    errors = []
    started = time.time()
    for i, seed in enumerate(seeds):
        for seat in (0, 1):
            try:
                mine, opp = play(candidate, base_actions, seed, seat)
                rows.append({"seed": seed, "seat": seat, "reward": mine, "opponent_reward": opp, "margin": mine - opp})
            except Exception as exc:
                errors.append({"seed": seed, "seat": seat, "error": repr(exc)[:1000]})
        if (i + 1) % 64 == 0:
            print(json.dumps({"progress_seeds": i + 1, "games": len(rows), "errors": len(errors), "elapsed_s": time.time() - started}))

    expected_games = 2 * len(seeds)
    overall = summarize(rows)
    seat0 = summarize([r for r in rows if r["seat"] == 0])
    seat1 = summarize([r for r in rows if r["seat"] == 1])
    gate = cfg["promotion_gate"]
    error_rate = len(errors) / expected_games
    checks = {
        "complete": len(rows) == expected_games and not errors,
        "score_rate": overall["score_rate"] is not None and overall["score_rate"] >= float(gate["min_score_rate_vs_cr029"]),
        "mean_margin": overall["mean_margin"] is not None and overall["mean_margin"] >= float(gate["min_mean_margin"]),
        "error_rate": error_rate <= float(gate["max_error_rate"]),
    }
    passed = all(checks.values())
    payload = {
        "experiment": cfg["experiment"],
        "engine": cfg["engine"],
        "candidate": expected,
        "receipt": receipt,
        "seed_generator": cfg["seed_generator"],
        "expected_games": expected_games,
        "completed_games": len(rows),
        "errors": errors,
        "error_rate": error_rate,
        "overall": overall,
        "seat0": seat0,
        "seat1": seat1,
        "checks": checks,
        "decision": "SHORTLIST_RAYK_V11_AS_ARCHITECTURE_PARENT" if passed else "CR048_DO_NOT_PROMOTE_RAYK_V11",
        "elapsed_s": time.time() - started,
        "held_out_touched": False,
        "automatic_kaggle_submission": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not checks["complete"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
