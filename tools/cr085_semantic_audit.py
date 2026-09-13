"""Score-blind semantic audit for frozen CR085.

No rewards are run or inspected. The audit proves route tapes/constants remain
identical and actively exercises the exact step-226/360/433 switch semantics on
synthetic legal current observations.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
import tempfile
from pathlib import Path


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def load_module(source: str, name: str):
    td = tempfile.TemporaryDirectory()
    p = Path(td.name) / "main.py"
    p.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.__audit_tmpdir = td
    return mod


def tiny_farm(money: float, animals: int, plants: int):
    # Full 10x10 public board; only the first cells carry test entities.
    cells = []
    cells.extend({"kind": "PASTURE", "animal": "COW", "fed_today": True, "consecutive_unfed": 0} for _ in range(animals))
    cells.extend({"kind": "PLANT", "crop": "WHEAT", "yield_units": 0} for _ in range(plants))
    cells.extend("EMPTY" for _ in range(100 - len(cells)))
    grid = [cells[i:i + 10] for i in range(0, 100, 10)]
    return {
        "money": money,
        "tiles": grid,
        "farmer": [9, 9],
        "hands": [],
        "hires_today": 0,
        "unlocked_quadrants": [],
    }


def obs(step: int, money_me: float, money_opp: float, animals_me: int = 2,
        animals_opp: int = 2, plants_me: int = 3, plants_opp: int = 3,
        yarn: int = 0, carrot: int = 0, milk_inv: int = 0):
    products = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
    prices = {p: 1 for p in products}
    inventory = {p: 0 for p in products}
    prices["CARROT"] = carrot
    inventory["MILK"] = milk_inv
    return {
        "step": step,
        "day": step // 24,
        "hour": step % 24,
        "player": 0,
        "farms": [tiny_farm(money_me, animals_me, plants_me), tiny_farm(money_opp, animals_opp, plants_opp)],
        "private": {"seeds": {}, "inventories": [{}], "shed": {}},
        "market": {"prices": prices, "inventory": inventory},
        "town": {"unlocked_shops": ["YARN_STORE"] * yarn},
    }


def exercise_route(mod, start_route: str, observation: dict) -> str:
    a = mod.Agent()
    a.cur = start_route
    a.act(observation)
    return a.cur


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    bsrc = extract_main(a.base)
    csrc = extract_main(a.candidate)
    b = load_module(bsrc, "cr085_base_audit")
    c = load_module(csrc, "cr085_candidate_audit")

    checks = {}
    checks["candidate_has_guard_helper"] = hasattr(c, "_public_pareto_dominant")
    checks["base_has_no_guard_helper"] = not hasattr(b, "_public_pareto_dominant")
    checks["decisions_unchanged"] = b.DECISIONS == c.DECISIONS
    checks["route_ids_unchanged"] = (b.MAIN, b.YARN, b.YARN_CARROT, b.MILK_GLUT) == (c.MAIN, c.YARN, c.YARN_CARROT, c.MILK_GLUT)
    checks["route_tapes_identical"] = b.routes() == c.routes()
    checks["guarded_steps_exact"] = csrc.count('if turn in (360, 433) and not _public_pareto_dominant(obs, me):') == 1
    checks["original_threshold_literals_present"] = '(360, "px_CARROT", 42, YARN_CARROT)' in csrc and '(433, "inv_MILK", 10067, MILK_GLUT)' in csrc
    checks["switch_ok_preserved"] = 'target != self.cur and self._switch_ok(target, turn)' in csrc

    fn = c._public_pareto_dominant
    checks["guard_equal_true"] = fn({"farms": [tiny_farm(10, 2, 3), tiny_farm(10, 2, 3)]}, 0) is True
    checks["guard_strictly_dominant_true"] = fn({"farms": [tiny_farm(11, 3, 4), tiny_farm(10, 2, 3)]}, 0) is True
    checks["guard_money_behind_false"] = fn({"farms": [tiny_farm(9, 3, 4), tiny_farm(10, 2, 3)]}, 0) is False
    checks["guard_animals_behind_false"] = fn({"farms": [tiny_farm(11, 1, 4), tiny_farm(10, 2, 3)]}, 0) is False
    checks["guard_plants_behind_false"] = fn({"farms": [tiny_farm(11, 3, 2), tiny_farm(10, 2, 3)]}, 0) is False
    checks["guard_is_seat_symmetric"] = fn({"farms": [tiny_farm(10, 2, 3), tiny_farm(11, 3, 4)]}, 1) is True

    # Step 226 must remain unguarded: original market condition alone switches MAIN->YARN.
    o226 = obs(226, 1, 100, animals_me=0, animals_opp=5, plants_me=0, plants_opp=5, yarn=1)
    checks["step226_candidate_unchanged"] = exercise_route(c, c.MAIN, o226) == c.YARN
    checks["step226_matches_base"] = exercise_route(b, b.MAIN, o226) == b.YARN

    # Step 360: same original CARROT trigger; inferior state blocks, dominant state allows.
    o360_bad = obs(360, 9, 10, carrot=42)
    o360_good = obs(360, 11, 10, animals_me=3, animals_opp=2, plants_me=4, plants_opp=3, carrot=42)
    checks["step360_guard_exercised_block"] = exercise_route(c, c.YARN, o360_bad) == c.YARN
    checks["step360_original_would_switch"] = exercise_route(b, b.YARN, o360_bad) == b.YARN_CARROT
    checks["step360_dominance_allows_switch"] = exercise_route(c, c.YARN, o360_good) == c.YARN_CARROT

    # Step 433: same original MILK inventory trigger; inferior state blocks, dominant state allows.
    o433_bad = obs(433, 9, 10, milk_inv=10067)
    o433_good = obs(433, 11, 10, animals_me=3, animals_opp=2, plants_me=4, plants_opp=3, milk_inv=10067)
    checks["step433_guard_exercised_block"] = exercise_route(c, c.MAIN, o433_bad) == c.MAIN
    checks["step433_original_would_switch"] = exercise_route(b, b.MAIN, o433_bad) == b.MILK_GLUT
    checks["step433_dominance_allows_switch"] = exercise_route(c, c.MAIN, o433_good) == c.MILK_GLUT

    for token, key in [
        ('# ---- CR053-like market counterplay (public trajectory only) ----', 'cr053_counter_present'),
        ('# ---- room_guard: at day close, sell enough to avoid shed overflow ----', 'room_guard_present'),
        ('# ---- dead_stock: sell what the rest of the route will never get to ----', 'dead_stock_present'),
        ('# CR083 Phase 2: after all route-switch checkpoints are resolved,', 'cr083_seed_clamp_present'),
    ]:
        checks[key] = csrc.count(token) == bsrc.count(token) == 1

    out = {
        "schema_version": "cr085-semantic-audit-v2",
        "score_blind": True,
        "guarded_switches_exercised": 2,
        "checks": checks,
        "pass": all(checks.values()),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    if not out["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
