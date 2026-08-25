"""Versioned deterministic low-complexity crop opponents for R2.

These agents intentionally remain simple: each farms only the tile currently
occupied by the main farmer, with no movement, expansion, hiring, livestock, or
market timing. Their purpose is matchup diversity and regression coverage, not
champion-level play.
"""

from __future__ import annotations

CROP_RULES = {
    "WHEAT": {"seed_cost": 10, "max_yield_day": 4, "ongoing": False},
    "CARROT": {"seed_cost": 20, "max_yield_day": 3, "ongoing": False},
    "TOMATO": {"seed_cost": 50, "max_yield_day": 8, "ongoing": True},
    "STRAWBERRY": {"seed_cost": 100, "max_yield_day": 10, "ongoing": True},
    "MELON": {"seed_cost": 80, "max_yield_day": 12, "ongoing": False},
}


def _pass():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def crop_agent(obs, crop: str):
    rule = CROP_RULES[crop]
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return _pass()

    farm = farms[player]
    x, y = farm["farmer"]
    tile = farm["tiles"][y][x]
    day = obs.get("day", 0)
    seeds = private.get("seeds", {}) or {}
    shed = private.get("shed", {}) or {}

    market = []
    quantity = int(shed.get(crop, 0) or 0)
    if quantity > 0:
        market.append(["SELL", crop, quantity])
    if int(seeds.get(crop, 0) or 0) == 0 and farm["money"] >= rule["seed_cost"]:
        market.append(["BUY_SEED", crop, 1])

    farmer = ["PASS"]
    if tile is None and int(seeds.get(crop, 0) or 0) > 0:
        farmer = ["PLANT", crop]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == crop:
        age = day - int(tile.get("planted_day", day))
        yield_units = int(tile.get("yield_units", 0) or 0)
        if rule["ongoing"] and yield_units > 0:
            farmer = ["HARVEST"]
        elif not rule["ongoing"] and age >= rule["max_yield_day"]:
            farmer = ["HARVEST"]
        elif not tile.get("watered_today", False):
            farmer = ["WATER"]

    return {"farmer": farmer, "hands": [], "market": market}


def wheat_agent(obs):
    return crop_agent(obs, "WHEAT")


def carrot_agent(obs):
    return crop_agent(obs, "CARROT")


def tomato_agent(obs):
    return crop_agent(obs, "TOMATO")


def strawberry_agent(obs):
    return crop_agent(obs, "STRAWBERRY")


def melon_agent(obs):
    return crop_agent(obs, "MELON")
