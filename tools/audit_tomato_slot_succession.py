"""KEXP-055: audit post-harvest succession of R4B's TOMATO-compatible slots.

Follow every development/exploratory R4B WHEAT/CARROT plant in states 240..527
whose next same-tile HARVEST is at least 192 turns later. After that HARVEST,
record the next same-tile tile action and the next same-tile PLANT. This measures
whether replacing the original one-shot crop with ongoing TOMATO would block a
later route action and whether an explicit DIG/release would be needed.

Development + exploratory live-meta environmental seeds only. No validation or
held-out outcomes are read.
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

AGENT = "file:candidates/r4b_ablation_market_only.py:agent"
START, END = 240, 527
MIN_TOMATO_DELAY = 192
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
IGNORE = MOVES | {"PASS"}


def live_seeds(path: Path) -> list[int]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    out: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int):
                out.append(v["seed"])
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(obj)
    return list(dict.fromkeys(out))


def observation(rep, t):
    return rep["steps"][t][0].get("observation") or {}


def action(rep, t):
    steps = rep.get("steps") or []
    return (steps[t + 1][0].get("action") or {}) if t + 1 < len(steps) else {}


def unit_positions(obs):
    farms = obs.get("farms") or []
    farm = farms[0] if farms else {}
    return [tuple(farm.get("farmer") or (-1, -1))] + [tuple(x) for x in (farm.get("hands") or [])]


def unit_ops(act):
    return [act.get("farmer")] + list(act.get("hands") or [])


def events(rep):
    out = []
    for t in range(len(rep.get("steps") or []) - 1):
        obs = observation(rep, t)
        pos = unit_positions(obs)
        ops = unit_ops(action(rep, t))
        day = int(obs.get("day", t // 24) or 0)
        for i, op in enumerate(ops):
            if i >= len(pos) or not (isinstance(op, list) and op):
                continue
            name = str(op[0])
            if name in IGNORE:
                continue
            out.append({
                "state": t,
                "day": day,
                "unit": i,
                "pos": pos[i],
                "op": name,
                "arg": str(op[1]) if len(op) > 1 else None,
            })
    return out


def analyze(rep, seed, source):
    ev = events(rep)
    by_pos = collections.defaultdict(list)
    for e in ev:
        by_pos[e["pos"]].append(e)
    rows = []
    for e in ev:
        if not (START <= e["state"] <= END and e["op"] == "PLANT" and e["arg"] in {"WHEAT", "CARROT"}):
            continue
        same = by_pos[e["pos"]]
        harvest = next((x for x in same if x["state"] > e["state"] and x["op"] == "HARVEST"), None)
        if harvest is None:
            continue
        delay = harvest["state"] - e["state"]
        if delay < MIN_TOMATO_DELAY:
            continue
        later = [x for x in same if x["state"] > harvest["state"]]
        next_tile = later[0] if later else None
        next_plant = next((x for x in later if x["op"] == "PLANT"), None)
        plant_gap = (next_plant["state"] - harvest["state"]) if next_plant else None
        rows.append({
            "seed": int(seed),
            "source": source,
            "plant_state": e["state"],
            "plant_crop": e["arg"],
            "pos": list(e["pos"]),
            "harvest_state": harvest["state"],
            "delay_to_harvest": delay,
            "next_tile_action_state": next_tile["state"] if next_tile else None,
            "next_tile_action": next_tile["op"] if next_tile else None,
            "next_tile_action_arg": next_tile["arg"] if next_tile else None,
            "next_plant_state": next_plant["state"] if next_plant else None,
            "next_plant_crop": next_plant["arg"] if next_plant else None,
            "turns_harvest_to_next_plant": plant_gap,
            "replant_within_24": bool(plant_gap is not None and plant_gap <= 24),
            "replant_within_48": bool(plant_gap is not None and plant_gap <= 48),
            "replant_within_96": bool(plant_gap is not None and plant_gap <= 96),
            "no_future_plant": next_plant is None,
        })
    return rows


def summarize(rows):
    gaps = [r["turns_harvest_to_next_plant"] for r in rows if isinstance(r["turns_harvest_to_next_plant"], int)]
    next_ops = collections.Counter(r["next_tile_action"] or "NONE" for r in rows)
    state_pos = collections.Counter((r["plant_state"], tuple(r["pos"])) for r in rows)
    return {
        "compatible_slots": len(rows),
        "episodes": len({r["seed"] for r in rows}),
        "next_tile_action_counts": dict(next_ops),
        "future_replant_slots": len(gaps),
        "no_future_plant_slots": sum(r["no_future_plant"] for r in rows),
        "replant_within_24": sum(r["replant_within_24"] for r in rows),
        "replant_within_48": sum(r["replant_within_48"] for r in rows),
        "replant_within_96": sum(r["replant_within_96"] for r in rows),
        "median_harvest_to_next_plant": statistics.median(gaps) if gaps else None,
        "min_harvest_to_next_plant": min(gaps) if gaps else None,
        "recurring_slots": [
            {"plant_state": s, "pos": list(p), "count": n}
            for (s, p), n in sorted(state_pos.items(), key=lambda z: (-z[1], z[0]))
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    rows = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        agent = resolve_agent(AGENT)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([agent, "starter"])
        rows.extend(analyze(env.toJSON(), int(seed), source))
    summary = {
        "development": summarize([r for r in rows if r["source"] == "development"]),
        "live_meta": summarize([r for r in rows if r["source"] == "live_meta"]),
        "all": summarize(rows),
    }
    # This is a diagnostic routing decision, not a performance gate.
    gate = {
        "simple_substitution_low_conflict": bool(
            summary["development"]["compatible_slots"] > 0
            and summary["live_meta"]["compatible_slots"] > 0
            and summary["all"]["replant_within_96"] <= 0.25 * summary["all"]["compatible_slots"]
        )
    }
    payload = {
        "schema_version": "tomato-slot-succession-v1",
        "window": [START, END],
        "minimum_tomato_delay": MIN_TOMATO_DELAY,
        "summary": summary,
        "gate": gate,
        "rows": rows,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"summary": summary, "gate": gate}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
