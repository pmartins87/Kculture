# V27D — Fresh Causal Benchmark for Distilled Structural Policy — 2026-09-21

## Status

DORMANT / PRE-REGISTERED while V27C2 workflow `35682535729` is still running and before any V27C2 holdout result is observed.

Activate only if V27C2 returns:
`V27C2_STRUCTURAL_POLICY_DISTILLATION_VIABLE`.

## Goal

Test whether the frozen first-party structural policy produced by V27C2 creates real W/L headroom over the current exact V47+ALL3 control on a fresh current-frontier population.

V27D is causal competition-performance validation, not imitation evaluation.

## Treatment

Exactly the frozen V27C2 artifacts:
- UNIT DecisionTreeClassifier;
- MARKET-SLOT DecisionTreeClassifier;
- V27C2 legal-memory / feature specification;
- no teacher source;
- no teacher call;
- no runtime opponent identity;
- no source rank/SHA/cluster features.

No model retraining, pruning, thresholding, feature editing, or fallback to teacher behavior is allowed between V27C2 and V27D.

## Control

Exact V47 + ALL3:
- O-RW1;
- O-TW1;
- O-LQ2.

## Fresh current-frontier population

At V27D workflow start:

1. query current public Kaggriculture Top-30 exactly once;
2. acquire refs serially with bounded retry/backoff;
3. SHA-deduplicate;
4. both-seat smoke every unique source against starter;
5. exclude exact V47 identity;
6. select up to 12 unique executable representatives by current representative rank only;
7. minimum selected sources: 8;
8. freeze exact selected source packages plus exact V47 base into an immutable workflow artifact before causal episodes;
9. no source reacquisition after snapshot.

Unavailable non-selected refs are recorded but do not invalidate the run.

## Fresh causal seeds

Exactly:
`80101,80102,80103,80104,80105,80106`.

Both seats.

With 12 selected sources:
`12 × 6 × 2 = 144 paired contexts`.

For every context run:
- CONTROL vs exact frozen opponent;
- TREATMENT vs the same exact frozen opponent.

## Mechanical validity

Require:
- >=8 selected unique executable source SHAs;
- every selected source passes both-seat smoke;
- source/base snapshot SHA exact;
- all expected CONTROL and TREATMENT episodes complete DONE/DONE with 720 steps and finite rewards;
- no runtime model exception;
- no missing/duplicate context key;
- no live Kaggle reacquisition during causal execution.

Failure:
`V27D_MECHANICS_INVALID`.

## Primary paired metrics

For every context:
`score_delta = treatment_score - control_score`.

Report:
- positive / neutral / negative score contexts;
- mean score delta;
- mean margin delta;
- source-SHA support;
- fresh-seed support;
- CONTROL functional outcome clusters derived only from CONTROL 12-tuple vectors;
- CONTROL-win -> TREATMENT-nonwin regressions;
- treatment/control aggregate score rate.

Margin-only improvement cannot pass.

## Frozen W/L headroom gate

V27D passes only if all are true:

1. positive-score contexts >= **8**;
2. positive-score contexts span >= **3 source SHAs**;
3. positive-score contexts span >= **3 fresh seeds**;
4. positive-score contexts span >= **2 CONTROL functional clusters**;
5. mean score delta > 0;
6. negative-score contexts <= positive-score contexts / 2;
7. CONTROL-win -> TREATMENT-nonwin regressions <= positive-score contexts / 2.

## Decisions

### `V27D_FRESH_CAUSAL_HEADROOM`

All gates pass.

Route:
- preserve V27C2 model/runtime unchanged;
- build a hosted-faithful package;
- run local package parity / dependency / latency checks;
- compare final-slot strategy against the existing hosted anchors;
- **do not submit** until explicit user authorization.

### `V27D_NO_FRESH_CAUSAL_HEADROOM`

Mechanics pass but W/L gate fails.

Route:
- close rank-1 behavioral distillation;
- do not tune V27C2 from V27D outcomes;
- do not reopen V47+ALL3 option mining;
- preserve research artifacts and move to final-slot / competition-strategy reassessment.

### `V27D_MECHANICS_INVALID`

Repair mechanics only; rerun the exact same snapshot, model, seeds, seats and gate.

## Anti-overfit restrictions

Forbidden after V27D outcomes:
- model retraining;
- tree-depth change;
- source-conditioned route;
- source/rank/SHA feature;
- seed-specific behavior;
- opponent-specific fallback;
- teacher calls;
- public leaderboard submission to decide whether the gate passed.

## Kaggle

No V27D result directly authorizes submission.
