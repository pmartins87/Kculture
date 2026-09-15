#!/usr/bin/env python3
"""CR091 gate 1 — exact CR053 physical backbone + CR086 latent-supply market option.

Rerun note: all submission packages execute through the hosted-faithful
kaggle_exact_runtime AgentProcess path. The frozen CR091 design, seeds, panel,
option logic, and promotion thresholds are unchanged from the preregistered gate.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import sys
import tarfile
import tempfile
import time
import traceback
import types
from collections import defaultdict
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

RUNTIME = ROOT / ".cr091_runtime"
SEEDS = tuple(range(91301, 91309))
TREATMENTS = ("CR053_BASE", "CR053_LATENT_PRIORITY")

PACKAGES = {
    "CR052_REAL": (RUNTIME / "CR052.tar.gz", "b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d"),
    "CR053_REAL": (RUNTIME / "CR053.tar.gz", "095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15"),
    "CR083": (RUNTIME / "CR083.tar.gz", "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8"),
    "CR086": (RUNTIME / "CR086.tar.gz", "11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888"),
}

CR086_SOURCE = ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
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
    """Fresh donor helper state per episode; no donor action is executed here."""
    mod = types.ModuleType(f"cr091_cr086_helpers_{load_cr086_helpers.counter}")
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


def market_multiset(market):
    rows = []
    for order in market or []:
        rows.append(json.dumps(list(order), sort_keys=True, separators=(",", ":")))
    return tuple(sorted(rows))


class ExactBaseProxy:
    """Expose the exact CR053 package action to the frozen option wrapper."""

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
    """Compare the option output to the exact CR053 action it actually wrapped."""

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

    def call(self, obs, config):
        t0 = time.perf_counter()
        act = freeze(self.candidate(obs, config))
        total_wall = time.perf_counter() - t0
        ref = freeze(self.base_proxy.last_action)
        self.calls += 1

        physical = act.get("farmer") == ref.get("farmer") and act.get("hands") == ref.get("hands")
        multiset = market_multiset(act.get("market")) == market_multiset(ref.get("market"))
        exact = act == ref
        self.physical_ok += int(physical)
        self.multiset_ok += int(multiset)
        self.exact_ok += int(exact)
        self.reorders += int(multiset and act.get("market") != ref.get("market"))

        if not physical or not multiset:
            self.violations.append({
                "step": int(obs.get("step", -1)) if hasattr(obs, "get") else -1,
                "physical": physical,
                "market_multiset": multiset,
                "ref": ref,
                "act": act,
            })

        wrapper_extra = max(0.0, total_wall - self.base_proxy.last_ipc_wall)
        duration = self.base_proxy.last_duration + wrapper_extra
        return act, duration


def make_candidate(treatment: str, base_process: AgentProcess):
    base_proxy = ExactBaseProxy(base_process)
    donor_mod = load_cr086_helpers()
    enabled = treatment == "CR053_LATENT_PRIORITY"
    if treatment not in TREATMENTS:
        raise ValueError(treatment)
    candidate = make_agent(base_proxy, donor_mod, enabled=enabled)
    return ParityChecker(candidate, base_proxy, treatment)


def reward_value(x):
    return None if x is None else float(x)


def run_one(treatment: str, opponent_name: str, seed: int, seat: int, package_dirs):
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
            ctx, package_dirs["CR053_REAL"],
            f"cr091_base_{treatment}_{opponent_name}_{seed}_{seat}",
        )
        opponent_process = AgentProcess(
            ctx, package_dirs[opponent_name],
            f"cr091_opp_{opponent_name}_{seed}_{seat}",
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
        "opponent": opponent_name,
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
    }


def summarize_edge(rows):
    valid = [r for r in rows if r["done"] and r["outcome"] is not None]
    wins = sum(r["outcome"] == 1.0 for r in valid)
    ties = sum(r["outcome"] == 0.5 for r in valid)
    losses = sum(r["outcome"] == 0.0 for r in valid)
    score = (wins + 0.5 * ties) / len(valid) if valid else None
    margins = [r["margin"] for r in valid]
    return {
        "n": len(valid),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "score": score,
        "mean_margin": mean(margins) if margins else None,
        "median_margin": median(margins) if margins else None,
        "seat_scores": {
            str(s): (
                sum(r["outcome"] for r in valid if r["seat"] == s)
                / max(1, sum(1 for r in valid if r["seat"] == s))
            )
            for s in (0, 1)
        },
        "reorders": sum(r["reorders"] for r in rows),
    }


def main():
    global CR086_SOURCE

    package_receipt = {}
    for name, (path, expected) in PACKAGES.items():
        if not path.exists():
            raise SystemExit(f"missing runtime package {path}")
        actual = sha256(path)
        package_receipt[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": actual,
            "expected": expected,
        }
        if actual != expected:
            raise SystemExit(f"SHA mismatch {name}: {actual} != {expected}")

    CR086_SOURCE = source_from_tar(PACKAGES["CR086"][0])

    rows = []
    with tempfile.TemporaryDirectory(prefix="cr091-reference-rerun-") as td:
        extract_root = Path(td)
        package_dirs = {
            name: extract(path, extract_root, f"pkg_{name}")
            for name, (path, _) in PACKAGES.items()
        }

        for opponent in PACKAGES:
            for seed in SEEDS:
                for seat in (0, 1):
                    for treatment in TREATMENTS:
                        row = run_one(treatment, opponent, seed, seat, package_dirs)
                        rows.append(row)
                        print(
                            "CR091_CASE", treatment, opponent, seed, seat,
                            "done", row["done"], "outcome", row["outcome"],
                            "margin", row["margin"], "reorders", row["reorders"],
                            "error", row["error"],
                            flush=True,
                        )

    by = defaultdict(list)
    for row in rows:
        by[(row["treatment"], row["opponent"])].append(row)

    edges = {t: {} for t in TREATMENTS}
    for treatment in TREATMENTS:
        for opponent in PACKAGES:
            edges[treatment][opponent] = summarize_edge(by[(treatment, opponent)])

    deltas = {}
    for opponent in PACKAGES:
        b = edges["CR053_BASE"][opponent]["score"]
        x = edges["CR053_LATENT_PRIORITY"][opponent]["score"]
        deltas[opponent] = None if b is None or x is None else x - b

    failures = [r for r in rows if not r["done"] or r["error"]]
    physical_calls = sum(r["calls"] for r in rows)
    physical_ok = sum(r["physical_ok"] for r in rows)
    multiset_ok = sum(r["multiset_ok"] for r in rows)
    base_rows = [r for r in rows if r["treatment"] == "CR053_BASE"]
    base_exact = sum(r["exact_ok"] for r in base_rows)
    base_calls = sum(r["calls"] for r in base_rows)
    latent_reorders = sum(r["reorders"] for r in rows if r["treatment"] == "CR053_LATENT_PRIORITY")
    violations = sum(len(r["violations"]) for r in rows)

    mechanics_pass = (
        not failures
        and physical_calls == physical_ok
        and physical_calls == multiset_ok
        and base_calls == base_exact
        and violations == 0
    )
    option_active = latent_reorders > 0

    numeric = [float(v) for v in deltas.values() if v is not None]
    mean_delta = mean(numeric) if numeric else float("nan")
    nonnegative = sum(v >= 0 for v in numeric)
    max_improvement = max(numeric) if numeric else float("nan")
    worst_regression = min(numeric) if numeric else float("nan")

    static_pass = (
        mechanics_pass and option_active and len(numeric) == 4
        and mean_delta >= 0.04
        and nonnegative >= 3
        and worst_regression >= -0.125
        and max_improvement >= 0.125
    )
    heterogeneous = (
        mechanics_pass and option_active and len(numeric) == 4
        and max_improvement >= 0.125
        and worst_regression <= -0.125
    )

    if not mechanics_pass:
        decision = "CR091_MECHANICS_FAIL"
    elif not option_active:
        decision = "CR091_OPTION_DORMANT"
    elif static_pass:
        decision = "CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER"
    elif heterogeneous:
        decision = "CR091_HETEROGENEOUS_OPTION_VALUE_ADVANCE_ROUTER_DISCOVERY"
    else:
        decision = "CR091_LATENT_OPTION_FAIL_CLOSE_OPTION"

    result = {
        "schema": "cr091-hierarchical-market-option-gate-v1",
        "engine": "kaggle-environments==1.32.7",
        "runner": {
            "reference_backend": "kaggle_exact_runtime.AgentProcess",
            "reference_agent_wrapper": "kaggle_environments.agent.Agent",
            "reference_observation_path": "Environment.__get_shared_state(seat).observation",
            "agent_process_isolation": "fresh_spawned_process_per_package_per_episode",
            "falsy_action_pass_substitution": False,
            "design_changed_from_frozen_protocol": False,
            "rerun_reason": "first run invalid: CR052 package was executed via direct main.py exec instead of package-faithful runner",
        },
        "seeds": [SEEDS[0], SEEDS[-1]],
        "opponents": list(PACKAGES),
        "treatments": list(TREATMENTS),
        "episodes_total": len(rows),
        "package_receipt": package_receipt,
        "mechanics": {
            "failures": len(failures),
            "physical_parity": [physical_ok, physical_calls],
            "market_multiset_parity": [multiset_ok, physical_calls],
            "base_exact_parity": [base_exact, base_calls],
            "violations": violations,
            "latent_reorders": latent_reorders,
            "mechanics_pass": mechanics_pass,
            "option_active": option_active,
            "failure_examples": [
                {
                    "treatment": r["treatment"],
                    "opponent": r["opponent"],
                    "seed": r["seed"],
                    "seat": r["seat"],
                    "statuses": r["statuses"],
                    "error": r["error"],
                    "error_phase": r["error_phase"],
                    "error_step": r["error_step"],
                    "error_traceback": r["error_traceback"],
                }
                for r in failures[:4]
            ],
        },
        "edges": edges,
        "edge_score_deltas_latent_minus_base": deltas,
        "gate": {
            "mean_edge_score_delta": mean_delta,
            "nonnegative_edges": nonnegative,
            "max_improvement": max_improvement,
            "worst_regression": worst_regression,
            "static_pass": static_pass,
            "heterogeneous_option_value": heterogeneous,
        },
        "decision": decision,
        "held_out_touched": False,
        "automatic_submission": False,
    }

    outdir = ROOT / "artifacts"
    outdir.mkdir(exist_ok=True)
    out = outdir / "cr091_hierarchical_market_option_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("CR091_RESULT", json.dumps(result, sort_keys=True))
    print("CR091_DECISION", decision)
    print("CR091_COMPLETE")

    if not mechanics_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
