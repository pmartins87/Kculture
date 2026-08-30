# CR022B — recent official top-episode forecast tournament

Successful unchanged V2 run: `33282366031`  
Artifact: `9723382603`

The initial run failed only on a Python import path before any dataset/model result. V2 changed only that mechanical import defect; the frozen protocol remained unchanged.

## Data

- train date: 2026-08-27, top 20 episodes;
- episode-grouped fit/calibration: 18 fit episodes + 2 calibration episodes;
- chronological OOT test: 2026-08-28, top 20 episodes;
- 2026-08-29 public daily dataset was not accessible at run time;
- 112 legal public-state features;
- identity features: none;
- fit rows: 10,800;
- calibration rows: 1,200;
- OOT test rows: 12,000.

Targets are opponent SELL within current..next 3 turns.

## CARROT

Frozen CR007 remains the preferred actionable head.

CR007 on the same OOT test:

- Brier 0.01319;
- PR AUC 0.3083;
- ROC AUC 0.9694;
- threshold 0.90;
- precision **0.62**;
- coverage 0.00417;
- 50 triggers.

Histogram GBDT had slightly better Brier (0.01240) but lower actionable precision (**0.40**) and only 25 triggers. Logistic was substantially worse for high-confidence action selection.

Observed CARROT target sale quantities: mean 10.70, median 9. Sale-position distribution was relatively dispersed, with position 0 only 83/176 target events.

## STRAWBERRY

This is a real precision-vs-coverage tradeoff rather than a clean classifier replacement.

Frozen CR007:

- Brier 0.11338;
- PR AUC 0.4571;
- ROC AUC 0.7967;
- precision **0.8032**;
- coverage 0.01567;
- 188 triggers.

Histogram GBDT:

- Brier **0.09952**;
- PR AUC **0.5421**;
- ROC AUC **0.8541**;
- precision **0.7832**;
- coverage **0.02575**;
- 309 triggers.

GBDT ranks/calibrates better and exposes ~64% more actions, but loses ~2 percentage points of precision. It is not promoted from predictive metrics alone; extra coverage must pass response-value/full-game testing.

Observed STRAWBERRY target quantities: mean 6.78, median 4. Position 0 dominated (1,335/1,895 target events).

## MELON — strongest new prediction opportunity

No MELON head is deployed in CR008.

Regularized logistic L2 on OOT test:

- Brier **0.02858**;
- PR AUC 0.5657;
- ROC AUC 0.9017;
- calibration-selected threshold ~0.6166;
- precision **0.80995**;
- coverage **0.01842**;
- **221 triggers**.

Histogram GBDT had stronger ranking metrics but its calibration threshold generalized poorly to actionable precision (~0.468), so logistic is the safer research head.

Observed MELON target quantities: mean 8.19, median 6. Position 0 in 475/555 events (~85.6%).

This is prediction evidence only. MELON must pass a causal response test before any strategy candidate.

## TOMATO

Histogram GBDT had excellent Brier/ROC but the frozen calibration selected a threshold above all test probabilities, giving zero triggers. It is not actionable yet.

## Decision

CR022B does **not** justify wholesale replacement of CR007.

- Keep CR007 CARROT.
- Keep CR007 STRAWBERRY as canonical high-precision baseline until extra GBDT coverage proves game value.
- Open a separate causal MELON-response research branch using the logistic head.
- Prioritize the response controller: quantity, queue position, exact market counterfactual and abstention/CVaR.

CR022C therefore tests quantity only before adding classifier/product changes.
