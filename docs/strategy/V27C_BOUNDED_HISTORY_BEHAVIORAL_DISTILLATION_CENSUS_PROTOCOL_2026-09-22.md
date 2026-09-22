# V27C — Bounded-History Behavioral Distillation Census Protocol — 2026-09-22

## Status

PRE-REGISTERED after corrected binding V27B returned
`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE` with selected horizon **256**,
before any V27C label-distribution or model-fit outcome.

## Binding upstream evidence

V27A:
- teacher: rank-1 V56 SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`;
- state-only complete-action parity: 0.9222222.

Corrected V27B:
- binding shard workflow: `35676166396`;
- aggregate-only workflow: `35725538992`;
- 72 episodes, failures 0;
- H=256 complete-action parity: **0.9962962963**;
- H=256 MARKET parity: **0.9962962963**;
- H=256 FARMER parity: **1.0**;
- H=256 HANDS parity: **1.0**;
- H=256 minimum source complete-action parity: **0.9777777778**;
- H=256 minimum checkpoint complete-action parity: **0.9444444444**;
- H=128 fails the frozen gate;
- FULL history parity: 1.0.

Therefore the history representation is frozen at **256 prior legal observations**. No history-window sweep is allowed.

## Question

Before spending time fitting a first-party behavioral clone, is the teacher's 720-turn policy compact enough that one source-agnostic legal-history representation can predict its actions with useful generalization?

V27C is a census/viability gate, not a competitive evaluation and not a Kaggle submission.

## Data source

Use only the immutable V26A snapshot:
- rank-1 V56 is the offline teacher oracle;
- all 12 exact V26A sources are opponents;
- no live Kaggle reacquisition.

Fresh seeds:
`79901, 79902, 79903, 79904`.

Both seats.

Expected teacher trajectories:
`12 × 4 × 2 = 96`.

Collect every candidate call over the full 720-step episode.

## Runtime-legal representation

For every teacher action at step t, construct one deterministic feature row from legal information only.

### Current-state block
- exact 114 `solver.programme_features` values for the current observation;
- current step and seat are already legal and may be included explicitly.

### Frozen bounded-history summary

History window:
last at most **256** prior legal observations.

For each of the 114 programme features, compute over the available history:
- value at lag 1;
- value at lag 4;
- value at lag 16;
- value at lag 64;
- value at lag 128;
- value at lag 256;
- min over window;
- max over window;
- mean over window;
- last-minus-first delta.

If a lag is unavailable, use the earliest available legal observation; at step 0 use current value.

This yields a fixed numeric representation and does not include:
- opponent ref/rank/SHA;
- hidden seed;
- EpisodeId;
- teacher globals;
- teacher source code state;
- future observations;
- private opponent state.

## Labels

Record canonical teacher:
- complete action key;
- market action key;
- farmer action key;
- hands action key.

Teacher source is an offline label oracle only.

## Frozen split

Split by **both seed and opponent**, so no exact opponent/seed trajectory appears on both sides.

Training seeds:
`79901, 79902`.

Validation seed:
`79903`.

Test seed:
`79904`.

All 12 opponents and both seats appear in each seed split, but outcome reporting must include leave-source-style support metrics by opponent.

No data from V27A/V27B seeds is used to fit V27C.

## Census metrics

Report:
- total rows;
- unique complete/market/farmer/hands labels;
- label frequency distributions;
- step-modal exact-action accuracy on validation/test;
- exact duplicate-feature conflicts: identical legal feature vector mapping to different labels;
- conflict rate overall and by component;
- nearest training-state label agreement on validation/test using exact standardized-feature equality where available;
- per-step label entropy;
- per-source and per-seed label support.

## Frozen viability gate

V27C returns `V27C_BEHAVIORAL_DISTILLATION_DATA_VIABLE` only if all are true:

1. mechanical validity passes;
2. total rows >= 60,000;
3. FARMER exact duplicate-feature conflict rate <= 0.005;
4. HANDS exact duplicate-feature conflict rate <= 0.02;
5. MARKET exact duplicate-feature conflict rate <= 0.05;
6. complete-action exact duplicate-feature conflict rate <= 0.06;
7. every validation/test complete-action label is either:
   - seen in training, or
   - decomposable into component labels each seen in training,
   for >= 98% of validation/test rows;
8. step-modal complete-action accuracy on test >= 0.70.

The 0.70 step-modal floor is only a compactness check; it is not the final model target.

If the gate passes:
- open exactly one V27D model-fit family;
- model selection is frozen before fitting.

If the gate fails:
`V27C_BEHAVIORAL_DISTILLATION_DATA_TOO_COMPLEX`;
- close fast rank-1 behavioral distillation;
- move to final-slot / competition strategy;
- do not tune history features post-hoc.

## V27D model family if V27C passes

Freeze now, before V27C outcome:
- component-wise gradient-boosted tree classifiers;
- one classifier each for MARKET, FARMER, HANDS;
- implementation: sklearn HistGradientBoostingClassifier where class cardinality permits; deterministic RandomForestClassifier fallback only if HistGradientBoosting cannot fit multiclass memory constraints;
- no neural network sweep;
- no architecture sweep;
- no source identity feature.

Train on seeds 79901-79902.
Tune nothing on test.
Validation 79903 may only choose between the two pre-frozen implementations by complete-action reconstruction accuracy.
Final untouched test is 79904.

V27D promotion requires:
- test MARKET accuracy >= 0.97;
- FARMER >= 0.995;
- HANDS >= 0.98;
- reconstructed complete-action accuracy >= 0.95;
- minimum opponent-source complete-action accuracy >= 0.90.

Only after V27D passes may a closed-loop causal agent be built and tested on entirely new seeds.

No V27C/V27D result authorizes Kaggle submission.
