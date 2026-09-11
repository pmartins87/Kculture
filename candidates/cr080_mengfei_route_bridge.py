"""CR080: coherent daily route bank, legal observations only; stdlib runtime."""
import copy
import gzip
import json
import math
from pathlib import Path

MOVES = {'NORTH': (0, -1), 'SOUTH': (0, 1), 'EAST': (1, 0), 'WEST': (-1, 0)}
PASS = {'farmer': ['PASS'], 'hands': [], 'market': []}
ITEMS = ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'MILK', 'WOOL', 'EGG', 'FERTILIZER', 'COW', 'SHEEP', 'GOOSE')


def clock(obs):
    raw = obs.get('step')
    return int(raw) if raw is not None else 24 * int(obs.get('day', 0)) + int(obs.get('hour', 0))


def tile_code(tile, day):
    # Weeds are stochastic empty-space obstacles, handled by the route follower.
    if tile is None or (isinstance(tile, dict) and tile.get('kind') == 'WEED'):
        return ['EMPTY']
    if not isinstance(tile, dict):
        return [str(tile)]
    return [tile.get('kind'), tile.get('crop'), tile.get('animal'),
            day - int(tile.get('planted_day', tile.get('placed_day', day)))]


def signature(obs):
    """Explicit legal allowlist. Own farm/private, public shops and market only."""
    day = clock(obs) // 24
    farm = obs['farms'][int(obs['player'])]
    private = obs.get('private') or {}
    market = obs.get('market') or {}
    economy = [math.log1p(max(0, float(farm.get('money', 0))))]
    for group in ('shed', 'seeds'):
        economy += [math.log1p(max(0, float((private.get(group) or {}).get(k, 0)))) for k in ITEMS]
    for group in ('prices', 'inventory'):
        economy += [math.log1p(max(0, float((market.get(group) or {}).get(k, 0)))) for k in ITEMS]
    shops = {}
    for shop in (obs.get('town') or {}).get('unlocked_shops') or []:
        shops[shop] = shops.get(shop, 0) + 1
    return {'farmer': list(farm['farmer']),
            'tiles': [tile_code(t, day) for row in farm['tiles'] for t in row],
            'quadrants': sorted(farm.get('unlocked_quadrants') or []),
            'shops': shops, 'economy': economy}


def route_cost(current, reference):
    # Lexicographic priorities preserve route feasibility before matching economics.
    spatial = sum(abs(a-b) for a, b in zip(current['farmer'], reference['farmer']))
    tile_mismatch = sum(a != b for a, b in zip(current['tiles'], reference['tiles']))
    quadrants = len(set(current['quadrants']) ^ set(reference['quadrants']))
    structural = 10 * spatial + tile_mismatch + 25 * quadrants
    shops = sum(abs(current['shops'].get(k, 0)-reference['shops'].get(k, 0))
                for k in current['shops'].keys() | reference['shops'].keys())
    economy = sum(abs(a-b) for a, b in zip(current['economy'], reference['economy']))
    return structural, shops, economy


def move_towards(position, target):
    x, y = position
    tx, ty = target
    if x < tx: return ['EAST']
    if x > tx: return ['WEST']
    if y < ty: return ['SOUTH']
    if y > ty: return ['NORTH']
    return ['PASS']


class RouteBridge:
    def __init__(self, bank):
        self.bank = bank
        self.day = None
        self.selected = 0
        self.last_step = -1
        self.stats = {'decisions': 0, 'position_repairs': 0, 'weed_repairs': 0, 'switches': 0}

    def act(self, obs):
        step = clock(obs)
        if not 0 <= step < 719:
            return copy.deepcopy(PASS)
        day = step // 24
        if self.day != day or step <= self.last_step:
            state = signature(obs)
            index = min(range(len(self.bank)), key=lambda i: (*route_cost(state, self.bank[i]['signatures'][day]), i))
            self.stats['switches'] += int(index != self.selected)
            self.selected = index
            self.day = day
        self.last_step = step
        ref = self.bank[self.selected]
        action = copy.deepcopy(ref['actions'][step])
        farm = obs['farms'][int(obs['player'])]
        positions = [farm['farmer']] + list(farm.get('hands') or [])
        expected = ref['positions'][step]
        planned = [action.get('farmer') or ['PASS']] + list(action.get('hands') or [])
        repaired = []
        for i, position in enumerate(positions):
            act = planned[i] if i < len(planned) else ['PASS']
            target = expected[i] if i < len(expected) else position
            if position != target:
                if act[0] in MOVES:
                    dx, dy = MOVES[act[0]]
                    target = [min(9, max(0, target[0]+dx)), min(9, max(0, target[1]+dy))]
                act = move_towards(position, target)
                self.stats['position_repairs'] += 1
            x, y = position
            tile = farm['tiles'][y][x]
            if act[0] in ('PLANT', 'WATER', 'HARVEST') and isinstance(tile, dict) and tile.get('kind') == 'WEED':
                act = ['DIG']
                self.stats['weed_repairs'] += 1
            repaired.append(act)
        self.stats['decisions'] += 1
        return {'farmer': repaired[0], 'hands': repaired[1:], 'market': list(action.get('market') or [])[:10]}


_INSTANCE = None


def agent(obs, configuration=None):
    # Do not catch policy failures as PASS: exact runner must expose regressions.
    global _INSTANCE
    if _INSTANCE is None or clock(obs) == 0:
        # Kaggle's path loader executes with an empty globals dict (__file__ absent).
        # build_agent supplies the original package path through configuration.
        raw_path = (configuration or {}).get('__raw_path__') or globals().get('__file__')
        if not raw_path:
            raise RuntimeError('CR080 package path not supplied by runner')
        with gzip.open(Path(raw_path).resolve().parent / 'routes.json.gz', 'rt') as f:
            _INSTANCE = RouteBridge(json.load(f))
    return _INSTANCE.act(obs)
