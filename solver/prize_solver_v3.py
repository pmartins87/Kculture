from __future__ import annotations

"""Prize Solver V3 — resource-feasible task scheduler.

V1 trace showed the executor could deadlock on urgent but impossible FEED tasks,
starving lower-priority setup work. V3 makes task generation resource-feasible and
prevents terminal-phase capex/seed spending.
"""

from collections import defaultdict
from typing import List

from .prize_solver_v0 import ANIMALS, PRODUCTS, Task, _all_inventory_count, _count, _farm, _fval, _get, _ival, _private, _step
from .prize_solver_v2 import PrizeSolverV2


class PrizeSolverV3(PrizeSolverV2):
    def _resource_feasible_tasks(self, obs, tasks):
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}

        # Current total own supply. A unit holding an item counts just like shed stock;
        # assignment may route/pick it up as needed in subsequent turns.
        quota = defaultdict(int)
        for item in ("WHEAT", "FERTILIZER", "COW", "SHEEP", "GOOSE"):
            quota[item] = _count(shed, item) + _all_inventory_count(private, item)
        seeds = _get(private, "seeds", {}) or {}
        for crop in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"):
            quota[f"SEED:{crop}"] = _count(seeds, crop)

        # Preserve priority order while capping actions by resources actually present
        # now. Market purchases made this turn are intentionally NOT assumed available.
        ordered = sorted(tasks, key=lambda t: (-t.priority, t.tag, t.pos))
        kept = []
        for task in ordered:
            key = None
            if task.op == "FEED":
                key = "WHEAT"
            elif task.op == "FERTILIZE":
                key = "FERTILIZER"
            elif task.op == "PLACE" and task.item in ANIMALS:
                key = task.item
            elif task.op == "PLANT" and task.item:
                key = f"SEED:{task.item}"

            if key is None:
                kept.append(task)
                continue
            if quota[key] <= 0:
                continue
            quota[key] -= 1
            kept.append(task)
        return kept

    def _tasks(self, obs, config, plan):
        tasks = super()._tasks(obs, config, plan)
        return self._resource_feasible_tasks(obs, tasks)

    def _terminal_orders(self, obs, config, plan):
        farm = _farm(obs)
        private = _private(obs)
        shed = _get(private, "shed", {}) or {}
        market = _get(obs, "market", {}) or {}
        prices = _get(market, "prices", {}) or {}
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        ep = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = ep - 1 - step
        orders: List[List] = []

        # Monetize output; no new animals, seeds or land in terminal mode.
        fert = _count(shed, "FERTILIZER")
        if fert:
            orders.append(["SELL", "FERTILIZER", fert])
        for product in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"):
            qty = _count(shed, product)
            if qty and (hour == 1 or remaining <= 12 or self.opp.product_pressure(product) >= 8.0):
                orders.append(["SELL", product, qty])

        # Existing animals still need feed so their final production can be harvested.
        animals, _ = self._existing_assets(farm)
        live_n = sum(animals.values())
        wheat = _count(shed, "WHEAT") + _all_inventory_count(private, "WHEAT")
        need = max(0, min(8, live_n * 2) - wheat)
        if need > 0 and remaining > 12:
            price = max(1.0, _fval(_get(prices, "WHEAT", 25.0), 25.0))
            money = _fval(_get(farm, "money", 0.0))
            buy = min(need, int(max(0.0, money - 25.0) // price))
            if buy:
                orders.append(["BUY_PRODUCT", "WHEAT", buy])
        elif remaining <= 12 and wheat:
            orders.append(["SELL", "WHEAT", wheat])

        # Cheap labor remains useful for harvesting/servicing existing assets.
        desired = min(5, max(1, live_n + 1)) if live_n else 3
        hired = max(0, _ival(_get(farm, "hires_today", 0)))
        fib = [1, 1, 2, 3, 5, 8, 13, 21]
        money = _fval(_get(farm, "money", 0.0))
        while hired < desired and len(orders) < 10:
            cost = fib[min(hired, len(fib) - 1)]
            if money < cost + 10:
                break
            orders.append(["HIRE"])
            hired += 1
        return orders[:10]

    def _market_orders(self, obs, config, plan):
        if plan.name == "TERMINAL":
            return self._terminal_orders(obs, config, plan)
        return super()._market_orders(obs, config, plan)


_SOLVER = PrizeSolverV3()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
