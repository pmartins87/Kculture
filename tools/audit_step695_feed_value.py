"""KEXP-027: audit mechanically useless FEED actions at executable step 695.

Frozen R4B is run unchanged vs starter on development and exploratory-live-meta
environmental seeds.  We inspect only FEED intents at step 695, the final action
before the last animal production refresh.  At this exact step there is no later
same-day unit action, so retaining a wheat cannot block a later pickup/harvest.
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

ANIMALS = {
    "GOOSE": {"first_yield_day": 4, "interval": 1, "max_held": 4},
    "COW": {"first_yield_day": 8, "interval": 2, "max_held": 6},
    "SHEEP": {"first_yield_day": 6, "interval": 3, "max_held": 6},
}
STEP = 695
FINAL_REFRESH_NEXT_DAY = 29
SHED_CAPACITY = 100


def live_seeds(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int): out.append(v["seed"])
            for child in v.values(): walk(child)
        elif isinstance(v, list):
            for child in v: walk(child)
    walk(payload)
    return list(dict.fromkeys(out))


def g(obj, key, default=None):
    try: return obj.get(key, default)
    except AttributeError:
        try: return obj[key]
        except Exception: return default


def inv_units(inv):
    if not isinstance(inv, dict): return 0
    total = 0
    for v in inv.values():
        try: total += max(0, int(v or 0))
        except (TypeError, ValueError): pass
    return total


def inspect_episode(replay, seed, source):
    entry = replay["steps"][STEP][0]
    obs = entry.get("observation") or {}
    action = entry.get("action") or {}
    farms = obs.get("farms") or []
    farm = farms[0] if farms else {}
    positions = [farm.get("farmer") or [0, 0], *list(farm.get("hands") or [])]
    acts = [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]
    private = obs.get("private") or {}
    inventories = list(private.get("inventories") or [])
    shed = private.get("shed") or {}
    total_before_drop = inv_units(shed) + sum(inv_units(x) for x in inventories)
    rows = []

    tiles = farm.get("tiles") or []
    for idx, act in enumerate(acts):
        if not (isinstance(act, list) and act and act[0] == "FEED"):
            continue
        pos = positions[idx] if idx < len(positions) else None
        tile = None
        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
            x, y = int(pos[0]), int(pos[1])
            if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
                tile = tiles[y][x]
        animal = g(tile or {}, "animal")
        spec = ANIMALS.get(animal)
        placed_day = g(tile or {}, "placed_day")
        try: consecutive = int(g(tile or {}, "consecutive_unfed", 0) or 0)
        except (TypeError, ValueError): consecutive = 0
        try: pending = max(0, int(g(tile or {}, "pending_care_bonus", 0) or 0))
        except (TypeError, ValueError): pending = 0
        try: held = max(0, int(g(tile or {}, "yield_units", 0) or 0))
        except (TypeError, ValueError): held = 0
        due = False
        effective_bonus = 0
        if spec is not None and isinstance(placed_day, int):
            dsf = FINAL_REFRESH_NEXT_DAY - placed_day - spec["first_yield_day"]
            due = dsf >= 0 and dsf % spec["interval"] == 0
            if due and pending > 0:
                without_feed = min(spec["max_held"], held + 1)
                with_feed = min(spec["max_held"], held + 1 + pending)
                effective_bonus = max(0, with_feed - without_feed)

        actor_inv = inventories[idx] if idx < len(inventories) else {}
        try: actor_wheat = max(0, int((actor_inv or {}).get("WHEAT", 0) or 0))
        except (TypeError, ValueError): actor_wheat = 0

        # Skipping FEED is terminal-production neutral only when the animal
        # cannot escape and feeding unlocks no realizable pending bonus.
        production_neutral = consecutive == 0 and effective_bonus == 0
        # If all current shed+carried inventory plus the retained wheat fits,
        # the saved unit survives the immediately following end-of-day drop.
        # total_before_drop already includes that wheat because this is pre-action.
        drop_safe = total_before_drop <= SHED_CAPACITY
        removable = production_neutral and drop_safe and actor_wheat > 0 and spec is not None
        rows.append({
            "actor_index": idx,
            "animal": animal,
            "position": pos,
            "consecutive_unfed": consecutive,
            "pending_care_bonus": pending,
            "yield_units": held,
            "production_due": due,
            "effective_pending_bonus_if_fed": effective_bonus,
            "actor_wheat": actor_wheat,
            "shed_plus_inventories_pre_action": total_before_drop,
            "production_neutral": production_neutral,
            "drop_safe": drop_safe,
            "mechanically_removable": removable,
        })

    return {"seed": int(seed), "source": source, "feed_intents": len(rows), "rows": rows}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    episodes = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        candidate = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": int(seed)}, debug=True)
        env.run([candidate, "starter"])
        episodes.append(inspect_episode(env.toJSON(), int(seed), source))

    summary = {}
    for source in ("development", "live_meta", "all"):
        ee = episodes if source == "all" else [e for e in episodes if e["source"] == source]
        rows = [r for e in ee for r in e["rows"]]
        removable = [r for r in rows if r["mechanically_removable"]]
        summary[source] = {
            "episodes": len(ee),
            "episodes_with_feed_step695": sum(e["feed_intents"] > 0 for e in ee),
            "feed_intents_step695": len(rows),
            "mechanically_removable_feed_intents": len(removable),
            "episodes_with_removable_feed": sum(any(r["mechanically_removable"] for r in e["rows"]) for e in ee),
            "removable_by_animal": dict(Counter(r["animal"] for r in removable)),
            "blocked_survival": sum(r["consecutive_unfed"] > 0 for r in rows),
            "blocked_effective_bonus": sum(r["effective_pending_bonus_if_fed"] > 0 for r in rows),
            "blocked_drop_capacity": sum(not r["drop_safe"] for r in rows),
        }

    payload = {"schema_version": "step695-feed-value-v1", "summary": summary, "episodes": episodes}
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__": main()
