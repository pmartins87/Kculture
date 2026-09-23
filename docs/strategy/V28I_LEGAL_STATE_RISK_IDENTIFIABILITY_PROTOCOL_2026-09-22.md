# V28I — Legal-State Residual-Risk Identifiability Protocol — 2026-09-22

## Status

PRE-REGISTERED while V28H is still running, before observing its selected checkpoint, explanatory window, or hard-vs-control feature differences.

V28I is an identifiability gate only. It cannot edit ALL3, create a deployable opponent-specific rule, or mutate Kaggle submissions.

## Strategic question

Once V28H mechanically selects the earliest structural separation checkpoint S, can the eventual ALL3 residual-loss regime be recognized from the player's **legal observation at S** in source-held-out current-frontier contexts?

This is deliberately different from memorizing the six V28G hard source identities.

## Binding inputs

Use only immutable evidence from:
- V28F workflow `35807910104`:
  - immutable frontier snapshot;
  - binding 144-context aggregate;
- V28G workflow `35812527508`:
  - source hard-core census;
- V28H workflow `35812876571`:
  - mechanically valid selected checkpoint S and explanatory action window W.

No Kaggle source reacquisition is allowed.

V28I must not start unless V28H is mechanically valid.

## Population

Re-run **all 144 V28F ALL3 contexts**:
- 12 frozen source SHAs;
- seeds 80401..80406;
- both seats.

Every replay must exactly reproduce the V28F ALL3 terminal score and margin. Any mismatch => mechanics invalid.

## Label

Context target:
- positive = V28F ALL3 terminal score == 0.0;
- negative = V28F ALL3 terminal score > 0.0.

Expected binding prevalence:
- 66 positive residual losses;
- 78 wins/non-losses.

The outcome label is offline training/evaluation metadata only and is never a runtime input.

## Legal feature vector

At the exact V28H-selected checkpoint S, extract only:
- the 114 `solver.programme_features` values from the candidate's legal player observation.

No source/rank/ref/SHA, opponent identity, seed, seat, terminal outcome, future state, rating, EpisodeId or hidden opponent-private state may enter the feature vector.

The seed and seat may be retained only as offline audit metadata.

## Frozen source-held-out split

Use V28G source groups only for stratification, never as model features.

Define:
- HARD sources = V28G sources with >=1 ALL3 loss;
- EASY sources = V28G sources with zero ALL3 losses.

Within HARD and EASY separately:
1. sort by representative rank, then SHA;
2. positions are zero-indexed;
3. positions where `index % 3 == 2` are HOLDOUT;
4. all other sources are TRAIN.

With the V28G 6-hard / 6-easy structure, this yields:
- train: 4 hard + 4 easy sources = 8 sources;
- holdout: 2 hard + 2 easy sources = 4 sources.

All contexts from a source stay entirely on one side.

No source may move after outcomes are inspected.

## Frozen model family

One deterministic decision tree:
- `max_depth=3`;
- `min_samples_leaf=8`;
- `class_weight="balanced"`;
- `random_state=20260922`.

No hyperparameter sweep.
No probability-threshold search.
Classification uses the tree's ordinary predicted class.

## Metrics

Report train and holdout:
- confusion matrix;
- precision;
- recall;
- specificity;
- balanced accuracy;
- positive prediction rate.

Also report holdout metrics separately for every held-out source.

Audit:
- tree depth / leaves;
- feature indices used;
- mapping of feature indices to semantic programme-feature names;
- whether any forbidden field entered the matrix (must be false).

## Frozen acceptance gate

Decision `V28I_LEGAL_STATE_RISK_PHENOTYPE_IDENTIFIABLE` only if:
1. mechanics PASS;
2. holdout precision >= 0.70;
3. holdout recall >= 0.60;
4. holdout balanced accuracy >= 0.75;
5. each of the two held-out HARD sources has recall >= 0.50;
6. each of the two held-out EASY sources has specificity >= 0.75;
7. tree depth <=3 and min leaf >=8 exactly as frozen.

Otherwise:
`V28I_LEGAL_STATE_RISK_PHENOTYPE_NOT_IDENTIFIABLE`.

Mechanical failure =>
`V28I_MECHANICS_INVALID`.

## Routing

If identifiable:
- freeze the compact legal state phenotype;
- open V28J mechanism/action discovery only within phenotype-positive states;
- runtime source identity remains forbidden.

If not identifiable:
- do not tune thresholds or tree depth;
- move to a bounded legal-history/stateful phenotype gate using the V28H explanatory window.

V28I never authorizes a Kaggle submission.
