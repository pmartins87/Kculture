# CR086 discovery — opponent inventory estimator feasibility protocol

Status: **FROZEN FEASIBILITY STUDY / NOT A CANDIDATE / NO HOSTED SUBMISSION**

Date: 2026-09-13

## Purpose

Test whether a legal runtime state estimator can recover useful bounds on the opponent's private commodity inventory from public state transitions and our own private state/action history.

This study does **not** change CR083, does not create CR086 yet, and does not use score/rating as an estimator feature.

## Why this representation matters

The current CR083 architecture reacts primarily to public market prices/inventory and fixed route checkpoints. It does not maintain an explicit estimate of the opponent's remaining private supply. In a shared market, two states with the same current market inventory can have very different future pressure depending on whether the opponent still holds zero, ten or fifty units ready to sell.

The environment mechanics permit substantial accounting from public state:

- SELL of a non-floor unit transfers one private unit into market inventory;
- SELL at price `$1` destroys the sold private unit without increasing market supply;
- BUY_PRODUCT is allowed only for WHEAT/FERTILIZER;
- town consumption is deterministic from `step` plus publicly visible unlocked shops;
- tile `yield_units`, crop/animal identity and farm state are public;
- harvesting moves public yield into private inventory without creating units;
- end-of-day carried inventory is deposited into the private shed up to capacity; overflow is destroyed;
- explicit DROP can likewise destroy overflow;
- own private inventory is directly visible to the controlled player.

Therefore premium/sell-only commodities admit a conservation-style estimator with uncertainty concentrated in identifiable loss channels.

## Commodities

Primary feasibility set:

- CARROT
- TOMATO
- STRAWBERRY
- MELON
- EGG
- MILK
- WOOL

WHEAT and FERTILIZER are excluded from the first pass because they also have direct BUY_PRODUCT flows and private consumption (FEED/FERTILIZE), increasing ambiguity. They may be added only after the premium-product estimator is validated.

## Runtime legality boundary

Allowed estimator inputs:

- current and previous public `farms`, `market`, `town`, `step/day/hour`;
- controlled player's own current/previous `private` state;
- controlled player's own previously emitted action;
- frozen public environment mechanics/constants.

Forbidden runtime inputs:

- opponent private observation;
- opponent action from replay;
- team identity/name/rank/rating;
- EpisodeId;
- hidden environment seed;
- future state;
- replay lookup.

Opponent private state and replay actions may be read **offline only as labels for feasibility/error analysis**. They must never enter the candidate estimator implementation used at runtime.

## State representation

For each commodity `i`, maintain:

- `opp_est_i`: point estimate of opponent loose private stock;
- `opp_lo_i`: conservative lower bound;
- `opp_hi_i`: conservative upper bound;
- `uncertainty_i = opp_hi_i - opp_lo_i`;
- flags/counters for ambiguity sources:
  - `floor_sale_risk_i`;
  - `overflow_loss_risk_i`;
  - `drop_loss_risk_i`;
  - `harvest_ambiguity_i`.

The first point estimator uses the zero-private-loss assumption inside the feasible interval; uncertainty expands instead of silently pretending loss channels do not exist.

## Conservation logic

For premium/sell-only products, private stock changes through three economically important channels:

1. harvest/public production becoming private stock;
2. sales from private stock into the shared market;
3. private destruction through floor-price SELL or overflow/DROP.

Non-floor opponent sales are inferable from market inventory change after accounting for deterministic town consumption and our own known successful non-floor sales. Public tile transitions constrain harvest quantity. Ambiguous transitions widen `[lo, hi]` rather than being resolved with future information.

The implementation must use the official Kaggriculture mechanics already frozen in the repository/mechanics probe; it must not fit transition rules from replay labels.

## Development corpus — spent

Use the already-frozen CR083 36-public-replay corpus from run `34745898829`, artifact `10314660085`.

These replays are **development only**. Opponent private truth/actions may be used as labels to debug accounting and classify ambiguity. They cannot establish generalization.

## Independent frozen holdout — preselected before estimator accuracy is inspected

Source archive: the already-downloaded read-only `current-frontier` snapshot from 2026-09-12. No new Kaggle collection is required.

Use exactly one previously stored replay from each of the first 10 ranked teams in that snapshot, selected as the first sampled episode already recorded by `meta_scout_report.json`:

1. team `16718819`, submission `56156662`, episode `108028156`
2. team `16732403`, submission `56161578`, episode `108028171`
3. team `16730612`, submission `56169353`, episode `108026194`
4. team `16621799`, submission `56158444`, episode `108017190`
5. team `16640510`, submission `56162707`, episode `108028485`
6. team `16760569`, submission `56097405`, episode `108027221`
7. team `16805699`, submission `56132899`, episode `108029554`
8. team `16730524`, submission `56167756`, episode `108028351`
9. team `16685556`, submission `56099704`, episode `108028193`
10. team `16704466`, submission `56149565`, episode `108029942`

This holdout selection is frozen before evaluating estimator accuracy.

## Metrics

Evaluate each commodity and aggregate:

- exact-match rate of point estimate to true opponent private total;
- MAE and median absolute error;
- 95th-percentile absolute error;
- interval coverage: fraction of true values inside `[lo, hi]`;
- mean/median interval width;
- signed bias;
- error conditioned on price floor (`price == 1`), shed-pressure regime, and day boundary;
- error by early/mid/late game.

Also report a decision-oriented classification metric:

- accuracy for `opponent_stock >= 5`;
- accuracy for `opponent_stock >= 10`;
- accuracy for `opponent_stock >= 25`.

These coarse thresholds test whether the estimator is useful for market-pressure decisions even when exact unit recovery is imperfect. They are evaluation thresholds only, not yet policy thresholds.

## Feasibility PASS rule

A CR086 policy layer may use this representation only if the independent 10-replay holdout satisfies all:

- interval coverage >= `0.95` aggregate across primary commodities;
- aggregate MAE <= `3.0` units;
- aggregate p95 absolute error <= `10` units;
- `stock >= 10` classification accuracy >= `0.90`;
- no identity/rank/seed/future/replay feature required for those metrics.

If exact point estimation misses these thresholds but intervals are well calibrated, the representation may still proceed only as uncertainty-aware bounds; point-estimate-conditioned policy is disallowed.

## Failure rule

If coverage or errors fail materially, do not tune against the frozen holdout. Improve the mechanics representation using the development corpus or abandon opponent-stock estimation as a primary CR086 feature.

## Relationship to public backbone acquisition

This estimator study is independent of the public-notebook acquisition workflow. Strong public agents are being acquired as architecture/backbone benchmarks. No public notebook score/result may alter this estimator's frozen feasibility thresholds.

No hosted submission is authorized by this protocol.
