"""Score-blind semantic audit for frozen CR086 latent-supply priority.

No environment rewards are read. The audit proves protected CR083 mechanisms and
routes are unchanged, and exercises the exact reorder/risk semantics on synthetic
legal market states.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import tarfile
import tempfile
from collections import Counter
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


def multiset(queue):
    return Counter(json.dumps(x, sort_keys=True) for x in queue)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    bsrc, csrc = extract_main(a.base), extract_main(a.candidate)
    b, c = load_module(bsrc, "cr086_base_audit"), load_module(csrc, "cr086_candidate_audit")
    checks = {}

    checks["routes_identical"] = b.routes() == c.routes()
    checks["decisions_identical"] = b.DECISIONS == c.DECISIONS
    checks["candidate_has_runtime_layer"] = all(hasattr(c, x) for x in (
        "_cr086_update", "_cr086_cash_risk", "_cr086_prioritize",
        "_cr086_market_price", "_cr086_advance", "_cr086_revenue",
    ))
    checks["offline_truth_label_code_absent"] = "evaluate_replay" not in csrc and "truth_obs" not in csrc
    checks["forbidden_identity_features_absent"] = all(x not in csrc for x in ("EpisodeId", "team_name", "leaderboard_rating"))
    checks["ordering_layer_exactly_once"] = csrc.count("final_market = _cr086_prioritize(self, obs, final_market)") == 1

    for token, key in [
        ('# ---- CR053-like market counterplay (public trajectory only) ----', 'cr053_counter_preserved'),
        ('# ---- room_guard: at day close, sell enough to avoid shed overflow ----', 'room_guard_preserved'),
        ('# ---- clamp_sells: a SELL the shed cannot fill burns one of only 10 slots ----', 'sell_clamp_preserved'),
        ('# ---- dead_stock: sell what the rest of the route will never get to ----', 'dead_stock_preserved'),
        ('# CR083 Phase 2: after all route-switch checkpoints are resolved,', 'seed_clamp_preserved'),
    ]:
        checks[key] = bsrc.count(token) == csrc.count(token) == 1

    # Official base-price checkpoints at I0=10000.
    expected_base = {"CARROT":35,"TOMATO":60,"STRAWBERRY":120,"MELON":250,"EGG":50,"MILK":160,"WOOL":200}
    checks["official_price_base_points"] = all(c._cr086_market_price(k, 10000) == v for k, v in expected_base.items())
    checks["price_nonincreasing_above_i0"] = all(
        c._cr086_market_price(k, 10000) >= c._cr086_market_price(k, 10001) >= c._cr086_market_price(k, 10020)
        for k in expected_base
    )

    agent = c.Agent()
    agent._cr086_upper = dict((x, 0) for x in c._CR086_PRIMARY)
    obs = {"market": {"inventory": dict((x,10000) for x in c._CR086_PRIMARY)}}

    # Risk-zero state: queue must remain byte/semantic order identical.
    q0 = [["HIRE"], ["SELL","MILK",10], ["SELL","EGG",4], ["BUY_SEED","CARROT",2]]
    r0 = c._cr086_prioritize(agent, obs, q0)
    checks["risk_zero_no_promotion"] = r0 == q0

    # Positive latent MILK supply creates strictly positive cash-at-risk and only reorders.
    agent._cr086_upper["MILK"] = 20
    milk_risk = c._cr086_cash_risk(agent, obs, q0[1])
    r1 = c._cr086_prioritize(agent, obs, q0)
    checks["positive_risk_exercised"] = milk_risk > 0 and r1[0] == ["SELL","MILK",10]
    checks["queue_length_unchanged"] = len(r1) == len(q0)
    checks["queue_multiset_unchanged"] = multiset(r1) == multiset(q0)
    checks["nonurgent_relative_order_preserved"] = r1[1:] == [["HIRE"], ["SELL","EGG",4], ["BUY_SEED","CARROT",2]]

    # Two identical-risk orders keep original index order (stable tie-break).
    agent._cr086_upper["MILK"] = 20
    qt = [["SELL","MILK",5], ["SELL","MILK",5], ["HIRE"]]
    rt = c._cr086_prioritize(agent, obs, qt)
    checks["stable_tie_source_present"] = "urgent.sort(key=lambda row: (-row[0], row[1]))" in csrc
    checks["tie_queue_multiset_unchanged"] = multiset(rt) == multiset(qt)

    # Floor mechanics: once quoted at $1, further SELL units do not advance inventory.
    floor_inventory = None
    for m in range(10000, 20000):
        if c._cr086_market_price("MILK", m) == 1:
            floor_inventory = m
            break
    checks["floor_reached"] = floor_inventory is not None
    checks["floor_no_supply_increment"] = (
        floor_inventory is not None
        and c._cr086_advance("MILK", floor_inventory, 50) == floor_inventory
        and c._cr086_revenue("MILK", floor_inventory, 50) == 50
    )

    out = {
        "schema_version": "cr086-latent-supply-semantic-audit-v1",
        "score_blind": True,
        "checks": checks,
        "synthetic_positive_milk_cash_risk": milk_risk,
        "synthetic_reorders_exercised": 1 if r1 != q0 else 0,
        "pass": all(checks.values()),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    if not out["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
