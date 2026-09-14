"""FP001 H8 — single-animal zero-lineage runtime logistics module.

Purpose: price real setup/logistics/cashflow for one animal on the starting NW
shed-access tile.  This is not a full competitive farm.

Design is mechanics-derived only:
- target tile is the initial farmer tile (4,4 on boardSize=10), which is owned
  and shed-adjacent;
- no movement is required for the one-animal proof;
- structure build is free;
- BUY_ANIMAL is a market order, then PICKUP and PLACE are legal unit actions;
- minimum-survival feeding triggers from public own animal state;
- fertilizer/product are collected and sold;
- product sale prefers hour 1, immediately after the town-center pulse at hour 0;
- no competitor replay, identity, rating, EpisodeId, hidden seed or future state.
"""
from __future__ import annotations

ANIMAL_META = {
    "GOOSE": {"structure": "COOP", "product": "EGG"},
    "COW": {"structure": "PASTURE", "product": "MILK"},
    "SHEEP": {"structure": "PASTURE", "product": "WOOL"},
}


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError, IndexError):
            return default


def _ival(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _main_inventory(private):
    invs = _get(private, "inventories", []) or []
    if not invs:
        return {}
    return invs[0] or {}


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


def _pass(obs):
    farm = _farm(obs)
    hands_n = len(_get(farm, "hands", []) or [])
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hands_n)], "market": []}


def make_agent(species="GOOSE"):
    if species not in ANIMAL_META:
        raise ValueError(species)
    structure = ANIMAL_META[species]["structure"]
    product = ANIMAL_META[species]["product"]
    build_op = "BUILD_COOP" if structure == "COOP" else "BUILD_PASTURE"

    def agent(obs, config=None):
        config = config or {}
        action = _pass(obs)
        farm = _farm(obs)
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        inv = _main_inventory(private)

        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        episode_steps = max(1, _ival(_get(config, "episodeSteps", 720), 720))
        hour = step % turns
        remaining = episode_steps - 1 - step

        farmer_pos = _get(farm, "farmer", [4, 4]) or [4, 4]
        fx, fy = _ival(farmer_pos[0], 4), _ival(farmer_pos[1], 4)
        tiles = _get(farm, "tiles", []) or []
        tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None

        # Market liquidation from SHED.  Product waits for hour 1, immediately
        # after the deterministic town-center pulse at hour 0. Fertilizer has no
        # town demand, so sell it whenever it is already in shed.
        market = []
        fert_shed = max(0, _ival(_get(shed, "FERTILIZER", 0)))
        prod_shed = max(0, _ival(_get(shed, product, 0)))
        if fert_shed > 0:
            market.append(["SELL", "FERTILIZER", fert_shed])
        if prod_shed > 0 and (hour == 1 or remaining <= 3):
            market.append(["SELL", product, prod_shed])

        # Setup: build on the initial shed-access tile while BUY_ANIMAL executes
        # later in the same interpreter step.
        if tile is None:
            action["farmer"] = [build_op]
            if max(0, _ival(_get(shed, species, 0))) <= 0 and max(0, _ival(_get(inv, species, 0))) <= 0:
                market.insert(0, ["BUY_ANIMAL", species, 1])
            action["market"] = market
            return action

        # Empty matching structure: retrieve then place purchased animal.
        if isinstance(tile, dict) and _get(tile, "kind", None) == structure and _get(tile, "animal", None) is None:
            if max(0, _ival(_get(inv, species, 0))) > 0:
                action["farmer"] = ["PLACE", species]
            elif max(0, _ival(_get(shed, species, 0))) > 0:
                action["farmer"] = ["PICKUP", species, 1]
            else:
                market.insert(0, ["BUY_ANIMAL", species, 1])
            action["market"] = market
            return action

        if not (isinstance(tile, dict) and _get(tile, "animal", None) == species):
            action["market"] = market
            return action

        # Final slice: no future end-of-day is valuable. Collect/harvest first;
        # DROP any carried inventory later, then sell it in the same step because
        # unit actions execute before market processing.
        if remaining <= 3:
            if bool(_get(tile, "fertilizer_available", False)):
                action["farmer"] = ["COLLECT_FERTILIZER"]
            elif max(0, _ival(_get(tile, "yield_units", 0))) > 0:
                action["farmer"] = ["HARVEST"]
            elif inv:
                action["farmer"] = ["DROP"]
                post_fert = fert_shed + max(0, _ival(_get(inv, "FERTILIZER", 0)))
                post_prod = prod_shed + max(0, _ival(_get(inv, product, 0)))
                market = [o for o in market if o[1] not in ("FERTILIZER", product)]
                if post_fert > 0:
                    market.append(["SELL", "FERTILIZER", post_fert])
                if post_prod > 0:
                    market.append(["SELL", product, post_prod])
            action["market"] = market
            return action

        # Highest-value daily state actions first. End-of-day auto-drop moves
        # collected output to shed, so no routine DROP action is needed.
        if bool(_get(tile, "fertilizer_available", False)):
            action["farmer"] = ["COLLECT_FERTILIZER"]
        elif max(0, _ival(_get(tile, "yield_units", 0))) > 0:
            action["farmer"] = ["HARVEST"]
        else:
            consecutive_unfed = max(0, _ival(_get(tile, "consecutive_unfed", 0)))
            fed_today = bool(_get(tile, "fed_today", False))
            must_feed = consecutive_unfed >= 1 and not fed_today
            if must_feed:
                if max(0, _ival(_get(inv, "WHEAT", 0))) > 0:
                    action["farmer"] = ["FEED"]
                elif max(0, _ival(_get(shed, "WHEAT", 0))) > 0:
                    action["farmer"] = ["PICKUP", "WHEAT", 1]
                else:
                    # Prefer buying before a town pulse when possible. If we
                    # reach the deadline later in the day, buy immediately.
                    shop_interval = max(1, _ival(_get(config, "townShopSellInterval", 4), 4))
                    center_interval = max(1, _ival(_get(config, "townCenterSellInterval", 24), 24))
                    if step % shop_interval == 0 or step % center_interval == 0 or hour >= turns - 4:
                        market.insert(0, ["BUY_PRODUCT", "WHEAT", 1])

        action["market"] = market[:10]
        return action

    return agent


agent = make_agent("GOOSE")
