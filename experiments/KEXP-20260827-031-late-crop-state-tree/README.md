# KEXP-20260827-031 — richer late-crop public-state tree

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this follows KEXP-029

KEXP-029 deliberately tested the smallest plausible rule family: CARROT demand plus current CARROT/WHEAT price relation. It failed the predeclared temporal gate: the selected rule was perfect on its training positives (58/58) but only 10/15 = 66.7% precise on Aug-26 winners.

That failure says the top-meta decision depends on more state than demand + price alone. This experiment adds legally observable economic and productive context while keeping the learned policy intentionally small and interpretable.

## Frozen data protocol

Official public top-20 episodes per day.

Training/model-selection days: 2026-08-22, 23, 24, 25.
Strict temporal test: 2026-08-26.

At winner seed-buy events during states 600..647, pair observation frame `t` with action frame `t+1` and classify whether the action buys any CARROT seed rather than WHEAT-only.

No team, episode or seed identity enters the feature matrix.

## Legal public-state feature families

- step/horizon;
- own and opponent public money;
- relative money;
- own/opponent farm-hand count and unlocked quadrants;
- own private WHEAT/CARROT seed stock and shed stock;
- public WHEAT/CARROT prices and market inventories;
- complete-shop WHEAT/CARROT demand weights and derived ratios;
- own/opponent public crop counts, animal counts and weeds.

Opponent private seeds/shed are never used.

## Model family and temporal selection

Only shallow decision trees are considered:

- depth 2, 3 or 4;
- minimum leaf size 10, 20, 30 or 40;
- Gini or entropy criterion.

Hyperparameters are selected using leave-one-day-out validation across Aug-22..25. Aug-26 is untouched until the single configuration is selected.

A configuration is CV-eligible only if:

- worst held-out-day precision >= 0.60;
- mean held-out precision >= 0.70;
- mean held-out recall >= 0.10;
- at least 3 predicted-positive events on every held-out training day.

Selection prioritizes worst-day precision, then mean precision, then mean recall, with simpler trees preferred on ties.

## Predeclared gate

A tree becomes eligible to be distilled into one bounded R4D crop-response candidate only if:

- it passed the cross-day CV eligibility above;
- Aug-26 predicted-positive support >= 10;
- Aug-26 precision >= **0.75**;
- Aug-26 recall >= **0.15**.

Passing does not authorize validation or Kaggle submission. It authorizes only a controlled development candidate that converts a bounded amount of late WHEAT seed purchasing/planting inside KEXP-023's mechanically clean windows.

If this richer shallow tree fails, stop threshold/tree tinkering and move the crop branch to an explicit value model / bounded lookahead controller.

No validation or held-out seeds are accessed.

Tool: `tools/late_crop_state_tree.py`
Frozen tool blob: `54b1b7b97103cf22541518569122ecf139540be0`
