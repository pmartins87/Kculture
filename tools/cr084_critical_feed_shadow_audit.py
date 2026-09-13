"""Score-blind semantic audit for frozen CR084 critical feed rescue.

CR083 drives both seats of the exact environment. CR083-shadow and CR084-shadow see
identical seat-0 observations. Every physical difference must be exactly the frozen
noop->FEED rescue rule; market actions must remain byte-for-byte equivalent.
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

START_STEP = 576
END_STEP_EXCLUSIVE = 696
AUDIT_MASTER = 91408409


def load_module(main_py: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, main_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {main_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def validate_diff(base_mod, obs: dict, base_action: dict, cand_action: dict, step: int) -> tuple[int, Counter]:
    if cand_action.get("market") != base_action.get("market"):
        raise AssertionError(f"market changed at step={step}")

    bacts = [base_action.get("farmer") or ["PASS"], *(base_action.get("hands") or [])]
    cacts = [cand_action.get("farmer") or ["PASS"], *(cand_action.get("hands") or [])]
    if len(bacts) != len(cacts):
        raise AssertionError(f"unit count changed at step={step}")

    me = int(obs.get("player", 0))
    farm = obs["farms"][me]
    tiles = farm["tiles"]
    board = len(tiles) or base_mod.BOARD
    priv = obs["private"]
    invs = priv.get("inventories") or []
    seeds = priv.get("seeds") or {}
    positions = [tuple(farm["farmer"])] + [tuple(p) for p in farm["hands"]]

    changed = 0
    animals = Counter()
    for i, (ba, ca) in enumerate(zip(bacts, cacts)):
        if ba == ca:
            continue
        changed += 1
        if not (START_STEP <= step < END_STEP_EXCLUSIVE):
            raise AssertionError(f"physical diff outside frozen window at step={step}: {ba}->{ca}")
        if ca != ["FEED"]:
            raise AssertionError(f"candidate diff is not FEED at step={step} unit={i}: {ba}->{ca}")
        if i >= len(positions):
            raise AssertionError(f"missing position at step={step} unit={i}")
        x, y = positions[i]
        if not (0 <= x < board and 0 <= y < board):
            raise AssertionError(f"invalid position at step={step} unit={i}: {(x,y)}")
        tile = tiles[y][x]
        inv = invs[i] if i < len(invs) else {}
        if not (isinstance(tile, dict) and tile.get("animal") is not None):
            raise AssertionError(f"FEED rescue not on live animal at step={step} unit={i}")
        if bool(tile.get("fed_today")):
            raise AssertionError(f"FEED rescue on already-fed animal at step={step} unit={i}")
        if int(tile.get("consecutive_unfed", 0)) < 1:
            raise AssertionError(f"FEED rescue without escape risk at step={step} unit={i}")
        if int(inv.get("WHEAT", 0)) <= 0:
            raise AssertionError(f"FEED rescue without carried wheat at step={step} unit={i}")
        if not base_mod._noop(ba, tile, inv, seeds, x, y, board):
            raise AssertionError(f"CR084 replaced non-noop at step={step} unit={i}: {ba}")
        animals[str(tile.get("animal"))] += 1
    return changed, animals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seed-count", type=int, default=8)
    a = ap.parse_args()

    seeds = make_seeds(a.seed_count, AUDIT_MASTER)
    report = {
        "schema_version": "cr084-critical-feed-shadow-audit-v1",
        "audit_master": AUDIT_MASTER,
        "audit_seeds": seeds,
        "score_blind": True,
        "steps_compared": 0,
        "changed_steps": 0,
        "rescued_unit_actions": 0,
        "rescues_by_animal": {},
        "market_mismatches": 0,
        "invalid_physical_differences": 0,
    }
    animal_counts = Counter()

    with tempfile.TemporaryDirectory(prefix="cr084-shadow-") as td:
        root = Path(td)
        bdir = extract(a.base, root, "base")
        cdir = extract(a.candidate, root, "candidate")
        for si, seed in enumerate(seeds):
            b0 = load_module(bdir / "main.py", f"cr084_b0_{si}")
            b1 = load_module(bdir / "main.py", f"cr084_b1_{si}")
            bs = load_module(bdir / "main.py", f"cr084_bs_{si}")
            cs = load_module(cdir / "main.py", f"cr084_cs_{si}")
            env = make_reference_env(seed)
            while not env.done:
                obs0 = agent_visible_observation(env, 0)
                obs1 = agent_visible_observation(env, 1)
                step = int(obs0.get("step", 0))
                act0 = b0.agent(obs0)
                act1 = b1.agent(obs1)
                base_shadow = bs.agent(obs0)
                cand_shadow = cs.agent(obs0)
                if act0 != base_shadow:
                    raise AssertionError(f"baseline shadow divergence seed={seed} step={step}")
                report["steps_compared"] += 1
                try:
                    n, kinds = validate_diff(bs, obs0, base_shadow, cand_shadow, step)
                except AssertionError:
                    report["invalid_physical_differences"] += 1
                    raise
                if n:
                    report["changed_steps"] += 1
                    report["rescued_unit_actions"] += n
                    animal_counts.update(kinds)
                reference_step(env, [act0, act1], [0.0, 0.0])

    report["rescues_by_animal"] = dict(sorted(animal_counts.items()))
    report["pass"] = (
        report["market_mismatches"] == 0
        and report["invalid_physical_differences"] == 0
        and report["rescued_unit_actions"] > 0
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
