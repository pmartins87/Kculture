# V27C — 256-Step Legal-History Behavioral Distillation Protocol — 2026-09-21

## Status

PRE-REGISTERED immediately after binding V27B returned
`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE` with selected horizon `256`,
before inspecting teacher action-label frequency or fitting any model.

## Binding provenance

Teacher:
- rank-1 V26A snapshot representative;
- ref `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`;
- SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

V27B:
- corrected 12-shard binding source workflow `35676166396`;
- aggregate-only binding workflow `35678269956`;
- 72 episodes, zero shard failures;
- selected minimum viable history horizon: **256 legal prior observations**;
- H=256 passes all frozen parity gates;
- FULL legal-history parity: 1.0.

No live Kaggle source reacquisition is allowed.

## Goal

Determine whether one source-agnostic, identity-free, first-party model can imitate the rank-1 teacher sufficiently well from:
- current legal player observation;
- a fixed legal history representation covering at most the previous 256 candidate observations;
- no opponent identity, rank, SHA, hidden seed, EpisodeId, teacher hidden state, or teacher source at runtime.

V27C is an offline behavioral-distillation gate. It does not authorize a submission.

## Dataset

Use the exact immutable V26A snapshot opponents.

Fresh seeds:
`79901..79908`.

Both seats.

Every candidate turn from every completed teacher episode is eligible as a labeled sample.

Expected episode grid with 12 opponents:
`12 × 8 × 2 = 192 episodes`.

Teacher runs normally and supplies the canonical complete action label.

## Frozen split

No random row split.

Training:
- seeds `79901..79905`;
- opponent representative ranks `1,2,4,5,6,7,9,10`.

Validation:
- seeds `79906`;
- all 12 opponents.

Holdout:
- seeds `79907,79908`;
- all 12 opponents.

This forces generalization across fresh temporal seeds and includes every opponent in final holdout.

No holdout row may be used for feature/model selection.

## Legal history representation

Window: exactly **256** prior candidate observations.

For each current turn, construct features from legal observations only.

### Current state
Use the existing `solver.programme_features.features` 114-dimensional current-state vector.

### Frozen lag snapshots
Append the same 114-dimensional feature vector at prior lags:

`[1,2,4,8,16,32,64,128,256]`.

If a lag is unavailable, use the earliest available observation and add a binary `lag_available` flag for that lag.

### Frozen delta snapshots
For each lag above, append:
`current_features - lag_features`.

### Legal previous-action summaries
For the previous own canonical action only, append deterministic structural summaries:
- market verb counts for BUY_PRODUCT, SELL, BUY_SEED, HIRE, EMPTY;
- farmer verb/kind one-hot over observed legal farmer action verbs;
- hand action verb counts;
- previous complete-action hash bucket is forbidden.

No opponent/source identity feature is allowed.

No raw string ref/rank/SHA/cluster feature.

## Label decomposition

Fit three independent deterministic classifiers:

1. MARKET label = exact canonical `market` component.
2. FARMER label = exact canonical `farmer` component.
3. HANDS label = exact canonical `hands` component.

Complete action is the composition of the three predicted components.

No component may query the teacher at runtime.

## Model family

Frozen family:
`sklearn.ensemble.ExtraTreesClassifier`.

One model per component.

Parameters:
- n_estimators = 256;
- max_depth = None;
- min_samples_leaf = 2;
- max_features = "sqrt";
- class_weight = "balanced_subsample";
- random_state = 20260921;
- n_jobs = -1.

No hyperparameter sweep.

If a component has only one class in training, use that constant label instead of fitting.

## Dataset size control

To keep training bounded:
- retain every sample whose complete teacher action differs from the immediately previous teacher action;
- additionally retain deterministic stride samples where `step % 4 == 0`;
- always retain steps `0..16`;
- no outcome-based sampling;
- no source-specific sampling.

Validation and holdout are evaluated on **all candidate turns**, not sampled subsets.

## Frozen viability gate

V27C passes only if all are true on the untouched holdout:

- complete-action exact parity >= **0.90**;
- MARKET parity >= **0.94**;
- FARMER parity >= **0.99**;
- HANDS parity >= **0.98**;
- minimum opponent-source complete-action parity >= **0.80**;
- minimum 120-turn stage-bucket complete-action parity >= **0.80**;
- no source identity features;
- no teacher call at inference;
- holdout episode coverage complete.

Decision:

### `V27C_HISTORY_POLICY_DISTILLATION_VIABLE`
All gates pass.

Route:
- freeze trained model artifact;
- export deterministic inference package;
- run V27D exact offline causal benchmark against current-frontier snapshot on fresh seeds;
- only if V27D shows multi-source/multi-seed W/L headroom may hosted packaging be considered.

### `V27C_HISTORY_POLICY_DISTILLATION_NOT_VIABLE`
Mechanical validity passes but one or more holdout gates fail.

Route:
- do not sweep ExtraTrees hyperparameters;
- do not increase/decrease history window;
- close fast rank-1 teacher distillation for this competition;
- move to final-slot / competition strategy while preserving the research artifact.

### `V27C_MECHANICS_INVALID`
Repair mechanics only; rerun same teacher, seeds, split, features, model family and gates.

## Restrictions

Forbidden:
- opponent identity/rank/SHA/cluster at runtime;
- hidden seed or EpisodeId;
- teacher source bundled into candidate;
- teacher calls at inference;
- post-hoc feature or hyperparameter search after holdout;
- changing the 256-step history window;
- Kaggle submission from V27C.

No Kaggle submission is authorized.
