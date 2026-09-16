from __future__ import annotations

"""Prize Solver V1: V0 architecture with budget-aware bootstrap and scaling."""

from typing import List

from .prize_solver_v0 import (
    ANIMALS,
    CROPS,
    PRODUCTS,
    Plan,
    PrizeSolver,
    _all_inventory_count,
    _count,
    _farm,
    _fval,
    _get,
    _iter_tiles,
    _private,
    _step,
)


class PrizeSolverV1(PrizeSolver):
    """Fix V0's startup failure without changing the solver architecture.

    V0 paid for near-maximum labor before it owned enough productive assets and
    repeatedly submitted unaffordable bulk animal orders. V1 treats cash as a hard
    resource and scales labor only behind deployed productive capacity.
    """

    def _productive_assets(self, farm):
        n = 0
        for _, tile in _iter_tiles(farm):
            if not isinstance(tile, dict):
                continue
            if _get(tile, "kind", None) == "PLANT":
                n += 1
            if _get(tile, "animal", None) in ANIMALS:
                n += 1
        return n

    def _occupied_unlocked(self, farm):
        used = 0
        available = 0
        for _, tile in _iter_tiles(farm):
            if tile == "LOCKED":
                continue
            available += 1
            if tile is not None:
                used += 1
        return used, available

    def _market_orders(self, obs, config, plan: Plan):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        seeds = _get(private, "seeds", {}) or {}
        money = _fval(_get(farm, "money", 0.0))
        step = _step(obs, config)
        turns = max(1, int(_get(config, "turnsPerDay", 24) or 24))
        ep = max(1, int(_get(config, "episodeSteps", 720) or 720))
        day = step // turns
        hour = step % turns
        remaining = ep - 1 - step
        orders: List[List] = []

        # 1) Revenue first. We preserve V0's adaptive early-sale signal.
        for product in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
            qty = _count(shed, product)
            if qty <= 0:
                continue
            pressure = self.opp.product_pressure(product)
            if remaining <= 12 or hour == 1 or pressure >= 8.0:
                orders.append(["SELL", product, qty])
        fert = _count(shed, "FERTILIZER")
        if fert > 10 or remaining <= 24:
            orders.append(["SELL", "FERTILIZER", fert])

        if remaining <= 48:
            return orders[:10]

        # Track a conservative local budget so every purchase order is intended to
        # be affordable even after earlier orders in this same market list.
        reserve = float(plan.cash_reserve)
        if day <= 2:
            reserve = max(reserve, 650.0)
        budget = max(0.0, money - reserve)

        # 2) Productive assets in affordable chunks. No more all-or-nothing COW10.
        desired_animals = {"COW": plan.cows, "SHEEP": plan.sheep, "GOOSE": plan.geese}
        for animal, target in desired_animals.items():
            missing = max(0, int(target) - self._count_owned(obs, animal))
            cost = float(ANIMALS[animal]["buy"])
            affordable = int(budget // cost)
            buy = min(missing, affordable, 4)
            if buy > 0:
                orders.append(["BUY_ANIMAL", animal, buy])
                budget -= buy * cost

        # 3) Seeds. Early game deliberately keeps crop capex modest until animals
        # start producing, because animals and crops compete for the same cash.
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
            cap = 4 if day < 5 else 8
            buy = min(need, affordable, cap)
            if buy > 0:
                orders.append(["BUY_SEED", crop, buy])
                budget -= buy * unit

        # 4) Wheat operational reserve sized to actually deployed/owned animals.
        live_or_owned_animals = sum(self._count_owned(obs, a) for a in ANIMALS)
        wheat_total = _count(shed, "WHEAT") + _all_inventory_count(private, "WHEAT")
        wheat_target = max(6, 2 * live_or_owned_animals)
        wheat_price = 25.0
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        wheat_price = max(1.0, _fval(_get(prices, "WHEAT", 25.0), 25.0))
        need_wheat = max(0, wheat_target - wheat_total)
        affordable_wheat = int(budget // wheat_price)
        buy_wheat = min(need_wheat, affordable_wheat)
        if buy_wheat > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", buy_wheat])
            budget -= buy_wheat * wheat_price

        # 5) Labor follows productive capacity. The exact Fibonacci hire sequence is
        # cheap later, but paying it before there are tasks is pure burn.
        productive = self._productive_assets(farm)
        owned_assets = productive + sum(_count(shed, a) + _all_inventory_count(private, a) for a in ANIMALS)
        if day == 0:
            desired_hires = min(plan.hands, 2)
        elif owned_assets < 4:
            desired_hires = min(plan.hands, 3)
        elif productive < 6:
            desired_hires = min(plan.hands, 5)
        elif productive < 10:
            desired_hires = min(plan.hands, 7)
        else:
            desired_hires = min(plan.hands, 9)

        hires_today = max(0, int(_get(farm, "hires_today", 0) or 0))
        # Cost table for the next hires: 1,1,2,3,5,8,13,21,34...
        fib = [1, 1]
        while len(fib) < 16:
            fib.append(fib[-1] + fib[-2])
        while hires_today < desired_hires and len(orders) < 10:
            hire_cost = float(fib[hires_today])
            if budget < hire_cost:
                break
            orders.append(["HIRE"])
            budget -= hire_cost
            hires_today += 1

        # 6) Expand only when current unlocked space is genuinely dense and there is
        # surplus cash after assets, feed and labor. NW can host the initial engine.
        unlocked = len(_get(farm, "unlocked_quadrants", []) or [])
        used, available = self._occupied_unlocked(farm)
        density = used / float(max(1, available))
        land_prices = {1: 1000.0, 2: 2000.0, 3: 4000.0}
        land_cost = land_prices.get(unlocked, 999999.0)
        if (
            unlocked < plan.lands
            and density >= 0.68
            and budget >= land_cost
            and day >= 4
            and len(orders) < 10
        ):
            orders.append(["BUY_LAND"])

        return orders[:10]


_SOLVER = PrizeSolverV1()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
