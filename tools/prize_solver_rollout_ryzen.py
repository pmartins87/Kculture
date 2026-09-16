#!/usr/bin/env python3
from __future__ import annotations

"""PS2 exact counterfactual rollout generator for the Ryzen workstation.

Runs one independent seed per process, checkpoints every completed seed, and can be
restarted safely. Training labels come from cloned exact-engine states. Runtime-facing
features never include seed/future/hidden opponent state.
"""

import argparse
import copy
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from kaggle_exact_runtime import (
    agent_visible_observation,
    done_status,
    make_reference_env,
    reference_config,
    reference_step,
)
from solver.prize_solver_v0 import PLANS, _step
from solver.prize_solver_v4 import PrizeSolverV4
from solver.rollout_search import clone_solver, forced_plan_solver
from solver.value_features import encode_value_features


def _git_head():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def _stable_hash(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _reward(env, seat):
    value = env.state[seat].reward
    return None if value is None else float(value)


def _margin(env):
    a, b = _reward(env, 0), _reward(env, 1)
    return None if a is None or b is None else a - b


def _advance_one(env, cfg, a0, a1):
    o0 = agent_visible_observation(env, 0)
    o1 = agent_visible_observation(env, 1)
    x0 = a0.act(o0, cfg)
    x1 = a1.act(o1, cfg)
    reference_step(env, [x0, x1], [0.0, 0.0])


def _run_to_step(env, cfg, a0, a1, target_step):
    while not all(done_status(s.status) for s in env.state):
        now = int(agent_visible_observation(env, 0).get("step", 0))
        if now >= target_step:
            break
        _advance_one(env, cfg, a0, a1)


def _run_to_end(env, cfg, a0, a1):
    guard = 0
    while not all(done_status(s.status) for s in env.state):
        _advance_one(env, cfg, a0, a1)
        guard += 1
        if guard > 725:
            raise RuntimeError("rollout exceeded episode length")


def _branch_label(env, cfg, base0, base1, plan, branch_step, force_steps):
    benv = copy.deepcopy(env)
    cand = forced_plan_solver(base0, plan, branch_step + force_steps)
    opp = clone_solver(base1)
    _run_to_end(benv, cfg, cand, opp)
    statuses = [str(s.status) for s in benv.state]
    m = _margin(benv)
    return {
        "plan": plan.name,
        "margin": m,
        "reward0": _reward(benv, 0),
        "reward1": _reward(benv, 1),
        "statuses": statuses,
        "ok": statuses == ["DONE", "DONE"] and m is not None,
    }


def _run_seed(job):
    seed = int(job["seed"])
    branch_days = tuple(int(x) for x in job["branch_days"])
    force_days = int(job["force_days"])

    env = make_reference_env(seed)
    cfg = reference_config(env)
    a0 = PrizeSolverV4()
    a1 = PrizeSolverV4()
    turns = max(1, int(cfg.get("turnsPerDay", 24)))
    force_steps = force_days * turns
    rows = []
    failures = []

    for day in branch_days:
        target = day * turns
        _run_to_step(env, cfg, a0, a1, target)
        if all(done_status(s.status) for s in env.state):
            failures.append({"seed": seed, "day": day, "error": "baseline ended before branch"})
            break

        obs = agent_visible_observation(env, 0)
        branch_step = _step(obs, cfg)
        features = encode_value_features(obs, cfg)
        heuristic_plan = a0._select_plan(obs, cfg).name

        labels = []
        for plan in PLANS:
            result = _branch_label(env, cfg, a0, a1, plan, branch_step, force_steps)
            labels.append(result)
            if not result["ok"]:
                failures.append({"seed": seed, "day": day, "plan": plan.name, "result": result})

        valid = [x for x in labels if x["ok"]]
        best = max(valid, key=lambda x: (x["margin"], x["plan"])) if valid else None
        h = next((x for x in valid if x["plan"] == heuristic_plan), None)
        rows.append({
            "seed": seed,
            "day": day,
            "step": branch_step,
            "force_days": force_days,
            "features": {k: float(v) for k, v in features.items()},
            "heuristic_plan": heuristic_plan,
            "heuristic_margin": None if h is None else h["margin"],
            "oracle_plan": None if best is None else best["plan"],
            "oracle_margin": None if best is None else best["margin"],
            "heuristic_regret": None if best is None or h is None else best["margin"] - h["margin"],
            "plan_returns": labels,
        })

        # Advance only the single unforced baseline trajectory to keep branch states
        # independent of the counterfactual labels just generated.
        _run_to_step(env, cfg, a0, a1, (day + 1) * turns)

    return {"seed": seed, "rows": rows, "failures": failures}


def _make_seeds(count, master_seed):
    rng = random.Random(int(master_seed))
    out = set()
    while len(out) < int(count):
        out.add(rng.randint(1, 2_147_483_646))
    return sorted(out)


def _write_json_atomic(path: Path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _aggregate(out_dir: Path, manifest):
    rows, failures = [], []
    for path in sorted((out_dir / "shards").glob("seed_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data.get("rows", []))
        failures.extend(data.get("failures", []))
    regrets = [r["heuristic_regret"] for r in rows if r.get("heuristic_regret") is not None]
    exact = sum(1 for r in rows if r.get("oracle_plan") and r.get("oracle_plan") == r.get("heuristic_plan"))
    plan_counts = {}
    for r in rows:
        p = r.get("oracle_plan")
        if p:
            plan_counts[p] = plan_counts.get(p, 0) + 1
    result = {
        "schema": "prize-solver-ps2-ryzen-v1",
        "manifest": manifest,
        "branch_states": len(rows),
        "rollouts": sum(len(r.get("plan_returns", [])) for r in rows),
        "failures": failures,
        "heuristic_oracle_exact_matches": exact,
        "heuristic_oracle_match_rate": exact / len(rows) if rows else 0.0,
        "mean_heuristic_regret": mean(regrets) if regrets else None,
        "max_heuristic_regret": max(regrets) if regrets else None,
        "oracle_plan_counts": plan_counts,
    }
    _write_json_atomic(out_dir / "SUMMARY.json", result)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/ps2_v4_pilot")
    ap.add_argument("--seed-count", type=int, default=250, help="250 seeds x 8 days = 2000 branch states")
    ap.add_argument("--master-seed", type=int, default=26091601)
    ap.add_argument("--branch-days", default="3,6,9,12,15,18,21,24")
    ap.add_argument("--force-days", type=int, default=3)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 8) - 2))
    args = ap.parse_args()

    branch_days = tuple(int(x.strip()) for x in args.branch_days.split(",") if x.strip())
    seeds = _make_seeds(args.seed_count, args.master_seed)
    config = {
        "schema": "prize-solver-ps2-ryzen-config-v1",
        "solver": "PrizeSolverV4",
        "engine": "kaggle-environments==1.32.7",
        "source_commit": _git_head(),
        "seed_count": args.seed_count,
        "master_seed": args.master_seed,
        "branch_days": list(branch_days),
        "force_days": args.force_days,
        "plans": [p.name for p in PLANS],
        "opponent": "PrizeSolverV4 self-play",
    }
    config["config_sha256"] = _stable_hash(config)

    out_dir = (ROOT / args.out).resolve()
    shards = out_dir / "shards"
    shards.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "MANIFEST.json"
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old.get("config_sha256") != config["config_sha256"]:
            raise SystemExit(
                f"refusing to mix incompatible run configs in {out_dir}; choose another --out"
            )
    else:
        _write_json_atomic(manifest_path, config)

    pending = [s for s in seeds if not (shards / f"seed_{s}.json").exists()]
    done_before = len(seeds) - len(pending)
    print(
        f"PS2_START states_target={len(seeds)*len(branch_days)} seeds={len(seeds)} "
        f"resume_done={done_before} pending={len(pending)} workers={args.workers}",
        flush=True,
    )
    start = time.time()

    if pending:
        jobs = ({"seed": s, "branch_days": branch_days, "force_days": args.force_days} for s in pending)
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_run_seed, job): job["seed"] for job in jobs}
            completed = done_before
            for fut in as_completed(futs):
                seed = futs[fut]
                try:
                    result = fut.result()
                except Exception as exc:
                    result = {"seed": seed, "rows": [], "failures": [{"seed": seed, "exception": repr(exc)}]}
                _write_json_atomic(shards / f"seed_{seed}.json", result)
                completed += 1
                if completed % 5 == 0 or completed == len(seeds):
                    elapsed = max(1.0, time.time() - start)
                    rate = max(0.0, (completed - done_before) / elapsed)
                    print(f"PS2_PROGRESS seeds={completed}/{len(seeds)} rate={rate:.3f}/s", flush=True)

    summary = _aggregate(out_dir, config)
    print("PS2_DONE", json.dumps({
        "branch_states": summary["branch_states"],
        "rollouts": summary["rollouts"],
        "failures": len(summary["failures"]),
        "match_rate": summary["heuristic_oracle_match_rate"],
        "mean_regret": summary["mean_heuristic_regret"],
        "max_regret": summary["max_heuristic_regret"],
        "out": str(out_dir),
    }, sort_keys=True), flush=True)
    if summary["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
