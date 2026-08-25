# Official mechanics snapshot — Kaggriculture

Snapshot date: 2026-08-25  
Upstream lock: `official/UPSTREAM_LOCK.md`

This file contains **documented current mechanics only** for the frozen Kaggriculture advanced environment. Strategy hypotheses belong under `research/`.

## Episode and resources

- Two players, separate farms, shared market/town state.
- 30 days × 24 turns = 720 turns.
- Default board: 10×10, split into four 5×5 quadrants.
- Starting bank: 3000 coins.
- Final reward and winner are based on **money in the bank only**. Unsold inventory has zero terminal value.
- Action timeout: 1 second.
- Maximum 10 market orders per player per turn; extras are silently dropped.

## Farm, shed, movement and land

- Only the NW quadrant starts unlocked.
- Additional land costs 1000, 2000, then 4000 coins.
- Locked tiles are passable for movement, but normal tile actions on them no-op.
- The shed is conceptually centered between four central tiles; it is not itself a board tile.
- Shed capacity is 100 non-seed items. Overflow is discarded.
- Farmer and hired hands return/drop inventory into the shed at end of day, subject to capacity.
- Weeds may spawn on empty unlocked tiles at end of day with default probability 0.005 per tile.

## Hiring

- `HIRE` is a market action.
- Hired hands last for the current day only.
- Daily hire costs follow Fibonacci: 1, 1, 2, 3, 5, 8, 13, 21, ... under the default multiplier.
- Hire count/cost resets each day.
- Hands spawn around the shed using the documented placement rule; spawn may occur on locked-but-passable tiles.

## Crops

| Crop | Seed | Base price | First yield | Peak/max timing | Max yield | Type |
|---|---:|---:|---:|---:|---:|---|
| Wheat | 10 | 25 | day 2 | day 4 | 6 fertilized / 4 unfertilized | one-time |
| Carrot | 20 | 35 | day 2 | day 3 | 4 fertilized / 3 unfertilized | one-time |
| Tomato | 50 | 60 | day 8 | scheduled days 8–11 | 4 scheduled productions | ongoing but finite |
| Strawberry | 100 | 120 | day 10 | scheduled days 10,12,14,16 | 4 scheduled productions | ongoing but finite |
| Melon | 80 | 250 | day 10 | watering reaches cap by age 10 | 6 | one-time |

Rules:

- Plants must be watered daily; two consecutive missed days turn the plant into a weed.
- A newly planted seed starts with one missed-water count, so failing to water on planting day can kill it that night.
- One-time crops gain yield from watering during their bonus window; fertilized qualifying watering contributes double bonus.
- Tomato/strawberry produce on fixed schedules. Fertilizer + watering on a production day doubles that scheduled yield from 1 to 2.
- After maximum lifespan/production, yield decays by 1 every other turn until the plant becomes a weed.

## Animals

| Animal | Cost | Structure | First yield | Interval | Product | Max unharvested held |
|---|---:|---|---:|---:|---|---:|
| Goose | 300 | Coop | day 4 | daily | Egg | 4 |
| Cow | 400 | Pasture | day 8 | every 2 days | Milk | 6 |
| Sheep | 500 | Pasture | day 6 | every 3 days | Wool | 6 |

Rules:

- Animals require daily wheat feed; after two consecutive unfed days they escape permanently.
- Newly placed animals start with zero consecutive-unfed count and therefore survive their first day without feed.
- `CARE` banks bonus yield for the next scheduled production when basic feed needs are met.
- Each surviving animal creates 1 collectible fertilizer at end of day; uncollected fertilizer does not accumulate beyond the available unit.

## Town demand

- A new shop instance unlocks every 3 days by default, sampled **with replacement**, up to 8 shop instances.
- Each shop instance consumes its products every 4 turns; single-product shops consume 2×.
- Town center consumes one of every non-fertilizer product every 24 turns.

Demand table:

| Shop | Products |
|---|---|
| Bakery | Egg, Wheat |
| Pizza Shop | Milk, Tomato, Wheat |
| Brunch Spot | Egg, Wheat, Strawberry |
| Yarn Store | Wool (2×) |
| Ice Cream Shop | Strawberry, Milk, Wheat |
| Pet Cafe | Carrot (2×) |
| Smoothie Shop | Strawberry, Milk |
| Farmers Market | Wheat, Carrot, Tomato, Strawberry |

## Market

All products/fertilizer begin at market inventory `I0 = 10,000`.

- Seeds and animals have fixed purchase prices.
- Only Wheat and Fertilizer can be bought back via `BUY_PRODUCT`.
- Any product including fertilizer can be sold.
- Market buy/sell orders are interleaved concurrently between players one unit at a time.
- Sell quote uses pre-sell inventory; buy quote uses post-buy inventory. Immediate buy→sell against an unchanged market therefore has zero arbitrage profit.
- Price floor is 1 coin.

Price function:

```text
price(inv) = base + sign * amp * f(|inv - I0|)
sign = +1 below I0, -1 above I0
amp = target * base / f(T)
```

Current frozen market parameters:

| Resource | Base | T | Scarcity curve / target | Glut curve / target | P(I0−T) | P(I0+T) |
|---|---:|---:|---|---|---:|---:|
| Wheat | 25 | 400 | sqrt / 0.80 | log / 0.20 | 45 | 20 |
| Carrot | 35 | 450 | hinge / 1.00 | sqrt / 0.70 | 70 | 10 |
| Tomato | 60 | 200 | hinge / 0.40 | sqrt / 0.60 | 84 | 24 |
| Strawberry | 120 | 100 | sqrt / 0.70 | linear / 1.60 | 204 | 1 |
| Melon | 250 | 300 | log / 0.20 | square / 3.60 | 300 | 1 |
| Egg | 50 | 332 | hinge / 0.40 | log / 0.20 | 70 | 40 |
| Milk | 160 | 122 | sqrt / 0.60 | linear / 1.60 | 256 | 1 |
| Wool | 200 | 105 | log / 0.20 | square / 3.20 | 240 | 1 |
| Fertilizer | 100 | 200 | linear / 0.40 | linear / 0.40 | 140 | 60 |

The `hinge` scarcity curve is linear until the `T` knee, then grows sharply. In the frozen engine Carrot, Tomato and Egg use this curve, making town-shop composition strategically important in the late game.

Premium resources can collapse quickly under overproduction: Strawberry, Melon, Milk and Wool reach the 1-coin floor around `I0 + T` under current defaults.

## Turn processing order

Official documentation gives this order:

1. validate actions;
2. process player actions;
3. process market actions;
4. process town consumption;
5. update observations/day refresh/market/income/farm state.

## Observation privacy

Public/shared:

- both farms' board state;
- both bank balances;
- farmer/hand positions;
- unlocked quadrants and hire counts;
- market inventory/prices;
- town unlocked shops;
- day/hour.

Private to each agent:

- its shed inventory;
- its farmer/hand inventories;
- its seed counts.

Opponent farm configuration is therefore observable enough for strategy classification, while opponent inventory/seeds remain hidden.

## Mechanics that must still be regression-tested locally

Even documented mechanics should receive controlled tests because competition engines can change. Priority tests:

- atomic multi-unit planting when seeds are insufficient;
- crop watering/fertilizer yield windows;
- decay timing;
- animal CARE/feed bonus timing;
- fertilizer collection;
- shed overflow loss;
- hire spawn/cost sequence;
- simultaneous market order pricing;
- town unlock/consumption schedule;
- land purchase order and accessibility;
- terminal reward with unsold inventory.
