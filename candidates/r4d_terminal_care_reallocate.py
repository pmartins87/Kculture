"""R4D candidate: reallocate terminally nonproductive CARE actions.

Delegates to frozen R4B.  Only during steps 672..695, when the base action for
an actor is CARE on an animal tile:
  1. HARVEST if the animal already holds product;
  2. else COLLECT_FERTILIZER if available;
  3. else PASS.

Mechanics basis: the end-of-day refresh after step 695 is the final animal
production opportunity. CARE issued during this day creates a pending bonus only
after that production check, so it cannot be consumed before terminal scoring.
Harvesting already-held product can also free max_held capacity for that final
production refresh. FEED and every other action remain untouched.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
START = 672
END = 695


def _load_base():
    spec = importlib.util.spec_from_file_location("kculture_r4d_care_base", BASE_PATH)
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
        except (KeyError, TypeError):
            return default


def _tile_at(farm, pos):
    if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
        return None
    try:
        x, y = int(pos[0]), int(pos[1])
        rows = _get(farm, "tiles", []) or []
        if y < 0 or y >= len(rows) or x < 0 or x >= len(rows[y]):
            return None
        return rows[y][x]
    except (TypeError, ValueError, IndexError):
        return None


def _replacement(tile):
    if not (isinstance(tile, dict) and tile.get("animal")):
        return ["PASS"]
    try:
        units = int(tile.get("yield_units", 0) or 0)
    except (TypeError, ValueError):
        units = 0
    if units > 0:
        return ["HARVEST"]
    if bool(tile.get("fertilizer_available", False)):
        return ["COLLECT_FERTILIZER"]
    return ["PASS"]


def agent(obs, config=None):
    action = _BASE.agent(obs, config)
    try:
        step = int(_get(obs, "step", 0) or 0)
    except (TypeError, ValueError):
        return action
    if step < START or step > END:
        return action

    farms = _get(obs, "farms", []) or []
    try:
        player = int(_get(obs, "player", 0) or 0)
    except (TypeError, ValueError):
        player = 0
    if player < 0 or player >= len(farms):
        return action
    farm = farms[player]

    farmer_op = action.get("farmer")
    if isinstance(farmer_op, list) and farmer_op and farmer_op[0] == "CARE":
        action["farmer"] = _replacement(_tile_at(farm, _get(farm, "farmer")))

    hands = _get(farm, "hands", []) or []
    hand_ops = list(action.get("hands") or [])
    for i, op in enumerate(hand_ops):
        if not (isinstance(op, list) and op and op[0] == "CARE"):
            continue
        pos = hands[i] if i < len(hands) else None
        hand_ops[i] = _replacement(_tile_at(farm, pos))
    action["hands"] = hand_ops
    return action
