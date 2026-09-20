# ALL3 V14B MARKET Phenotype Atlas — Binding Result — 2026-09-20

Workflow: **`35526759114`**.

Decision: **`V14B_RECURRENT_DOMAIN_PHENOTYPE_READY`**.

## Mechanical result

- 24/24 V13C binding hard contexts replayed exactly;
- failures: 0;
- 4,490 market-divergence events;
- 137 coarse phenotype families;
- 90 families passed the pre-registered recurrence gate.

## Deterministically selected phenotype

The pre-registered ordering selected:

**`EARLY|REORDER`**

because it maximized source support/context support and then had the earliest median turn.

Support:
- contexts: **24/24**;
- source SHAs: **10/10**;
- occurrences: **148**;
- direction share: **1.0**;
- median turn: **150**;
- observed money-gap bucket: `-999..999`.

This phenotype says that the shadow teachers repeatedly preserve the same market multiset as ALL3
but use a different order during the EARLY phase. It does not by itself define which order should come first.

## Directional translation

A separate outcome-free translation workflow **`35532446891`** decomposed only those 148 selected
reorder events into teacher-preferred pairwise precedence relations.

Decision:
**`V14B_REORDER_DIRECTION_READY`**.

Selected relation:
- earlier: **`SELL FERTILIZER`**;
- later: **`HIRE`**;
- contexts: **24/24**;
- sources: **10/10**;
- occurrences: **48**;
- direction share: **1.0**;
- turns observed in the atlas: **96 and 120**;
- median turn: **108**.

No game outcome was used in this pairwise translation.

## Binding interpretation

The single first-party family allowed to advance is:

**O-LQ4E — Early Fertilizer-before-Hire**

Candidate semantics:
- EARLY phase only (`step < 336`);
- if exact ALL3 contains both `SELL FERTILIZER` and `HIRE`;
- preserve every market order and quantity;
- preserve all non-target occupied slots;
- stably reorder only target slots so every `SELL FERTILIZER` target precedes every `HIRE` target;
- never modify farmer/hands;
- never use opponent identity, source SHA, seed, rating, replay metadata, or future state.

The exact turns 96/120 are descriptive evidence only; the candidate trigger is the legal EARLY structural state,
not an exact-turn whitelist.

This candidate is not promoted. It must pass a causal W/L gate first.

No Kaggle submission.
