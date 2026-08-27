"""KEXP-049: midgame marginal HIRE utilization audit for frozen R4B.

Each farm hand is a one-day rental. The n-th same-day HIRE costs Fibonacci(n)
and disappears at the daily reset. Attribute every successfully observed R4B
HIRE in states 192..383 to the newly appended hand(s), then count that hand's
remaining PASS, movement and productive actions before the day ends.

Diagnostic only. Development + exploratory live-meta environmental seeds; no
validation or held-out access.
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

START, END = 192, 383
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}


def fib(n: int) -> int:
    a, b = 1, 1
    for _ in range(max(0, int(n))):
        a, b = b, a + b
    return a


def live_seeds(path: Path) -> list[int]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int): out.append(v["seed"])
            for x in v.values(): walk(x)
        elif isinstance(v, list):
            for x in v: walk(x)
    walk(obj)
    return list(dict.fromkeys(out))


def state_obs(rep, t):
    return rep["steps"][t][0].get("observation") or {}


def state_action(rep, t):
    steps = rep.get("steps") or []
    return (steps[t + 1][0].get("action") or {}) if t + 1 < len(steps) else {}


def farm(obs):
    fs = obs.get("farms") or []
    return fs[0] if fs else {}


def hire_intents(action) -> int:
    return sum(isinstance(x, list) and x and x[0] == "HIRE" for x in list((action or {}).get("market") or []))


def hand_action(action, hand_index_zero_based):
    hs = list((action or {}).get("hands") or [])
    if hand_index_zero_based < len(hs):
        op = hs[hand_index_zero_based]
        if isinstance(op, list) and op:
            return str(op[0])
    return "PASS"


def classify_name(name: str) -> str:
    if name == "PASS": return "pass"
    if name in MOVES: return "move"
    return "productive"


def analyze(rep, seed: int, source: str):
    rows = []
    steps = rep.get("steps") or []
    max_t = min(END, len(steps) - 2)
    for t in range(START, max_t + 1):
        obs = state_obs(rep, t)
        f = farm(obs)
        day = int(obs.get("day", 0) or 0)
        hour = int(obs.get("hour", t % 24) or 0)
        action = state_action(rep, t)
        intended = hire_intents(action)
        if intended <= 0:
            continue

        old_hands = len(f.get("hands", []) or [])
        try:
            hires_before = int(f.get("hires_today", old_hands) or 0)
        except Exception:
            hires_before = old_hands

        # A hire at the last hour is erased by the daily reset before the next
        # visible state, so it cannot be attributed to a persistent hand.
        if hour >= 23 or t + 1 >= len(steps):
            rows.append({
                "seed": int(seed), "source": source, "state": t, "day": day,
                "hour": hour, "intended_hires": intended, "ambiguous_day_end": True,
            })
            continue

        next_obs = state_obs(rep, t + 1)
        next_f = farm(next_obs)
        if int(next_obs.get("day", day) or day) != day:
            rows.append({
                "seed": int(seed), "source": source, "state": t, "day": day,
                "hour": hour, "intended_hires": intended, "ambiguous_day_end": True,
            })
            continue
        new_hands = len(next_f.get("hands", []) or [])
        committed = max(0, new_hands - old_hands)

        for j in range(committed):
            hand_idx = old_hands + j  # zero-based within action['hands']
            ordinal = hires_before + j
            cost = fib(ordinal)
            counts = collections.Counter()
            op_counts = collections.Counter()
            first_state = t + 1
            last_state = first_state - 1

            for s in range(first_state, min(len(steps) - 1, (day + 1) * 24)):
                so = state_obs(rep, s)
                if int(so.get("day", day) or day) != day:
                    break
                sf = farm(so)
                if hand_idx >= len(sf.get("hands", []) or []):
                    break
                name = hand_action(state_action(rep, s), hand_idx)
                counts[classify_name(name)] += 1
                op_counts[name] += 1
                last_state = s

            total = sum(counts.values())
            rows.append({
                "seed": int(seed), "source": source, "state": t, "day": day,
                "hour": hour, "hand_index": hand_idx, "hire_ordinal_zero_based": ordinal,
                "hire_cost": cost, "intended_hires_same_state": intended,
                "committed_hires_same_state": committed, "ambiguous_day_end": False,
                "remaining_action_slots": total,
                "pass_actions": counts["pass"], "move_actions": counts["move"],
                "productive_actions": counts["productive"],
                "nonpass_actions": total - counts["pass"],
                "productive_fraction": counts["productive"] / total if total else None,
                "nonpass_fraction": (total - counts["pass"]) / total if total else None,
                "op_counts": dict(op_counts),
                "last_observed_state": last_state,
            })
    return rows


def safe_mean(xs):
    vals = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.mean(vals) if vals else None


def safe_median(xs):
    vals = [float(x) for x in xs if isinstance(x, (int, float))]
    return statistics.median(vals) if vals else None


def summarize(rows):
    clean = [r for r in rows if not r.get("ambiguous_day_end") and "hire_cost" in r]
    high = [r for r in clean if r["hire_cost"] >= 34]
    very_high = [r for r in clean if r["hire_cost"] >= 89]
    lowprod = [r for r in clean if r["productive_actions"] <= 1]
    high_lowprod = [r for r in high if r["productive_actions"] <= 1]

    def block(rr):
        return {
            "n": len(rr),
            "mean_cost": safe_mean([r["hire_cost"] for r in rr]),
            "median_cost": safe_median([r["hire_cost"] for r in rr]),
            "mean_remaining_slots": safe_mean([r["remaining_action_slots"] for r in rr]),
            "mean_pass_actions": safe_mean([r["pass_actions"] for r in rr]),
            "mean_move_actions": safe_mean([r["move_actions"] for r in rr]),
            "mean_productive_actions": safe_mean([r["productive_actions"] for r in rr]),
            "mean_productive_fraction": safe_mean([r["productive_fraction"] for r in rr]),
            "mean_nonpass_fraction": safe_mean([r["nonpass_fraction"] for r in rr]),
            "zero_productive_fraction": sum(r["productive_actions"] == 0 for r in rr) / len(rr) if rr else None,
            "at_most_one_productive_fraction": sum(r["productive_actions"] <= 1 for r in rr) / len(rr) if rr else None,
        }

    by_cost = {}
    for c in sorted({r["hire_cost"] for r in clean}):
        by_cost[str(c)] = block([r for r in clean if r["hire_cost"] == c])
    by_ordinal = {}
    for o in sorted({r["hire_ordinal_zero_based"] for r in clean}):
        by_ordinal[str(o)] = block([r for r in clean if r["hire_ordinal_zero_based"] == o])

    return {
        "clean_hires": len(clean),
        "ambiguous_day_end_rows": sum(bool(r.get("ambiguous_day_end")) for r in rows),
        "all": block(clean),
        "cost_ge_34": block(high),
        "cost_ge_89": block(very_high),
        "all_low_productivity": block(lowprod),
        "high_cost_low_productivity": block(high_lowprod),
        "by_cost": by_cost,
        "by_ordinal": by_ordinal,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    rows = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        agent = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([agent, "starter"])
        rows.extend(analyze(env.toJSON(), int(seed), source))

    summary = {
        "development": summarize([r for r in rows if r["source"] == "development"]),
        "live_meta": summarize([r for r in rows if r["source"] == "live_meta"]),
        "all": summarize(rows),
    }
    payload = {
        "schema_version": "midgame-hire-marginal-value-v1",
        "window": [START, END],
        "hire_cost": "fib(hires_today), fib(0)=1,fib(1)=1",
        "summary": summary,
        "rows": rows,
    }
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
