"""Audit CR058/CR070 local live-agent isolation.

Purpose
-------
The historical CR058 harness loads two submission packages into one interpreter.
That can leak package-local modules, globals and import state through sys.modules.
This auditor compares:
  1. legacy A->B load order,
  2. legacy B->A load order while keeping seats fixed,
  3. one fresh spawned Python process per agent/game (reference).

No candidate selection should use legacy live-agent H2H until this audit is clean.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing as mp
import os
import random
import statistics
import sys
import tarfile
import tempfile
import time
import traceback
from pathlib import Path

import kagsim

PASS = {"farmer": ["PASS"], "hands": [], "market": []}
MASTER_SEED = 5809072026
DEFAULT_SEED_COUNT = 8
CALL_TIMEOUT_S = 30.0


def make_seeds(n: int) -> list[int]:
    r = random.Random(MASTER_SEED)
    out: set[int] = set()
    while len(out) < n:
        out.add(r.randint(1, 2147483646))
    return sorted(out)


def extract(archive: Path, root: Path, tag: str) -> Path:
    dst = root / tag
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as tf:
        base = dst.resolve()
        for member in tf.getmembers():
            target = (dst / member.name).resolve()
            if target != base and base not in target.parents:
                raise RuntimeError(f"unsafe member {member.name!r} in {archive}")
        tf.extractall(dst)
    if not (dst / "main.py").is_file():
        raise RuntimeError(f"main.py absent in {archive}")
    return dst


def under(path: object, root: Path) -> bool:
    if not path:
        return False
    try:
        p = Path(str(path)).resolve()
        r = root.resolve()
        return p == r or r in p.parents
    except Exception:
        return False


def modules_under(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if under(f, root):
            out[name] = str(Path(str(f)).resolve())
    return dict(sorted(out.items()))


def purge_roots(*roots: Path) -> None:
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if f and any(under(f, root) for root in roots):
            sys.modules.pop(name, None)


def load_legacy(package_dir: Path, tag: str):
    # Intentionally mirrors CR058's unsafe isolation semantics:
    # clear only this package's already-loaded modules, not the opponent's.
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if under(f, package_dir):
            sys.modules.pop(name, None)
    sys.path.insert(0, str(package_dir.resolve()))
    try:
        p = package_dir / "main.py"
        spec = importlib.util.spec_from_file_location(
            f"legacy_{tag}_{time.time_ns()}", p
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {p}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "agent", None)
        if not callable(fn):
            raise RuntimeError(f"no callable agent in {p}")
        return fn
    finally:
        try:
            sys.path.remove(str(package_dir.resolve()))
        except ValueError:
            pass


def call_agent(agent, obs):
    config = {"episodeSteps": 720}
    try:
        return agent(obs, config)
    except TypeError:
        return agent(obs)


def play_legacy(
    a_dir: Path, b_dir: Path, seed: int, a_seat: int, load_order: str
) -> tuple[float, dict]:
    purge_roots(a_dir, b_dir)
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed % (2**32 - 1))
    except Exception:
        pass

    before = {"a": modules_under(a_dir), "b": modules_under(b_dir)}
    if load_order == "ab":
        a = load_legacy(a_dir, f"a_{seed}_{a_seat}")
        after_first = {"a": modules_under(a_dir), "b": modules_under(b_dir)}
        b = load_legacy(b_dir, f"b_{seed}_{a_seat}")
    elif load_order == "ba":
        b = load_legacy(b_dir, f"b_{seed}_{a_seat}")
        after_first = {"a": modules_under(a_dir), "b": modules_under(b_dir)}
        a = load_legacy(a_dir, f"a_{seed}_{a_seat}")
    else:
        raise ValueError(load_order)
    after_both = {"a": modules_under(a_dir), "b": modules_under(b_dir)}

    game = kagsim.Game(int(seed))
    while not game.done:
        if a_seat == 0:
            x = call_agent(a, game.observe(0)) or PASS
            y = call_agent(b, game.observe(1)) or PASS
        else:
            x = call_agent(b, game.observe(0)) or PASS
            y = call_agent(a, game.observe(1)) or PASS
        game.step(x, y)

    r0 = float(game.reward(0))
    r1 = float(game.reward(1))
    if not math.isfinite(r0) or not math.isfinite(r1):
        raise RuntimeError("nonfinite reward")
    margin = (r0 - r1) if a_seat == 0 else (r1 - r0)
    provenance = {
        "before": before,
        "after_first": after_first,
        "after_both": after_both,
    }
    purge_roots(a_dir, b_dir)
    return float(margin), provenance


def _worker(conn, package_dir_s: str, label: str, seed: int) -> None:
    package_dir = Path(package_dir_s).resolve()
    # Fresh process + package root left on sys.path for the entire episode,
    # matching a normal standalone submission process and supporting lazy imports.
    sys.path.insert(0, str(package_dir))
    os.chdir(package_dir)
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed % (2**32 - 1))
    except Exception:
        pass
    try:
        p = package_dir / "main.py"
        spec = importlib.util.spec_from_file_location(f"isolated_{label}", p)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {p}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "agent", None)
        if not callable(fn):
            raise RuntimeError(f"no callable agent in {p}")
        conn.send(
            {
                "ok": True,
                "ready": True,
                "modules": modules_under(package_dir),
            }
        )
        while True:
            msg = conn.recv()
            if msg.get("cmd") == "close":
                break
            if msg.get("cmd") != "call":
                raise RuntimeError(f"unknown command {msg!r}")
            try:
                action = call_agent(fn, msg["obs"]) or PASS
                conn.send({"ok": True, "action": action})
            except Exception as exc:
                conn.send(
                    {
                        "ok": False,
                        "error": repr(exc),
                        "traceback": traceback.format_exc()[-5000:],
                    }
                )
    except Exception as exc:
        try:
            conn.send(
                {
                    "ok": False,
                    "ready": False,
                    "error": repr(exc),
                    "traceback": traceback.format_exc()[-5000:],
                }
            )
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


class AgentProcess:
    def __init__(self, ctx, package_dir: Path, label: str, seed: int):
        self.parent, child = ctx.Pipe()
        self.proc = ctx.Process(
            target=_worker,
            args=(child, str(package_dir), label, int(seed)),
            daemon=True,
        )
        self.proc.start()
        child.close()
        self.ready = self._recv()
        if not self.ready.get("ok") or not self.ready.get("ready"):
            self.close(force=True)
            raise RuntimeError(f"worker {label} failed: {self.ready}")

    def _recv(self):
        if not self.parent.poll(CALL_TIMEOUT_S):
            raise TimeoutError("agent worker timed out")
        return self.parent.recv()

    def call(self, obs):
        self.parent.send({"cmd": "call", "obs": obs})
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
            self.proc.join(timeout=2.0)
        if self.proc.is_alive():
            self.proc.terminate()
            self.proc.join(timeout=2.0)
        try:
            self.parent.close()
        except Exception:
            pass


def play_isolated(a_dir: Path, b_dir: Path, seed: int, a_seat: int) -> tuple[float, dict]:
    ctx = mp.get_context("spawn")
    a = AgentProcess(ctx, a_dir, f"a_{seed}_{a_seat}", seed)
    b = AgentProcess(ctx, b_dir, f"b_{seed}_{a_seat}", seed)
    try:
        game = kagsim.Game(int(seed))
        while not game.done:
            if a_seat == 0:
                x = a.call(game.observe(0)) or PASS
                y = b.call(game.observe(1)) or PASS
            else:
                x = b.call(game.observe(0)) or PASS
                y = a.call(game.observe(1)) or PASS
            game.step(x, y)
        r0 = float(game.reward(0))
        r1 = float(game.reward(1))
        if not math.isfinite(r0) or not math.isfinite(r1):
            raise RuntimeError("nonfinite reward")
        margin = (r0 - r1) if a_seat == 0 else (r1 - r0)
        provenance = {
            "a_worker_modules": a.ready.get("modules", {}),
            "b_worker_modules": b.ready.get("modules", {}),
        }
        return float(margin), provenance
    finally:
        a.close()
        b.close()


def summarize(rows: list[dict]) -> dict:
    margins = [float(r["margin"]) for r in rows if "margin" in r]
    w = sum(x > 0 for x in margins)
    l = sum(x < 0 for x in margins)
    t = len(margins) - w - l
    return {
        "games": len(margins),
        "wins": w,
        "losses": l,
        "ties": t,
        "score_rate": (w + 0.5 * t) / len(margins) if margins else None,
        "mean_margin": statistics.mean(margins) if margins else None,
        "median_margin": statistics.median(margins) if margins else None,
    }


def compact_provenance(prov: dict) -> dict:
    # Store names + paths but only for first diagnostic sample to keep artifacts small.
    return prov


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--a-id", required=True)
    ap.add_argument("--b-id", required=True)
    ap.add_argument("--seed-count", type=int, default=DEFAULT_SEED_COUNT)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7":
        raise RuntimeError(
            f"wrong engine {getattr(kagsim, 'ENGINE_VERSION', None)!r}; expected 1.32.7"
        )

    seeds = make_seeds(args.seed_count)
    modes = ("legacy_ab", "legacy_ba", "isolated")
    rows_by_mode: dict[str, list[dict]] = {m: [] for m in modes}
    errors: list[dict] = []
    provenance_samples: dict[str, dict] = {}
    paired: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="kculture-agent-isolation-audit-") as td:
        root = Path(td)
        a_dir = extract(Path(args.a), root, "agent_a")
        b_dir = extract(Path(args.b), root, "agent_b")
        started = time.time()

        for seed in seeds:
            for a_seat in (0, 1):
                sample: dict[str, float] = {}
                for mode in modes:
                    try:
                        if mode == "legacy_ab":
                            margin, prov = play_legacy(a_dir, b_dir, seed, a_seat, "ab")
                        elif mode == "legacy_ba":
                            margin, prov = play_legacy(a_dir, b_dir, seed, a_seat, "ba")
                        else:
                            margin, prov = play_isolated(a_dir, b_dir, seed, a_seat)
                        rows_by_mode[mode].append(
                            {"seed": seed, "a_seat": a_seat, "margin": margin}
                        )
                        sample[mode] = margin
                        key = f"{mode}_seat{a_seat}"
                        if key not in provenance_samples:
                            provenance_samples[key] = compact_provenance(prov)
                    except Exception as exc:
                        errors.append(
                            {
                                "seed": seed,
                                "a_seat": a_seat,
                                "mode": mode,
                                "error": repr(exc)[:2000],
                                "traceback": traceback.format_exc()[-5000:],
                            }
                        )
                if sample:
                    paired.append(
                        {
                            "seed": seed,
                            "a_seat": a_seat,
                            **sample,
                            "legacy_order_delta": (
                                sample.get("legacy_ab") - sample.get("legacy_ba")
                                if "legacy_ab" in sample and "legacy_ba" in sample
                                else None
                            ),
                            "legacy_ab_vs_isolated_delta": (
                                sample.get("legacy_ab") - sample.get("isolated")
                                if "legacy_ab" in sample and "isolated" in sample
                                else None
                            ),
                        }
                    )
            print(
                json.dumps(
                    {
                        "pair": f"{args.a_id}-{args.b_id}",
                        "seed": seed,
                        "completed_samples": len(paired),
                        "errors": len(errors),
                        "elapsed_s": round(time.time() - started, 1),
                    }
                ),
                flush=True,
            )

    order_changed = [
        r
        for r in paired
        if r.get("legacy_order_delta") is not None
        and abs(float(r["legacy_order_delta"])) > 1e-9
    ]
    legacy_vs_isolated_changed = [
        r
        for r in paired
        if r.get("legacy_ab_vs_isolated_delta") is not None
        and abs(float(r["legacy_ab_vs_isolated_delta"])) > 1e-9
    ]
    payload = {
        "experiment": "KCULTURE_AGENT_ISOLATION_AUDIT_V1",
        "engine": "1.32.7",
        "a": args.a_id,
        "b": args.b_id,
        "master_seed": MASTER_SEED,
        "seed_count": args.seed_count,
        "hypothesis": (
            "CR058 in-process package loading may leak modules/global import state "
            "between opponents; isolated subprocess results are the reference."
        ),
        "metrics": {m: summarize(rows_by_mode[m]) for m in modes},
        "order_sensitive_samples": len(order_changed),
        "legacy_vs_isolated_changed_samples": len(legacy_vs_isolated_changed),
        "paired": paired,
        "provenance_samples": provenance_samples,
        "errors": errors,
        "interpretation": {
            "legacy_order_dependency_is_bug": bool(order_changed),
            "legacy_differs_from_isolated": bool(legacy_vs_isolated_changed),
            "legacy_h2h_safe_for_selection": not (
                order_changed or legacy_vs_isolated_changed or errors
            ),
        },
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "experiment": payload["experiment"],
                "a": args.a_id,
                "b": args.b_id,
                "metrics": payload["metrics"],
                "order_sensitive_samples": payload["order_sensitive_samples"],
                "legacy_vs_isolated_changed_samples": payload[
                    "legacy_vs_isolated_changed_samples"
                ],
                "errors": len(errors),
                "interpretation": payload["interpretation"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    mp.freeze_support()
    main()
