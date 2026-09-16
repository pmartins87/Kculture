from __future__ import annotations

"""Rich, stable feature contract for Prize Solver value learning."""

from typing import Mapping

from .prize_solver_v0 import ANIMALS, CROPS, PRODUCTS, _count, _farms, _fval, _get, _iter_tiles, _ival, _player, _private, _step


def _farm_summary(farm, prices):
    out = {
        "land": float(len(_get(farm, "unlocked_quadrants", []) or [])),
        "hands": float(len(_get(farm, "hands", []) or [])),
        "field_value": 0.0,
        "risk": 0.0,
    }
    for a in ANIMALS:
        out[f"animal_{a.lower()}"] = 0.0
    for c in CROPS:
        out[f"crop_{c.lower()}"] = 0.0
    for product in ("MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
        out[f"pressure_{product.lower()}"] = 0.0

    for _, tile in _iter_tiles(farm):
        if not isinstance(tile, Mapping):
            continue
        if _get(tile, "kind", None) == "PLANT":
            crop = _get(tile, "crop", None)
            if crop in CROPS:
                out[f"crop_{crop.lower()}"] += 1.0
                y = max(0.0, _fval(_get(tile, "yield_units", 0)))
                price = max(1.0, _fval(_get(prices, crop, CROPS[crop]["base"]), CROPS[crop]["base"]))
                out["field_value"] += CROPS[crop]["seed"] + y * price
                out[f"pressure_{crop.lower()}"] += y + CROPS[crop]["daily"]
                if _ival(_get(tile, "consecutive_unwatered", 0)) >= 1 and not bool(_get(tile, "watered_today", False)):
                    out["risk"] += 1.0
        animal = _get(tile, "animal", None)
        if animal in ANIMALS:
            meta = ANIMALS[animal]
            product = meta["product"]
            out[f"animal_{animal.lower()}"] += 1.0
            y = max(0.0, _fval(_get(tile, "yield_units", 0)))
            price = max(1.0, _fval(_get(prices, product, meta["base"]), meta["base"]))
            out["field_value"] += meta["buy"] + y * price
            out[f"pressure_{product.lower()}"] += y + 1.5 * meta["daily"]
            if _ival(_get(tile, "consecutive_unfed", 0)) >= 1 and not bool(_get(tile, "fed_today", False)):
                out["risk"] += 1.0
    return out


def encode_value_features(obs, config=None):
    config = config or {}
    farms = _farms(obs)
    p = _player(obs)
    own = farms[p] if p < len(farms) else {}
    opp = farms[1 - p] if len(farms) >= 2 else {}
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    private = _private(obs)
    shed = _get(private, "shed", {}) or {}

    own_s = _farm_summary(own, prices)
    opp_s = _farm_summary(opp, prices)

    step = _step(obs, config)
    episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
    progress = min(1.0, max(0.0, step / float(max(1, episode_steps - 1))))
    remaining_frac = 1.0 - progress

    feats = {
        "bias": 1.0,
        "progress": progress,
        "remaining_frac": remaining_frac,
        "money_diff": _fval(_get(own, "money", 0.0)) - _fval(_get(opp, "money", 0.0)),
        "own_money": _fval(_get(own, "money", 0.0)),
        "opp_money": _fval(_get(opp, "money", 0.0)),
        "land_diff": own_s["land"] - opp_s["land"],
        "hands_diff": own_s["hands"] - opp_s["hands"],
        "own_risk": own_s["risk"],
        "opp_risk": opp_s["risk"],
        "field_value_diff": own_s["field_value"] - opp_s["field_value"],
        "own_field_value": own_s["field_value"],
        "opp_field_value": opp_s["field_value"],
        "town_shop_count": float(len(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])),
    }

    for a in ANIMALS:
        key = a.lower()
        feats[f"own_{key}"] = own_s[f"animal_{key}"]
        feats[f"opp_{key}"] = opp_s[f"animal_{key}"]
        feats[f"diff_{key}"] = own_s[f"animal_{key}"] - opp_s[f"animal_{key}"]
    for c in ("MELON", "STRAWBERRY", "TOMATO", "WHEAT"):
        key = c.lower()
        feats[f"own_{key}"] = own_s[f"crop_{key}"]
        feats[f"opp_{key}"] = opp_s[f"crop_{key}"]
        feats[f"diff_{key}"] = own_s[f"crop_{key}"] - opp_s[f"crop_{key}"]

    # Private liquidation potential for our side.
    shed_value = 0.0
    for product in PRODUCTS:
        if product == "FERTILIZER":
            unit = 100.0
        else:
            unit = max(1.0, _fval(_get(prices, product, 0.0)))
        shed_value += _count(shed, product) * unit
    for animal in ANIMALS:
        shed_value += _count(shed, animal) * ANIMALS[animal]["buy"]
    feats["shed_value"] = shed_value
    feats["terminal_shed_value"] = shed_value * (1.0 if remaining_frac <= (48.0 / episode_steps) else 0.0)

    # Price regime and opponent visible pressure are essential for deciding between
    # animals/crops and when to liquidate.
    for product, base in (("MILK", 160), ("WOOL", 200), ("EGG", 50), ("MELON", 250), ("STRAWBERRY", 120), ("TOMATO", 60)):
        k = product.lower()
        feats[f"price_{k}_ratio"] = max(1.0, _fval(_get(prices, product, base), base)) / float(base)
        feats[f"opp_pressure_{k}"] = opp_s[f"pressure_{k}"]
        feats[f"own_pressure_{k}"] = own_s[f"pressure_{k}"]

    return feats


FEATURE_NAMES = tuple(encode_value_features({"player": 0, "farms": [{}, {}], "private": {}, "market": {}, "town": {}}, {"episodeSteps": 720}).keys())
