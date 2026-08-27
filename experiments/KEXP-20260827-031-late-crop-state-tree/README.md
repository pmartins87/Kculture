# KEXP-20260827-031 — richer late-crop public-state tree

Status: **COMPLETE / SHALLOW IMITATION TREE REJECTED**

## Why this followed KEXP-029

KEXP-029 showed that CARROT demand plus current CARROT/WHEAT price carried signal but did not generalize strongly enough. KEXP-031 added legal economic/productive context while deliberately restricting model capacity to shallow, auditable trees.

## Frozen protocol

Official public top-20 episodes per day. Winner seed-buy events in states 600..647, with exact observation frame `t` → action frame `t+1` alignment.

Training/model-selection: Aug-22..25 using leave-one-day-out validation.
Strict temporal test: Aug-26, untouched until hyperparameters were selected.

Legal features included step, own/opponent public money, relative money, workers/quadrants, own private WHEAT/CARROT seed and shed stock, public market prices/inventories, complete shop demand, public crop/animal counts and weeds. No team/episode/seed identity entered the model.

Tree family: depth 2..4, minimum leaf 10/20/30/40, Gini/entropy.

Predeclared CV eligibility required worst held-out-day precision >=0.60, mean precision >=0.70, mean recall >=0.10 and >=3 predicted positives every held-out day. Final Aug-26 gate additionally required support >=10, precision >=0.75 and recall >=0.15.

## Canonical result

Actions run **`33041559384` — SUCCESS**.
Artifact **`9634097003`**, ZIP digest **SHA-256 `c1d4ddd807d8191276772a6fc4c9da9fa1b359b300e40c939e3ce564ddfb9e78`**.

Best selected configuration under the frozen ordering:

- Gini;
- max depth 2;
- min leaf 10.

Leave-one-day-out precision / recall:

- Aug-22: **0.5542 / 0.7419**;
- Aug-23: **0.8800 / 0.7416**;
- Aug-24: **0.6429 / 0.4286**;
- Aug-25: **0.9355 / 0.7296**.

Mean precision **0.7531**, mean recall **0.6604**, but worst-day precision **0.5542 < 0.60**. Therefore the configuration is **not CV-eligible**.

Strict Aug-26 temporal test was strong descriptively:

- support 72 predictions;
- TP 68 / FP 4;
- precision **0.9444**;
- recall **0.6602**.

The fitted depth-2 tree mostly used CARROT/WHEAT price ratio, own weeds and public WHEAT market inventory. This is informative but cannot override the predeclared cross-day failure.

## Decision

**NO POLICY PROTOTYPE from the shallow imitation tree.**

Do not reinterpret the excellent Aug-26 result after the fact. The cross-day instability means a rule that imitates observed winner seed purchases is not robust enough to become our crop controller.

The crop branch now leaves threshold/tree imitation and moves to an **explicit value model / bounded lookahead**: estimate the terminal economic consequence of changing a WHEAT seed purchase/plant into CARROT under the actual current state, rather than predicting what a named high-Elo policy happened to do.

No validation or held-out seeds were accessed.

Tool blob: `661a78aa75648592f7aa291052afff9fadd1837d`.
