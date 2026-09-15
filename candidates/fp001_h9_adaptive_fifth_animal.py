"""FP001 / CR090 — public-shop adaptive marginal fifth animal.

Phase-1 controller only.  Four COWs are built/cared using the frozen H10/B4
scheduler.  Once the first public town shop is visible, the fifth animal is
activated with identical timing across three treatments:

- DELAY_COW: always COW
- DELAY_SHEEP: always SHEEP
- H9_ADAPT: SHEEP iff H9 expected remaining WOOL demand exceeds MILK demand

The adaptive choice uses only obs.town.unlocked_shops[0] plus official mechanics.
It never uses identity, rating, EpisodeId, hidden seed, future state, or private
opponent information.
"""
from __future__ import annotations

from collections import defaultdict

from candidates.fp001_h10_cow_scale_care_wrapper import make_agent as make_cow_care_agent
from candidates.fp001_e5_elite_mixed_animal import make_care_agent as make_mixed_care_agent
from candidates.fp001_h10_cow_scale_module import _get

TURNS_PER_DAY = 24
EPISODE_STEPS = 720
SHOP_UNLOCK_DAYS = tuple(range(3, 25, 3))
SHOP_SELL_INTERVAL = 4
CENTER_SELL_INTERVAL = 24

SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
ANIMAL_PRODUCTS = ("EGG", "MILK", "WOOL")

C4 = ("COW", "COW", "COW", "COW")
C5 = ("COW", "COW", "COW", "COW", "COW")
C4S1 = ("COW", "COW", "COW", "COW", "SHEEP")


def _shop_pull_per_tick(shop: str, product: str) -> int:
    products = SHOPS[shop]
    if product not in products:
        return 0
    return 2 if len(products) == 1 else 1


def _ticks_from_step(first_step: int, interval: int, end_step: int = EPISODE_STEPS - 1) -> int:
    first = first_step + ((-first_step) % interval)
    if first > end_step:
        return 0
    return (end_step - first) // interval + 1


def expected_remaining(step: int, unlocked_shops: tuple[str, ...]) -> dict[str, float]:
    """H9 expected public-town pulls at/after step under official default rules."""
    step = max(0, int(step))
    shops = tuple(str(x) for x in unlocked_shops)
    out = defaultdict(float)

    center_ticks = _ticks_from_step(step, CENTER_SELL_INTERVAL)
    for product in ANIMAL_PRODUCTS:
        out[product] += center_ticks

    shop_ticks_now = _ticks_from_step(step, SHOP_SELL_INTERVAL)
    for shop in shops:
        if shop not in SHOPS:
            continue
        for product in ANIMAL_PRODUCTS:
            out[product] += shop_ticks_now * _shop_pull_per_tick(shop, product)

    names = tuple(sorted(SHOPS))
    revealed = len(shops)
    for day in SHOP_UNLOCK_DAYS[revealed:]:
        first_step = max(step, day * TURNS_PER_DAY)
        ticks = _ticks_from_step(first_step, SHOP_SELL_INTERVAL)
        for product in ANIMAL_PRODUCTS:
            expected_per_tick = sum(_shop_pull_per_tick(shop, product) for shop in names) / len(names)
            out[product] += ticks * expected_per_tick

    return dict(out)


def first_shop(obs) -> str | None:
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    if not shops:
        return None
    shop = str(shops[0])
    return shop if shop in SHOPS else None


def choose_h9_fifth(first_shop_name: str) -> str:
    """Frozen CR090 selector; ties resolve to COW by the stronger runtime prior."""
    if first_shop_name not in SHOPS:
        raise ValueError(first_shop_name)
    demand = expected_remaining(3 * TURNS_PER_DAY, (first_shop_name,))
    return "SHEEP" if demand.get("WOOL", 0.0) > demand.get("MILK", 0.0) else "COW"


def make_agent(mode: str = "H9_ADAPT"):
    mode = str(mode).upper()
    if mode not in {"DELAY_COW", "DELAY_SHEEP", "H9_ADAPT"}:
        raise ValueError(mode)

    # The same exact four-COW DAILY controller is used by all treatments until
    # the first shop becomes public.  That makes purchase timing a matched control.
    core4 = make_cow_care_agent(4, "DAILY")
    five_cow = make_mixed_care_agent(C5, "DAILY")
    four_cow_one_sheep = make_mixed_care_agent(C4S1, "DAILY")

    def agent(obs, config=None):
        shop = first_shop(obs)
        if shop is None:
            return core4(obs, config)

        if mode == "DELAY_COW":
            fifth = "COW"
        elif mode == "DELAY_SHEEP":
            fifth = "SHEEP"
        else:
            fifth = choose_h9_fifth(shop)

        return five_cow(obs, config) if fifth == "COW" else four_cow_one_sheep(obs, config)

    return agent


agent = make_agent("H9_ADAPT")
