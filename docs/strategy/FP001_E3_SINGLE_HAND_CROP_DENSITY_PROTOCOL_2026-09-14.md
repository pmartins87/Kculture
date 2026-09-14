# FP001 E3 — single-hand crop-density causal gate

Date: 2026-09-14
Branch: `research/first-principles-economy-v1`

## Why this gate exists

E2D (`34866890716`) established a clean causal PASS for one H11 STRAWBERRY serviced by one dedicated daily hand while preserving the animal backbone. In the deterministic-town causal environment, the full module beat animal-only by +907 on COW4_DAILY and +919 on both COW5_SURVIVAL and COW5_DAILY, with 8/8 matched wins for every architecture.

The same run also showed that the hand is heavily under-utilized when assigned to one plant. The next question is therefore not whether to hire more hands; it is how much crop work one first daily hand can profitably absorb.

## Engine facts frozen before results

Official Kaggriculture mechanics at commit `bbda347572cf5134e56f0eb49e8058e2560f9844`:

- STRAWBERRY seed cost 100, ongoing, first yield day 10, interval 2, max yield count 4. H11 already established two fertilizer windows (ages 9 and 13), producing 8 berries total when maintained correctly.
- MELON seed cost 80, non-ongoing, first yield day 10, max-yield day 12, max yield 6.
- A non-ongoing crop starts with one harvestable unit and WATER during its yield window adds one unit, or two while fertilized. Therefore MELON reaches its cap of 6 with five ordinary productive WATER actions and does not require fertilizer.
- First HIRE of each day costs 1 and resets daily.

## Causal environment

This gate is deliberately not a leaderboard simulator. It measures production economics without the known RNG coupling between tile occupancy and random town-shop selection:

- `weedSpawnChance = 0`
- `townShopUnlockInterval = 999`
- normal deterministic town-center consumption remains active
- `episodeSteps = 720`
- `startingMoney = 3000`
- exact `kaggle-environments==1.32.7`

Only after this causal gate is closed does a finalist return to the normal stochastic environment.

## Frozen backbone

Primary backbone: `COW5_DAILY` from H10/B4.

Reason: it was the mean-best animal-only B4 architecture in the normal environment, and E2D proved a dedicated hand can preserve its FEED/CARE/MILK work exactly.

The crop overlay may not reassign main-farmer animal work. One hand maximum exists at any time; the same daily first hand services the whole crop block.

## Frozen treatment grid

Compare each treatment against exact animal-only `COW5_DAILY`:

- `BASE`: no crop, no hand
- `S1`: 1 STRAWBERRY
- `S2`: 2 STRAWBERRY
- `S4`: 4 STRAWBERRY
- `M1`: 1 MELON
- `M2`: 2 MELON
- `M4`: 4 MELON
- `M6`: 6 MELON
- `M4S2`: 4 MELON + 2 STRAWBERRY
- `M6S1`: 6 MELON + 1 STRAWBERRY

No treatment is added or removed after observing results.

The grid intentionally stops at six MELONs for the pure density ladder: six appears repeatedly in CR087 elite macro families and fits inside the opening liquidity budget without changing the COW5 + WHEAT setup. `M6S1` is included as a high-density mixed stress test while still fitting opening liquidity.

## Crop layout

Use a compact NW cluster disjoint from the five COW positions. Planned crop positions, in route order:

`(4,3), (3,3), (2,3), (2,2), (3,2), (4,2), (4,1), (3,1)`.

STRAWBERRY positions are allocated first, then MELON positions. On planting day the hand must WATER a newly planted tile before leaving it, because planting day counts as the first unwatered day.

## Crop execution

- Buy only the exact opening seed quantities.
- Preserve the base market orders and animal scheduler.
- Reserve fertilizer only for remaining STRAWBERRY H11 applications; MELON receives no fertilizer in E3.
- STRAWBERRY: fertilize at ages 9 and 13, WATER daily through productive life, HARVEST after maintenance.
- MELON: WATER through the productive window and HARVEST at/after age 10; no fertilizer.
- Sell crop output from the shed promptly.
- Hire at most one first-cost hand per day, only while crop work remains.
- No late rescue/replant ladder; missed production is evidence of capacity saturation.

## Measurement

For every treatment record:

- final-bank delta from starting cash;
- paired delta versus BASE;
- COW survival;
- MILK sold;
- main FEED/CARE/movement counts;
- crop units sold by product;
- seed quantities bought;
- fertilizer sold;
- HIRE count;
- hand movement / PASS / crop actions.

Because shops and weeds are disabled and the passive opponent performs no actions, nominal seed should not affect the result. Use two fresh seeds and both seats as a symmetry / hidden-dependence sanity check, not as independent statistical evidence.

## PASS / selection rule

A treatment is eligible only if:

1. all five COWs survive in every case;
2. no engine/non-DONE failure occurs;
3. the animal backbone is not materially degraded (MILK output and main FEED/CARE must remain intact);
4. paired final-bank delta versus BASE is positive in every matched case.

Among eligible treatments, advance the highest economic treatment. If two are within 250 final-bank units, prefer the simpler / lower-action treatment unless the denser treatment has clearly higher output headroom.

## Stop rule

Do not retune this deterministic density grid. The selected E3 treatment moves once to a fresh normal-environment robustness gate with weeds and stochastic shops restored. Treatments that lose this frozen grid are closed unless later evidence introduces a genuinely new mechanism, not a threshold tweak.
