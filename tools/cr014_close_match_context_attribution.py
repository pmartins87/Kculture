"""CR-014: explain CR-011 on the frozen CR-013 near-boundary pairs.

The pair set is copied verbatim from CR-013 before this diagnostic exists.  We
replay frozen R4B and CR-011, require exact terminal parity with CR-013, then
attribute every adaptive action divergence to identity-free public-state
features.  This is diagnostic only: it may choose the next refinement axis but
cannot authorize hosted promotion or tune on these same pairs.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidates import cr008_adaptive_frontrun as C

CONFIG = ROOT / "configs/cr014_close_match_context_pairs_v1.json"
BASE = "candidates/r4b_ablation_market_only.py"
CAND = "candidates/cr011_adaptive_early_order.py"


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(
        f"cr014_{path.stem}_{time.time_ns()}", path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.agent


def play(candidate_path: Path, opponent_path: Path, seed: int, seat: int):
    c = load_agent(candidate_path)
    o = load_agent(opponent_path)
    agents = [c, o] if seat == 0 else [o, c]
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=True,
    )
    env.run(agents)
    return env.toJSON()


def final_values(rep, seat: int):
    frame = rep["steps"][-1]
    statuses = [frame[i].get("status") for i in range(2)]
    rewards = [frame[i].get("reward") for i in range(2)]
    if statuses != ["DONE", "DONE"]:
        raise RuntimeError(f"non-DONE statuses: {statuses}")
    own = float(rewards[seat])
    opp = float(rewards[1 - seat])
    return own, opp, own - opp


def action_at(rep, seat: int, t: int):
    if t + 1 >= len(rep.get("steps") or []):
        return {}
    action = rep["steps"][t + 1][seat].get("action")
    return action if isinstance(action, dict) else {}


def obs_at(rep, seat: int, t: int):
    if t < 0 or t >= len(rep.get("steps") or []):
        return {}
    obs = rep["steps"][t][seat].get("observation")
    return obs if isinstance(obs, dict) else {}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def counter(xs):
    return collections.Counter(canon(x) for x in (xs or []))


def added_orders(candidate_action, base_action):
    ca = counter(candidate_action.get("market"))
    cb = counter(base_action.get("market"))
    out = []
    for encoded, n in (ca - cb).items():
        try:
            order = json.loads(encoded)
        except Exception:
            continue
        out.extend([order] * n)
    return out


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


def score(delta: float):
    return 1.0 if delta > 0 else 0.0 if delta < 0 else 0.5


def numeric_summary(values):
    vals = [float(v) for v in values if isinstance(v, (int, float))]
    if not vals:
        return None
    return {
        "n": len(vals),
        "mean": statistics.mean(vals),
        "median": statistics.median(vals),
        "min": min(vals),
        "max": max(vals),
    }


def summarize_pairs(rows):
    groups = {}
    for row in rows:
        sg = row["score_gain"]
        label = "favorable" if sg > 0 else "unfavorable" if sg < 0 else "neutral"
        groups.setdefault(label, []).append(row)
    out = {}
    for label, xs in groups.items():
        first = [x["triggers"][0] for x in xs if x["triggers"]]
        out[label] = {
            "pairs": len(xs),
            "affected_pairs": sum(bool(x["triggers"]) for x in xs),
            "mean_relative_gain": statistics.mean(x["relative_gain"] for x in xs),
            "mean_self_gain": statistics.mean(x["self_gain"] for x in xs),
            "trigger_count": numeric_summary([x["trigger_count"] for x in xs]),
            "first_probability": numeric_summary([x.get("probability") for x in first]),
            "first_quantity": numeric_summary([x.get("qty") for x in first]),
            "first_market_price": numeric_summary([x.get("market_price") for x in first]),
            "first_market_inventory": numeric_summary([x.get("market_inventory") for x in first]),
            "first_gap_money": numeric_summary([x.get("gap_money") for x in first]),
            "first_step": numeric_summary([x.get("step") for x in first]),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    opp_dir = Path(args.opponent_dir)
    if not opp_dir.is_absolute():
        opp_dir = ROOT / opp_dir

    base_path = ROOT / BASE
    cand_path = ROOT / CAND
    rows = []
    parity_errors = []

    for expected in cfg["pairs"]:
        opp_name = expected["opponent"]
        opp_path = opp_dir / f"{opp_name}.py"
        seed = int(expected["seed"])
        seat = int(expected["seat"])

        cand_rep = play(cand_path, opp_path, seed, seat)
        base_rep = play(base_path, opp_path, seed, seat)
        c_self, c_opp, c_delta = final_values(cand_rep, seat)
        b_self, b_opp, b_delta = final_values(base_rep, seat)
        rel_gain = c_delta - b_delta
        self_gain = c_self - b_self
        score_gain = score(c_delta) - score(b_delta)

        checks = {
            "base_delta": close(b_delta, expected["base_delta"]),
            "candidate_delta": close(c_delta, expected["candidate_delta"]),
            "relative_gain": close(rel_gain, expected["relative_gain"]),
            "self_gain": close(self_gain, expected["self_gain"]),
            "score_gain": close(score_gain, expected["score_gain"]),
        }
        if not all(checks.values()):
            parity_errors.append(
                {
                    "opponent": opp_name,
                    "seed": seed,
                    "seat": seat,
                    "checks": checks,
                    "observed": {
                        "base_delta": b_delta,
                        "candidate_delta": c_delta,
                        "relative_gain": rel_gain,
                        "self_gain": self_gain,
                        "score_gain": score_gain,
                    },
                    "expected": expected,
                }
            )

        triggers = []
        max_t = min(719, len(cand_rep["steps"]) - 1, len(base_rep["steps"]) - 1)
        for t in range(max_t):
            ca = action_at(cand_rep, seat, t)
            ba = action_at(base_rep, seat, t)
            if ca == ba:
                continue
            added = added_orders(ca, ba)
            adaptive = [
                o
                for o in added
                if isinstance(o, list)
                and len(o) >= 3
                and o[0] == "SELL"
                and o[1] in ("CARROT", "STRAWBERRY")
            ]
            if not adaptive:
                continue

            obs = obs_at(cand_rep, seat, t)
            prev = obs_at(cand_rep, seat, t - 24)
            features = C._public_features(obs, prev, seat) if prev else {}
            names = C._MODELS["feature_names"]
            market = obs.get("market") or {}
            prices = market.get("prices") or {}
            inventory = market.get("inventory") or {}

            for order in adaptive:
                item = order[1]
                target = f"SELL_{item}"
                try:
                    qty = max(0, int(order[2] or 0))
                except Exception:
                    qty = 0
                probability = (
                    C._tree_prob(C._MODELS["models"][target], features, names)
                    if features
                    else None
                )
                threshold = float(C._MODELS["thresholds"][target])
                triggers.append(
                    {
                        "step": t,
                        "item": item,
                        "qty": qty,
                        "probability": probability,
                        "threshold": threshold,
                        "market_price": prices.get(item),
                        "market_inventory": inventory.get(item),
                        "gap_money": features.get("gap_money") if features else None,
                        "self_money": features.get("self_money") if features else None,
                        "opp_money": features.get("opp_money") if features else None,
                        "self_crop_strawberry": features.get("self_crop_strawberry") if features else None,
                        "opp_crop_strawberry": features.get("opp_crop_strawberry") if features else None,
                        "dself_crop_strawberry": features.get("dself_crop_strawberry") if features else None,
                        "dopp_crop_strawberry": features.get("dopp_crop_strawberry") if features else None,
                        "dmarket_price_strawberry": features.get("dmarket_price_strawberry") if features else None,
                        "dmarket_inventory_strawberry": features.get("dmarket_inventory_strawberry") if features else None,
                        "base_market_count": len(ba.get("market") or []),
                        "base_market": ba.get("market") or [],
                        "model_features": {k: features.get(k, 0.0) for k in names} if features else {},
                    }
                )

        rows.append(
            {
                "opponent": opp_name,
                "seed": seed,
                "seat": seat,
                "base_reward": b_self,
                "candidate_reward": c_self,
                "base_delta": b_delta,
                "candidate_delta": c_delta,
                "relative_gain": rel_gain,
                "self_gain": self_gain,
                "score_gain": score_gain,
                "trigger_count": len(triggers),
                "triggers": triggers,
            }
        )

    affected = [r for r in rows if r["trigger_count"] > 0]
    catastrophic = [r for r in rows if r["score_gain"] < 0]
    favorable = [r for r in rows if r["score_gain"] > 0]

    payload = {
        "experiment": "CR-014",
        "status": "DIAGNOSTIC_COMPLETE" if not parity_errors else "PARITY_FAIL",
        "source_run": cfg["source_run"],
        "pairs": len(rows),
        "parity_errors": parity_errors,
        "affected_pairs": len(affected),
        "total_triggers": sum(r["trigger_count"] for r in rows),
        "outcome_groups": summarize_pairs(rows),
        "catastrophic_pairs": [
            {k: r[k] for k in ("opponent", "seed", "seat", "base_delta", "candidate_delta", "relative_gain", "self_gain", "score_gain", "trigger_count")}
            for r in catastrophic
        ],
        "favorable_pairs": [
            {k: r[k] for k in ("opponent", "seed", "seat", "base_delta", "candidate_delta", "relative_gain", "self_gain", "score_gain", "trigger_count")}
            for r in favorable
        ],
        "rows": rows,
        "interpretation_rule": "Use identity-free state context to choose the next refinement axis. Do not tune a hosted candidate on opponent names or promote directly from these 40 already-observed pairs.",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    printed = {k: v for k, v in payload.items() if k not in ("rows", "parity_errors")}
    printed["parity_error_count"] = len(parity_errors)
    print(json.dumps(printed, indent=2, sort_keys=True))
    if parity_errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
