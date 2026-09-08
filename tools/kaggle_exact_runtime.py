"""Hosted-faithful execution primitives for Kaggriculture evaluation.

This module deliberately uses kaggle-environments==1.32.7 internals where needed
because the promotion harness must reproduce what Kaggle actually gives an agent,
not the raw per-seat state object.  In particular, shared observation fields such
as ``step`` are reconstructed by Environment.__get_shared_state before Agent.act.

Submission code is loaded through Kaggle's own Agent wrapper in a fresh spawned
process per package/episode.  This preserves package isolation while matching the
official path loader, structify conversion, callable selection, exception capture,
and timeout decision logic.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import random
import sys
import tarfile
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace

PASS = {"farmer": ["PASS"], "hands": [], "market": []}
MASTER_SEED = 5809072026
CALL_TIMEOUT_S = 35.0
EXPECTED_KAGGLE_VERSION = "1.32.7"


def norm(x):
    """Convert Kaggle Struct / tuples to plain JSON-compatible Python values."""
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


def assert_reference_version() -> None:
    from importlib.metadata import version

    installed = version("kaggle-environments")
    if installed != EXPECTED_KAGGLE_VERSION:
        raise RuntimeError(
            f"reference backend must be kaggle-environments=={EXPECTED_KAGGLE_VERSION}, got {installed}"
        )


def make_reference_env(seed: int):
    from kaggle_environments import make

    assert_reference_version()
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    env.reset(2)
    return env


def agent_visible_observation(env, seat: int) -> dict:
    """Return exactly the observation the pinned Kaggle runner gives this seat.

    Reading ``env.state[seat].observation`` is wrong for seat > 0 because shared
    fields are stored on state[0] and injected only by __get_shared_state.
    """
    getter = getattr(env, "_Environment__get_shared_state", None)
    if not callable(getter):
        raise RuntimeError("pinned Kaggle Environment shared-state accessor not found")
    shared_state = getter(int(seat))
    return norm(shared_state.observation)


def reference_config(env) -> dict:
    return norm(env.configuration)


def _worker(conn, package_dir_s: str, label: str) -> None:
    """One hosted-like package sandbox using Kaggle's own Agent wrapper."""
    package_dir = Path(package_dir_s).resolve()
    sys.path.insert(0, str(package_dir))
    os.chdir(package_dir)
    runtime_agent = None
    try:
        from kaggle_environments.agent import Agent as KaggleAgent
        from kaggle_environments.utils import structify

        conn.send({"ok": True, "ready": True})
        while True:
            msg = conn.recv()
            if msg.get("cmd") == "close":
                break
            if msg.get("cmd") != "call":
                raise RuntimeError(f"unknown worker command: {msg!r}")
            try:
                if runtime_agent is None:
                    # Agent expects the small subset of Environment attributes below.
                    # Configuration is structified exactly as in the official runner.
                    env_stub = SimpleNamespace(
                        agents={},
                        configuration=structify(msg["config"]),
                        debug=False,
                        name="kaggriculture",
                    )
                    runtime_agent = KaggleAgent(str(package_dir / "main.py"), env_stub)
                # Official Environment.__agent_runner passes a Struct-like observation
                # to Agent.act; Agent.act itself reads observation.remainingOverageTime
                # after invoking the submission.  Passing a plain dict here would be
                # observably different from hosted execution.
                action, log = runtime_agent.act(structify(msg["obs"]))
                conn.send(
                    {
                        "ok": True,
                        "action": action,
                        "duration": float(log.get("duration", 0.0)),
                        "stdout": log.get("stdout", ""),
                        "stderr": log.get("stderr", ""),
                    }
                )
            except Exception as exc:
                conn.send(
                    {
                        "ok": False,
                        "error": repr(exc),
                        "traceback": traceback.format_exc()[-8000:],
                    }
                )
    except Exception as exc:
        try:
            conn.send(
                {
                    "ok": False,
                    "ready": False,
                    "error": repr(exc),
                    "traceback": traceback.format_exc()[-8000:],
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
    """Fresh spawned process for one submission package in one episode."""

    def __init__(self, ctx: mp.context.BaseContext, package_dir: Path, label: str):
        self.parent, child = ctx.Pipe()
        self.proc = ctx.Process(
            target=_worker,
            args=(child, str(package_dir), label),
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
            raise TimeoutError("agent worker IPC timed out")
        return self.parent.recv()

    def call(self, obs: dict, config: dict):
        self.parent.send({"cmd": "call", "obs": obs, "config": config})
        msg = self._recv()
        if not msg.get("ok"):
            raise RuntimeError(f"agent call failed: {msg}")
        return msg["action"], float(msg.get("duration", 0.0))

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


def apply_official_overage_accounting(env, durations: list[float]) -> None:
    """Mirror Environment.__loop_through_interpreter duration bank accounting.

    Manual env.step([...]) has no runner logs, so without this adjustment a slow
    agent would incorrectly retain all remainingOverageTime in subsequent turns.
    Official Agent.act records duration rounded to six decimals; that is the value
    returned by AgentProcess and used here.
    """
    act_timeout = float(env.configuration.actTimeout)
    for p, duration in enumerate(durations):
        over = max(0.0, float(duration) - act_timeout)
        if over:
            env.state[p].observation.remainingOverageTime -= over


def reference_step(env, actions: list, durations: list[float]) -> None:
    # Do NOT replace None/falsy actions with PASS. Kaggle does not do that; invalid
    # output must remain invalid so local tests cannot silently rescue a bad agent.
    env.step(actions)
    apply_official_overage_accounting(env, durations)


def done_status(status) -> bool:
    return str(status) in {"DONE", "ERROR", "INVALID", "TIMEOUT"}


def kagsim_agent_observation(game, seat: int, remaining_overage_time: float = 60.0) -> dict:
    """Adapt only framework-supplied fields absent from the accelerator."""
    obs = norm(game.observe(int(seat)))
    obs["step"] = int(game.step_count)
    obs["remainingOverageTime"] = float(remaining_overage_time)
    return obs


def temporary_packages(a_archive: Path, b_archive: Path):
    """Context manager-like generator kept simple for callers using ExitStack."""
    td = tempfile.TemporaryDirectory(prefix="kculture-exact-runtime-")
    root = Path(td.name)
    return td, extract(a_archive, root, "agent_a"), extract(b_archive, root, "agent_b")
