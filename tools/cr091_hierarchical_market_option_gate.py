#!/usr/bin/env python3
"""CR091 gate 1 — exact CR053 physical backbone + CR086 latent-supply market option."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import tarfile
import types
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates.cr091_cr053_market_option import make_agent

RUNTIME = ROOT / ".cr091_runtime"
SEEDS = tuple(range(91301, 91309))
TREATMENTS = ("CR053_BASE", "CR053_LATENT_PRIORITY")

PACKAGES = {
    "CR052_REAL": (RUNTIME / "CR052.tar.gz", "b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d"),
    "CR053_REAL": (RUNTIME / "CR053.tar.gz", "095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15"),
    "CR083": (RUNTIME / "CR083.tar.gz", "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8"),
    "CR086": (RUNTIME / "CR086.tar.gz", "11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888"),
}


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


SOURCES = {}


def load_fresh(name: str):
    source = SOURCES[name]
    mod = types.ModuleType(f"cr091_{name}_{id(source)}_{load_fresh.counter}")
    load_fresh.counter += 1
    mod.__file__ = f"<{name}:main.py>"
    exec(compile(source, mod.__file__, "exec"), mod.__dict__)
    if not callable(mod.__dict__.get("agent")):
        raise RuntimeError(f"{name} has no callable agent")
    return mod


load_fresh.counter = 0


def call_agent(fn, obs, config=None):
    try:
        return fn(obs, config)
    except TypeError:
        return fn(obs)


def freeze(obj):
    return json.loads(json.dumps(obj))


def market_multiset(market):
    rows = []
    for order in market or []:
        rows.append(json.dumps(list(order), sort_keys=True, separators=(",", ":")))
    return tuple(sorted(rows))


class ParityChecker:
    def __init__(self, candidate, reference, treatment):
        self.candidate = candidate
        self.reference = reference
        self.treatment = treatment
        self.calls = 0
        self.physical_ok = 0
        self.multiset_ok = 0
        self.exact_ok = 0
        self.reorders = 0
        self.violations = []

    def __call__(self, obs, config=None):
        ref = freeze(call_agent(self.reference, obs, config))
        act = freeze(call_agent(self.candidate, obs, config))
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
        return act


def make_candidate(treatment: str):
    base_mod = load_fresh("CR053_REAL")
    ref_mod = load_fresh("CR053_REAL")
    if treatment == "CR053_BASE":
        candidate = base_mod.agent
    elif treatment == "CR053_LATENT_PRIORITY":
        donor_mod = load_fresh("CR086")
        candidate = make_agent(base_mod.agent, donor_mod, enabled=True)
    else:
        raise ValueError(treatment)
    return ParityChecker(candidate, ref_mod.agent, treatment)


def run_one(treatment: str, opponent_name: str, seed: int, seat: int):
    checked = make_candidate(treatment)
    opponent_mod = load_fresh(opponent_name)
    opponent = opponent_mod.agent
    agents = [checked, opponent] if seat == 0 else [opponent, checked]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "startingMoney": 3000, "seed": seed},
        debug=True,
    )
    err = None
    try:
        env.run(agents)
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"

    payload = env.toJSON()
    statuses = list(payload.get("statuses") or [])
    rewards = list(payload.get("rewards") or [])
    done = statuses == ["DONE", "DONE"] and len(rewards) == 2 and all(x is not None for x in rewards)

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
        "candidate_reward": cand_reward,
        "opponent_reward": opp_reward,
        "margin": margin,
        "outcome": outcome,
        "calls": checked.calls,
        "physical_ok": checked.physical_ok,
        "multiset_ok": checked.multiset_ok,
        "exact_ok": checked.exact_ok,
        "reorders": checked.reorders,
        "violations": checked.violations[:3],
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
            str(seat): (sum(r["outcome"] for r in valid if r["seat"] == seat) /
                        max(1, sum(1 for r in valid if r["seat"] == seat)))
            for seat in (0, 1)
        },
        "reorders": sum(r["reorders"] for r in rows),
    }


def main():
    package_receipt = {}
    for name, (path, expected) in PACKAGES.items():
        if not path.exists():
            raise SystemExit(f"missing runtime package {path}")
        actual = sha256(path)
        package_receipt[name] = {"path": str(path.relative_to(ROOT)), "sha256": actual, "expected": expected}
        if actual != expected:
            raise SystemExit(f"SHA mismatch {name}: {actual} != {expected}")
        SOURCES[name] = source_from_tar(path)

    rows = []
    for opponent in PACKAGES:
        for seed in SEEDS:
            for seat in (0, 1):
                for treatment in TREATMENTS:
                    row = run_one(treatment, opponent, seed, seat)
                    rows.append(row)
                    print(
                        "CR091_CASE", treatment, opponent, seed, seat,
                        "done", row["done"], "outcome", row["outcome"],
                        "margin", row["margin"], "reorders", row["reorders"],
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
