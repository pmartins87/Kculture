# CR086 discovery — opponent inventory estimator v2 frozen before holdout

Status: **FROZEN BEFORE INDEPENDENT TOP-10 HOLDOUT**

Date: 2026-09-13

Parent protocol: `CR086_OPPONENT_INVENTORY_ESTIMATOR_FEASIBILITY_2026-09-13.md`.

## Development-only finding

The first zero-private-loss point estimator was evaluated only on the already-spent CR083 36-replay development corpus. It showed two sharply different observability regimes.

Before a commodity has ever reached market price `$1`, the conservation estimate is nearly exact for the premium/sell-only products. Once the price reaches `$1`, SELL still removes private stock but the environment intentionally does **not** add that unit to market inventory. Therefore subsequent opponent private stock is no longer point-identifiable from market conservation alone.

Development errors before any observed price-floor event:

- CARROT MAE ~`0.62`, p95 `3`;
- TOMATO MAE ~`0.02`, p95 `0`;
- STRAWBERRY MAE ~`0.27`, p95 `0`;
- MELON MAE ~`1.04`, p95 `9`;
- EGG MAE ~`0.21`, p95 `2`;
- MILK MAE ~`0.08`, p95 `0`;
- WOOL MAE ~`0.10`, p95 `0`.

The large development errors in STRAWBERRY/MILK/WOOL occurred almost entirely after a price-floor regime began, exactly matching the official `_commit_unit` mechanic that destroys `$1` sales from private stock without increasing market supply.

## Frozen v2 rule

For each primary commodity independently:

### Before the first observed price `$1`

- `point = upper_zero_loss`;
- use the conservation estimate from public state transitions + own private state;
- floor-sale ambiguity flag is false.

### At and after the first observed price `$1`

- `point = 0`;
- `lower = 0`;
- `upper = upper_zero_loss`;
- `floor_sale_risk = true` permanently for the remainder of that episode/commodity.

Rationale: after floor activation, an arbitrary number of opponent units can be sold invisibly at `$1`; zero is the conservative point estimate and the zero-loss conservation track remains a valid upper hypothesis absent other unmodeled destruction.

This is a mechanics-derived regime switch, not a fitted numeric threshold. `$1` is the engine's literal price floor.

No commodity-specific fitted constants are introduced.

## Development metrics for frozen v2

On the 36 spent CR083 development replays:

- aggregate MAE: ~`1.20` units;
- aggregate p95 absolute error: `9` units;
- signed bias: ~`-1.09` units;
- interval coverage with `[0, upper]` after floor and point interval before floor: ~`96.15%`;
- `stock >= 5` classification accuracy: ~`91.54%`;
- `stock >= 10` classification accuracy: ~`95.31%`;
- `stock >= 25` classification accuracy: ~`99.41%`.

These values are development evidence only. They do not alter the previously frozen holdout PASS thresholds.

## Independent holdout remains untouched

The exact 10 replay IDs frozen in the parent protocol remain the only independent holdout for this v2 feasibility decision.

No further rule, commodity exception, buffer, threshold or reset may be added after holdout metrics are inspected.

## Holdout decision

Apply the parent PASS rule unchanged:

- aggregate interval coverage >= `0.95`;
- aggregate MAE <= `3.0`;
- aggregate p95 absolute error <= `10`;
- `stock >= 10` classification accuracy >= `0.90`;
- no forbidden runtime feature required.

PASS means the representation is eligible to become an input to later CR086 policy research. It does **not** authorize a CR086 candidate, promotion, or hosted submission.
