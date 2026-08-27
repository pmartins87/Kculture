"""KEXP-030: exact marginal terminal-production value of R4B FEED intents in 672..695.

Diagnostic only.  Uses exact engine mechanics and corrected replay alignment:
observation/state frame t is paired with submitted action frame t+1.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.run_episode import resolve_agent

ANIMALS = {
    "GOOSE": {"first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW": {"first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
START, END = 672, 695
FINAL_REFRESH_NEXT_DAY = 29


def live_seeds(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    found: list[int] = []
    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("seed"), int): found.append(v["seed"])
            for c in v.values(): walk(c)
        elif isinstance(v, list):
            for c in v: walk(c)
    walk(payload)
    return list(dict.fromkeys(found))


def pos_for(farm: dict, actor: int):
    if actor == 0:
        return farm.get("farmer")
    hands = farm.get("hands") or []
    return hands[actor - 1] if actor - 1 < len(hands) else None


def tile_at(farm: dict, pos):
    if not (isinstance(pos, (list, tuple)) and len(pos) == 2): return None
    try:
        x, y = int(pos[0]), int(pos[1])
        return farm["tiles"][y][x]
    except Exception:
        return None


def inv_for(private: dict, actor: int) -> dict:
    invs = private.get("inventories") or []
    return invs[actor] if actor < len(invs) and isinstance(invs[actor], dict) else {}


def action_ops(action: dict | None):
    if not isinstance(action, dict): return []
    return [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]


def feed_value(tile: dict) -> dict:
    animal = tile.get("animal")
    a = ANIMALS.get(animal)
    if not a:
        return {"valid_animal": False}
    placed = int(tile.get("placed_day", 0) or 0)
    days_since_first = FINAL_REFRESH_NEXT_DAY - placed - a["first_yield_day"]
    production_due = days_since_first >= 0 and days_since_first % a["interval"] == 0
    already_fed = bool(tile.get("fed_today", False))
    consecutive = int(tile.get("consecutive_unfed", 0) or 0)
    would_escape_if_skip = (not already_fed) and consecutive + 1 >= 2
    held = max(0, int(tile.get("yield_units", 0) or 0))
    cap = max(0, int(a["max_held"]) - held)
    pending = max(0, int(tile.get("pending_care_bonus", 0) or 0))

    # Production at final refresh occurs only once more. Base production is one.
    # An animal that survives produces base even when unfed. Feeding matters only
    # to prevent an escape before a due production or to unlock pending care bonus.
    if already_fed:
        incremental = 0
        reason = "already_fed_noop"
    elif not production_due:
        incremental = 0
        reason = "no_final_production_due"
    elif would_escape_if_skip:
        incremental = min(cap, 1 + pending)
        reason = "feed_preserves_survival_for_due_production"
    else:
        cap_after_unfed_base = max(0, cap - 1)
        incremental = min(cap_after_unfed_base, pending)
        reason = "feed_unlocks_pending_bonus" if incremental > 0 else "survives_and_no_incremental_bonus"

    return {
        "valid_animal": True,
        "animal": animal,
        "product": a["product"],
        "production_due": production_due,
        "already_fed": already_fed,
        "consecutive_unfed": consecutive,
        "would_escape_if_skip": would_escape_if_skip,
        "yield_units": held,
        "capacity": cap,
        "pending_care_bonus": pending,
        "incremental_terminal_product_units_from_feed": incremental,
        "zero_terminal_production_value": incremental == 0,
        "reason": reason,
    }


def analyze(rep: dict, seed: int, source: str) -> dict:
    rows = []
    steps = rep.get("steps") or []
    for t in range(START, min(END, len(steps) - 2) + 1):
        obs = steps[t][0].get("observation") or {}
        action = steps[t + 1][0].get("action") or {}
        farms = obs.get("farms") or []
        if not farms: continue
        farm = farms[0]
        private = obs.get("private") or {}
        for actor, op in enumerate(action_ops(action)):
            if not (isinstance(op, list) and op and op[0] == "FEED"):
                continue
            pos = pos_for(farm, actor)
            tile = tile_at(farm, pos)
            val = feed_value(tile) if isinstance(tile, dict) else {"valid_animal": False}
            inv = inv_for(private, actor)
            val.update({
                "step": t,
                "actor": actor,
                "position": pos,
                "holds_wheat": max(0, int(inv.get("WHEAT", 0) or 0)),
            })
            rows.append(val)
    valid = [r for r in rows if r.get("valid_animal")]
    zero = [r for r in valid if r.get("zero_terminal_production_value")]
    zero_with_wheat = [r for r in zero if r.get("holds_wheat", 0) > 0]
    return {
        "seed": int(seed), "source": source,
        "feed_intents": len(rows),
        "valid_animal_feed_intents": len(valid),
        "zero_value_feed_intents": len(zero),
        "zero_value_with_wheat_feed_intents": len(zero_with_wheat),
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    dev = json.loads((ROOT / "configs/seed_partitions.json").read_text(encoding="utf-8"))["development"]
    live = live_seeds(ROOT / "configs/exploratory_live_meta_seeds_20260825.json")
    episodes = []
    for seed, source in [(s, "development") for s in dev] + [(s, "live_meta") for s in live]:
        agent = resolve_agent("file:candidates/r4b_ablation_market_only.py:agent")
        env = make("kaggriculture", configuration={"episodeSteps":720,"seed":int(seed)}, debug=True)
        env.run([agent, "starter"])
        episodes.append(analyze(env.toJSON(), int(seed), source))

    summary = {}
    for source in ("development", "live_meta", "all"):
        ee = episodes if source == "all" else [e for e in episodes if e["source"] == source]
        total = sum(e["valid_animal_feed_intents"] for e in ee)
        zero = sum(e["zero_value_feed_intents"] for e in ee)
        zero_w = sum(e["zero_value_with_wheat_feed_intents"] for e in ee)
        summary[source] = {
            "episodes": len(ee),
            "episodes_with_feed": sum(e["valid_animal_feed_intents"] > 0 for e in ee),
            "episodes_with_zero_value_feed": sum(e["zero_value_feed_intents"] > 0 for e in ee),
            "episodes_with_zero_value_feed_holding_wheat": sum(e["zero_value_with_wheat_feed_intents"] > 0 for e in ee),
            "feed_intents": total,
            "zero_value_feed_intents": zero,
            "zero_value_with_wheat_feed_intents": zero_w,
            "zero_value_fraction_of_feed": zero / total if total else None,
        }
    devs, lives = summary["development"], summary["live_meta"]
    gate = {
        "eligible_for_candidate": (
            devs["episodes_with_zero_value_feed_holding_wheat"] >= 4
            and lives["episodes_with_zero_value_feed_holding_wheat"] >= 5
            and (summary["all"]["zero_value_fraction_of_feed"] or 0) >= 0.20
        ),
        "criteria": "zero-value FEED holding WHEAT in >=25% of each pool and >=20% of all valid FEED intents",
    }
    payload = {"schema_version":"late-feed-marginal-value-v1","window":[START,END],"summary":summary,"gate":gate,"episodes":episodes}
    out = ROOT / args.output; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"summary":summary,"gate":gate}, indent=2, sort_keys=True))

if __name__ == "__main__": main()
