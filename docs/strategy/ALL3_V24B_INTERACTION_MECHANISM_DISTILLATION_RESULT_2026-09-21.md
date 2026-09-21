# ALL3 V24B Interaction Mechanism Distillation — Result — 2026-09-21

## Binding audit

Workflow: **`35645479016`**  
Job: `106484776088`  
Artifact: `10659194469`  
Digest: `sha256:57dbc846d235d2673922cb1a4c55c71938d12c9d4b5cba41a171bac40b2c1478`

Protocol:
`docs/strategy/ALL3_V24B_INTERACTION_MECHANISM_DISTILLATION_PROTOCOL_2026-09-21.md`.

Decision:

**`V24B_NOT_DISTILLABLE_COMPACTLY`**

## R1 — exact signature mechanism

Frozen training clusters:
- F01, F03, F05.

Frozen holdout clusters:
- F02, F04, F08.

Training occurrences: 21.  
Holdout occurrences: 42.

The best single training action-pair signature covers:
- **14/21 = 66.67%** of training;
- required: >=70%.

Therefore R1 fails before holdout.

The same training-dominant signature has:
- **0/42 = 0%** holdout coverage.

So there is no single canonical two-leg signature with the required cross-cluster generalization.

## R2 — compact legal-state classifier

R2 is not merely weak; its target is not identifiable.

The selected `M_TO_P|hands|2` family is present in:
- **93/93 hard contexts**.

Therefore:
- OTHER_HARD contexts without the family: **0**;
- interaction-exclusive contexts without the family: **0**;
- valid negative turn-0 states for the frozen target “family start event”: **0**.

More importantly, exact legal-state reconstruction at turn 0 found:
- unique legal 114-feature + ALL3-action states: **1**;
- conflicting legal-state keys: **1**.

That single identical runtime-observable state maps to both shadow market labels.

Thus no identity-free decision tree — or any deterministic function of the allowed legal state — can choose the correct first leg.

The missing discriminator is source/opponent-specific information, which is forbidden as a runtime feature.

## Consequence

The compact <=2-turn interaction controller family is closed.

Do not:
- lower R1 coverage thresholds;
- relabel OTHER_HARD as negatives despite containing the event;
- use source SHA/rank/cluster/opponent identity;
- train a per-source router;
- reopen MARKET_ONLY or PHYSICAL_ONLY patches.

Per the frozen V24B protocol, move to longer-horizon state-basin architecture.

Next block:
**`V25A_SHADOW_PREFIX_STATE_BASIN_HORIZON`**.

No V24C compact causal gate is opened.

No Kaggle submission is authorized.
