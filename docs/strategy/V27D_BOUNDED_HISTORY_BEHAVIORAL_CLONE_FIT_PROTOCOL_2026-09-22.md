# V27D — Bounded-History Behavioral Clone Fit Protocol — 2026-09-22

## Status

DORMANT / PRE-REGISTERED while binding V27C workflow `35725924827` is still running.

Activate only if V27C returns:
`V27C_BEHAVIORAL_DISTILLATION_DATA_VIABLE`.

No V27C outcome may change this model family, history window, split, hyperparameters, or thresholds.

## Binding teacher/history

Teacher:
rank-1 V56 SHA
`a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

History window:
**256** prior legal observations.

Feature representation:
exactly the V27C 1254-dimensional numeric representation:
- current 114 programme features;
- lags 1/4/16/64/128/256;
- history min/max/mean/window delta.

No source/rank/SHA/opponent identity feature.

## Data split

Reuse the frozen V27C data split:
- train: seeds 79901, 79902;
- validation: seed 79903;
- untouched test: seed 79904;
- all 12 immutable V26A opponents;
- both seats.

The data collection may be rerun deterministically from the same teacher/opponent bytes because V27C stores hashes/labels rather than the full training matrix.

## Targets

Fit three independent component classifiers:
- MARKET canonical component label;
- FARMER canonical component label;
- HANDS canonical component label.

Reconstruct the complete action from the three predicted component labels.

No direct complete-action classifier is fitted.

## Frozen model-selection rule

For each component separately:

### Primary model — HistGradientBoostingClassifier

Use iff the number of distinct training labels for that component is <= **64**.

Hyperparameters:
- learning_rate = 0.08
- max_iter = 150
- max_leaf_nodes = 31
- min_samples_leaf = 20
- l2_regularization = 1.0
- random_state = 20260922
- early_stopping = false

### Deterministic fallback — RandomForestClassifier

Use iff training label cardinality >64 or HistGradientBoosting raises an explicit fit-time memory/class-cardinality failure.

Hyperparameters:
- n_estimators = 160
- max_depth = 24
- min_samples_leaf = 2
- max_features = "sqrt"
- class_weight = "balanced_subsample"
- n_jobs = -1
- random_state = 20260922

No hyperparameter tuning.
No model sweep.
No neural network.
No per-source model.
No source-conditioned ensembling.

## Validation role

Validation seed 79903 may be used only to report accuracy and to choose the pre-frozen HGB-vs-RF fallback when HGB cannot fit for the permitted technical reason.

Validation cannot change hyperparameters or features.

## Frozen acceptance gate

On untouched test seed 79904, require all:

- MARKET exact accuracy >= 0.97;
- FARMER exact accuracy >= 0.995;
- HANDS exact accuracy >= 0.98;
- reconstructed complete-action accuracy >= 0.95;
- minimum opponent-source complete-action accuracy >= 0.90.

Also require:
- all test component labels decodable;
- zero invalid reconstructed actions after canonicalization;
- no source identity input.

Decision:
- pass => `V27D_BEHAVIORAL_CLONE_OFFLINE_PASS`;
- fail => `V27D_BEHAVIORAL_CLONE_OFFLINE_FAIL`;
- mechanics failure => `V27D_MECHANICS_INVALID`.

## Post-pass route

A V27D offline pass does not authorize submission.

It opens one V27E closed-loop causal gate:
- package the fitted first-party models only;
- no teacher code;
- no teacher source bytes;
- maintain a rolling 256-observation legal history at runtime;
- test on entirely new seeds and current-frontier immutable opponents;
- paired against ALL3 and the original teacher ceiling;
- require multi-source/multi-seed W/L evidence before any hosted candidate.

## Post-fail route

If V27D fails:
- close fast teacher behavioral distillation;
- do not tune the model family;
- move to final-slot / competition strategy.

No Kaggle submission is authorized.
