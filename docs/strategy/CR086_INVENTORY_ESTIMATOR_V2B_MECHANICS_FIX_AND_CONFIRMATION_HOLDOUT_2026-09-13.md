# CR086 discovery — inventory estimator v2b mechanics correction + independent confirmation holdout

Status: **FROZEN BEFORE CONFIRMATION HOLDOUT METRICS**

Date: 2026-09-13

## Why v2a holdout is not reused

The first top-10 holdout showed that the point estimate generalized strongly but interval coverage failed (`~90.35%` vs required `>=95%`). Inspection identified a mechanics correctness defect in the purported upper bound: the implementation could undercount publicly possible production when production and harvest occurred in the same transition.

The first holdout is now **spent**. It may not be reused to certify the corrected interval.

No empirical margin/buffer is fitted from that holdout.

## Mechanics correction

The v2 point estimate is unchanged.

Only interval mechanics are corrected.

### Lower bound

`lower = 0` for every premium commodity at every step.

This is mechanically conservative because private DROP/end-of-day shed overflow and `$1` floor sales can destroy private stock without a fully observable quantity. No positive lower bound is guaranteed from public state alone.

### Upper-bound production accounting

Maintain a separate `upper_zero_loss` conservation track that assumes no private destruction and uses **maximum mechanically possible public production** consistent with the observed transition.

Corrections:

1. **Ongoing crops (TOMATO/STRAWBERRY) on scheduled production day**
   - if the plant survives the transition, maximum possible creation is the full scheduled increment (`1` or fertilizer-water bonus `2`), even when `post_yield >= pre_yield`;
   - rationale: HARVEST may reset yield to zero before end-of-day refresh and refresh may then recreate units, making net public-yield delta hide the production event.

2. **Animals (EGG/MILK/WOOL) on scheduled production day**
   - if the animal survives the transition, maximum possible creation is the full scheduled base + publicly determined pending-care bonus;
   - rationale is the same harvest-then-production ambiguity.

3. **Non-ongoing crops (CARROT/MELON)**
   - when the plant survives, visible watering determines production as before;
   - when the plant disappears, hidden same-turn `WATER -> HARVEST/DIG` production is possible only if at least two controlled units began the turn on that tile, because each unit receives only one physical action;
   - in that case, upper accounting includes the maximum legal water increment for the crop/age/fertilization state.

No replay action, opponent private value, future state, team identity, rank or hidden seed is used by these rules.

The interval is:

- `lower = 0`;
- `upper = max(point, upper_zero_loss_residual)`.

The point-estimate floor rule from frozen v2 remains unchanged:

- before first observed commodity price `$1`: conservation point;
- at/after first `$1`: point `0`.

## Development-only verification after mechanics fix

On the already-spent CR083 36-replay development corpus:

- point MAE remains ~`1.20`;
- point p95 remains `9`;
- `stock >= 10` classification remains ~`95.31%`;
- corrected interval coverage becomes ~`97.91%`;
- median interval width remains `0`; mean width ~`14.16` units.

These are development checks only.

## Independent confirmation holdout — frozen now, before metrics

Source is the same already-downloaded 2026-09-12 `current-frontier` archive, but use the **second** previously sampled replay for each of the first 10 ranked teams. None of these episode IDs were in the first holdout.

1. team `16718819`, submission `56156662`, episode `108023488`
2. team `16732403`, submission `56161578`, episode `108028159`
3. team `16730612`, submission `56169353`, episode `108021535`
4. team `16621799`, submission `56158444`, episode `108004087`
5. team `16640510`, submission `56162707`, episode `108025405`
6. team `16760569`, submission `56097405`, episode `108022563`
7. team `16805699`, submission `56132899`, episode `108028176`
8. team `16730524`, submission `56167756`, episode `108025404`
9. team `16685556`, submission `56099704`, episode `108023529`
10. team `16704466`, submission `56149565`, episode `108028169`

Seat convention remains both seats per replay, exactly as frozen previously.

## Confirmation PASS rule

Unchanged from the parent feasibility protocol:

- aggregate interval coverage >= `0.95`;
- aggregate MAE <= `3.0`;
- aggregate p95 absolute error <= `10`;
- `stock >= 10` classification accuracy >= `0.90`;
- no forbidden runtime feature required.

No further estimator logic, threshold, commodity exception or interval expansion may be introduced after these confirmation metrics are inspected.

PASS makes opponent-inventory estimate/bounds an **eligible representation for later CR086 policy research only**. It does not authorize a CR086 policy candidate or hosted submission.
