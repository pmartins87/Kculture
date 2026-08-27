"""R4D bounded terminal collector.

The official game has its final daily production refresh after step 695.  From
states 696..718 no WATER/FEED/CARE/PLANT/FERTILIZE can create additional product
before terminal scoring.  This wrapper therefore turns the last partial day into
a small receding-horizon collection/routing problem while retaining frozen R4B
before step 696 and retaining its market policy as a base.

At every final-day state the planner:
- sends any actor carrying inventory toward the nearest shed-access tile and
  DROPs when adjacent;
- HARVESTs positive yield under an empty actor immediately;
- otherwise assigns empty actors to distinct harvestable crop/animal tiles that
  can still be harvested AND returned to the shed by step 718;
- uses current public market price × yield as the target value and Manhattan
  travel/action cost as the bounded planning cost;
- if no feasible profitable collection job exists, preserves only already useful
  base actions (HARVEST, DROP, COLLECT_FERTILIZER and movement), otherwise PASS;
- strips terminally useless BUY_SEED/BUY_ANIMAL/BUY_PRODUCT/BUY_LAND orders but
  keeps SELL and HIRE; HIRE can still create collection labor during the day;
- recomputes frozen R4B terminal liquidation on the modified step-718 unit action
  so a same-turn DROP is included in projected shed sales.

No opponent identity, seed identity or replay identity is used.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
START, END = 696, 718
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
KEEP_IDLE_BASE = MOVES | {"HARVEST", "DROP", "COLLECT_FERTILIZER"}
SELLABLE = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4d_terminal_collector_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen R4B base: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BASE = _load_base()


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


def _inventory_total(inv):
    if not isinstance(inv, dict):
        return 0
    return sum(max(0, _ival(inv.get(k, 0))) for k in SELLABLE)


def _shed_access(board_size):
    half = board_size // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


def _manhattan(a, b):
    return abs(int(a[0]) - int(b[0])) + abs(int(a[1]) - int(b[1]))


def _nearest_shed(pos, board_size):
    access = _shed_access(board_size)
    return min(access, key=lambda q: (_manhattan(pos, q), q[1], q[0]))


def _at_shed_access(pos, board_size):
    try:
        p = (int(pos[0]), int(pos[1]))
    except Exception:
        return False
    return p in set(_shed_access(board_size))


def _move_toward(pos, target):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])
    # Deterministic x-first route. Locked/occupied tiles are passable and units
    # may share cells under the official rules.
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _actor_positions(farm):
    return [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]


def _inventories(private, n):
    invs = list(_get(private, "inventories", []) or [])
    while len(invs) < n:
        invs.append({})
    return invs[:n]


def _tile_at(farm, pos):
    if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
        return None
    try:
        x, y = int(pos[0]), int(pos[1])
        rows = _get(farm, "tiles", []) or []
        if y < 0 or y >= len(rows) or x < 0 or x >= len(rows[y]):
            return None
        tile = rows[y][x]
        return tile if isinstance(tile, dict) else None
    except Exception:
        return None


def _product_for_tile(tile):
    if not isinstance(tile, dict):
        return None
    crop = tile.get("crop")
    if crop in SELLABLE:
        return crop
    animal = tile.get("animal")
    return {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}.get(animal)


def _yield_targets(farm, prices, board_size):
    rows = _get(farm, "tiles", []) or []
    targets = []
    access = _shed_access(board_size)
    for y, row in enumerate(rows):
        if not isinstance(row, list):
            continue
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            units = max(0, _ival(tile.get("yield_units", 0)))
            product = _product_for_tile(tile)
            if units <= 0 or product is None:
                continue
            price = max(1.0, _fval(_get(prices, product, 1), 1.0))
            shed_dist = min(_manhattan((x, y), q) for q in access)
            targets.append({
                "pos": (x, y),
                "units": units,
                "product": product,
                "gross": price * units,
                "shed_dist": shed_dist,
            })
    return targets


def _base_ops(action, n):
    ops = [action.get("farmer") or ["PASS"], *list(action.get("hands") or [])]
    while len(ops) < n:
        ops.append(["PASS"])
    return ops[:n]


def _set_ops(action, ops):
    action["farmer"] = ops[0] if ops else ["PASS"]
    action["hands"] = list(ops[1:])


def _trim_market(action):
    kept = []
    for order in list(action.get("market") or []):
        if not (isinstance(order, list) and order):
            continue
        if order[0] in {"SELL", "HIRE"}:
            kept.append(order)
    action["market"] = kept[:10]


def _plan_units(obs, base_action, step):
    action = copy.deepcopy(base_action)
    farms = _get(obs, "farms", []) or []
    player = _ival(_get(obs, "player", 0), 0)
    if player < 0 or player >= len(farms):
        return action
    farm = farms[player]
    private = _get(obs, "private", {}) or {}
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    positions = _actor_positions(farm)
    n = len(positions)
    if not n:
        return action
    invs = _inventories(private, n)
    board_size = len(_get(farm, "tiles", []) or []) or 10
    base_ops = _base_ops(action, n)
    ops = [["PASS"] for _ in range(n)]
    free = []

    # Inventory already harvested is terminally valuable only if it reaches the shed.
    for i, (pos, inv) in enumerate(zip(positions, invs)):
        if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
            continue
        if _inventory_total(inv) > 0:
            if _at_shed_access(pos, board_size):
                ops[i] = ["DROP"]
            else:
                ops[i] = _move_toward(pos, _nearest_shed(pos, board_size))
            continue

        tile = _tile_at(farm, pos)
        if tile is not None and max(0, _ival(tile.get("yield_units", 0))) > 0:
            ops[i] = ["HARVEST"]
            continue
        if tile is not None and bool(tile.get("fertilizer_available", False)):
            # Fertilizer has direct sell value and no future-production dependency.
            ops[i] = ["COLLECT_FERTILIZER"]
            continue
        free.append(i)

    # Receding-horizon assignment of empty actors to distinct yield tiles. A job
    # is feasible only if travel + HARVEST + return + DROP fit before terminal.
    targets = _yield_targets(farm, prices, board_size)
    turns_left = END - step + 1
    pairs = []
    for i in free:
        pos = positions[i]
        if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
            continue
        for j, target in enumerate(targets):
            d1 = _manhattan(pos, target["pos"])
            total_actions = d1 + 1 + target["shed_dist"] + 1
            if total_actions > turns_left:
                continue
            # Value density first, then gross value, then shorter plan.
            density = target["gross"] / max(1, total_actions)
            pairs.append((density, target["gross"], -total_actions, -i, -j, i, j))
    pairs.sort(reverse=True)
    used_actors, used_targets = set(), set()
    assignment = {}
    for *_rank, i, j in pairs:
        if i in used_actors or j in used_targets:
            continue
        used_actors.add(i); used_targets.add(j); assignment[i] = targets[j]

    for i in free:
        target = assignment.get(i)
        if target is not None:
            ops[i] = _move_toward(positions[i], target["pos"])
            continue
        # No feasible collection job: preserve only unit actions that can still
        # help collection/pathing. Terminal maintenance/investment becomes PASS.
        bop = base_ops[i]
        opname = bop[0] if isinstance(bop, list) and bop else "PASS"
        ops[i] = copy.deepcopy(bop) if opname in KEEP_IDLE_BASE else ["PASS"]

    _set_ops(action, ops)
    _trim_market(action)
    return action


def agent(obs, config=None):
    base_action = _BASE.agent(obs, config)
    step = _ival(_get(obs, "step", 0), 0)
    if step < START or step > END:
        return base_action
    action = _plan_units(obs, base_action, step)
    if step == END:
        # R4B originally computed projected liquidation before our unit rewrite.
        # Recompute on the modified action so same-turn terminal DROPs are sold.
        action = _BASE._terminal_market_only(obs, action)
    return action
