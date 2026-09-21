# ALL3 V24A — Coupled Divergence Trace Discovery Protocol — 2026-09-21

## Status

PRE-REGISTERED after the binding V23B decision
`V23B_CROSS_DOMAIN_INTERACTION_HEADROOM` and before any V24 trace execution.

V24A is explanatory discovery only. It does not create, promote, or submit an option.

## Binding inputs

Use only immutable binding artifacts:

- V23A workflow: `35627972979`;
- V23A snapshot artifact: `all3-v23a-immutable-source-snapshot`,
  artifact ID `10655240502`,
  digest `sha256:12a6f45ebd3ed44c3d9b57d49b6a53d77514dccf48d8cddff17cb2c829c99054`;
- V23 config artifact from the same V23A workflow;
- V23B binding workflow: `35632311093`;
- V23B final aggregate artifact: `10656170070`,
  digest `sha256:6d626768832cd29029094bc8d4f129e6f78acece250fa39a67ed51530520509f`.

No Kaggle source reacquisition is allowed.

## Population

Trace **all 93 V23A hard contexts**, not a post-hoc subset.

For descriptive reporting, contexts are annotated as:

- `INTERACTION_EXCLUSIVE`: FULL_SHADOW score improves while both MARKET_ONLY and PHYSICAL_ONLY do not improve;
- `OTHER_HARD`: every other V23 hard context.

The binding V23B result contains 63 INTERACTION_EXCLUSIVE contexts spanning:
- 9 source SHAs;
- 6 V23 functional clusters;
- 4 seeds.

This annotation may be reported but may not remove contexts from trace execution.

## Trajectory

For each frozen hard context:

1. use the exact V47+ALL3 base from the immutable snapshot;
2. use the exact frozen source as both shadow teacher and opponent;
3. run the candidate on the **FULL_SHADOW trajectory**;
4. on every candidate turn, compute on the same legal observation:
   - exact ALL3 action;
   - shadow-teacher action;
5. return the shadow action, preserving the exact V23B FULL_SHADOW trajectory.

The final score and margin must exactly reproduce the binding V23B FULL_SHADOW row for that context. Otherwise V24A is mechanically invalid.

## Turn-level divergence definitions

At turn `t`:

- `M(t)`: ALL3 market action differs from shadow market action;
- `P(t)`: physical action differs, where physical means `farmer` and/or `hands`;
- physical kind is one of:
  - `farmer`;
  - `hands`;
  - `farmer+hands`.

### Frozen compact coupling topologies

Only these three topologies are eligible:

1. **SAME**
   - `M(t) && P(t)`;
   - lag = 0.

2. **M_TO_P**
   - a market-only divergence `M(t0) && !P(t0)`;
   - followed by a physical divergence at `t1`;
   - `1 <= t1-t0 <= 3`.

3. **P_TO_M**
   - a physical-only divergence `P(t0) && !M(t0)`;
   - followed by a market divergence at `t1`;
   - `1 <= t1-t0 <= 3`.

The 3-turn compact window is frozen before trace data. Longer-horizon state-basin effects are recorded as out-of-scope for V24A and cannot be converted post-hoc into a compact candidate.

## Event family

A family key is:

`(topology, physical_kind, lag)`

where:
- SAME always has lag 0;
- M_TO_P / P_TO_M have lag 1, 2, or 3.

For each context, retain only the **first occurrence** of each family.

For every retained occurrence record:
- start and end step;
- topology / lag / physical kind;
- exact ALL3 and shadow action keys;
- exact market/farmer/hands actions at the event;
- structural market verb profiles;
- legal player-observation 114-feature snapshot at event end;
- source SHA, functional cluster, seed, seat;
- V23B context annotation.

## Recurrence eligibility

A family is recurrent only if, within INTERACTION_EXCLUSIVE contexts, it appears in at least:

- 4 contexts;
- 2 source SHAs;
- 2 functional clusters;
- 2 seeds.

No outcome-value threshold or margin threshold is used to select a trace family.

## Frozen selector — "earliest recurrent coupled divergence"

Among recurrent families, select exactly one by this ordered rule:

1. smallest median **end step**;
2. greater number of functional clusters;
3. greater number of source SHAs;
4. greater number of seeds;
5. greater number of INTERACTION_EXCLUSIVE contexts;
6. smaller median lag;
7. lexical family key tie-break.

This selector is frozen before V24A data.

## Decisions

- `V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND`
  - at least one recurrent family exists;
  - exactly one selected family proceeds to distillation.

- `V24A_NO_COMPACT_RECURRENT_INTERACTION`
  - no family passes recurrence;
  - compact <=3-turn interaction control is closed;
  - next work must be long-horizon architecture/state-basin analysis, not threshold relaxation.

- `V24A_MECHANICS_INVALID`
  - any frozen source/snapshot mismatch;
  - any V23B FULL_SHADOW replay mismatch;
  - missing contexts;
  - episode failure;
  - duplicate/missing trace keys.

## Post-V24A restriction

If a family is selected:
- V24B may distill **one** identity-free interaction mechanism from that family;
- runtime opponent identity is forbidden;
- source rank/SHA is forbidden as a runtime feature;
- V24B must use legal player observation only;
- a later untouched fresh causal gate is mandatory before any hosted candidate;
- no V24A result authorizes Kaggle submission.
