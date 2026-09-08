"""Kaggriculture head-to-head harness whose promotion reference is Kaggle itself.

The default backend is kaggle-environments==1.32.7, not kagsim.  kagsim is an
optional accelerator and may be used for candidate screening only after the
closed-loop parity gate is green for the packages being evaluated.

Production invariants:
* each submission package lives in a fresh spawned Python process per episode;
* both seats are played for every environment seed;
* Kaggle's path-dependent RNG is preserved (no forced shop/draw tape);
* primary promotion evidence is seat-balanced W/L score rate;
* money/coin margin is diagnostic only, never a promotion metric;
* uncertainty is bootstrapped over paired seat results for each seed.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import random
import statistics
import sys
import tarfile
import tempfile
import traceback
from pathlib import Path

PASS = {"farmer": ["PASS"], "hands": [], "market": []}
MASTER_SEED = 5809072026
CALL_TIMEOUT_S = 30.0
BOOTSTRAP_DRAWS = 10000


def norm(x):
    return json.loads(json.dumps(x))


def make_seeds(n: int, master_seed: int = MASTER_SEED) -> list[int]:
    r = random.Random(master_seed)
    out: set[int] = set()
    while len(out) < n:
        out.add(r.randint(1, 2147483646))
    return sorted(out)


def extract(archive: Path, root: Path, tag: str) -> Path:
    dst = root / tag
    dst.mkdir(parents=True, exist_ok=True)
    base = dst.resolve()
    with tarfile.open(archive, "r:*") as tf:
        for member in tf.getmembers():
            target = (dst / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name!r}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"links are not accepted in submission archive: {member.name!r}")
        tf.extractall(dst)
    if not (dst / "main.py").is_file():
        raise RuntimeError(f"main.py absent in {archive}")
    return dst


def _call_agent(fn, obs, config):
    try:
        return fn(obs, config)
    except TypeError:
        return fn(obs)


def _worker(conn, package_dir_s: str, label: str, rng_seed: int) -> None:
    """One submission sandbox. Process isolation prevents sys.modules leakage."""
    package_dir = Path(package_dir_s).resolve()
    sys.path.insert(0, str(package_dir))
    os.chdir(package_dir)
    # Deterministic agent RNG makes local experiments reproducible.  The parity
    # gate verifies transition/observation fidelity; stochastic-agent calibration
    # must be treated separately if a candidate actually consumes these RNGs.
    random.seed(int(rng_seed))
    try:
        import numpy as np
        np.random.seed(int(rng_seed) % (2**32 - 1))
    except Exception:
        pass
    try:
        import importlib.util
        p = package_dir / "main.py"
        spec = importlib.util.spec_from_file_location(f"kculture_{label}", p)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {p}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "agent", None)
        if not callable(fn):
            fn = getattr(mod, "kaggriculture_agent", None)
        if not callable(fn):
            raise RuntimeError(f"no callable agent in {p}")
        conn.send({"ok": True, "ready": True})
        while True:
            msg = conn.recv()
            if msg.get("cmd") == "close":
                break
            if msg.get("cmd") != "call":
                raise RuntimeError(f"unknown worker command: {msg!r}")
            try:
                action = _call_agent(fn, msg["obs"], msg["config"])
                conn.send({"ok": True, "action": action or PASS})
            except Exception as exc:
                conn.send({
                    "ok": False,
                    "error": repr(exc),
                    "traceback": traceback.format_exc()[-6000:],
                })
    except Exception as exc:
        try:
            conn.send({
                "ok": False,
                "ready": False,
                "error": repr(exc),
                "traceback": traceback.format_exc()[-6000:],
            })
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


class AgentProcess:
    def __init__(self, ctx, package_dir: Path, label: str, rng_seed: int):
        self.parent, child = ctx.Pipe()
        self.proc = ctx.Process(
            target=_worker,
            args=(child, str(package_dir), label, int(rng_seed)),
            daemon=True,
        )
        self.proc.start()
        child.close()
        ready = self._recv()
        if not ready.get("ok") or not ready.get("ready"):
            self.close(force=True)
            raise RuntimeError(f"agent worker {label} failed: {ready}")

    def _recv(self):
        if not self.parent.poll(CALL_TIMEOUT_S):
            raise TimeoutError("agent worker timed out")
        return self.parent.recv()

    def call(self, obs, config):
        self.parent.send({"cmd": "call", "obs": obs, "config": config})
        msg = self._recv()
        if not msg.get("ok"):
            raise RuntimeError(f"agent call failed: {msg}")
        return msg["action"]

    def close(self, force: bool = False):
        if getattr(self, "proc", None) is None:
            return
        if self.proc.is_alive() and not force:
            try:
                self.parent.send({"cmd": "close"})
            except Exception:
                pass
            self.proc.join(timeout=2)
        if self.proc.is_alive():
            self.proc.terminate()
            self.proc.join(timeout=2)
        try:
            self.parent.close()
        except Exception:
            pass


def _done_status(status) -> bool:
    return str(status) in {"DONE", "ERROR", "INVALID", "TIMEOUT"}


def _kaggle_episode(a: AgentProcess, b: AgentProcess, seed: int, a_seat: int):
    from kaggle_environments import make

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    env.reset(2)
    config = norm(env.configuration)
    steps = 0
    while not all(_done_status(s.status) for s in env.state):
        obs0 = norm(env.state[0].observation)
        obs1 = norm(env.state[1].observation)
        if a_seat == 0:
            x = a.call(obs0, config)
            y = b.call(obs1, config)
        else:
            x = b.call(obs0, config)
            y = a.call(obs1, config)
        env.step([x or PASS, y or PASS])
        steps += 1
        if steps > 725:
            raise RuntimeError("Kaggle environment exceeded expected episode length")
    r0 = float(env.state[0].reward or 0.0)
    r1 = float(env.state[1].reward or 0.0)
    statuses = [str(env.state[0].status), str(env.state[1].status)]
    return r0, r1, steps, statuses


def kagsim_agent_obs(game, seat: int):
    """Adapter that makes accelerator observations agent-facing equivalent.

    The simulator historically exposed step_count on Game rather than always in
    the observation dict. Kaggle passes observation.step, so inject it here.
    """
    obs = norm(game.observe(seat))
    obs["step"] = int(game.step_count)
    return obs


def _kagsim_episode(a: AgentProcess, b: AgentProcess, seed: int, a_seat: int):
    import kagsim

    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7":
        raise RuntimeError(f"wrong kagsim engine: {getattr(kagsim, 'ENGINE_VERSION', None)!r}")
    game = kagsim.Game(int(seed))
    config = {"episodeSteps": 720, "seed": int(seed)}
    while not game.done:
        obs0 = kagsim_agent_obs(game, 0)
        obs1 = kagsim_agent_obs(game, 1)
        if a_seat == 0:
            x = a.call(obs0, config)
            y = b.call(obs1, config)
        else:
            x = b.call(obs0, config)
            y = a.call(obs1, config)
        game.step(x or PASS, y or PASS)
    return float(game.reward(0)), float(game.reward(1)), int(game.step_count), ["DONE", "DONE"]


def play(a_dir: Path, b_dir: Path, seed: int, a_seat: int, backend: str) -> dict:
    ctx = mp.get_context("spawn")
    # Independent, deterministic worker seeds; seat is included to avoid sharing
    # stochastic streams between seat-swapped episodes.
    a_rng = (int(seed) * 1009 + a_seat * 17 + 1) % 2147483647
    b_rng = (int(seed) * 1013 + a_seat * 19 + 2) % 2147483647
    a = AgentProcess(ctx, a_dir, f"a_{seed}_{a_seat}", a_rng)
    b = AgentProcess(ctx, b_dir, f"b_{seed}_{a_seat}", b_rng)
    try:
        if backend == "kaggle":
            r0, r1, steps, statuses = _kaggle_episode(a, b, seed, a_seat)
        elif backend == "kagsim":
            r0, r1, steps, statuses = _kagsim_episode(a, b, seed, a_seat)
        else:
            raise ValueError(backend)
    finally:
        a.close()
        b.close()
    if not math.isfinite(r0) or not math.isfinite(r1):
        raise RuntimeError("nonfinite reward")
    margin = (r0 - r1) if a_seat == 0 else (r1 - r0)
    score = 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)
    return {
        "seed": int(seed),
        "a_seat": int(a_seat),
        "reward_seat0": r0,
        "reward_seat1": r1,
        "margin_a": float(margin),
        "score_a": score,
        "steps": int(steps),
        "statuses": statuses,
    }


def basic_summary(rows: list[dict]) -> dict:
    margins = [float(r["margin_a"]) for r in rows]
    scores = [float(r["score_a"]) for r in rows]
    w = sum(x == 1.0 for x in scores)
    t = sum(x == 0.5 for x in scores)
    l = sum(x == 0.0 for x in scores)
    return {
        "games": len(rows),
        "wins": w,
        "losses": l,
        "ties": t,
        "score_rate": statistics.mean(scores) if scores else None,
        "mean_margin": statistics.mean(margins) if margins else None,
        "median_margin": statistics.median(margins) if margins else None,
        "min_margin": min(margins) if margins else None,
        "max_margin": max(margins) if margins else None,
    }


def paired_bootstrap(rows: list[dict], draws: int = BOOTSTRAP_DRAWS) -> dict:
    by_seed: dict[int, list[float]] = {}
    for row in rows:
        by_seed.setdefault(int(row["seed"]), []).append(float(row["score_a"]))
    incomplete = sorted(seed for seed, vals in by_seed.items() if len(vals) != 2)
    if incomplete:
        raise RuntimeError(f"seat pairing incomplete for seeds: {incomplete[:10]}")
    pair_scores = [statistics.mean(by_seed[s]) for s in sorted(by_seed)]
    estimate = statistics.mean(pair_scores)
    if len(pair_scores) == 1:
        return {"paired_seeds": 1, "estimate": estimate, "ci95": [estimate, estimate]}
    rng = random.Random(MASTER_SEED ^ 0x5A17)
    boots = []
    n = len(pair_scores)
    for _ in range(draws):
        boots.append(statistics.mean(pair_scores[rng.randrange(n)] for _ in range(n)))
    boots.sort()
    lo = boots[int(0.025 * (draws - 1))]
    hi = boots[int(0.975 * (draws - 1))]
    return {
        "paired_seeds": n,
        "estimate": estimate,
        "bootstrap_draws": draws,
        "ci95": [lo, hi],
        "pair_scores": pair_scores,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--a-id", required=True)
    ap.add_argument("--b-id", required=True)
    ap.add_argument("--seed-count", type=int, default=16)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--backend", choices=["kaggle", "kagsim"], default="kaggle")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.backend == "kaggle":
        from importlib.metadata import version
        installed = version("kaggle-environments")
        if installed != "1.32.7":
            raise RuntimeError(f"reference backend must be kaggle-environments==1.32.7, got {installed}")

    rows: list[dict] = []
    errors: list[dict] = []
    seeds = make_seeds(args.seed_count, args.master_seed)
    with tempfile.TemporaryDirectory(prefix="kculture-faithful-h2h-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        for seed in seeds:
            for a_seat in (0, 1):
                try:
                    rows.append(play(a_dir, b_dir, seed, a_seat, args.backend))
                except Exception as exc:
                    errors.append({
                        "seed": seed,
                        "a_seat": a_seat,
                        "error": repr(exc),
                        "traceback": traceback.format_exc()[-6000:],
                    })
            print(json.dumps({
                "pair": f"{args.a_id}-{args.b_id}",
                "backend": args.backend,
                "completed_games": len(rows),
                "errors": len(errors),
                "last_seed": seed,
            }), flush=True)

    metrics = basic_summary(rows)
    by_seat = {
        str(seat): basic_summary([r for r in rows if r["a_seat"] == seat])
        for seat in (0, 1)
    }
    uncertainty = paired_bootstrap(rows) if not errors else None
    payload = {
        "schema_version": "kculture-kaggle-faithful-h2h-v1",
        "simulation_mode": (
            "hosted_reference_kaggle_environments_1.32.7"
            if args.backend == "kaggle"
            else "hosted_faithful_path_dependent_rng_accelerator"
        ),
        "backend": args.backend,
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": args.master_seed,
        "seed_count": args.seed_count,
        "seat_balanced": True,
        "forced_environment_tape": False,
        "agent_process_isolation": "fresh_process_per_package_per_episode",
        "agent_rng": "deterministically_seeded_for_reproducibility",
        "promotion_metric": "seat_balanced_score_rate",
        "mean_margin_is_secondary": True,
        "metrics_a_vs_b": metrics,
        "metrics_by_a_seat": by_seat,
        "paired_seed_uncertainty": uncertainty,
        "errors": errors,
        "rows": rows,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
