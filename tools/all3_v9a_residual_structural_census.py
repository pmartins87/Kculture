#!/usr/bin/env python3
"""Dormant V9A: residual ALL3 vs V48-shadow structural divergence census.

Pre-registered before the binding V8C result. This file has no workflow trigger.
Activate only if V8C closes without reusable W/L headroom.

V48 is an offline shadow proposal source only: its action is evaluated on the exact
ALL3 candidate observation at every turn but never applied to the environment.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.o_pc1_dev_shard import EXPECTED_ENGINE, BASE, V2_OPPONENTS, acquire
from tools.programme_adaptive_expert_gate import load_public_agent, purge_package_modules
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action, plain, score
from tools.first_party_option_host_v1 import OptionHostState, apply_option_host

V48_KEY = "v48"


def json_key(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def market_multiset(market):
    return sorted(json_key(x) for x in market)


def nonempty_orders(market):
    return [copy.deepcopy(x) for x in market if isinstance(x, list) and x]


def order_signature(order):
    if not isinstance(order, list) or not order:
        return ("EMPTY",)
    op = str(order[0])
    product = str(order[1]) if len(order) >= 2 else None
    return (op, product)


def qty(order):
    if not isinstance(order, list) or len(order) < 3:
        return None
    try:
        return int(order[2])
    except Exception:
        return None


def classify_market(base_market, shadow_market):
    if base_market == shadow_market:
        return "EXACT", {}

    if market_multiset(base_market) == market_multiset(shadow_market):
        return "REORDER_ONLY", {
            "base_nonempty": len(nonempty_orders(base_market)),
            "shadow_nonempty": len(nonempty_orders(shadow_market)),
        }

    b = nonempty_orders(base_market)
    s = nonempty_orders(shadow_market)
    bsig = [order_signature(x) for x in b]
    ssig = [order_signature(x) for x in s]

    if len(b) != len(s):
        return "INSERT_DROP", {
            "base_nonempty": len(b),
            "shadow_nonempty": len(s),
            "base_signatures": bsig,
            "shadow_signatures": ssig,
        }

    if bsig == ssig:
        ups = downs = 0
        deltas = []
        for bo, so in zip(b, s):
            bq, sq = qty(bo), qty(so)
            if bq is None or sq is None:
                if bo != so:
                    return "OTHER", {"reason": "same_signature_nonquantity_payload_diff"}
                continue
            d = sq - bq
            deltas.append(d)
            ups += d > 0
            downs += d < 0
        if ups and not downs:
            return "QTY_UP", {"qty_deltas": deltas}
        if downs and not ups:
            return "QTY_DOWN", {"qty_deltas": deltas}
        if ups and downs:
            return "MIXED_STRUCTURAL", {"qty_deltas": deltas, "reason": "mixed_qty_direction"}
        return "OTHER", {"reason": "same_signature_no_numeric_delta"}

    # Same number of occupied slots but changed op/product structure.
    # If signatures also contain permutations plus replacements, keep it in mixed.
    if sorted(bsig) == sorted(ssig):
        return "MIXED_STRUCTURAL", {
            "reason": "signature_multiset_same_but_full_order_multiset_diff",
            "base_signatures": bsig,
            "shadow_signatures": ssig,
        }

    return "REPLACE", {
        "base_signatures": bsig,
        "shadow_signatures": ssig,
    }


class CandidateWithShadow:
    def __init__(self, base_main, shadow_main, index, ctx):
        self.base = load_public_agent(base_main)
        self.shadow = load_public_agent(shadow_main)
        self.state = OptionHostState()
        self.index = int(index)
        self.ctx = ctx
        self.turn = 0
        self.rows = []

    def __call__(self, obs, config=None):
        turn = self.turn
        self.turn += 1
        exact_v47 = canonical_action(call_agent(self.base, obs, config))
        all3 = apply_option_host(
            obs, config, exact_v47, self.state,
            use_rw=True, use_tw=True, use_lq2=True,
        )
        v48 = canonical_action(call_agent(self.shadow, obs, config))

        same_physical = (
            all3["farmer"] == v48["farmer"]
            and all3["hands"] == v48["hands"]
        )
        category, detail = classify_market(all3["market"], v48["market"])
        if (not same_physical) or category != "EXACT":
            p = plain(obs)
            self.rows.append({
                "index": self.index,
                "opponent": self.ctx["opponent"],
                "family": self.ctx.get("family"),
                "seed": self.ctx["seed"],
                "seat": self.ctx["seat"],
                "turn": turn,
                "obs_step": p.get("step") if isinstance(p, dict) else None,
                "day": p.get("day") if isinstance(p, dict) else None,
                "hour": p.get("hour") if isinstance(p, dict) else None,
                "same_physical": same_physical,
                "category": category,
                "detail": detail,
                "all3_market": copy.deepcopy(all3["market"]),
                "v48_shadow_market": copy.deepcopy(v48["market"]),
                "all3_farmer": copy.deepcopy(all3["farmer"]),
                "v48_shadow_farmer": copy.deepcopy(v48["farmer"]),
                "all3_hands": copy.deepcopy(all3["hands"]),
                "v48_shadow_hands": copy.deepcopy(v48["hands"]),
            })
        return all3


def finish(env, seat):
    p = env.toJSON()
    st = [str(x) for x in p.get("statuses", [])]
    rw = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if st != ["DONE", "DONE"] or len(rw) != 2 or not all(math.isfinite(x) for x in rw) or steps < 720:
        raise RuntimeError(f"invalid episode status={st} rewards={rw} steps={steps}")
    mine, opp = (rw[0], rw[1]) if seat == 0 else (rw[1], rw[0])
    margin = mine - opp
    return {"reward": mine, "opponent_reward": opp, "margin": margin, "score": score(margin), "steps": steps}


def purge(paths):
    seen = set()
    for p in paths:
        k = str(p.parent.resolve())
        if k in seen:
            continue
        seen.add(k)
        purge_package_modules(p.parent)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg = json.loads(Path(args.config).read_text())
    contexts = list(cfg.get("selected_hard_contexts") or [])
    if len(contexts) != 4:
        raise SystemExit(f"expected 4 frozen hard contexts, got {len(contexts)}")

    v48_spec = next(x for x in V2_OPPONENTS if x["key"] == V48_KEY)
    rows = []
    context_rows = []
    failures = []
    provenance = {}
    paths = []
    started = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory(prefix="all3-v9a-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            v48_main, provenance["v48_shadow"] = acquire(v48_spec, tmp / "v48_shadow")
            opp_cache = {}
            paths = [base_main, v48_main]

            for index, ctx in enumerate(contexts):
                opp_key = str(ctx["opponent"])
                spec = next(x for x in V2_OPPONENTS if x["key"] == opp_key)
                if opp_key not in opp_cache:
                    if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
                        opp_cache[opp_key] = base_main
                    elif spec["expected_main_sha256"] == v48_spec["expected_main_sha256"]:
                        opp_cache[opp_key] = v48_main
                    else:
                        pp, rec = acquire(spec, tmp / f"opp_{opp_key}")
                        opp_cache[opp_key] = pp
                        provenance[f"opp_{opp_key}"] = rec
                        paths.append(pp)
                opp_main = opp_cache[opp_key]

                try:
                    purge(paths)
                    cand = CandidateWithShadow(base_main, v48_main, index, ctx)
                    opp = load_public_agent(opp_main)
                    env = make(
                        "kaggriculture",
                        configuration={"episodeSteps": 720, "seed": int(ctx["seed"])},
                        debug=False,
                    )
                    if int(ctx["seat"]) == 0:
                        env.run([cand, opp])
                    else:
                        env.run([opp, cand])
                    fin = finish(env, int(ctx["seat"]))
                    if float(fin["score"]) != float(ctx["score"]) or float(fin["margin"]) != float(ctx["margin"]):
                        raise RuntimeError(
                            f"ALL3 replay mismatch idx={index}: "
                            f"{(fin['score'], fin['margin'])} != {(ctx['score'], ctx['margin'])}"
                        )
                    cr = list(cand.rows)
                    rows.extend(cr)
                    cats = Counter(r["category"] for r in cr)
                    physical = sum(not r["same_physical"] for r in cr)
                    context_rows.append({
                        "index": index,
                        "context": ctx,
                        "final": fin,
                        "divergence_rows": len(cr),
                        "category_counts": dict(sorted(cats.items())),
                        "physical_divergences": physical,
                        "first_divergent_turn": min((r["turn"] for r in cr), default=None),
                        "first_structural_turn": min(
                            (r["turn"] for r in cr if r["category"] in {"QTY_UP","QTY_DOWN","REPLACE","INSERT_DROP","MIXED_STRUCTURAL"}),
                            default=None,
                        ),
                    })
                    print("V9A_CONTEXT", json.dumps(context_rows[-1], sort_keys=True), flush=True)
                except Exception as exc:
                    failures.append({"index": index, "error": f"{type(exc).__name__}: {exc}"})
                finally:
                    purge(paths)

    except Exception as exc:
        failures.append({"phase": "setup", "error": f"{type(exc).__name__}: {exc}"})

    cats = Counter(r["category"] for r in rows)
    structural = {"QTY_UP", "QTY_DOWN", "REPLACE", "INSERT_DROP", "MIXED_STRUCTURAL"}
    structural_contexts = sorted({int(r["index"]) for r in rows if r["category"] in structural})
    market_divs = sum(r["category"] != "EXACT" for r in rows)
    physical_divs = sum(not r["same_physical"] for r in rows)
    mech = not failures and len(context_rows) == 4

    if not mech:
        decision = "V9A_MECHANICS_INVALID"
    elif market_divs == 0:
        decision = "V9A_NO_RESIDUAL_MARKET_DIFFERENCE"
    elif not structural_contexts and cats.get("REORDER_ONLY", 0) > 0:
        decision = "V9A_ORDER_ONLY_RESIDUAL"
    elif len(structural_contexts) >= 2:
        decision = "V9A_STRUCTURAL_RESIDUAL_READY"
    else:
        decision = "V9A_STRUCTURAL_RESIDUAL_NARROW"

    result = {
        "schema": "kculture-all3-v9a-residual-structural-census-v1",
        "status": "DORMANT_HARNESS_UNLESS_V8C_CLOSES",
        "engine": EXPECTED_ENGINE,
        "mechanical_pass": mech,
        "decision": decision,
        "contexts": context_rows,
        "divergence_rows": rows,
        "category_counts": dict(sorted(cats.items())),
        "structural_contexts": structural_contexts,
        "market_divergences": market_divs,
        "physical_divergences": physical_divs,
        "failures": failures,
        "provenance": provenance,
        "seconds": time.perf_counter() - started,
        "automatic_kaggle_submission": False,
    }
    p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("V9A_RESULT", json.dumps({
        "mechanical_pass": mech,
        "decision": decision,
        "market_divergences": market_divs,
        "physical_divergences": physical_divs,
        "category_counts": dict(sorted(cats.items())),
        "structural_contexts": structural_contexts,
        "failures": len(failures),
    }, sort_keys=True), flush=True)
    if not mech:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
