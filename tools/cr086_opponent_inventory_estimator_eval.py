"""CR086 opponent inventory estimator feasibility evaluator.

The estimator itself uses only public state transitions, the controlled player's
own private state, and frozen public mechanics. Opponent private state is read
ONLY in ``evaluate_replay`` as an offline truth label for error metrics.

This is a discovery/evaluation tool, not a hosted agent.
"""
from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path

PRIMARY = ["CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]

CROPS = {
    "CARROT": {"first": 2, "maxday": 3, "max": 4, "ongoing": False, "interval": 0},
    "TOMATO": {"first": 8, "maxday": 8, "max": 4, "ongoing": True, "interval": 1},
    "STRAWBERRY": {"first": 10, "maxday": 10, "max": 4, "ongoing": True, "interval": 2},
    "MELON": {"first": 10, "maxday": 12, "max": 6, "ongoing": False, "interval": 0},
}

ANIMALS = {
    "GOOSE": {"first": 4, "interval": 1, "max": 4, "product": "EGG"},
    "COW": {"first": 8, "interval": 2, "max": 6, "product": "MILK"},
    "SHEEP": {"first": 6, "interval": 3, "max": 6, "product": "WOOL"},
}

SHOPS = {
    "BAKERY": ["EGG", "WHEAT"],
    "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


def private_total(private: dict, item: str) -> int:
    return int(private.get("shed", {}).get(item, 0)) + sum(
        int(inv.get(item, 0)) for inv in private.get("inventories", [])
    )


def public_yield_total(farms: list[dict], item: str) -> int:
    total = 0
    for farm in farms:
        for row in farm["tiles"]:
            for tile in row:
                if not isinstance(tile, dict):
                    continue
                if tile.get("kind") == "PLANT" and tile.get("crop") == item:
                    total += int(tile.get("yield_units", 0))
                animal = tile.get("animal")
                if animal in ANIMALS and ANIMALS[animal]["product"] == item:
                    total += int(tile.get("yield_units", 0))
    return total


def town_demand(obs: dict, item: str, step: int) -> int:
    demand = 0
    if step % 4 == 0:
        for shop in obs.get("town", {}).get("unlocked_shops", []):
            products = SHOPS.get(shop, [])
            multiplier = 2 if len(products) == 1 else 1
            if item in products:
                demand += multiplier
    if step % 24 == 0:
        # Every primary commodity is sold by the town center.
        demand += 1
    return demand


def units_on_tile(farm: dict, x: int, y: int) -> int:
    positions = [farm.get("farmer", [-999, -999]), *farm.get("hands", [])]
    return sum(1 for p in positions if tuple(p) == (x, y))


def point_creation(pre: dict, post: dict, item: str, step: int) -> int:
    """Mechanics-only point estimate of newly created public product units."""
    day = step // 24
    eod = (step + 1) % 24 == 0
    total = 0
    for fi in range(2):
        f0, f1 = pre["farms"][fi], post["farms"][fi]
        for y, row in enumerate(f0["tiles"]):
            for x, a in enumerate(row):
                b = f1["tiles"][y][x]
                if item in CROPS and isinstance(a, dict) and a.get("kind") == "PLANT" and a.get("crop") == item:
                    cd = CROPS[item]
                    pre_y = int(a.get("yield_units", 0))
                    if not cd["ongoing"]:
                        water = False
                        if isinstance(b, dict) and b.get("kind") == "PLANT" and b.get("crop") == item:
                            if not a.get("watered_today", False):
                                water = (
                                    int(b.get("consecutive_unwatered", 99)) == 0
                                    if eod
                                    else bool(b.get("watered_today", False))
                                )
                        if water:
                            age = day - int(a.get("planted_day", 0))
                            window_start = (cd["maxday"] + 1) // 2
                            if window_start <= age <= cd["maxday"]:
                                fert_until = (
                                    b.get("fertilized_until_day", -1)
                                    if isinstance(b, dict)
                                    else a.get("fertilized_until_day", -1)
                                )
                                bonus = 2 if int(fert_until) >= day else 1
                                total += max(0, min(cd["max"], pre_y + bonus) - pre_y)
                    elif eod and isinstance(b, dict) and b.get("kind") == "PLANT" and b.get("crop") == item:
                        next_day = day + 1
                        planted = int(b.get("planted_day", a.get("planted_day", 0)))
                        dsf = next_day - planted - cd["first"]
                        if dsf >= 0 and dsf % cd["interval"] == 0:
                            production_count = dsf // cd["interval"] + 1
                            if production_count <= cd["max"]:
                                watered = int(b.get("consecutive_unwatered", 99)) == 0
                                fertilized = watered and int(b.get("fertilized_until_day", -1)) >= day
                                bonus = 2 if fertilized else 1
                                post_y = int(b.get("yield_units", 0))
                                total += min(cd["max"], bonus) if post_y < pre_y else max(0, post_y - pre_y)

                if item in ("EGG", "MILK", "WOOL") and isinstance(a, dict) and a.get("animal") in ANIMALS:
                    ad = ANIMALS[a["animal"]]
                    if ad["product"] != item:
                        continue
                    if eod and isinstance(b, dict) and b.get("animal") == a.get("animal"):
                        next_day = day + 1
                        dsf = next_day - int(a.get("placed_day", 0)) - ad["first"]
                        if dsf >= 0 and dsf % ad["interval"] == 0:
                            fed = int(b.get("consecutive_unfed", 99)) == 0
                            bonus = int(a.get("pending_care_bonus", 0)) if fed else 0
                            increment = 1 + bonus
                            pre_y = int(a.get("yield_units", 0))
                            post_y = int(b.get("yield_units", 0))
                            total += min(ad["max"], increment) if post_y < pre_y else max(0, post_y - pre_y)
    return total


def upper_creation(pre: dict, post: dict, item: str, step: int) -> int:
    """Maximum mechanically possible creation consistent with public transition."""
    day = step // 24
    eod = (step + 1) % 24 == 0
    total = 0
    for fi in range(2):
        f0, f1 = pre["farms"][fi], post["farms"][fi]
        for y, row in enumerate(f0["tiles"]):
            for x, a in enumerate(row):
                b = f1["tiles"][y][x]
                if item in CROPS and isinstance(a, dict) and a.get("kind") == "PLANT" and a.get("crop") == item:
                    cd = CROPS[item]
                    pre_y = int(a.get("yield_units", 0))
                    if not cd["ongoing"]:
                        age = day - int(a.get("planted_day", 0))
                        window_start = (cd["maxday"] + 1) // 2
                        can_gain = window_start <= age <= cd["maxday"] and not bool(a.get("watered_today", False))
                        fert_until = (
                            b.get("fertilized_until_day", -1)
                            if isinstance(b, dict)
                            else a.get("fertilized_until_day", -1)
                        )
                        bonus = 2 if int(fert_until) >= day else 1
                        if isinstance(b, dict) and b.get("kind") == "PLANT" and b.get("crop") == item:
                            water = (
                                int(b.get("consecutive_unwatered", 99)) == 0
                                if eod
                                else bool(b.get("watered_today", False))
                            )
                            if can_gain and water:
                                total += max(0, min(cd["max"], pre_y + bonus) - pre_y)
                        elif can_gain and units_on_tile(f0, x, y) >= 2:
                            # A hidden WATER followed by HARVEST/DIG can make the
                            # plant disappear while still creating units this turn.
                            total += max(0, min(cd["max"], pre_y + bonus) - pre_y)
                    elif eod and isinstance(b, dict) and b.get("kind") == "PLANT" and b.get("crop") == item:
                        next_day = day + 1
                        planted = int(b.get("planted_day", a.get("planted_day", 0)))
                        dsf = next_day - planted - cd["first"]
                        if dsf >= 0 and dsf % cd["interval"] == 0:
                            production_count = dsf // cd["interval"] + 1
                            if production_count <= cd["max"]:
                                watered = int(b.get("consecutive_unwatered", 99)) == 0
                                fertilized = watered and int(b.get("fertilized_until_day", -1)) >= day
                                total += min(cd["max"], 2 if fertilized else 1)

                if item in ("EGG", "MILK", "WOOL") and isinstance(a, dict) and a.get("animal") in ANIMALS:
                    ad = ANIMALS[a["animal"]]
                    if ad["product"] != item:
                        continue
                    if eod and isinstance(b, dict) and b.get("animal") == a.get("animal"):
                        next_day = day + 1
                        dsf = next_day - int(a.get("placed_day", 0)) - ad["first"]
                        if dsf >= 0 and dsf % ad["interval"] == 0:
                            fed = int(b.get("consecutive_unfed", 99)) == 0
                            bonus = int(a.get("pending_care_bonus", 0)) if fed else 0
                            total += min(ad["max"], 1 + bonus)
    return total


def evaluate_replay(replay: dict, own: int) -> list[dict]:
    """Run legal estimator; opponent private is accessed only for truth labels."""
    opp = 1 - own
    steps = replay["steps"]
    initial = steps[0][own]["observation"]
    point_mass = {
        item: int(initial["market"]["inventory"][item])
        + public_yield_total(initial["farms"], item)
        + private_total(initial["private"], item)
        for item in PRIMARY
    }
    upper_mass = dict(point_mass)
    ever_floor = {item: False for item in PRIMARY}
    rows = []

    for step in range(len(steps) - 1):
        pre = steps[step][own]["observation"]
        post = steps[step + 1][own]["observation"]
        truth_obs = steps[step + 1][opp]["observation"]  # OFFLINE LABEL ONLY
        for item in PRIMARY:
            if int(pre["market"]["prices"][item]) <= 1 or int(post["market"]["prices"][item]) <= 1:
                ever_floor[item] = True
            demand = town_demand(pre, item, step)
            point_mass[item] += point_creation(pre, post, item, step) - demand
            upper_mass[item] += upper_creation(pre, post, item, step) - demand
            known_post = (
                int(post["market"]["inventory"][item])
                + private_total(post["private"], item)
                + public_yield_total(post["farms"], item)
            )
            zero_loss_point = max(0, point_mass[item] - known_post)
            point = 0 if ever_floor[item] else zero_loss_point
            upper = max(point, max(0, upper_mass[item] - known_post))
            truth = private_total(truth_obs["private"], item)
            rows.append(
                {
                    "step": step + 1,
                    "item": item,
                    "point": point,
                    "lower": 0,
                    "upper": upper,
                    "truth": truth,
                    "error": point - truth,
                    "floor_risk": ever_floor[item],
                }
            )
    return rows


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return float(xs[lo])
    w = pos - lo
    return float(xs[lo] * (1 - w) + xs[hi] * w)


def summarize(rows: list[dict]) -> dict:
    abs_err = [abs(float(r["error"])) for r in rows]
    errors = [float(r["error"]) for r in rows]
    coverage = [r["lower"] <= r["truth"] <= r["upper"] for r in rows]
    widths = [float(r["upper"] - r["lower"]) for r in rows]
    out = {
        "observations": len(rows),
        "mae": sum(abs_err) / len(abs_err),
        "p95_abs_error": percentile(abs_err, 0.95),
        "bias": sum(errors) / len(errors),
        "interval_coverage": sum(coverage) / len(coverage),
        "mean_interval_width": sum(widths) / len(widths),
        "median_interval_width": percentile(widths, 0.5),
    }
    for threshold in (5, 10, 25):
        correct = [((r["point"] >= threshold) == (r["truth"] >= threshold)) for r in rows]
        out[f"stock_ge_{threshold}_accuracy"] = sum(correct) / len(correct)
    per = {}
    for item in PRIMARY:
        sub = [r for r in rows if r["item"] == item]
        ae = [abs(float(r["error"])) for r in sub]
        es = [float(r["error"]) for r in sub]
        per[item] = {
            "observations": len(sub),
            "mae": sum(ae) / len(ae),
            "p95_abs_error": percentile(ae, 0.95),
            "bias": sum(es) / len(es),
            "coverage": sum(r["lower"] <= r["truth"] <= r["upper"] for r in sub) / len(sub),
        }
    out["per_commodity"] = per
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", dest="zip_path", type=Path, required=True)
    ap.add_argument("--episode-ids", required=True, help="comma-separated replay episode ids")
    ap.add_argument("--both-seats", action="store_true")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    wanted = [x.strip() for x in args.episode_ids.split(",") if x.strip()]
    rows = []
    matched = {}
    with zipfile.ZipFile(args.zip_path) as zf:
        names = zf.namelist()
        for eid in wanted:
            candidates = [n for n in names if f"episode-{eid}-replay.json" in n]
            if len(candidates) != 1:
                raise RuntimeError(f"episode {eid}: expected one replay, got {candidates}")
            member = candidates[0]
            matched[eid] = member
            replay = json.loads(zf.read(member))
            seats = (0, 1) if args.both_seats else (0,)
            for own in seats:
                for row in evaluate_replay(replay, own):
                    row["episode_id"] = eid
                    row["controlled_seat"] = own
                    rows.append(row)

    metrics = summarize(rows)
    metrics.update(
        {
            "schema_version": "cr086-opponent-inventory-estimator-v2b",
            "runtime_forbidden_features_used": False,
            "opponent_private_used_only_as_offline_label": True,
            "episodes": wanted,
            "both_seats": bool(args.both_seats),
            "matched_members": matched,
            "pass_thresholds": {
                "coverage_ge_0_95": metrics["interval_coverage"] >= 0.95,
                "mae_le_3": metrics["mae"] <= 3.0,
                "p95_le_10": metrics["p95_abs_error"] <= 10.0,
                "stock_ge_10_accuracy_ge_0_90": metrics["stock_ge_10_accuracy"] >= 0.90,
            },
        }
    )
    metrics["pass"] = all(metrics["pass_thresholds"].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
