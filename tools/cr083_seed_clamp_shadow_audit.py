"""Score-blind CR083 Phase-2 semantic audit on exact Kaggriculture observations.

CR071M drives the environment. CR071M-shadow and CR083-shadow receive the exact same
seat-0 observations. The audit verifies that CR083 changes only BUY_SEED quantities
according to the frozen future-demand formula and never changes farmer/hands or any
non-seed market order.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from collections import Counter
from pathlib import Path

from kaggle_exact_runtime import (
    agent_visible_observation,
    extract,
    make_reference_env,
    make_seeds,
    reference_step,
)

CLAMP_START = 434
AUDIT_MASTER = 91308309


def load_module(main_py: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, main_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {main_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def expected_market(base_action: dict, cand_mod, obs: dict, step: int) -> list:
    base_market = [list(o) for o in (base_action.get("market") or [])]
    if step < CLAMP_START:
        return base_market
    acts = [base_action.get("farmer") or ["PASS"], *(base_action.get("hands") or [])]
    plant_now = Counter()
    for a in acts:
        if a and len(a) >= 2 and a[0] == "PLANT":
            plant_now[a[1]] += 1
    seeds = dict((obs.get("private") or {}).get("seeds") or {})
    projected = dict(seeds)
    for crop, demand in plant_now.items():
        have = max(0, int(projected.get(crop, 0)))
        if demand <= have:
            projected[crop] = have - demand
    agent_obj = getattr(cand_mod, "_A", None)
    if agent_obj is None:
        raise RuntimeError("candidate Agent not initialized")
    out = []
    for o in base_market:
        if o and len(o) >= 3 and o[0] == "BUY_SEED":
            crop = o[1]
            qty = max(0, int(o[2]))
            future = int(agent_obj.future_plants(crop, step + 1))
            have = max(0, int(projected.get(crop, 0)))
            keep = min(qty, max(0, future - have))
            if keep > 0:
                out.append(["BUY_SEED", crop, keep])
                projected[crop] = have + keep
        else:
            out.append(o)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seed-count", type=int, default=2)
    a = ap.parse_args()

    seeds = make_seeds(a.seed_count, AUDIT_MASTER)
    report = {
        "schema_version": "cr083-seed-clamp-shadow-audit-v1",
        "audit_master": AUDIT_MASTER,
        "audit_seeds": seeds,
        "score_blind": True,
        "steps_compared": 0,
        "farmer_hands_mismatches": 0,
        "pre434_market_mismatches": 0,
        "formula_mismatches": 0,
        "non_seed_market_mismatches": 0,
        "seed_units_removed": 0,
        "seed_units_removed_by_crop": {},
        "changed_steps": 0,
    }
    removed = Counter()

    with tempfile.TemporaryDirectory(prefix="cr083-shadow-audit-") as td:
        root = Path(td)
        bdir = extract(a.base, root, "base")
        cdir = extract(a.candidate, root, "candidate")
        for si, seed in enumerate(seeds):
            b0 = load_module(bdir / "main.py", f"cr083_b0_{si}")
            b1 = load_module(bdir / "main.py", f"cr083_b1_{si}")
            bs = load_module(bdir / "main.py", f"cr083_bs_{si}")
            cs = load_module(cdir / "main.py", f"cr083_cs_{si}")
            env = make_reference_env(seed)
            while not env.done:
                step = int(agent_visible_observation(env, 0).get("step", 0))
                obs0 = agent_visible_observation(env, 0)
                obs1 = agent_visible_observation(env, 1)
                act0 = b0.agent(obs0)
                act1 = b1.agent(obs1)
                base_shadow = bs.agent(obs0)
                cand = cs.agent(obs0)
                if act0 != base_shadow:
                    raise AssertionError(f"baseline shadow divergence at seed={seed} step={step}")
                report["steps_compared"] += 1
                if cand.get("farmer") != base_shadow.get("farmer") or cand.get("hands") != base_shadow.get("hands"):
                    report["farmer_hands_mismatches"] += 1
                if step < CLAMP_START and cand.get("market") != base_shadow.get("market"):
                    report["pre434_market_mismatches"] += 1
                exp = expected_market(base_shadow, cs, obs0, step)
                if cand.get("market") != exp:
                    report["formula_mismatches"] += 1
                # Removing BUY_SEED from each queue must leave identical order sequence.
                strip = lambda m: [o for o in (m or []) if not (o and o[0] == "BUY_SEED")]
                if strip(cand.get("market")) != strip(base_shadow.get("market")):
                    report["non_seed_market_mismatches"] += 1
                bseed = Counter()
                cseed = Counter()
                for o in base_shadow.get("market") or []:
                    if o and len(o) >= 3 and o[0] == "BUY_SEED": bseed[o[1]] += int(o[2])
                for o in cand.get("market") or []:
                    if o and len(o) >= 3 and o[0] == "BUY_SEED": cseed[o[1]] += int(o[2])
                diff = sum(max(0, bseed[k] - cseed[k]) for k in bseed)
                if diff:
                    report["changed_steps"] += 1
                    for k in bseed:
                        removed[k] += max(0, bseed[k] - cseed[k])
                reference_step(env, [act0, act1], [0.0, 0.0])

    report["seed_units_removed_by_crop"] = dict(sorted(removed.items()))
    report["seed_units_removed"] = sum(removed.values())
    report["pass"] = all(report[k] == 0 for k in (
        "farmer_hands_mismatches", "pre434_market_mismatches",
        "formula_mismatches", "non_seed_market_mismatches"
    )) and report["seed_units_removed"] > 0
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
