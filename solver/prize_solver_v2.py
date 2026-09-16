from __future__ import annotations

"""Prize Solver V2 — top-informed bootstrap + adaptive solver.

V2 fixes the V1 cashflow failure using a robust pattern shared by the frozen top-agent
replays: mixed early livestock, cheap labor, melon + wheat seed production, and rapid
fertilizer monetization. The prior controls only bootstrap; later strategy remains
state-adaptive and is intended to be replaced by exact-rollout/value decisions.
"""

from typing import List

from .prize_solver_v0 import (
    ANIMALS,
    CROP_SLOTS,
    CROPS,
    Plan,
    _all_inventory_count,
    _count,
    _farm,
    _fval,
    _get,
    _iter_tiles,
    _ival,
    _private,
    _step,
    _tile,
)
from .prize_solver_v1 import PrizeSolverV1


# All post-bootstrap choices retain the two-sheep early commitment, so the monotone
# planner can still choose among materially different cow/crop scales.
PLANS_V2 = (
    Plan("COW_HEAVY_S2", 8, 2, 0, 4, 1, 0, 9, 2, 350),
    Plan("COW_MELON_S2", 6, 2, 0, 8, 1, 0, 9, 2, 300),
    Plan("MIXED_HEDGE_S2", 7, 2, 0, 5, 1, 0, 9, 2, 350),
    Plan("CROP_PRESSURE_S2", 4, 2, 0, 10, 2, 0, 8, 2, 250),
    Plan("CONSERVE_S2", 2, 2, 0, 6, 0, 0, 5, 1, 100),
)
BOOTSTRAP = PLANS_V2[-1]


