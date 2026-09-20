#!/usr/bin/env python3
"""V8C: one-shot causal value atlas for every actual O-LQ3 firing state.

Discovery is performed on the four frozen ALL3 hard contexts. Each branch applies the
frozen O-LQ3 priority transform on exactly one turn, then immediately resumes ALL3.
This isolates state-dependent causal value from the cumulative Stage-A failure.
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
from tools.bounded_transaction_oracle_v1 import call_agent, canonical_action, action_key, plain, score
from tools.first_party_option_host_v1 import OptionHostState, apply_option_host
from tools.first_party_lq3_priority_sell_order import lq3_action
from tools.cq2_projected_queue_dev_matrix import projected_shed_after_physical

TARGETS = ("MILK", "WOOL", "FERTILIZER")
EXPECTED_FIRES_PER_CONTEXT = 12


def getv(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return getattr(obj, key, default)


def as_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return int(default)


def public_features(obs, config, all3, treated, meta, turn):
    p = plain(obs)
    private = getv(p, "private", {}) or {}
    shed = getv(private, "shed", {}) or {}
    projected = projected_shed_after_physical(obs, config, all3)
    market_obs = getv(p, "market", {}) or {}
    prices = getv(market_obs, "prices", {}) or {}
    inventory = getv(market_obs, "inventory", {}) or {}
    town = getv(p, "town", {}) or {}
    shops = list(getv(town, "unlocked_shops", []) or [])

    sells = []
    target_qty = {k: 0 for k in TARGETS}
    before_targets = []
    after_targets = []
    for idx, order in enumerate(all3["market"]):
        if isinstance(order, list) and len(order) >= 3 and str(order[0]) == "SELL":
            prod = str(order[1]); qty = max(0, as_int(order[2], 0))
            sells.append({"slot": idx, "product": prod, "qty": qty})
            if prod in target_qty:
                target_qty[prod] += qty
                before_targets.append(prod)
    for order in treated["market"]:
        if isinstance(order, list) and len(order) >= 3 and str(order[0]) == "SELL":
            prod = str(order[1])
            if prod in target_qty:
                after_targets.append(prod)

    return {
        "turn": int(turn),
        "obs_step": getv(p, "step", None),
        "day": as_int(getv(p, "day", -1), -1),
        "hour": as_int(getv(p, "hour", -1), -1),
        "target_qty": target_qty,
        "target_qty_total": sum(target_qty.values()),
        "target_distinct": sum(1 for v in target_qty.values() if v > 0),
        "before_targets": before_targets,
        "after_targets": after_targets,
        "sell_orders": sells,
        "sell_order_count": len(sells),
        "market_order_count": sum(1 for x in all3["market"] if x),
        "hire_count": sum(1 for x in all3["market"] if isinstance(x, list) and x and str(x[0]) == "HIRE"),
        "buy_count": sum(1 for x in all3["market"] if isinstance(x, list) and x and str(x[0]).startswith("BUY")),
        "own_shed": {k: as_int(getv(shed, k, 0), 0) for k in TARGETS},
        "projected_shed": {k: as_int(getv(projected, k, 0), 0) for k in TARGETS},
        "prices": {k: as_int(getv(prices, k, 0), 0) for k in TARGETS},
        "market_inventory": {k: as_int(getv(inventory, k, 0), 0) for k in TARGETS},
        "shop_counts": dict(sorted(Counter(str(x) for x in shops).items())),
        "moves": copy.deepcopy(meta.get("moves", [])),
        "base_action_key": action_key(all3),
        "base_market": copy.deepcopy(all3["market"]),
        "treated_market": copy.deepcopy(treated["market"]),
    }


class Discovery:
    def __init__(self, main):
        self.agent = load_public_agent(main)
        self.state = OptionHostState()
        self.turn = 0
        self.events = []

    def __call__(self, obs, config=None):
        turn = self.turn
        self.turn += 1
        base = canonical_action(call_agent(self.agent, obs, config))
        all3 = apply_option_host(obs, config, base, self.state, use_rw=True, use_tw=True, use_lq2=True)
        treated, meta = lq3_action(all3)
        if meta.get("fired"):
            self.events.append(public_features(obs, config, all3, treated, meta, turn))
        return all3


class OneShot:
    def __init__(self, main, event):
        self.agent = load_public_agent(main)
        self.state = OptionHostState()
        self.event = event
        self.turn = 0
        self.target_seen = False

    def __call__(self, obs, config=None):
        turn = self.turn
        self.turn += 1
        base = canonical_action(call_agent(self.agent, obs, config))
        all3 = apply_option_host(obs, config, base, self.state, use_rw=True, use_tw=True, use_lq2=True)
        if turn != int(self.event["turn"]):
            return all3
        self.target_seen = True
        if action_key(all3) != str(self.event["base_action_key"]):
            raise RuntimeError(f"ALL3 action mismatch at target turn {turn}")
        treated, meta = lq3_action(all3)
        if not meta.get("fired"):
            raise RuntimeError(f"O-LQ3 no longer fires at target turn {turn}")
        if treated["market"] != self.event["treated_market"]:
            raise RuntimeError(f"O-LQ3 treated market mismatch at target turn {turn}")
        return treated


def finish(env, seat, wrapper=None):
    p = env.toJSON()
    st = [str(x) for x in p.get("statuses", [])]
    rw = [float(x) for x in p.get("rewards", [])]
    steps = len(p.get("steps") or [])
    if st != ["DONE", "DONE"] or len(rw) != 2 or not all(math.isfinite(x) for x in rw) or steps < 720:
        raise RuntimeError(f"invalid episode {st} {rw} {steps}")
    if wrapper is not None and not wrapper.target_seen:
        raise RuntimeError(f"target turn {wrapper.event['turn']} not reached")
    mine, opp = (rw[0], rw[1]) if seat == 0 else (rw[1], rw[0])
    margin = mine - opp
    return {"reward": mine, "opponent_reward": opp, "margin": margin, "score": score(margin), "steps": steps}


def run_discovery(base_main, opp_main, seed, seat):
    cand = Discovery(base_main); opp = load_public_agent(opp_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0: env.run([cand, opp])
    else: env.run([opp, cand])
    out = finish(env, seat)
    out["events"] = cand.events
    return out


def run_one(base_main, opp_main, seed, seat, event):
    cand = OneShot(base_main, event); opp = load_public_agent(opp_main)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=False)
    if seat == 0: env.run([cand, opp])
    else: env.run([opp, cand])
    return finish(env, seat, cand)


def purge(paths):
    seen = set()
    for p in paths:
        k = str(p.parent.resolve())
        if k in seen: continue
        seen.add(k); purge_package_modules(p.parent)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--index", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import kaggle_environments
    if str(getattr(kaggle_environments, "__version__", "")) != EXPECTED_ENGINE:
        raise SystemExit("engine mismatch")

    cfg = json.loads(Path(args.config).read_text())
    contexts = list(cfg.get("selected_hard_contexts") or [])
    ctx = contexts[args.index]
    opp_key = str(ctx["opponent"]); seed = int(ctx["seed"]); seat = int(ctx["seat"])
    spec = next(x for x in V2_OPPONENTS if x["key"] == opp_key)
    failures = []; rows = []; provenance = {}; started = time.perf_counter(); result = None
    paths = []
    try:
        with tempfile.TemporaryDirectory(prefix=f"v8c-{args.index}-{opp_key}-") as td:
            tmp = Path(td)
            base_main, provenance["base"] = acquire(BASE, tmp / "base")
            if spec["expected_main_sha256"] == BASE["expected_main_sha256"]:
                opp_main = base_main
                provenance["opponent"] = {**provenance["base"], "key": opp_key, "family": spec.get("family"), "reused_exact_base_bytes": True}
            else:
                opp_main, rec = acquire(spec, tmp / "opp")
                provenance["opponent"] = {**rec, "family": spec.get("family")}
            paths = [base_main, opp_main]

            purge(paths)
            discovery = run_discovery(base_main, opp_main, seed, seat)
            if float(discovery["score"]) != float(ctx["score"]) or float(discovery["margin"]) != float(ctx["margin"]):
                raise RuntimeError(f"ALL3 discovery mismatch {(discovery['score'], discovery['margin'])} != {(ctx['score'], ctx['margin'])}")
            events = discovery["events"]
            for event in events:
                try:
                    purge(paths)
                    tr = run_one(base_main, opp_main, seed, seat, event)
                    row = {
                        "index": args.index, "opponent": opp_key, "family": ctx.get("family"),
                        "seed": seed, "seat": seat,
                        "turn": int(event["turn"]), "day": event["day"], "hour": event["hour"],
                        "base_score": discovery["score"], "base_margin": discovery["margin"],
                        "treatment_score": tr["score"], "treatment_margin": tr["margin"],
                        "score_delta": float(tr["score"]) - float(discovery["score"]),
                        "margin_delta": float(tr["margin"]) - float(discovery["margin"]),
                        "features": {k: v for k, v in event.items() if k not in ("base_action_key", "base_market", "treated_market")},
                    }
                    rows.append(row)
                    print("V8C_BRANCH", json.dumps({
                        "index": args.index, "opponent": opp_key, "seed": seed, "seat": seat,
                        "turn": row["turn"], "day": row["day"], "hour": row["hour"],
                        "target_qty": row["features"]["target_qty"],
                        "before_targets": row["features"]["before_targets"],
                        "after_targets": row["features"]["after_targets"],
                        "score_delta": row["score_delta"], "margin_delta": row["margin_delta"],
                    }, sort_keys=True), flush=True)
                except Exception as exc:
                    failures.append({"turn": event.get("turn"), "error": f"{type(exc).__name__}: {exc}"})

            mech = not failures and len(events) > 0 and len(rows) == len(events)
            result = {
                "schema": "kculture-v8c-local-priority-value-context-v1",
                "mechanical_pass": mech,
                "index": args.index, "context": ctx,
                "base": {k: discovery[k] for k in ("reward", "opponent_reward", "margin", "score", "steps")},
                "event_count": len(events), "branches": rows,
                "failures": failures, "provenance": provenance,
                "seconds": time.perf_counter() - started,
            }
    except Exception as exc:
        failures.append({"phase": "setup_or_discovery", "error": f"{type(exc).__name__}: {exc}"})
        result = {
            "schema": "kculture-v8c-local-priority-value-context-v1",
            "mechanical_pass": False, "index": args.index, "context": ctx,
            "branches": rows, "failures": failures, "seconds": time.perf_counter() - started,
        }
    finally:
        try: purge(paths)
        except Exception: pass

    p = Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    pos = [r for r in rows if r["margin_delta"] > 0]
    neg = [r for r in rows if r["margin_delta"] < 0]
    print("V8C_CONTEXT_RESULT", json.dumps({
        "index": args.index, "opponent": opp_key, "seed": seed, "seat": seat,
        "mechanical_pass": result.get("mechanical_pass"), "branch_count": len(rows),
        "loss_to_win_flips": sum(r["base_score"] == 0.0 and r["treatment_score"] == 1.0 for r in rows),
        "positive_margin_states": len(pos), "negative_margin_states": len(neg),
        "mean_margin_delta": statistics.fmean(r["margin_delta"] for r in rows) if rows else 0.0,
        "best": max(rows, key=lambda r: (r["treatment_score"], r["margin_delta"])) if rows else None,
        "failures": len(failures),
    }, sort_keys=True), flush=True)
    if not result.get("mechanical_pass"): raise SystemExit(2)


if __name__ == "__main__":
    main()
