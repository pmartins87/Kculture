# V22B Source-Unavailable Sensitivity Closure Protocol — 2026-09-21

## Status

FROZEN before reading the outcome of current-source sensitivity workflow `35624589618`.

The exact binding V22B remains mechanically incomplete at 356/368 keys because:
- frozen rank-11 source SHA: `254eba4713f092e7bbdd6efe8b2b31ee8cf2873fcfbdf16ca7c530628a0f51ef`;
- current public `romantamrazov/kaggriculture-yummers` SHA: `338a1a08fa612585e01ace53fbd9e83d294750e13d6f981739b174209a967080`;
- historical versions 1..60 are inaccessible through the authenticated Kaggle API (HTTP 403);
- no other V22A ref shares the frozen SHA.

This protocol does **not** relabel a non-exact run as binding.

## Exact evidence already available

- 356/368 exact V22B keys;
- 89/92 exact contexts;
- 0 cross-attempt conflicts;
- 9/12 exact rank-11 contexts, covering 36 treatment rows;
- those 36/36 rank-11 rows match rank-1 and rank-2 functional peers exactly on `score_delta` and `margin_delta`.

The only unavailable exact contexts are:
- `v22a_hard_059` — seed 79101, seat 1;
- `v22a_hard_063` — seed 79103, seat 1;
- `v22a_hard_067` — seed 79105, seat 1.

## Non-binding current-source sensitivity

Workflow: `35624589618`.

The current rank-11 source may be used only for sensitivity analysis.

Sensitivity confirmation requires **all** of the following:

1. all 3 current-source BASE episodes exactly reproduce frozen V22A BASE `score` and `margin`;
2. all 12 current-source rows complete successfully;
3. for each missing `(seed, seat, mode)`, current-source `score_delta` and `margin_delta` exactly match rank-1 peer values;
4. the same 12 rows also exactly match rank-2 peer values;
5. rank-1 and rank-2 peer values agree with each other on all 12 rows.

If any condition fails:
- reject current-source sensitivity;
- do not impute the 12 missing exact rows;
- mark V22B exact routing inconclusive due frozen-source unavailability;
- refresh the current-frontier population under a new pre-registered block rather than changing V22B thresholds.

## If sensitivity confirmation passes

Construct a **sensitivity-only completion**, never an exact mechanical completion:
- retain the 356 exact rows unchanged;
- fill the 12 unavailable rows only with the unanimous rank-1/rank-2/current-source values;
- run the original frozen V22B aggregator unchanged on that sensitivity completion;
- label the result `V22B_SOURCE_UNAVAILABLE_SENSITIVITY_CONFIRMED_<ORIGINAL_DECISION>`.

The resulting route may open the next discovery family, but:
- it cannot promote an option;
- it cannot authorize a Kaggle submission;
- the next derived mechanism must pass an untouched fresh exact causal validation before any promotion.

This rule prevents permanent stalling on a third-party notebook mutation while keeping the distinction between exact evidence and sensitivity evidence explicit.
