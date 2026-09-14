# CR086 discovery — opponent inventory estimator confirmation result

Status: **FEASIBILITY PASS / REPRESENTATION ELIGIBLE / NOT YET A POLICY**

Date: 2026-09-13

## Frozen inputs

Parent feasibility protocol:
`docs/strategy/CR086_OPPONENT_INVENTORY_ESTIMATOR_FEASIBILITY_2026-09-13.md`

V2 floor-regime rule frozen before first holdout:
`docs/strategy/CR086_OPPONENT_INVENTORY_ESTIMATOR_V2_FROZEN_BEFORE_HOLDOUT_2026-09-13.md`

Mechanics correction and independent confirmation holdout frozen before confirmation metrics:
`docs/strategy/CR086_INVENTORY_ESTIMATOR_V2B_MECHANICS_FIX_AND_CONFIRMATION_HOLDOUT_2026-09-13.md`

Seat convention:
`docs/strategy/CR086_INVENTORY_HOLDOUT_EXECUTION_CONVENTION_2026-09-13.md`

## Method

Primary commodities:

- CARROT
- TOMATO
- STRAWBERRY
- MELON
- EGG
- MILK
- WOOL

Runtime-legal representation uses only public state transitions, controlled-player private state and frozen public mechanics.

Point rule:

- before first observed commodity price `$1`: public-conservation point estimate;
- at/after first `$1`: point estimate `0` because floor-price opponent sales can destroy arbitrary private units without increasing public market inventory.

Interval:

- lower `0`;
- upper from a separate no-private-loss conservation track with maximum mechanically possible production for harvest/production-ambiguous transitions.

The corrected upper explicitly handles:

- ongoing crop HARVEST followed by scheduled end-of-day production;
- animal HARVEST followed by scheduled end-of-day production;
- non-ongoing same-turn WATER -> HARVEST/DIG only where at least two units began the turn on the relevant tile.

No result-dependent numeric buffer was fitted.

## First holdout — spent / not certification evidence

The first frozen top-10 replay set showed strong point generalization but failed interval coverage (~90.35%). That revealed that the purported upper bound was mechanically incomplete. This holdout was declared spent and was not reused for certification.

Point metrics from that spent set were nonetheless diagnostic:

- MAE ~`1.35`;
- p95 `10`;
- `stock >= 10` accuracy ~`95.02%`.

## Independent confirmation holdout

Used exactly the second pre-stored replay for each of the first 10 ranked teams from the already-downloaded 2026-09-12 frontier archive, with both seats evaluated per replay.

Frozen episode IDs:

`108023488, 108028159, 108021535, 108004087, 108025405, 108022563, 108028176, 108025404, 108023529, 108028169`

Total evaluated commodity-step observations: **100,660**.

## Confirmation metrics

Aggregate:

- MAE: **`1.25005`** units;
- p95 absolute error: **`9`** units;
- signed bias: **`-0.76501`** units;
- interval coverage: **`0.969462`**;
- mean interval width: **`7.41434`** units;
- median interval width: **`0`**;
- `stock >= 10` classification accuracy: **`0.956338`**.

Per commodity:

| Commodity | MAE | p95 | bias |
|---|---:|---:|---:|
| CARROT | 1.355 | 11 | -1.334 |
| TOMATO | 0.287 | 2 | -0.075 |
| STRAWBERRY | 2.514 | 16 | +0.037 |
| MELON | 1.216 | 12 | -1.216 |
| EGG | 0.183 | 2 | +0.017 |
| MILK | 1.756 | 10 | -1.521 |
| WOOL | 1.439 | 9 | -1.263 |

## Frozen PASS thresholds and result

Required:

- interval coverage >= `0.95`: **PASS (`0.969462`)**;
- aggregate MAE <= `3.0`: **PASS (`1.25005`)**;
- aggregate p95 <= `10`: **PASS (`9`)**;
- `stock >= 10` accuracy >= `0.90`: **PASS (`0.956338`)**;
- no forbidden runtime feature: **PASS**.

Decision:

**`OPPONENT_INVENTORY_REPRESENTATION_FEASIBILITY_PASS`**

## What this does and does not prove

This is the first new CR086-era representation to generalize on a frozen cohort of strong public agents rather than merely on CR071M/legacy anchors.

It proves that useful opponent private-supply state can be estimated from legal public mechanics with low aggregate point error and calibrated bounds.

It does **not** prove that conditioning actions on this state improves W/L. The representation must next be paired with an independently justified market-value policy or a strong public backbone, frozen before performance evaluation.

No hosted submission is authorized by this PASS.
