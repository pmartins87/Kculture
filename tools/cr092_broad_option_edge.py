#!/usr/bin/env python3
"""CR092 edge evaluator: exact CR053 BASE vs frozen O1 on one population edge.

Every package is executed through the hosted-faithful AgentProcess path.  O1 is
exactly the CR091 survivor: only the ordering of CR053's existing market orders is
changed by the exact CR086 latent-supply priority operator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import tarfile
import tempfile
import time
import traceback
import types
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from candidates.cr091_cr053_market_option import make_agent
from kaggle_exact_runtime import (
    AgentProcess,
    agent_visible_observation,
    done_status,
    extract,
    make_reference_env,
    reference_config,
    reference_step,
)

SEEDS = tuple(range(91401, 91407))
TREATMENTS = ("CR053_BASE", "CR053_O1")

EXPECTED_SHA = {
    "CR053_REAL": "095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15",
    "CR052_REAL": "b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d",
    "CR083": "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8",
    "CR086": "11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888",
    "r01_e108766633_s56156662": "225e078f35213a71e6eb8ff2daa424578e195d6c8a8fa0be6fb9b416ffd7a646",
    "r02_e108761464_s56114097": "d744c0a660d9c1a6b71cc9ca847c9c6f09c55f79bcce9e897cdfae1542f19b85",
    "r03_e108766659_s56209748": "7f50916df07cc5d1c81f8d8952eb1c95ee11a2242f48e00b27170fc37a4cb9d4",
    "r06_e108754069_s56205640": "24e78d657d6c16371fcc7393fbea4d23ce695fd456e722e37f5398f7866ab16e",
    "r07_e108766657_s56132899": "dbabe60a1b7e6670eb244f7a060461006e1677a0a8c3bc3cb58aebea3a2ab60e",
    "r09_e108766659_s56097405": "0c655157e8e62d7055ca12fc80951fcba1b5f9eab3536fd077c0ce3b119e03f6",
    "r10_e108754200_s56210228": "67916f5819ebb4416cfe0448a61b76c3123194f0ef7aa3aac6ef1d526018f279",
}

CR086_SOURCE = ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_from_tar(path: Path) -> str:
    with tarfile.open(path, "r:gz") as tf:
        member = tf.getmember("main.py")
        fh = tf.extractfile(member)
        if fh is None:
            raise RuntimeError(f"main.py unreadable in {path}")
        return fh.read().decode("utf-8")


def load_cr086_helpers():
    mod = types.ModuleType(f"cr092_cr086_helpers_{load_cr086_helpers.counter}")
    load_cr086_helpers.counter += 1
    mod.__file__ = "<CR086_REAL:main.py>"
    exec(compile(CR086_SOURCE, mod.__file__, "exec"), mod.__dict__)
    for name in ("_cr086_update", "_cr086_prioritize"):
        if not callable(mod.__dict__.get(name)):
            raise RuntimeError(f"CR086 helper absent: {name}")
    return mod


load_cr086_helpers.counter = 0


def freeze(obj):
    return json.loads(json.dumps(obj))


def safe_json(obj):
    return json.loads(json.dumps(obj, default=lambda x: repr(x)))


def strategic_observation(obs):
    out = freeze(obs)
    if isinstance(out, dict):
        out.pop("remainingOverageTime", None)
    return out


def strategic_hash(obs) -> str:
    payload = json.dumps(
        strategic_observation(obs), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def market_multiset(market):
    rows = []
    for order in market or []:
        rows.append(json.dumps(list(order), sort_keys=True, separators=(",", ":")))
    return tuple(sorted(rows))


class ExactBaseProxy:
    def __init__(self, process: AgentProcess):
        self.process = process
        self.last_action = None
        self.last_duration = 0.0
        self.last_ipc_wall = 0.0

    def __call__(self, obs, config=None):
        t0 = time.perf_counter()
        action, duration = self.process.call(obs, config)
        self.last_ipc_wall = time.perf_counter() - t0
        self.last_action = freeze(action)
        self.last_duration = float(duration)
        return action


class ParityChecker:
    def __init__(self, candidate, base_proxy: ExactBaseProxy, treatment: str):
        self.candidate = candidate
        self.base_proxy = base_proxy
        self.treatment = treatment
        self.calls = 0
        self.physical_ok = 0
        self.multiset_ok = 0
        self.exact_ok = 0
        self.reorders = 0
        self.violations = []
        self.observation_hashes = {}
        self.first_reorder_step = None
        self.first_reorder_observation_hash = None
        self.first_reorder_observation = None
        self.first_reorder_latent_state = None

    def call(self, obs, config):
        step = int(obs.get("step", self.calls)) if hasattr(obs, "get") else self.calls
        pre_hash = strategic_hash(obs)
        self.observation_hashes[str(step)] = pre_hash
        pre_obs = strategic_observation(obs)
        before = int(getattr(self.candidate, "reorders", 0))

        t0 = time.perf_counter()
        act = freeze(self.candidate(obs, config))
        total_wall = time.perf_counter() - t0
        ref = freeze(self.base_proxy.last_action)
        after = int(getattr(self.candidate, "reorders", 0))
        reordered = after > before
        self.calls += 1

        physical = act.get("farmer") == ref.get("farmer") and act.get("hands") == ref.get("hands")
        multiset = market_multiset(act.get("market")) == market_multiset(ref.get("market"))
        exact = act == ref
        self.physical_ok += int(physical)
        self.multiset_ok += int(multiset)
        self.exact_ok += int(exact)
        self.reorders += int(reordered)

        if reordered and self.first_reorder_step is None:
            self.first_reorder_step = step
            self.first_reorder_observation_hash = pre_hash
            self.first_reorder_observation = pre_obs
            state = getattr(self.candidate, "state", None)
            self.first_reorder_latent_state = safe_json(getattr(state, "__dict__", {}))

        if not physical or not multiset:
            self.violations.append(
                {
                    "step": step,
                    "physical": physical,
                    "market_multiset": multiset,
                    "ref": ref,
                    "act": act,
                }
            )

        wrapper_extra = max(0.0, total_wall - self.base_proxy.last_ipc_wall)
        duration = self.base_proxy.last_duration + wrapper_extra
        return act, duration


def make_candidate(treatment: str, base_process: AgentProcess):
    base_proxy = ExactBaseProxy(base_process)
    donor = load_cr086_helpers()
    if treatment == "CR053_BASE":
        enabled = False
    elif treatment == "CR053_O1":
        enabled = True
    else:
        raise ValueError(treatment)
    candidate = make_agent(base_proxy, donor, enabled=enabled)
    return ParityChecker(candidate, base_proxy, treatment)


def reward_value(x):
    return None if x is None else float(x)


def run_one(treatment: str, opponent: str, seed: int, seat: int, package_dirs):
    env = make_reference_env(seed)
    config = reference_config(env)
    ctx = mp.get_context("spawn")
    base_process = None
    opponent_process = None
    checked = None
    err = None
    err_tb = None
    err_phase = None
    err_step = None
    steps = 0

    try:
        base_process = AgentProcess(
            ctx,
            package_dirs["CR053_REAL"],
            f"cr092_base_{treatment}_{opponent}_{seed}_{seat}",
        )
        opponent_process = AgentProcess(
            ctx,
            package_dirs[opponent],
            f"cr092_opp_{opponent}_{seed}_{seat}",
        )
        checked = make_candidate(treatment, base_process)

        while not all(done_status(s.status) for s in env.state):
            cand_obs = agent_visible_observation(env, seat)
            opp_seat = 1 - seat
            opp_obs = agent_visible_observation(env, opp_seat)

            err_phase = "candidate_call"
            cand_action, cand_duration = checked.call(cand_obs, config)
            err_phase = "opponent_call"
            opp_action, opp_duration = opponent_process.call(opp_obs, config)

            actions = [None, None]
            durations = [0.0, 0.0]
            actions[seat] = cand_action
            durations[seat] = cand_duration
            actions[opp_seat] = opp_action
            durations[opp_seat] = opp_duration

            err_phase = "reference_step"
            reference_step(env, actions, durations)
            steps += 1
            if steps > 725:
                raise RuntimeError("Kaggle environment exceeded expected episode length")

        err_phase = None
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        err_tb = traceback.format_exc()[-12000:]
        err_step = steps
    finally:
        if base_process is not None:
            base_process.close()
        if opponent_process is not None:
            opponent_process.close()

    statuses = [str(env.state[p].status) for p in (0, 1)]
    rewards = [reward_value(env.state[p].reward) for p in (0, 1)]
    done = err is None and statuses == ["DONE", "DONE"] and all(x is not None for x in rewards)

    if done:
        cand_reward = float(rewards[seat])
        opp_reward = float(rewards[1 - seat])
        margin = cand_reward - opp_reward
        outcome = 1.0 if margin > 0 else (0.5 if margin == 0 else 0.0)
    else:
        cand_reward = None
        opp_reward = None
        margin = None
        outcome = None

    return {
        "treatment": treatment,
        "opponent": opponent,
        "seed": seed,
        "seat": seat,
        "done": done,
        "statuses": statuses,
        "error": err,
        "error_phase": err_phase,
        "error_step": err_step,
        "error_traceback": err_tb,
        "candidate_reward": cand_reward,
        "opponent_reward": opp_reward,
        "margin": margin,
        "outcome": outcome,
        "steps": steps,
        "calls": checked.calls if checked is not None else 0,
        "physical_ok": checked.physical_ok if checked is not None else 0,
        "multiset_ok": checked.multiset_ok if checked is not None else 0,
        "exact_ok": checked.exact_ok if checked is not None else 0,
        "reorders": checked.reorders if checked is not None else 0,
        "violations": checked.violations[:3] if checked is not None else [],
        "observation_hashes": checked.observation_hashes if checked is not None else {},
        "first_reorder_step": checked.first_reorder_step if checked is not None else None,
        "first_reorder_observation_hash": (
            checked.first_reorder_observation_hash if checked is not None else None
        ),
        "first_reorder_observation": checked.first_reorder_observation if checked is not None else None,
        "first_reorder_latent_state": checked.first_reorder_latent_state if checked is not None else None,
    }


def summarize(rows):
    valid = [r for r in rows if r["done"] and r["outcome"] is not None]
    scores = [float(r["outcome"]) for r in valid]
    margins = [float(r["margin"]) for r in valid]
    return {
        "n": len(valid),
        "wins": sum(x == 1.0 for x in scores),
        "ties": sum(x == 0.5 for x in scores),
        "losses": sum(x == 0.0 for x in scores),
        "score": mean(scores) if scores else None,
        "mean_margin": mean(margins) if margins else None,
        "median_margin": median(margins) if margins else None,
        "seat_scores": {
            str(seat): mean([float(r["outcome"]) for r in valid if r["seat"] == seat])
            if any(r["seat"] == seat for r in valid)
            else None
            for seat in (0, 1)
        },
        "reorders": sum(int(r["reorders"]) for r in rows),
    }


def main():
    global CR086_SOURCE

    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", required=True, choices=sorted(EXPECTED_SHA))
    ap.add_argument("--runtime", default="cr092_runtime")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    runtime = (ROOT / args.runtime).resolve()
    needed = {"CR053_REAL", "CR086", args.opponent}
    package_paths = {name: runtime / f"{name}.tar.gz" for name in needed}
    receipts = {}
    for name, path in package_paths.items():
        if not path.is_file():
            raise SystemExit(f"missing CR092 package: {path}")
        actual = sha256(path)
        expected = EXPECTED_SHA[name]
        receipts[name] = {"path": str(path), "sha256": actual, "expected": expected}
        if actual != expected:
            raise SystemExit(f"SHA mismatch {name}: {actual} != {expected}")

    CR086_SOURCE = source_from_tar(package_paths["CR086"])

    rows = []
    with tempfile.TemporaryDirectory(prefix=f"cr092-{args.opponent}-") as td:
        root = Path(td)
        package_dirs = {
            name: extract(path, root, f"pkg_{name}") for name, path in package_paths.items()
        }
        for seed in SEEDS:
            for seat in (0, 1):
                for treatment in TREATMENTS:
                    row = run_one(treatment, args.opponent, seed, seat, package_dirs)
                    rows.append(row)
                    print(
                        "CR092_CASE",
                        args.opponent,
                        treatment,
                        seed,
                        seat,
                        "done",
                        row["done"],
                        "outcome",
                        row["outcome"],
                        "reorders",
                        row["reorders"],
                        "first",
                        row["first_reorder_step"],
                        "error",
                        row["error"],
                        flush=True,
                    )

    by_treatment = {t: [r for r in rows if r["treatment"] == t] for t in TREATMENTS}
    summaries = {t: summarize(by_treatment[t]) for t in TREATMENTS}

    failures = [r for r in rows if not r["done"] or r["error"]]
    calls = sum(int(r["calls"]) for r in rows)
    physical_ok = sum(int(r["physical_ok"]) for r in rows)
    multiset_ok = sum(int(r["multiset_ok"]) for r in rows)
    base_rows = by_treatment["CR053_BASE"]
    base_calls = sum(int(r["calls"]) for r in base_rows)
    base_exact = sum(int(r["exact_ok"]) for r in base_rows)
    o1_reorders = sum(int(r["reorders"]) for r in by_treatment["CR053_O1"])
    violations = sum(len(r["violations"]) for r in rows)

    mechanics_pass = (
        not failures
        and calls == physical_ok
        and calls == multiset_ok
        and base_calls == base_exact
        and violations == 0
    )

    base_score = summaries["CR053_BASE"]["score"]
    o1_score = summaries["CR053_O1"]["score"]
    delta = None if base_score is None or o1_score is None else float(o1_score - base_score)

    payload = {
        "schema": "cr092-broad-option-edge-v1",
        "engine": "kaggle-environments==1.32.7",
        "opponent": args.opponent,
        "seeds": list(SEEDS),
        "treatments": list(TREATMENTS),
        "package_receipts": receipts,
        "summaries": summaries,
        "edge_score_delta_o1_minus_base": delta,
        "mechanics": {
            "failures": len(failures),
            "physical_parity": [physical_ok, calls],
            "market_multiset_parity": [multiset_ok, calls],
            "base_exact_parity": [base_exact, base_calls],
            "violations": violations,
            "o1_reorders": o1_reorders,
            "mechanics_pass": mechanics_pass,
        },
        "rows": rows,
        "held_out_touched": False,
        "automatic_submission": False,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "CR092_EDGE_RESULT",
        json.dumps(
            {
                "opponent": args.opponent,
                "delta": delta,
                "mechanics": payload["mechanics"],
                "summaries": summaries,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    print("CR092_EDGE_COMPLETE", args.opponent, flush=True)


if __name__ == "__main__":
    main()
