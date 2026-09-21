# ALL3 V18B2 P2 Transition-Event Market Controller Protocol — 2026-09-21

## Status

Frozen after V18B state-classifier closure and before V18B2 model results.

## Purpose

Test whether the same recurrent P2 market residual families are predictable as **state transitions/events** rather than persistent state labels.

V18B2 uses:
- the exact same 3072 binding P2 rows;
- the exact same 19 actionable recurrent SELL residual families;
- the exact same source-held-out generalization gates;
- no causal outcomes.

No new game is run.

## Runtime legality

Every predictive feature must be available at decision time from:
- current legal observation/current exact ALL3 action;
- immediately previous turn's stored legal feature vector/current-action aggregates.

Forbidden:
- source/ref/rank;
- context id;
- seed metadata;
- seat;
- score/result/margin/reward;
- future state.

## Frozen temporal feature transform

Sort rows within each context by turn.

For every existing numeric V18B feature `f`, expose exactly:

1. `cur__f` = current value;
2. `prev__f` = immediately previous P2-row value;
3. `delta__f` = current - previous;
4. `absdelta__f` = abs(current - previous).

Additional legal booleans:
- `edge__any_numeric_change`;
- `edge__all3_market_changed`.

For the first P2 row (turn 464), previous=current and all deltas are zero.

No hand-selected per-product edge feature and no threshold search.

## Candidate rows

Use all 3072 rows. Do not downsample negatives and do not filter by exact turn.

## Labels

Exactly the same family ids used by V18B:
`(group_key, dominant_direction)`.

Family eligibility remains exactly the V18B actionable rule:
- SELL QTY;
- SELL PRESENCE;
- SELL DUPLICATE;
- real products only;
- recurrent in binding V14B;
- positive rows present in P2.

## Fixed classifier

Independent `DecisionTreeClassifier` per family:

- max_depth = 4;
- min_samples_leaf = **8** fixed;
- class_weight = "balanced";
- random_state = 20260921;
- no hyperparameter search.

The change from percentage-scaled min leaf to fixed 8 is part of the event representation: V18B showed 1-turn event supports as low as 10–40 rows, and percentage-scaled leaves mechanically smear these pulses. Generalization thresholds remain unchanged.

## Source-held-out validation

Leave-one-source-SHA-out across the same 10 source SHAs.

Retain only if:
- positive support spans >=4 source SHAs;
- precision >=0.80;
- recall >=0.70;
- F1 >=0.75.

No threshold is relaxed from V18B.

## Export / compiler

For retained families:
- refit on all 3072 rows;
- export exact JSON trees;
- pure-Python JSON predictions must equal sklearn on all 3072 rows;
- reuse the **unchanged frozen V18B SELL compiler semantics**.

Controller keeps one previous-feature vector as runtime state.

## Discovery PASS

**`V18B2_EVENT_CONTROLLER_READY_FOR_CAUSAL`** requires:
- exact 3072-row transformed dataset;
- >=3 retained families;
- retained families span >=3 kinds among QTY/PRESENCE/DUPLICATE;
- retained positives span >=4 source SHAs;
- exact sklearn/JSON parity;
- structural compiler validity on all rows;
- no prohibited features.

Otherwise:
**`V18B2_EVENT_CONTROLLER_NOT_DISTILLABLE`**.

No causal game is run in V18B2.
No Kaggle submission.
