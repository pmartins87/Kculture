from __future__ import annotations

"""Prize Solver V0.

Competition-first end-to-end adaptive Kaggriculture policy.

Design goals:
- no replay tape or future-state assumptions;
- receding-horizon strategic mode selection every in-game day;
- public-state opponent pressure model;
- pluggable state/value scorer;
- deterministic task generation + greedy multi-unit assignment;
- all decisions are derived from the current observation.

V0 is deliberately compact. The solver architecture is the product; parameters are
expected to be replaced by learned value weights and stronger opponent beliefs in
subsequent iterations.
"""

from dataclasses import dataclass
from math import exp
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


# ----------------------------- generic helpers -----------------------------


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def _ival(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _fval(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _count(d, key):
    return max(0, _ival(_get(d, key, 0)))


def _step(obs, config):
    raw = _get(obs, "step", None)
    if raw is not None:
        return max(0, _ival(raw))
    turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
    return max(0, _ival(_get(obs, "day", 0))) * turns + max(0, _ival(_get(obs, "hour", 0)))


def _player(obs):
    return max(0, _ival(_get(obs, "player", 0)))


def _farms(obs):
    return list(_get(obs, "farms", []) or [])


def _farm(obs, player=None):
    farms = _farms(obs)
    p = _player(obs) if player is None else int(player)
    return farms[p] if 0 <= p < len(farms) else {}


def _private(obs):
    return _get(obs, "private", {}) or {}


def _tile(farm, pos):
    x, y = int(pos[0]), int(pos[1])
    tiles = _get(farm, "tiles", []) or []
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def _dist(a, b):
    return abs(int(a[0]) - int(b[0])) + abs(int(a[1]) - int(b[1]))


def _move_toward(pos, target):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _iter_tiles(farm):
    tiles = _get(farm, "tiles", []) or []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            yield (x, y), tile


def _shed_access(board_size=10):
    half = int(board_size) // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def _nearest_shed(pos, board_size=10):
    return min(_shed_access(board_size), key=lambda p: _dist(pos, p))


def _is_shed(pos, board_size=10):
    return tuple(pos) in _shed_access(board_size)


def _inv_count(inv, item):
    return _count(inv or {}, item)


def _all_inventory_count(private, item):
    return sum(_inv_count(inv, item) for inv in (_get(private, "inventories", []) or []))


def _board_size(farm):
    tiles = _get(farm, "tiles", []) or []
    return len(tiles) if tiles else 10


# ------------------------------- game metadata ------------------------------

CROPS = {
    "WHEAT": {"seed": 10, "first": 2, "max_day": 4, "ongoing": False, "base": 25, "daily": 0.80},
    "CARROT": {"seed": 20, "first": 2, "max_day": 3, "ongoing": False, "base": 35, "daily": 0.75},
    "TOMATO": {"seed": 50, "first": 8, "max_day": 11, "ongoing": True, "base": 60, "daily": 0.33},
    "STRAWBERRY": {"seed": 100, "first": 10, "max_day": 16, "ongoing": True, "base": 120, "daily": 0.24},
    "MELON": {"seed": 80, "first": 10, "max_day": 10, "ongoing": False, "base": 250, "daily": 0.55},
}

ANIMALS = {
    "GOOSE": {"product": "EGG", "buy": 300, "base": 50, "daily": 1.00, "structure": "COOP", "build": "BUILD_COOP"},
    "COW": {"product": "MILK", "buy": 400, "base": 160, "daily": 0.50, "structure": "PASTURE", "build": "BUILD_PASTURE"},
    "SHEEP": {"product": "WOOL", "buy": 500, "base": 200, "daily": 0.33, "structure": "PASTURE", "build": "BUILD_PASTURE"},
}

PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")

# Stable tile order. It intentionally starts close to the shed and only spills
# into the NE quadrant after the NW quadrant is dense.
ANIMAL_SLOTS = (
    (4, 4), (3, 4), (2, 4), (1, 4), (1, 3), (2, 3), (3, 3), (4, 3),
    (4, 2), (3, 2), (2, 2), (1, 2),
    (5, 4), (6, 4), (7, 4), (8, 4), (8, 3), (7, 3), (6, 3), (5, 3),
)

CROP_SLOTS = (
    (4, 1), (3, 1), (2, 1), (1, 1), (0, 1),
    (4, 0), (3, 0), (2, 0), (1, 0), (0, 0),
    (0, 2), (0, 3), (0, 4),
    (5, 1), (6, 1), (7, 1), (8, 1), (9, 1),
    (5, 0), (6, 0), (7, 0), (8, 0), (9, 0),
    (9, 2), (9, 3), (9, 4),
)


# --------------------------- strategic/value layer --------------------------

@dataclass(frozen=True)
class Plan:
    name: str
    cows: int
    sheep: int
    geese: int
    melons: int
    strawberries: int
    tomatoes: int
    hands: int
    lands: int
    cash_reserve: int


PLANS = (
    Plan("COW_HEAVY", 10, 0, 0, 4, 1, 0, 9, 2, 700),
    Plan("COW_MELON", 7, 0, 0, 8, 1, 0, 9, 2, 650),
    Plan("MIXED_HEDGE", 7, 2, 0, 4, 1, 0, 9, 2, 700),
    Plan("CROP_PRESSURE", 5, 0, 0, 10, 2, 0, 8, 2, 600),
    Plan("CONSERVE", 4, 0, 0, 4, 0, 0, 6, 1, 1000),
)


class OpponentModel:
    """Public-state belief model.

    V0 does not pretend to recover private inventory. It estimates product pressure
    from visible production assets and unharvested output. The interface is stable so
    learned CR007/CR086-derived beliefs can replace these priors later.
    """

    def __init__(self):
        self.last_step = -1
        self.pressure = {p: 0.0 for p in PRODUCTS}
        self.asset_counts = {k: 0 for k in tuple(CROPS) + tuple(ANIMALS)}

    def reset(self):
        self.__init__()

    def observe(self, obs):
        farms = _farms(obs)
        if len(farms) < 2:
            return
        p = _player(obs)
        opp = farms[1 - p]
        pressure = {x: 0.0 for x in PRODUCTS}
        counts = {k: 0 for k in tuple(CROPS) + tuple(ANIMALS)}

        for _, tile in _iter_tiles(opp):
            if not isinstance(tile, Mapping):
                continue
            kind = str(_get(tile, "kind", ""))
            if kind == "PLANT":
                crop = str(_get(tile, "crop", ""))
                if crop in CROPS:
                    counts[crop] += 1
                    pressure[crop] += max(0.0, _fval(_get(tile, "yield_units", 0)))
                    # visible productive capacity matters even before current yield.
                    pressure[crop] += 0.8 * CROPS[crop]["daily"]
            animal = _get(tile, "animal", None)
            if animal in ANIMALS:
                counts[animal] += 1
                product = ANIMALS[animal]["product"]
                pressure[product] += max(0.0, _fval(_get(tile, "yield_units", 0)))
                pressure[product] += 1.5 * ANIMALS[animal]["daily"]

        # Smooth because a single harvest should not erase the inferred productive base.
        alpha = 0.45
        for product in PRODUCTS:
            self.pressure[product] = alpha * pressure[product] + (1.0 - alpha) * self.pressure.get(product, 0.0)
        self.asset_counts = counts
        self.last_step = _ival(_get(obs, "step", -1), -1)

    def product_pressure(self, product):
        return max(0.0, float(self.pressure.get(product, 0.0)))


class ValueModel:
    """Small pluggable value function.

    The initial coefficients are economic priors. The feature contract is designed
    for replacement by regression/NN training without touching the executor.
    """

    def __init__(self, weights: Optional[Mapping[str, float]] = None):
        self.weights = {
            "money_diff": 1.0,
            "own_land": 75.0,
            "own_hands": 8.0,
            "survival_risk": -500.0,
            "shed_value": 0.65,
            "field_value": 0.45,
            "opp_field_value": -0.20,
            "terminal_liquidity": 1.25,
        }
        if weights:
            self.weights.update({str(k): float(v) for k, v in weights.items()})

    def state_features(self, obs, config=None):
        config = config or {}
        p = _player(obs)
        own = _farm(obs, p)
        opp = _farm(obs, 1 - p)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        step = _step(obs, config)
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        remaining = max(0, ep - 1 - step)

        own_field = 0.0
        opp_field = 0.0
        survival_risk = 0.0
        for farm, sign in ((own, 1), (opp, -1)):
            val = 0.0
            for _, tile in _iter_tiles(farm):
                if not isinstance(tile, Mapping):
                    continue
                if _get(tile, "kind", None) == "PLANT":
                    crop = _get(tile, "crop", None)
                    if crop in CROPS:
                        val += CROPS[crop]["seed"] + _fval(_get(tile, "yield_units", 0)) * _fval(_get(prices, crop, CROPS[crop]["base"]))
                        if sign > 0 and _ival(_get(tile, "consecutive_unwatered", 0)) >= 1 and not bool(_get(tile, "watered_today", False)):
                            survival_risk += 1.0
                animal = _get(tile, "animal", None)
                if animal in ANIMALS:
                    product = ANIMALS[animal]["product"]
                    val += ANIMALS[animal]["buy"] + _fval(_get(tile, "yield_units", 0)) * _fval(_get(prices, product, ANIMALS[animal]["base"]))
                    if sign > 0 and _ival(_get(tile, "consecutive_unfed", 0)) >= 1 and not bool(_get(tile, "fed_today", False)):
                        survival_risk += 1.0
            if sign > 0:
                own_field = val
            else:
                opp_field = val

        shed_value = 0.0
        for product in PRODUCTS:
            if product == "FERTILIZER":
                unit = 100.0
            else:
                unit = _fval(_get(prices, product, 0.0))
            shed_value += _count(shed, product) * unit
        for animal in ANIMALS:
            shed_value += _count(shed, animal) * ANIMALS[animal]["buy"]

        money_diff = _fval(_get(own, "money", 0.0)) - _fval(_get(opp, "money", 0.0))
        unlocked = len(_get(own, "unlocked_quadrants", []) or [])
        hands = len(_get(own, "hands", []) or [])
        terminal = shed_value if remaining <= 48 else 0.0
        return {
            "money_diff": money_diff,
            "own_land": float(unlocked),
            "own_hands": float(hands),
            "survival_risk": survival_risk,
            "shed_value": shed_value,
            "field_value": own_field,
            "opp_field_value": opp_field,
            "terminal_liquidity": terminal,
        }

    def score_state(self, obs, config=None):
        feats = self.state_features(obs, config)
        return sum(float(self.weights.get(k, 0.0)) * float(v) for k, v in feats.items())

    def score_plan(self, obs, config, plan: Plan, opp: OpponentModel):
        own = _farm(obs)
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        money = _fval(_get(own, "money", 0.0))
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        days_left = max(0.25, (ep - 1 - step) / float(turns))

        def product_price(product, fallback):
            return max(1.0, _fval(_get(prices, product, fallback), fallback))

        # Productive value per remaining day. Pressure discount is intentionally
        # bounded; it influences product choice without pretending to know private stock.
        milk = product_price("MILK", 160)
        wool = product_price("WOOL", 200)
        egg = product_price("EGG", 50)
        melon = product_price("MELON", 250)
        straw = product_price("STRAWBERRY", 120)
        tomato = product_price("TOMATO", 60)

        def pressure_discount(product):
            return 1.0 / (1.0 + 0.025 * opp.product_pressure(product))

        daily = (
            plan.cows * 0.90 * milk * pressure_discount("MILK")
            + plan.sheep * 0.52 * wool * pressure_discount("WOOL")
            + plan.geese * 1.05 * egg * pressure_discount("EGG")
            + plan.melons * 0.52 * melon * pressure_discount("MELON")
            + plan.strawberries * 0.23 * straw * pressure_discount("STRAWBERRY")
            + plan.tomatoes * 0.30 * tomato * pressure_discount("TOMATO")
        )

        capex = (
            plan.cows * 400 + plan.sheep * 500 + plan.geese * 300
            + plan.melons * 80 + plan.strawberries * 100 + plan.tomatoes * 50
        )
        # Only a fraction of capex is charged per plan decision because assets persist.
        amort = capex / max(4.0, min(12.0, days_left))
        labor_cost = max(0, plan.hands - 5) * 3.0
        reserve_penalty = max(0.0, plan.cash_reserve - money) * 0.9
        late_capex_penalty = (capex * 0.15) if days_left < 8.0 else 0.0
        land_bonus = plan.lands * 55.0
        return daily - amort - labor_cost - reserve_penalty - late_capex_penalty + land_bonus


# ------------------------------- task planner -------------------------------

@dataclass(frozen=True)
class Task:
    priority: int
    op: str
    pos: Tuple[int, int]
    item: Optional[str] = None
    amount: int = 1
    tag: str = ""


class PrizeSolver:
    def __init__(self, value_weights: Optional[Mapping[str, float]] = None):
        self.opp = OpponentModel()
        self.value = ValueModel(value_weights)
        self.last_step = -1
        self.current_plan: Optional[Plan] = None
        self.current_day = -1

    def reset(self):
        self.opp.reset()
        self.last_step = -1
        self.current_plan = None
        self.current_day = -1

    # ----------------------------- strategic layer -----------------------------

    def _existing_assets(self, farm):
        animals = {k: 0 for k in ANIMALS}
        crops = {k: 0 for k in CROPS}
        for _, tile in _iter_tiles(farm):
            if not isinstance(tile, Mapping):
                continue
            animal = _get(tile, "animal", None)
            if animal in animals:
                animals[animal] += 1
            if _get(tile, "kind", None) == "PLANT":
                crop = _get(tile, "crop", None)
                if crop in crops:
                    crops[crop] += 1
        return animals, crops

    def _select_plan(self, obs, config):
        own = _farm(obs)
        animals, crops = self._existing_assets(own)
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns

        # Do not select plans that require destroying existing animals/crops. Existing
        # physical commitments become hard lower bounds, so replanning is monotone.
        feasible = []
        for p in PLANS:
            if p.cows < animals["COW"] or p.sheep < animals["SHEEP"] or p.geese < animals["GOOSE"]:
                continue
            if p.melons < min(crops["MELON"], 12) or p.strawberries < min(crops["STRAWBERRY"], 4) or p.tomatoes < min(crops["TOMATO"], 4):
                continue
            feasible.append(p)
        if not feasible:
            feasible = list(PLANS)

        scored = [(self.value.score_plan(obs, config, p, self.opp), p) for p in feasible]
        scored.sort(key=lambda x: (x[0], x[1].name), reverse=True)
        chosen = scored[0][1]

        # Near terminal, stop new scale-up. Existing assets stay serviced.
        if day >= 24:
            chosen = Plan("TERMINAL", animals["COW"], animals["SHEEP"], animals["GOOSE"], 0, 0, 0, 5, len(_get(own, "unlocked_quadrants", []) or []), 0)
        return chosen

    # ------------------------------- market layer ------------------------------

    def _count_owned(self, obs, item):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        total = _count(shed, item) + _all_inventory_count(private, item)
        for _, tile in _iter_tiles(farm):
            if isinstance(tile, Mapping) and _get(tile, "animal", None) == item:
                total += 1
        return total

    def _crop_count(self, farm, crop):
        return sum(1 for _, t in _iter_tiles(farm) if isinstance(t, Mapping) and _get(t, "kind", None) == "PLANT" and _get(t, "crop", None) == crop)

    def _market_orders(self, obs, config, plan: Plan):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        seeds = _get(private, "seeds", {}) or {}
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        money = _fval(_get(farm, "money", 0.0))
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = ep - 1 - step
        orders: List[List] = []

        # Terminal liquidation and ordinary product sales. Sell timing is adaptive:
        # high opponent pressure -> sell earlier; otherwise prefer just after daily town pulse.
        for product in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
            qty = _count(shed, product)
            if qty <= 0:
                continue
            pressure = self.opp.product_pressure(product)
            now = remaining <= 12 or hour == 1 or pressure >= 8.0
            if now:
                orders.append(["SELL", product, qty])
        fert = _count(shed, "FERTILIZER")
        if fert > 10 or remaining <= 24:
            orders.append(["SELL", "FERTILIZER", fert])

        if remaining <= 48:
            return orders[:10]

        # Hire early each day. The first 8-9 hands are cheap and create the action
        # capacity required by the task layer. Avoid spending the full market budget.
        hires_today = max(0, _ival(_get(farm, "hires_today", 0)))
        desired_hires = max(0, plan.hands)
        if hour <= 2 and hires_today < desired_hires:
            for _ in range(min(desired_hires - hires_today, 7)):
                orders.append(["HIRE"])

        # Land expansion. Keep a reserve so scale-up does not destroy survival cash.
        unlocked = len(_get(farm, "unlocked_quadrants", []) or [])
        if unlocked < plan.lands and money >= plan.cash_reserve + (1000 if unlocked == 1 else 2000):
            orders.append(["BUY_LAND"])

        desired_animals = {"COW": plan.cows, "SHEEP": plan.sheep, "GOOSE": plan.geese}
        for animal, target in desired_animals.items():
            missing = max(0, int(target) - self._count_owned(obs, animal))
            if missing and money >= plan.cash_reserve + ANIMALS[animal]["buy"]:
                orders.append(["BUY_ANIMAL", animal, missing])

        crop_targets = {"MELON": plan.melons, "STRAWBERRY": plan.strawberries, "TOMATO": plan.tomatoes}
        for crop, target in crop_targets.items():
            existing = self._crop_count(farm, crop)
            seed_qty = _count(seeds, crop)
            need = max(0, int(target) - existing - seed_qty)
            if need and money >= plan.cash_reserve + CROPS[crop]["seed"] * need:
                orders.append(["BUY_SEED", crop, need])

        # Wheat is operational fuel. Include all carried wheat because hands drop it at EOD.
        live_animals = sum(self._count_owned(obs, a) for a in ANIMALS)
        wheat_total = _count(shed, "WHEAT") + _all_inventory_count(private, "WHEAT")
        wheat_target = max(12, 3 * live_animals)
        if wheat_total < wheat_target and money >= plan.cash_reserve:
            orders.append(["BUY_PRODUCT", "WHEAT", wheat_target - wheat_total])

        return orders[:10]

    # ------------------------------- task layer --------------------------------

    def _unlocked(self, farm, pos):
        tile = _tile(farm, pos)
        return tile != "LOCKED"

    def _desired_animal_slots(self, farm, plan):
        desired = []
        species = ["COW"] * plan.cows + ["SHEEP"] * plan.sheep + ["GOOSE"] * plan.geese
        for pos, animal in zip(ANIMAL_SLOTS, species):
            if self._unlocked(farm, pos):
                desired.append((pos, animal))
        return desired

    def _desired_crop_slots(self, farm, plan):
        desired = []
        crops = ["MELON"] * plan.melons + ["STRAWBERRY"] * plan.strawberries + ["TOMATO"] * plan.tomatoes
        for pos, crop in zip(CROP_SLOTS, crops):
            if self._unlocked(farm, pos):
                desired.append((pos, crop))
        return desired

    def _tasks(self, obs, config, plan: Plan):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        remaining = ep - 1 - step
        tasks: List[Task] = []

        # Existing assets first: survival and output extraction.
        for pos, tile in _iter_tiles(farm):
            if not isinstance(tile, Mapping):
                continue
            kind = _get(tile, "kind", None)
            if kind == "WEED":
                tasks.append(Task(48, "DIG", pos, tag="weed"))
                continue
            if kind == "PLANT":
                crop = _get(tile, "crop", None)
                unwatered = _ival(_get(tile, "consecutive_unwatered", 0))
                watered = bool(_get(tile, "watered_today", False))
                if not watered:
                    tasks.append(Task(122 if unwatered >= 1 else 102, "WATER", pos, tag="plant_survival"))
                yld = max(0, _ival(_get(tile, "yield_units", 0)))
                planted_day = _ival(_get(tile, "planted_day", day))
                age = max(0, day - planted_day)
                meta = CROPS.get(crop)
                if meta and yld > 0:
                    if remaining <= 48 or (not meta["ongoing"] and age >= meta["max_day"]) or meta["ongoing"]:
                        tasks.append(Task(92 if remaining <= 48 else 66, "HARVEST", pos, tag=f"harvest_{crop}"))
                # Fertilizer improves the proven crop branches, but only if fertilizer
                # exists somewhere on our side; item logistics is resolved per unit.
                fert_until = _ival(_get(tile, "fertilized_until_day", -1), -1)
                if crop in {"MELON", "STRAWBERRY", "TOMATO"} and fert_until < day and (_count(shed, "FERTILIZER") + _all_inventory_count(private, "FERTILIZER")) > 0:
                    tasks.append(Task(72, "FERTILIZE", pos, item="FERTILIZER", tag=f"fert_{crop}"))

            animal = _get(tile, "animal", None)
            if animal in ANIMALS:
                unfed = _ival(_get(tile, "consecutive_unfed", 0))
                fed = bool(_get(tile, "fed_today", False))
                cared = bool(_get(tile, "cared_today", False))
                if not fed:
                    tasks.append(Task(125 if unfed >= 1 else 104, "FEED", pos, item="WHEAT", tag="animal_survival"))
                if fed and not cared:
                    tasks.append(Task(84, "CARE", pos, tag="care"))
                if bool(_get(tile, "fertilizer_available", False)):
                    tasks.append(Task(78, "COLLECT_FERTILIZER", pos, tag="collect_fert"))
                yld = max(0, _ival(_get(tile, "yield_units", 0)))
                if yld >= 4 or (remaining <= 48 and yld > 0):
                    tasks.append(Task(88 if remaining <= 48 else 70, "HARVEST", pos, tag="animal_harvest"))

        # Setup desired animal slots without ever digging a live animal.
        for pos, animal in self._desired_animal_slots(farm, plan):
            tile = _tile(farm, pos)
            meta = ANIMALS[animal]
            if tile is None:
                tasks.append(Task(64, meta["build"], pos, tag=f"build_{animal}"))
            elif isinstance(tile, Mapping):
                current_animal = _get(tile, "animal", None)
                if _get(tile, "kind", None) == meta["structure"] and current_animal is None:
                    tasks.append(Task(63, "PLACE", pos, item=animal, tag=f"place_{animal}"))

        # Setup crop slots only when empty. Existing plants are never dug to chase a plan.
        seeds = _get(private, "seeds", {}) or {}
        for pos, crop in self._desired_crop_slots(farm, plan):
            tile = _tile(farm, pos)
            if tile is None and _count(seeds, crop) > 0:
                tasks.append(Task(60, "PLANT", pos, item=crop, tag=f"plant_{crop}"))

        return tasks

    def _unit_inventories(self, obs):
        private = _private(obs)
        invs = list(_get(private, "inventories", []) or [])
        return [inv or {} for inv in invs]

    def _item_available(self, obs, item):
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        return _count(shed, item) + _all_inventory_count(private, item)

    def _action_for_task(self, obs, farm, pos, inv, task: Task, reserved_pickups: MutableMapping[str, int]):
        board = _board_size(farm)
        if tuple(pos) == tuple(task.pos):
            if task.op == "PLACE":
                if _inv_count(inv, task.item) > 0:
                    return ["PLACE", task.item]
            elif task.op == "FERTILIZE":
                if _inv_count(inv, "FERTILIZER") > 0:
                    return ["FERTILIZE"]
            elif task.op == "FEED":
                if _inv_count(inv, "WHEAT") > 0:
                    return ["FEED"]
            else:
                return [task.op]

        # Required item missing: acquire it from shed. Market purchases become visible
        # in later turns; no same-turn assumptions are made.
        required = task.item if task.op in {"PLACE", "FERTILIZE", "FEED"} else None
        if task.op == "FEED":
            required = "WHEAT"
        if required and _inv_count(inv, required) <= 0:
            private = _private(obs)
            shed = _get(private, "shed", {}) or {}
            available = max(0, _count(shed, required) - int(reserved_pickups.get(required, 0)))
            if available > 0:
                if _is_shed(pos, board):
                    take = min(3 if required == "WHEAT" else 1, available)
                    reserved_pickups[required] = int(reserved_pickups.get(required, 0)) + take
                    return ["PICKUP", required, take]
                return _move_toward(pos, _nearest_shed(pos, board))
            return ["PASS"]

        return _move_toward(pos, task.pos)

    def _assign_units(self, obs, config, plan: Plan):
        farm = _farm(obs)
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])
        hands = [tuple(p) for p in (_get(farm, "hands", []) or [])]
        units = [farmer] + hands
        invs = self._unit_inventories(obs)
        while len(invs) < len(units):
            invs.append({})

        tasks = self._tasks(obs, config, plan)
        # Deterministic priority + travel ordering. A target/op pair is reserved once.
        remaining = list(tasks)
        actions: List[List] = []
        reserved_pickups: Dict[str, int] = {}

        for idx, pos in enumerate(units):
            if not remaining:
                actions.append(["PASS"])
                continue
            # If a high-priority task is on the current tile, execute it first.
            here = [t for t in remaining if tuple(t.pos) == pos]
            if here:
                task = max(here, key=lambda t: (t.priority, t.tag))
            else:
                best_priority = max(t.priority for t in remaining)
                band = [t for t in remaining if t.priority >= best_priority - 8]
                task = min(band, key=lambda t: (_dist(pos, t.pos), -t.priority, t.tag, t.pos))
            act = self._action_for_task(obs, farm, pos, invs[idx], task, reserved_pickups)
            actions.append(act)
            # Reserve actual task unless this unit is merely acquiring an item. This
            # prevents every worker from walking to the same plant/animal.
            if act and act[0] not in {"PICKUP", "PASS"}:
                try:
                    remaining.remove(task)
                except ValueError:
                    pass

        return actions[0], actions[1:]

    # --------------------------------- public ---------------------------------

    def act(self, obs, config=None):
        config = config or {}
        step = _step(obs, config)
        if self.last_step >= 0 and step <= self.last_step:
            self.reset()
        self.last_step = step
        self.opp.observe(obs)

        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns
        if self.current_plan is None or day != self.current_day:
            self.current_plan = self._select_plan(obs, config)
            self.current_day = day
        plan = self.current_plan

        farmer_action, hand_actions = self._assign_units(obs, config, plan)
        market_orders = self._market_orders(obs, config, plan)
        return {
            "farmer": farmer_action,
            "hands": hand_actions,
            "market": market_orders,
        }


_SOLVER = PrizeSolver()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
