"""Kculture R1 reference baseline.

This is a self-contained port of Kaggle's built-in Kaggriculture `starter_agent`
from kaggle-environments 1.32.7. It intentionally preserves the simple carrot
loop so local/hosted behavior can be reconciled before strategy work begins.
"""

CARROT_SEED_COST = 20
CARROT_MAX_YIELD_DAY = 3


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def agent(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}

    if not farms or player >= len(farms):
        return _pass_action()

    farm = farms[player]
    fx, fy = farm["farmer"]
    tile = farm["tiles"][fy][fx]
    day = obs.get("day", 0)
    seeds = private.get("seeds", {})
    shed = private.get("shed", {})

    market = []
    if shed.get("CARROT", 0) > 0:
        market.append(["SELL", "CARROT", shed["CARROT"]])
    if seeds.get("CARROT", 0) == 0 and farm["money"] >= CARROT_SEED_COST:
        market.append(["BUY_SEED", "CARROT", 1])

    farmer = ["PASS"]
    if tile is None and seeds.get("CARROT", 0) > 0:
        farmer = ["PLANT", "CARROT"]
    elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "CARROT":
        age = day - tile["planted_day"]
        if age >= CARROT_MAX_YIELD_DAY:
            farmer = ["HARVEST"]
        elif not tile["watered_today"]:
            farmer = ["WATER"]

    return {"farmer": farmer, "hands": [], "market": market}
