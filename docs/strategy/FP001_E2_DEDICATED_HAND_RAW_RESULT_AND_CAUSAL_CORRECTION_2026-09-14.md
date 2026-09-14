# FP001 E2 — raw result and causal correction — 2026-09-14

Workflow: `34864820833`

## Raw mechanical result

The frozen E2 implementation completed successfully and preserved all expected cows in every treatment.

The dedicated hand successfully unlocked the intended H11 mechanism:

- 136 HIRE orders across 8 episodes per hand treatment = 17 hires/episode;
- 8/8 opening STRAWBERRY established per hand treatment;
- 136 WATER actions = 17/episode;
- 16 FERTILIZE actions = exactly 2/episode;
- 32 crop HARVEST actions = 4/episode;
- 64 STRAWBERRY sold = **8 berries/episode**;
- main-farmer FEED/CARE/movement and MILK output matched the corresponding animal backbone totals.

Thus the scheduler itself worked: labor can preserve the animal backbone while realizing the H11 fertilizer-to-STRAWBERRY conversion.

Raw paired deltas:

### COW4_DAILY
- S1H1 − S1H0: **+1468.25 mean, 8W-0L**;
- S1H1 − S0H0: −4056 mean, 4W-4L, range −26311 to +13709.

### COW5_SURVIVAL
- S1H1 − S1H0: **+577.5 mean, 8W-0L**;
- S1H1 − S0H0: +2299 mean, 4W-4L, range −5601 to +19289.

### COW5_DAILY
- S1H1 − S1H0: +2167.25 mean, only 2W-6L, range −8215 to +24334;
- S1H1 − S0H0: +2067.25 mean, 2W-6L, range −8315 to +24234;
- S1H0 − S0H0 remained exactly −100 in 8/8, as expected from an unplanted seed.

## Why total-module deltas are not causal evidence yet

The extreme paired ranges are far too large to be explained by one crop, two fertilizer units and ~17 one-unit HIRE costs. Investigation of the official engine identified the confound:

`_spawn_weeds` calls RNG only for tiles that are currently `None`. A treatment that occupies one otherwise-empty tile with STRAWBERRY therefore consumes a different number of RNG calls than its animal-only control. From that point onward, subsequent weed locations can diverge across the entire farm despite identical episode seed/seat.

This changes physical routing and setup opportunity costs, so default-weed paired comparisons between policies with different occupied-tile histories are not common-random-number causal estimates.

This is a **test-design issue, not a policy failure or policy success**.

## Instrumentation correction

The E2 logger's `crop_failed` flag also over-counted failure: an ongoing crop naturally decays to WEED after completing its production/lifespan. Since S1H1 produced and sold 8 berries per episode, its later WEED state must not be labeled a production failure.

Future instrumentation records pre-productive death separately from natural post-production decay.

## Binding correction — E2B

Do not use the raw S1H1-vs-S0H0 deltas to promote or close the architecture.

Run an infrastructure-identical causal diagnostic with:

- exact same candidate code/parameters;
- `weedSpawnChance=0` for **all** matched treatments;
- fresh seeds and both seats;
- explicit per-case output and corrected crop-failure metric.

Disabling weed spawning is not a strategy change and is not intended to estimate hosted strength. It removes an action-dependent RNG path from a causal economics experiment. Production survivors still require later default-environment population testing.

## Additional positive signal, not yet promotion

The dedicated hand spent roughly 331 PASS actions per episode after servicing one STRAWBERRY. Therefore one-crop labor utilization is extremely low. If E2B validates positive total-module economics, the next question should be multi-crop utilization of the same hand—not more threshold tuning of a single crop.
