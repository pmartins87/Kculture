"""FP001 H10 — compact zero-lineage COW scale scheduler.

Purpose: test whether the proven COW3/H0 primitive scales to 4-6 cows when we
remove obvious scheduler waste.  No replay-derived routes are used.

Key mechanics-derived changes versus B2:
- bulk PICKUP of all purchased cows during setup;
- contiguous NW snake layout, completed inside day 0 for <=6 cows;
- no routine HIRE;
- fertilizer collected daily;
- survival FEED only when consecutive_unfed >= 1;
- milk HARVEST can be batched up to max_held instead of harvesting each unit;
- milk sales use the already-proven post-town-pulse timing (hour 1).
"""
from __future__ import annotations

ANIMAL = "COW"
PRODUCT = "MILK"
STRUCTURE = "PASTURE"
BUILD_OP = "BUILD_PASTURE"

# Contiguous path in the default unlocked NW quadrant. First tile is also shed access.
TARGET_POSITIONS = (
    (4, 4),
    (3, 4),
    (2, 4),
    (1, 4),
    (1, 3),
    (2, 3),
)
SHED_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))


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


def _farm(obs):
    player = max(0, _ival(_get(obs, "player", 0)))
    farms = _get(obs, "farms", []) or []
    return farms[player] if player < len(farms) else {}


def _step(obs, config):
    raw = _get(obs, "step", None)
    if raw is not None:
        return max(0, _ival(raw))
    turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
    return max(0, _ival(_get(obs, "day", 0))) * turns + max(0, _ival(_get(obs, "hour", 0)))


def _tile(farm, pos):
    x, y = pos
    tiles = _get(farm, "tiles", []) or []
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def _dist(a, b):
    return abs(_ival(a[0]) - _ival(b[0])) + abs(_ival(a[1]) - _ival(b[1]))


def _move_toward(pos, target):
    x, y = _ival(pos[0]), _ival(pos[1])
    tx, ty = _ival(target[0]), _ival(target[1])
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _is_shed(pos):
    return tuple(pos) in SHED_ACCESS


def _nearest_shed(pos):
    return min(SHED_ACCESS, key=lambda p: _dist(pos, p))


def _count(d, key):
    return max(0, _ival(_get(d, key, 0)))


