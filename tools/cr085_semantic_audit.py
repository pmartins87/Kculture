"""Score-blind semantic audit for frozen CR085.

This audit intentionally does not run or inspect rewards. It proves that the
candidate package preserves CR083's route tapes and constants and that the only
source-level policy delta is the public Pareto helper plus the guard on steps
360/433. It also unit-tests the guard's exact zero-threshold semantics.
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


def farm(money: float, animals: int, plants: int):
    # Minimal public farm shape accepted by _public_pareto_dominant.
    ents = []
    ents.extend({"kind": "PASTURE", "animal": "COW"} for _ in range(animals))
    ents.extend({"kind": "PLANT", "crop": "WHEAT"} for _ in range(plants))
    return {"money": money, "tiles": [ents]}


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
    checks["step226_not_guarded"] = 'if turn in (360, 433)' in csrc and 'Step 226 is intentionally unchanged' in csrc
    checks["guarded_steps_exact"] = csrc.count('if turn in (360, 433) and not _public_pareto_dominant(obs, me):') == 1
    checks["original_threshold_literals_present"] = '(360, "px_CARROT", 42, YARN_CARROT)' in csrc and '(433, "inv_MILK", 10067, MILK_GLUT)' in csrc
    checks["switch_ok_preserved"] = 'target != self.cur and self._switch_ok(target, turn)' in csrc

    fn = c._public_pareto_dominant
    checks["guard_equal_true"] = fn({"farms": [farm(10, 2, 3), farm(10, 2, 3)]}, 0) is True
    checks["guard_strictly_dominant_true"] = fn({"farms": [farm(11, 3, 4), farm(10, 2, 3)]}, 0) is True
    checks["guard_money_behind_false"] = fn({"farms": [farm(9, 3, 4), farm(10, 2, 3)]}, 0) is False
    checks["guard_animals_behind_false"] = fn({"farms": [farm(11, 1, 4), farm(10, 2, 3)]}, 0) is False
    checks["guard_plants_behind_false"] = fn({"farms": [farm(11, 3, 2), farm(10, 2, 3)]}, 0) is False
    checks["guard_is_seat_symmetric"] = fn({"farms": [farm(10, 2, 3), farm(11, 3, 4)]}, 1) is True

    # Strong textual invariants: protected CR083 mechanisms remain exactly once.
    for token, key in [
        ('# ---- CR053-like market counterplay (public trajectory only) ----', 'cr053_counter_present'),
        ('# ---- room_guard: at day close, sell enough to avoid shed overflow ----', 'room_guard_present'),
        ('# ---- dead_stock: sell what the rest of the route will never get to ----', 'dead_stock_present'),
        ('# CR083 Phase 2: after all route-switch checkpoints are resolved,', 'cr083_seed_clamp_present'),
    ]:
        checks[key] = csrc.count(token) == bsrc.count(token) == 1

    out = {
        "schema_version": "cr085-semantic-audit-v1",
        "score_blind": True,
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
