# V27C2 — Stateful Structural Action Distillation Protocol — 2026-09-21

## Status

PRE-REGISTERED after two identical computational failures of V27C whole-component classification and before any V27C/V27C2 validation or holdout model performance is observed.

## Goal

Distill the rank-1 teacher into a compact first-party policy by respecting the natural action structure instead of treating variable-length action lists as giant classes.

This is a representation/mechanics correction, not a hyperparameter search.

## Binding provenance

Teacher:
- ref `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`;
- SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

Opponent population:
- exact immutable V26A snapshot from workflow `35653189539`;
- all 12 selected sources.

Seeds / split are unchanged from V27C:
- train seeds: `79901..79905`;
- validation seed: `79906`;
- holdout seeds: `79907,79908`;
- both seats.

Training opponent ranks remain:
`1,2,4,5,6,7,9,10`.

Validation and holdout use all 12 opponents.

No holdout row may be used for model or feature selection.

## Legal state memory

The public teacher architecture audit shows that long-lived policy state can be represented by legally observable events without using source identity or internal route IDs.

V27C2 records only raw legal observations:

1. current 114-dimensional `solver.programme_features`;
2. at step 2:
   - opponent money;
   - public market WHEAT inventory;
   - a binary “step-2 memory observed” flag;
3. on the first candidate call at or after step 144:
   - first unlocked shop;
   - second unlocked shop;
   - encoded as two independent one-hot vectors over the eight legal shop names;
   - plus a “shop-pair memory observed” flag;
4. phase flags:
   - step >= 144;
   - step >= 648.

Forbidden:
- teacher route ID;
- teacher router state;
- source ref/SHA/rank;
- opponent identity;
- hidden seed;
- EpisodeId;
- copied route lookup tables.

## Unit-action factorization

The real number of unit actions is known from the legal observation:
- actor 0 = farmer;
- actors 1..N = current hands/workers.

Train **one shared UNIT classifier**.

Each unit sample contains:
- the global legal state-memory features above;
- actor index one-hot over the 40 action-encoding unit positions;
- farmer flag;
- current actor x/y;
- actor private inventory counts for the 12 canonical items;
- current-tile features:
  - tile-kind one-hot;
  - crop/animal item one-hot;
  - yield / water / feed / care / fertilizer legal fields;
- four-neighbor tile-kind one-hots.

Label:
- exact canonical unit action list, e.g. `["NORTH"]`, `["PLANT","WHEAT"]`, `["PICKUP","WHEAT",2]`.

At inference, predict exactly one unit action for every actor currently present.

No hand-list length classifier is used.

## Market-action factorization

The environment allows at most 10 market orders.

Train **one shared MARKET-SLOT classifier**.

For every turn create exactly 10 samples, one for each market slot 0..9.

Each market-slot sample contains:
- global legal state-memory features;
- slot-index one-hot over 10 slots.

Label:
- exact canonical order at that slot; or
- `<NONE>` if the true list ended before the slot.

At inference:
- predict slots 0..9;
- output orders in order until the first `<NONE>`;
- `[]` remains a valid explicit order and is distinct from `<NONE>`.

No copied market table is allowed.

## Frozen model family

Two independent models:

### UNIT
`sklearn.tree.DecisionTreeClassifier`

### MARKET-SLOT
`sklearn.tree.DecisionTreeClassifier`

Parameters for both:
- criterion = `gini`;
- splitter = `best`;
- max_depth = **32**;
- min_samples_split = 2;
- min_samples_leaf = 2;
- max_features = None;
- class_weight = None;
- random_state = 20260921.

Rationale frozen before holdout:
- one tree per structural decision keeps inference small enough for a hosted agent;
- exact-action class cardinality on the frozen TRAIN split is bounded (83 unit-action labels and 236 market-order labels);
- no ensemble-size or depth sweep is permitted.

## Dataset

V27C2 recollects the exact same 192 teacher episodes only because the original V27C artifacts did not retain actor-local legal observation fields needed for structural unit features.

No new seed or opponent is introduced.

Every teacher candidate turn is retained.

Training uses all eligible structural samples from the frozen training split:
- no outcome sampling;
- no action-frequency filtering.

## Evaluation

Validation/holdout use every turn.

For each turn:
- FARMER parity = predicted actor-0 action equals teacher farmer;
- HANDS parity = predicted list for all observed hands equals teacher hands exactly;
- MARKET parity = predicted ordered market list equals teacher market exactly;
- complete-action parity = all three components equal.

Report:
- overall component parity;
- complete-action parity;
- per-source complete-action parity;
- 120-turn stage buckets.

## Frozen viability gate

V27C2 passes only if all are true on untouched holdout:

- complete-action exact parity >= **0.90**;
- MARKET parity >= **0.94**;
- FARMER parity >= **0.99**;
- HANDS parity >= **0.98**;
- minimum opponent-source complete-action parity >= **0.80**;
- minimum 120-turn stage-bucket complete-action parity >= **0.80**;
- no identity feature;
- no teacher call at inference;
- complete holdout episode coverage.

These are exactly the original V27C holdout thresholds.

## Decisions

### `V27C2_STRUCTURAL_POLICY_DISTILLATION_VIABLE`
All gates pass.

Route:
- freeze UNIT and MARKET-SLOT model artifacts plus feature spec;
- implement deterministic first-party runtime;
- open V27D fresh causal benchmark on untouched seeds and a fresh immutable current-frontier snapshot;
- no hosted submission before V27D.

### `V27C2_STRUCTURAL_POLICY_DISTILLATION_NOT_VIABLE`
Mechanics pass but a holdout gate fails.

Route:
- no tree-depth sweep;
- no alternate class weighting;
- no new history window;
- close fast rank-1 behavioral distillation for this competition;
- move to final-slot / competition strategy.

### `V27C2_MECHANICS_INVALID`
Repair mechanics only and rerun the exact same experiment.

## Restrictions

No post-hoc:
- source-conditioned model;
- route-ID feature;
- copied tape/action table;
- threshold/model sweep;
- holdout-guided feature addition;
- Kaggle submission.

No Kaggle submission is authorized.