def make_agent(n_cows=6, harvest_threshold=6):
    n_cows = int(n_cows)
    harvest_threshold = max(1, min(6, int(harvest_threshold)))
    if not (1 <= n_cows <= len(TARGET_POSITIONS)):
        raise ValueError(n_cows)
    targets = TARGET_POSITIONS[:n_cows]

    def agent(obs, config=None):
        config = config or {}
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        invs = list(_get(private, "inventories", []) or [])
        inv = invs[0] if invs else {}
        farmer = tuple(_get(farm, "farmer", [4, 4]) or [4, 4])

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = episode_steps - 1 - step
        day = step // turns

        action = {"farmer": ["PASS"], "hands": [], "market": []}
        market = []

        # Liquidate shed output. MILK waits one step after the daily center pulse.
        fert = _count(shed, "FERTILIZER")
        if fert:
            market.append(["SELL", "FERTILIZER", fert])
        milk = _count(shed, PRODUCT)
        if milk and (hour == 1 or remaining <= 8):
            market.append(["SELL", PRODUCT, milk])

        # Count purchased/placed/in-transit cows to prevent duplicate buys.
        placed = 0
        for pos in targets:
            t = _tile(farm, pos)
            if isinstance(t, dict) and _get(t, "animal", None) == ANIMAL:
                placed += 1
        owned = placed + _count(shed, ANIMAL) + _count(inv, ANIMAL)
        missing = max(0, n_cows - owned)
        if missing:
            market.append(["BUY_ANIMAL", ANIMAL, missing])

        # Maintain enough WHEAT for several feed waves. Market processing will
        # naturally stop at affordability; later fertilizer/milk income refills it.
        wheat_total = _count(shed, "WHEAT") + _count(inv, "WHEAT")
        wheat_floor = max(n_cows, 2 * n_cows)
        wheat_target = max(3 * n_cows, wheat_floor)
        if wheat_total < wheat_floor and remaining > turns:
            market.append(["BUY_PRODUCT", "WHEAT", wheat_target - wheat_total])

        # ---------------- Setup: bulk-carry cows along a contiguous path. ----------------
        if placed < n_cows:
            # If all not-yet-placed purchased cows are still in shed, pick all up at once.
            carried = _count(inv, ANIMAL)
            shed_cows = _count(shed, ANIMAL)
            if carried == 0 and shed_cows > 0:
                if _is_shed(farmer):
                    action["farmer"] = ["PICKUP", ANIMAL, shed_cows]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                action["market"] = market[:10]
                return action

            # First incomplete target in path order.
            target = None
            target_tile = None
            for pos in targets:
                t = _tile(farm, pos)
                if not (isinstance(t, dict) and _get(t, "animal", None) == ANIMAL):
                    target, target_tile = pos, t
                    break

            if target is not None:
                if farmer != tuple(target):
                    action["farmer"] = _move_toward(farmer, target)
                elif target_tile is None:
                    action["farmer"] = [BUILD_OP]
                elif isinstance(target_tile, dict) and _get(target_tile, "kind", None) == STRUCTURE and _get(target_tile, "animal", None) is None:
                    if _count(inv, ANIMAL) > 0:
                        action["farmer"] = ["PLACE", ANIMAL]
                elif isinstance(target_tile, dict) and _get(target_tile, "animal", None) is None:
                    action["farmer"] = ["DIG"]
                action["market"] = market[:10]
                return action

        cows = []
        for pos in targets:
            t = _tile(farm, pos)
            if isinstance(t, dict) and _get(t, "animal", None) == ANIMAL:
                cows.append((pos, t))

        # Terminal: harvest any milk early enough to reach shed via automatic EOD drop
        # and sell before final reward. Never sacrifice animal survival first.
        terminal_harvest = remaining <= 2 * turns

        # Build current task set. Fertilizer is non-storable on-animal, so collect
        # has high value. Milk can wait up to max_held=6 before one batched HARVEST.
        urgent_feed = [(pos, t) for pos, t in cows if _ival(_get(t, "consecutive_unfed", 0)) >= 1 and not bool(_get(t, "fed_today", False))]

        # Need wheat in main inventory before taking an urgent FEED route.
        if urgent_feed and _count(inv, "WHEAT") <= 0:
            if _count(shed, "WHEAT") > 0:
                if _is_shed(farmer):
                    take = min(max(n_cows, len(urgent_feed)), _count(shed, "WHEAT"))
                    action["farmer"] = ["PICKUP", "WHEAT", take]
                else:
                    action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                action["market"] = market[:10]
                return action

        tasks = []
        for pos, t in cows:
            if _ival(_get(t, "consecutive_unfed", 0)) >= 1 and not bool(_get(t, "fed_today", False)):
                tasks.append((100, "FEED", pos))
            if bool(_get(t, "fertilizer_available", False)):
                tasks.append((80, "COLLECT_FERTILIZER", pos))
            yld = _ival(_get(t, "yield_units", 0))
            if yld >= harvest_threshold or (terminal_harvest and yld > 0):
                tasks.append((50, "HARVEST", pos))

        if tasks:
            # Service the current tile before moving; otherwise nearest pending task.
            here = [task for task in tasks if tuple(task[2]) == farmer]
            if here:
                priority, op, target = max(here, key=lambda x: x[0])
                if op == "FEED" and _count(inv, "WHEAT") <= 0:
                    if _is_shed(farmer) and _count(shed, "WHEAT") > 0:
                        action["farmer"] = ["PICKUP", "WHEAT", min(n_cows, _count(shed, "WHEAT"))]
                    else:
                        action["farmer"] = _move_toward(farmer, _nearest_shed(farmer))
                else:
                    action["farmer"] = [op]
            else:
                # Priority class first, then shortest travel. Urgent feed cannot be
                # delayed by fertilizer; within same class choose nearest target.
                best_priority = max(t[0] for t in tasks)
                candidates = [t for t in tasks if t[0] == best_priority]
                _, _, target = min(candidates, key=lambda t: (_dist(farmer, t[2]), targets.index(t[2])))
                action["farmer"] = _move_toward(farmer, target)

        action["market"] = market[:10]
        return action

    return agent


agent = make_agent(6, harvest_threshold=6)
