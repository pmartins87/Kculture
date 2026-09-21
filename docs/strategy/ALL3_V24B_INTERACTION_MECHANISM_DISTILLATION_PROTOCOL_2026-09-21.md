# ALL3 V24B — Interaction Mechanism Distillation Protocol — 2026-09-21

## Status

PRE-REGISTERED after V24A selected `M_TO_P|hands|2` and before inspecting the selected event-state feature distribution or action-signature frequencies in detail.

V24B is a distillation block. It may produce at most one identity-free candidate mechanism for fresh causal testing. It does not promote or submit anything.

## Binding V24A result

Workflow: `35641081142`.  
Decision: `V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND`.  
Selected family: **`M_TO_P|hands|2`**.

Frozen family properties:
- topology: market-only divergence -> physical hands divergence;
- lag: 2 turns;
- median start step: 0;
- median end step: 2;
- interaction-exclusive coverage: 63/63 contexts;
- source SHAs: 9;
- functional clusters: 6;
- seeds: 4.

## Goal

Determine whether the recurrent two-turn sequence can be represented by one compact, identity-free, legal-runtime mechanism.

The mechanism must explain both:
1. the turn-0 market divergence;
2. the turn-2 hands divergence that follows on the resulting trajectory.

A market-only one-turn patch is forbidden because V23B MARKET_ONLY failed the frozen multi-seed gate.

A physical-only patch is forbidden because V23B PHYSICAL_ONLY produced 0 score improvements.

## Inputs

Use only:
- V24A selected occurrences for `M_TO_P|hands|2`;
- legal player observation;
- exact ALL3 base action;
- exact shadow action only as offline label;
- V23 functional cluster only for train/holdout stratification, never as runtime feature.

Forbidden runtime inputs:
- source ref;
- source SHA;
- source rank;
- functional cluster;
- opponent identity;
- V23/V24 outcome label.

## Frozen train/holdout split

Split by functional cluster, not by row.

Order V23 functional clusters lexically.

Training clusters:
- odd lexical positions: F01, F03, F05.

Holdout clusters:
- even lexical positions: F02, F04, F08.

This split is fixed before feature inspection.

All occurrences from a cluster remain entirely on one side.

## Candidate representation

V24B may only consider two representations, in this order:

### R1 — exact action-signature mechanism

If one canonical pair of labels covers at least:
- 70% of training occurrences;
- all 3 training clusters;
- at least 3 training source SHAs;
- at least 2 training seeds;

then define a candidate as:

- trigger on the legal state/action predicate distilled from that dominant signature;
- at trigger turn t, replace only the market component;
- arm a two-turn pending state;
- at t+2, replace only the hands component;
- farmer remains ALL3 in both turns.

If R1 passes holdout coverage >=50% across all 3 holdout clusters, select R1.

### R2 — compact state classifier

R2 is considered only if R1 cannot be represented by one legal deterministic predicate or fails holdout coverage.

Inputs:
- 114 legal `solver.programme_features`;
- current ALL3 action structural features:
  - market verb counts;
  - farmer verb/kind;
  - hand count;
- no source/identity fields.

Model family is fixed:
- deterministic decision tree;
- max_depth <= 3;
- min_samples_leaf >= 8;
- class_weight balanced;
- random_state 20260921.

Target:
- whether the current state is a V24A family start event.

Negative rows:
- legal turn-0 states from OTHER_HARD contexts;
- plus legal non-event turn-0 states from interaction-exclusive contexts if present.

The tree may only trigger the **market first leg**.

The second leg is stateful and deterministic:
- exactly t+2;
- hands replacement only;
- only if the pending state remains in the same episode;
- cancel on episode reset.

No second classifier is allowed.

## Label/action distillation

The market and hands replacements must be expressed without calling a third-party teacher at runtime.

Allowed:
- direct deterministic transformation of the ALL3 action;
- deterministic action literal if invariant and legal;
- deterministic transformation based on legal state values.

Forbidden:
- teacher/shadow query at runtime;
- source-specific lookup;
- nearest-neighbor retrieval keyed by source;
- memorized per-opponent action table.

## R1/R2 acceptance before causal testing

A distilled mechanism is `V24B_DISTILLABLE` only if:

1. identity-free runtime;
2. no third-party call at runtime;
3. train trigger precision >=0.80;
4. train trigger recall >=0.50;
5. holdout trigger precision >=0.70;
6. holdout trigger recall >=0.40;
7. all 3 holdout clusters represented;
8. selected market action transformation matches V24A shadow label on >=70% of triggered holdout starts;
9. selected t+2 hands transformation matches V24A shadow label on >=70% of corresponding holdout second legs;
10. no post-hoc threshold search.

Otherwise:
`V24B_NOT_DISTILLABLE_COMPACTLY`.

## Output

If distillable:
- emit exactly one mechanism spec;
- freeze it before any causal outcome test;
- open V24C fresh causal validation on untouched seeds.

If not distillable:
- close compact <=2-turn controller distillation;
- move to longer-horizon state-basin architecture, not threshold relaxation.

No Kaggle submission is authorized.
