# FP001 E2C — RNG/shop interference diagnosis — 2026-09-14

Workflow **`34866389261`**, job `104051175946`, SUCCESS.

## Question

Why did the E2/E2B COW5_DAILY treatment sometimes gain a few thousand and sometimes lose `-12k` to `-21k` even though the direct crop cashflow is only on the order of hundreds?

Focused seeds with weeds disabled:

- `69304`: positive E2B control case;
- `69305`: catastrophic case;
- `69306`: catastrophic case.

Compared exact animal-only COW5_DAILY against the exact frozen E2 dedicated-hand policy. Candidate bytes were not modified.

## What did **not** diverge

Across base and treatment in all three traced seeds:

- five cows were established by step 15;
- main FEED count = 121;
- main CARE count = 112;
- main HARVEST count = 26;
- main COLLECT_FERTILIZER count = 145;
- main movement count = 274;
- max aggregate pending-care counter observed = 25;
- WHEAT BUY quantities and steps were identical;
- MILK SELL quantities and steps were identical:
  - step 217: 18;
  - 265: 12;
  - 313: 12;
  - 361: 6;
  - 409: 24;
  - 505: 18;
  - 553: 12;
  - 601: 12;
  - 649: 6;
  - 673: 3;
  - 697: 24.

Therefore the catastrophic deltas were **not caused by animal setup, FEED/CARE timing, harvest batching, WHEAT affordability, or different MILK volume/timing**.

The first direct cash difference is only the expected treatment setup cost: after the opening market phase the base has 585 while treatment has 484, approximately the 100-cost seed plus first HIRE.

## Yet rewards diverged massively

- seed 69304: base `40715`, treatment `46147`, delta `+5432`;
- seed 69305: base `40183`, treatment `18778`, delta **`-21405`**;
- seed 69306: base `47177`, treatment `34610`, delta **`-12567`**.

Because the same quantities of MILK were sold at the same steps, those reward differences require materially different market prices/demand paths.

## Root cause in the official engine

The exact `_end_of_day` ordering is:

1. build one deterministic daily RNG from `env.info['seed']` and `day`;
2. for each player's farm, call `_spawn_weeds(..., rng)`;
3. `_spawn_weeds` calls `rng.random()` for every currently empty tile, even when `weedSpawnChance=0`;
4. after all farms, if a shop unlock is due, call `rng.choice(sorted(SHOPS))` using the **same RNG object**.

Therefore `weedSpawnChance=0` prevents weeds from appearing but does **not** preserve the RNG stream. A treatment that occupies one tile with STRAWBERRY consumes one fewer `rng.random()` call each day than the animal-only control. At shop-unlock days, `rng.choice(...)` therefore sees a different RNG state and can unlock a different shop. That changes long-run product demand and, through shared market inventory, the price received for the exact same MILK sales.

This fully explains the E2B pathology:

`crop occupancy -> different number of weed RNG draws -> different town shops -> different MILK demand -> different MILK prices -> ±10k/20k reward deltas`.

## Methodological correction

Same seed is **not** a common-random-number pairing when policy changes tile occupancy under the current engine. Setting weed probability to zero is insufficient if a downstream stochastic consumer still uses the same RNG.

For crop causal/economic gates, one of the following is required:

- equalize RNG consumption exactly; or
- eliminate downstream stochastic consumers for the attribution test.

E2D chooses the second route because it requires no engine patch and no policy change:

- `weedSpawnChance=0`;
- `townShopUnlockInterval` larger than the 30-day season, so no random shop unlock occurs;
- deterministic town-center demand remains active;
- exact frozen E2 policy is reused.

This environment is for causal attribution only. Default-shop/default-weed robustness returns later during population testing.

## Status

E2/E2B large total-module deltas are quarantined as causal evidence. The stable `S1H1-S1H0` labor signal on COW4_DAILY and COW5_SURVIVAL remains informative, but final crop-module promotion waits for E2D.
