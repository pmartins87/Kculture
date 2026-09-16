from __future__ import annotations

"""CR086 latent-supply estimator extracted as a reusable Prize Solver sensor.

Provenance: exact mechanics of the frozen CR086 hosted candidate. This module keeps
only the conserved-mass opponent inventory estimator; it does not carry CR086's replay
route, decision tree or market-action policy.
"""

import copy

PRIMARY = ("CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")
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
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
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
        demand += 1
    return demand


def units_on_tile(farm: dict, x: int, y: int) -> int:
    positions = [farm.get("farmer", [-999, -999]), *farm.get("hands", [])]
    return sum(1 for p in positions if tuple(p) == (x, y))


def point_creation(pre: dict, post: dict, item: str, step: int) -> int:
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
                                water = int(b.get("consecutive_unwatered", 99)) == 0 if eod else bool(b.get("watered_today", False))
                        if water:
                            age = day - int(a.get("planted_day", 0))
                            window_start = (cd["maxday"] + 1) // 2
                            if window_start <= age <= cd["maxday"]:
                                fert_until = b.get("fertilized_until_day", -1) if isinstance(b, dict) else a.get("fertilized_until_day", -1)
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
                        fert_until = b.get("fertilized_until_day", -1) if isinstance(b, dict) else a.get("fertilized_until_day", -1)
                        bonus = 2 if int(fert_until) >= day else 1
                        if isinstance(b, dict) and b.get("kind") == "PLANT" and b.get("crop") == item:
                            water = int(b.get("consecutive_unwatered", 99)) == 0 if eod else bool(b.get("watered_today", False))
                            if can_gain and water:
                                total += max(0, min(cd["max"], pre_y + bonus) - pre_y)
                        elif can_gain and units_on_tile(f0, x, y) >= 2:
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


def snapshot(obs):
    return {
        "farms": copy.deepcopy(obs.get("farms") or []),
        "market": copy.deepcopy(obs.get("market") or {}),
        "town": copy.deepcopy(obs.get("town") or {}),
        "private": copy.deepcopy(obs.get("private") or {}),
    }


class LatentSupplyModel:
    """Conserved-mass estimate of opponent hidden primary-product inventory."""

    def __init__(self):
        self.prev = None
        self.point_mass = None
        self.upper_mass = None
        self.ever_floor = {x: False for x in PRIMARY}
        self.point = {x: 0 for x in PRIMARY}
        self.upper = {x: 0 for x in PRIMARY}
        self.last_step = -1

    def reset(self):
        self.__init__()

    def observe(self, obs: dict, step: int):
        step = int(step)
        if self.last_step >= 0 and step <= self.last_step:
            self.reset()
        self.last_step = step

        if self.prev is None:
            self.point_mass = {}
            self.upper_mass = {}
            for item in PRIMARY:
                mass = (
                    int(obs["market"]["inventory"].get(item, 0))
                    + public_yield_total(obs["farms"], item)
                    + private_total(obs.get("private") or {}, item)
                )
                self.point_mass[item] = mass
                self.upper_mass[item] = mass
            self.prev = snapshot(obs)
            return

        if step <= 0:
            self.prev = snapshot(obs)
            return

        pre = self.prev
        transition_step = step - 1
        for item in PRIMARY:
            if int((pre.get("market") or {}).get("prices", {}).get(item, 999)) <= 1 or int(obs["market"]["prices"].get(item, 999)) <= 1:
                self.ever_floor[item] = True
            demand = town_demand(pre, item, transition_step)
            self.point_mass[item] += point_creation(pre, obs, item, transition_step) - demand
            self.upper_mass[item] += upper_creation(pre, obs, item, transition_step) - demand
            known = (
                int(obs["market"]["inventory"].get(item, 0))
                + private_total(obs.get("private") or {}, item)
                + public_yield_total(obs["farms"], item)
            )
            zero_loss_point = max(0, int(self.point_mass[item] - known))
            point = 0 if self.ever_floor[item] else zero_loss_point
            upper = max(point, max(0, int(self.upper_mass[item] - known)))
            self.point[item] = point
            self.upper[item] = upper
        self.prev = snapshot(obs)

    def estimate(self, item: str) -> int:
        return max(0, int(self.point.get(item, 0)))

    def upper_bound(self, item: str) -> int:
        return max(0, int(self.upper.get(item, 0)))

    def features(self):
        out = {}
        for item in PRIMARY:
            key = item.lower()
            out[f"latent_{key}_point"] = float(self.estimate(item))
            out[f"latent_{key}_upper"] = float(self.upper_bound(item))
        return out
