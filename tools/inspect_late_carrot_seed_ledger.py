"""KEXP-026: exact late CARROT seed ledger and truly unreserved stock audit.

Runs frozen R4B unchanged vs starter on development + exploratory live-meta
environmental seeds. Unlike KEXP-025, this diagnostic never sums repeated
snapshots of the same seed stock. It reconstructs the per-step seed ledger and
asks whether any CARROT seed at a mechanically safe WHEAT-plant step is truly
unreserved by same-turn and all later base CARROT plant intents.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

SAFE_STEPS = frozenset(list(range(614, 619)) + list(range(620, 624)) + list(range(636, 648)))


def live_seeds(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    found: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int):
                found.append(v["seed"])
            for child in v.values(): walk(child)
        elif isinstance(v, list):
            for child in v: walk(child)
    walk(payload)
    return list(dict.fromkeys(found))


def ops(action):
    if not isinstance(action, dict): return []
    return [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]


def plant_count(action, crop):
    return sum(isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", crop] for op in ops(action))


def buy_seed(action, crop):
    total = 0
    for order in (action or {}).get("market", []) or []:
        if isinstance(order, list) and len(order) >= 3 and order[:2] == ["BUY_SEED", crop]:
            try: total += max(0, int(order[2] or 0))
            except (TypeError, ValueError): pass
    return total


def seed_stock(entry, crop):
    obs = entry.get("observation") or {}
    private = obs.get("private") or {}
    seeds = private.get("seeds") or {}
    try: return max(0, int(seeds.get(crop, 0) or 0))
    except (TypeError, ValueError): return 0


def analyze(replay, seed, source):
    steps = replay["steps"]
    ledger = []
    for t in range(600, min(719, len(steps) - 1)):
        entry = steps[t][0]
        nxt = steps[t + 1][0]
        action = entry.get("action") or {}
        c0, c1 = seed_stock(entry, "CARROT"), seed_stock(nxt, "CARROT")
        w0, w1 = seed_stock(entry, "WHEAT"), seed_stock(nxt, "WHEAT")
        cp, wp = plant_count(action, "CARROT"), plant_count(action, "WHEAT")
        cb, wb = buy_seed(action, "CARROT"), buy_seed(action, "WHEAT")
        c_consumed = c0 + cb - c1
        w_consumed = w0 + wb - w1
        ledger.append({
            "step": t,
            "carrot_stock": c0,
            "carrot_stock_next": c1,
            "carrot_plant_intents": cp,
            "carrot_buy": cb,
            "carrot_inferred_consumed": c_consumed,
            "wheat_stock": w0,
            "wheat_stock_next": w1,
            "wheat_plant_intents": wp,
            "wheat_buy": wb,
            "wheat_inferred_consumed": w_consumed,
        })

    alignment_bad = [r for r in ledger if not (
        isinstance(r["carrot_inferred_consumed"], int)
        and isinstance(r["wheat_inferred_consumed"], int)
        and 0 <= r["carrot_inferred_consumed"] <= r["carrot_plant_intents"]
        and 0 <= r["wheat_inferred_consumed"] <= r["wheat_plant_intents"]
    )]

    safe_candidates = []
    for i, r in enumerate(ledger):
        same_turn_unreserved = r["carrot_stock"] - r["carrot_plant_intents"]
        if r["step"] not in SAFE_STEPS or r["wheat_plant_intents"] <= 0 or same_turn_unreserved <= 0:
            continue
        later_carrot_intents = sum(x["carrot_plant_intents"] for x in ledger[i + 1:])
        if later_carrot_intents == 0:
            safe_candidates.append({
                "step": r["step"],
                "carrot_stock": r["carrot_stock"],
                "same_turn_carrot_plant_intents": r["carrot_plant_intents"],
                "same_turn_unreserved_carrot_stock": same_turn_unreserved,
                "wheat_plant_intents": r["wheat_plant_intents"],
                "later_carrot_plant_intents": 0,
                "max_extra_stock_only_swaps_this_turn": min(r["wheat_plant_intents"], same_turn_unreserved),
            })

    return {
        "seed": int(seed), "source": source,
        "alignment_bad_count": len(alignment_bad),
        "alignment_bad_rows": alignment_bad[:10],
        "last_carrot_intent_step": max((r["step"] for r in ledger if r["carrot_plant_intents"] > 0), default=None),
        "last_carrot_consumption_step": max((r["step"] for r in ledger if r["carrot_inferred_consumed"] > 0), default=None),
        "safe_unreserved_candidates": safe_candidates,
        "first_safe_unreserved_step": safe_candidates[0]["step"] if safe_candidates else None,
        "max_extra_stock_only_swaps": max((r["max_extra_stock_only_swaps_this_turn"] for r in safe_candidates), default=0),
        "ledger": ledger,
    }


def string_hist(values):
    return {str(k): v for k, v in sorted(Counter(values).items(), key=lambda kv: (kv[0] is None, -1 if kv[0] is None else kv[0]))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    episodes = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        candidate = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([candidate, "starter"])
        episodes.append(analyze(env.toJSON(), int(seed), source))

    summary = {}
    for source in ("development", "live_meta", "all"):
        ee = episodes if source == "all" else [e for e in episodes if e["source"] == source]
        firsts = [e["first_safe_unreserved_step"] for e in ee if e["first_safe_unreserved_step"] is not None]
        counts = [len(e["safe_unreserved_candidates"]) for e in ee]
        capacities = [e["max_extra_stock_only_swaps"] for e in ee]
        summary[source] = {
            "episodes": len(ee),
            "alignment_bad_total": sum(e["alignment_bad_count"] for e in ee),
            "episodes_with_safe_unreserved_stock": sum(c > 0 for c in counts),
            "safe_unreserved_candidate_snapshots": sum(counts),
            "total_max_episode_stock_only_capacity": sum(capacities),
            "max_episode_stock_only_capacity_histogram": string_hist(capacities),
            "first_safe_unreserved_step_histogram": string_hist(firsts),
            "last_carrot_intent_step_histogram": string_hist([e["last_carrot_intent_step"] for e in ee]),
        }
    payload = {"schema_version": "late-carrot-seed-ledger-v2", "safe_steps": sorted(SAFE_STEPS), "summary": summary, "episodes": episodes}
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__": main()