class PrizeSolverV2(PrizeSolverV1):
    def _select_plan(self, obs, config):
        own = _farm(obs)
        animals, crops = self._existing_assets(own)
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns

        # The first four days are a deliberately narrow prior taken from the common
        # top-agent opening. This avoids asking an untrained value model to solve the
        # hardest cold-start cashflow problem.
        if day < 4:
            return BOOTSTRAP

        feasible = []
        for p in PLANS_V2:
            if p.cows < animals["COW"] or p.sheep < animals["SHEEP"] or p.geese < animals["GOOSE"]:
                continue
            if p.melons < min(crops["MELON"], 12) or p.strawberries < min(crops["STRAWBERRY"], 4) or p.tomatoes < min(crops["TOMATO"], 4):
                continue
            feasible.append(p)
        if not feasible:
            feasible = list(PLANS_V2)

        scored = [(self.value.score_plan(obs, config, p, self.opp), p) for p in feasible]
        scored.sort(key=lambda row: (row[0], row[1].name), reverse=True)
        chosen = scored[0][1]
        if day >= 24:
            chosen = Plan(
                "TERMINAL",
                animals["COW"], animals["SHEEP"], animals["GOOSE"],
                0, 0, 0, 5,
                len(_get(own, "unlocked_quadrants", []) or []),
                0,
            )
        return chosen

    def _wheat_target(self, obs, plan):
        farm = _farm(obs)
        animals, _ = self._existing_assets(farm)
        live = sum(animals.values())
        # Top replays typically bought 7–14 wheat seeds on day 0. Keep enough wheat
        # tiles to become feed-self-sufficient as livestock grows.
        return max(6, min(12, 2 * max(2, live)))

    def _desired_crop_slots(self, farm, plan):
        desired = []
        primary = (
            ["MELON"] * plan.melons
            + ["STRAWBERRY"] * plan.strawberries
            + ["TOMATO"] * plan.tomatoes
        )
        used = set()
        for pos, crop in zip(CROP_SLOTS, primary):
            if self._unlocked(farm, pos):
                desired.append((pos, crop))
                used.add(pos)

        # Fill remaining crop slots with wheat. Feed production is part of the plan,
        # not an emergency market purchase after livestock is already starving.
        target_wheat = max(6, min(12, 2 * max(2, plan.cows + plan.sheep + plan.geese)))
        existing_wheat = sum(
            1 for _, t in _iter_tiles(farm)
            if isinstance(t, dict) and _get(t, "kind", None) == "PLANT" and _get(t, "crop", None) == "WHEAT"
        )
        needed_slots = max(0, target_wheat - existing_wheat)
        for pos in CROP_SLOTS:
            if needed_slots <= 0:
                break
            if pos in used or not self._unlocked(farm, pos):
                continue
            tile = _tile(farm, pos)
            if tile is None:
                desired.append((pos, "WHEAT"))
                used.add(pos)
                needed_slots -= 1
        return desired

    def _market_orders(self, obs, config, plan: Plan):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        seeds = _get(private, "seeds", {}) or {}
        money = _fval(_get(farm, "money", 0.0))
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        day = step // turns
        hour = step % turns
        remaining = ep - 1 - step
        orders: List[List] = []

        # Revenue/cashflow first. Fertilizer is a daily livestock by-product; keep a
        # small working reserve for crop fertilization and monetize the rest promptly.
        fert = _count(shed, "FERTILIZER")
        fert_reserve = 3 if remaining > 96 else 0
        if fert > fert_reserve:
            orders.append(["SELL", "FERTILIZER", fert - fert_reserve])

        for product in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"):
            qty = _count(shed, product)
            if qty <= 0:
                continue
            pressure = self.opp.product_pressure(product)
            if remaining <= 12 or hour == 1 or pressure >= 8.0:
                orders.append(["SELL", product, qty])

        if remaining <= 48:
            wheat = _count(shed, "WHEAT")
            if wheat:
                orders.append(["SELL", "WHEAT", wheat])
            return orders[:10]

        # Affordable incremental livestock. Bootstrap target is exactly 2C+2S.
        reserve = float(plan.cash_reserve)
        budget = max(0.0, money - reserve)
        desired_animals = {"COW": plan.cows, "SHEEP": plan.sheep, "GOOSE": plan.geese}
        for animal in ("COW", "SHEEP", "GOOSE"):
            target = desired_animals[animal]
            missing = max(0, int(target) - self._count_owned(obs, animal))
            cost = float(ANIMALS[animal]["buy"])
            affordable = int(budget // cost)
            per_turn_cap = 2 if day < 4 else 3
            buy = min(missing, affordable, per_turn_cap)
            if buy > 0:
                orders.append(["BUY_ANIMAL", animal, buy])
                budget -= buy * cost

        # Crop seeds: melon for high-value output; wheat for feed independence.
        crop_targets = {
            "MELON": plan.melons,
            "STRAWBERRY": plan.strawberries,
            "TOMATO": plan.tomatoes,
        }
        for crop, target in crop_targets.items():
            existing = self._crop_count(farm, crop)
            seed_qty = _count(seeds, crop)
            need = max(0, int(target) - existing - seed_qty)
            unit = float(CROPS[crop]["seed"])
            affordable = int(budget // unit)
            buy = min(need, affordable, 6 if day < 4 else 8)
            if buy > 0:
                orders.append(["BUY_SEED", crop, buy])
                budget -= buy * unit

        wheat_tiles = self._crop_count(farm, "WHEAT")
        wheat_seed = _count(seeds, "WHEAT")
        wheat_target = max(6, min(12, 2 * max(2, plan.cows + plan.sheep + plan.geese)))
        wheat_seed_need = max(0, wheat_target - wheat_tiles - wheat_seed)
        if wheat_seed_need > 0:
            affordable = int(budget // 10.0)
            buy = min(wheat_seed_need, affordable, 10)
            if buy > 0:
                orders.append(["BUY_SEED", "WHEAT", buy])
                budget -= buy * 10.0

        # Bridge feed is survival spending and may consume the nominal reserve. Buy
        # only enough market wheat to cover the gap until planted wheat can begin yield.
        live_animals, _ = self._existing_assets(farm)
        live_n = sum(live_animals.values())
        wheat_total = _count(shed, "WHEAT") + _all_inventory_count(private, "WHEAT")
        bridge_target = max(0, min(8, live_n * 2))
        bridge_need = max(0, bridge_target - wheat_total)
        wheat_price = max(1.0, _fval(_get(prices, "WHEAT", 25.0), 25.0))
        # Survival feed can use all current cash except a tiny safety floor.
        survival_budget = max(0.0, money - 40.0)
        affordable_bridge = int(survival_budget // wheat_price)
        buy_bridge = min(bridge_need, affordable_bridge)
        if buy_bridge > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", buy_bridge])

        # Labor: top-agent day-0 median is five. Later scale with deployed workload.
        productive = self._productive_assets(farm)
        if day < 2:
            desired_hires = min(plan.hands, 5)
        elif productive < 6:
            desired_hires = min(plan.hands, 5)
        elif productive < 10:
            desired_hires = min(plan.hands, 7)
        else:
            desired_hires = min(plan.hands, 9)
        hires_today = max(0, _ival(_get(farm, "hires_today", 0)))
        fib = [1, 1]
        while len(fib) < 16:
            fib.append(fib[-1] + fib[-2])
        # Hiring costs are tiny at this scale; ensure market cap leaves room for them.
        while hires_today < desired_hires and len(orders) < 10:
            cost = fib[hires_today]
            if money < cost + 25:
                break
            orders.append(["HIRE"])
            hires_today += 1

        # Expand only when space, not aspiration, is the bottleneck.
        unlocked = len(_get(farm, "unlocked_quadrants", []) or [])
        used, available = self._occupied_unlocked(farm)
        density = used / float(max(1, available))
        land_prices = {1: 1000.0, 2: 2000.0, 3: 4000.0}
        land_cost = land_prices.get(unlocked, 999999.0)
        if unlocked < plan.lands and density >= 0.76 and money >= land_cost + 200 and day >= 4 and len(orders) < 10:
            orders.append(["BUY_LAND"])

        return orders[:10]

    def _tasks(self, obs, config, plan: Plan):
        tasks = super()._tasks(obs, config, plan)
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns

        live_animals, _ = self._existing_assets(farm)
        live_n = sum(live_animals.values())
        wheat_available = _count(shed, "WHEAT") + _all_inventory_count(private, "WHEAT")
        urgent_feed_supply = live_n > 0 and wheat_available < max(2, live_n * 2)

        # V0 waits for one-time crops to max yield. For wheat that can starve the
        # livestock bootstrap. Add an early-harvest task as soon as wheat is legally
        # harvestable when feed runway is short.
        if urgent_feed_supply:
            existing_keys = {(t.op, t.pos, t.tag) for t in tasks}
            for pos, tile in _iter_tiles(farm):
                if not isinstance(tile, dict):
                    continue
                if _get(tile, "kind", None) != "PLANT" or _get(tile, "crop", None) != "WHEAT":
                    continue
                planted = _ival(_get(tile, "planted_day", day), day)
                age = max(0, day - planted)
                yld = max(0, _ival(_get(tile, "yield_units", 0)))
                if age >= CROPS["WHEAT"]["first"] and yld > 0:
                    from .prize_solver_v0 import Task
                    key = ("HARVEST", pos, "feed_wheat_harvest")
                    if key not in existing_keys:
                        tasks.append(Task(118, "HARVEST", pos, tag="feed_wheat_harvest"))
        return tasks


_SOLVER = PrizeSolverV2()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
