# ALL3 V18B Temporal Market-Controller Distillation Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V18A RESULT.**

Activate only if V18A returns one of:
- `V18A_SINGLE_PARTITION_HEADROOM`;
- `V18A_ADJACENT_PARTITIONS_HEADROOM`;
- `V18A_DISTRIBUTED_HEADROOM`.

Do not activate if V18A fails exact V14A replication.

## Architectural purpose

The causal programme has now falsified several isolated market edits even though V14A showed large cumulative market-domain W/L headroom.

V18B therefore stops selecting one hand-written edit at a time.

Instead, it will distill a **cumulative first-party market controller** over exactly the temporal scope selected by V18A.

No opponent/source identity may be used at runtime.

## Frozen temporal scope mapping

The V18A selected mode maps mechanically to V18B scope:

- `MARKET_P1_ONLY` -> turns 336..463;
- `MARKET_P2_ONLY` -> turns 464..591;
- `MARKET_P3_ONLY` -> turns 592..718;
- `MARKET_P12` -> turns 336..591;
- `MARKET_P23` -> turns 464..718;
- `MARKET_P123` -> turns 336..718.

The scope is determined only by V18A's frozen decision rule.

## Training-data population

Use the same 24 binding V13C hard contexts only for **controller discovery/training**.

For every turn in the selected scope, replay exact ALL3 BASE and record:

1. current legal observation available to our agent;
2. exact ALL3 action;
3. exact shadow-teacher market action from that context's pinned public source;
4. normalized V14B-style elementary market residual families.

The shadow teacher is an offline label source only.

## Runtime-prohibited features

The following may never enter training features or runtime inference:

- opponent/source SHA;
- notebook/ref identity;
- source rank;
- seed;
- context id;
- replay label;
- future state;
- eventual score/margin/result.

Seat may not be used as a predictive feature.

## Allowed feature families

Only current-state/action information legal at decision time:

- current turn / normalized progress within the selected scope;
- own money and own resource/product inventories;
- own shed/carried product quantities;
- public prices / public market state exposed by the environment;
- exact current ALL3 market queue structure;
- exact current ALL3 farmer/hands action;
- current legal observation fields independent of opponent identity.

No feature threshold may be chosen from causal game outcomes.

## Label universe

Use **all recurrent V14B market-residual families that occur inside the V18A-selected temporal scope** and are expressible as a legal first-party market mutation.

Do not select only one family.

The already tested isolated families (reorder, FERTILIZER +2, STRAWBERRY insertion) remain eligible as components because V18B tests cumulative interaction, not their standalone causal effect.

## Learning form

For each eligible residual family, train an independent deterministic shallow decision tree classifier:

- max depth: 4;
- min leaf support: max(8, 1% of training rows);
- class weighting allowed only to balance positive/negative examples;
- no hyperparameter search beyond these frozen values.

Training implementation may use sklearn offline, but every accepted tree must be exported to a pure JSON/rule representation and inference must be pure first-party Python with no sklearn dependency.

## Source-held-out validation

Use **leave-one-source-SHA-out** validation across the 10 unique hard sources.

A residual-family classifier is retained only if, aggregated over held-out-source predictions:

- positive support spans >=4 source SHAs;
- precision >=0.80;
- recall >=0.70;
- F1 >=0.75;
- zero use of prohibited features.

These thresholds are frozen before V18A result.

## Composition

At runtime inside the selected temporal scope:

1. compute exact ALL3 action;
2. evaluate every retained residual-family classifier;
3. apply all predicted residual edits in a deterministic canonical order:
   - removals / quantity decreases;
   - insertions / quantity increases;
   - duplicate compaction;
   - reorder canonicalization;
4. resolve conflicts by conservative semantics:
   - never sell more than currently legal own inventory;
   - never create invalid order cardinality;
   - never alter farmer/hands;
   - if two predicted edits are structurally incompatible, skip the lower-support family.

Family support is fixed from the training dataset, not game outcomes.

Outside the selected V18A temporal scope, return exact ALL3.

## Discovery gate

Before any causal games, the compiled controller must pass:

- pure-Python replay parity with exported trees;
- no prohibited runtime features;
- deterministic output;
- legal-action validation on every training/held-out row;
- retained families span >=3 distinct residual kinds;
- retained families span >=4 source SHAs.

If these fail:
**`V18B_CONTROLLER_NOT_DISTILLABLE`**.

If they pass:
**`V18B_CONTROLLER_READY_FOR_CAUSAL`**.

## Causal stage

A later V18C causal test, frozen before its outcomes, will compare:

- BASE exact ALL3;
- ALL3 + compiled V18B cumulative market controller;

on the same 24 hard contexts.

Only real W/L improvement can activate untouched fresh validation.

No Kaggle submission is authorized by V18B alone.
