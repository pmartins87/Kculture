# ALL3 V14B Domain Phenotype Atlas — Conditional Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V14A RESULT.**

Activate only after a mechanically valid V14A result.

## Purpose

V14A answers *which broad domain has W/L upper-bound headroom*.
V14B does not test another hosted candidate. It localizes the reusable action/state phenotype inside
the V14A-passing domain before any first-party option is invented.

Opponent identity is evaluation metadata only and is forbidden as a runtime feature.

## Frozen source population

Use the same 24 V13C binding hard contexts and exact source SHAs.

For each context, replay:
- exact ALL3;
- exact shadow teacher;

and record turn-by-turn paired action/state differences.

No V14B context may be selected/dropped using V14A treatment magnitude. Population remains all 24
hard contexts; V14A passing modes only determine which difference dimensions are analyzed.

## Legal state features

At every divergence turn record candidate-visible quantities only:

Public own/opponent:
- money and money gap;
- unlocked quadrants;
- active plant/pasture counts;
- WHEAT/CARROT/TOMATO/STRAWBERRY/MELON counts and gaps;
- public hands count;
- public market prices if present;
- turn number and coarse phase:
  `EARLY <336`, `W2 336..503`, `W3 504..623`, `TERMINAL >=624`.

Own-private legal state:
- seed counts;
- shed inventory by product;
- carried inventory;
- own hand identities/state when available to the acting player.

Never record/use:
- opponent identity as candidate feature;
- opponent hidden/private inventory;
- future state;
- final outcome as a runtime condition.

## Action phenotype

For every teacher-vs-ALL3 divergence record:

### MARKET dimensions
- order-count delta;
- product set added/removed;
- per-product signed quantity delta;
- BUY/SELL side change;
- order-position/reordering changes;
- duplicate-product compaction/splitting;
- total projected sell units;
- total projected buy units.

### PHYSICAL dimensions
- farmer action/type/target difference;
- hand-action count difference;
- per-hand verb difference;
- PLANT crop substitution;
- BUY/SELL/BUILD/FEED/PROCESS physical verb substitution where applicable;
- target tile/worker/hand index changes.

### JOINT dimensions
- whether market and physical diverge on the same turn;
- first market divergence turn;
- first physical divergence turn;
- lead/lag between domains;
- whether one domain's divergence persists after the other begins.

## Branch selection from V14A

### If `V14A_MARKET_DOMAIN_HEADROOM`
Analyze MARKET dimensions only.

### If `V14A_PHYSICAL_DOMAIN_HEADROOM`
Analyze PHYSICAL dimensions only.

### If `V14A_BOTH_DOMAINS_HEADROOM`
Analyze MARKET and PHYSICAL independently first.
Do not create a joint policy unless neither domain has a recurrent phenotype meeting the recurrence gate below.

### If `V14A_CROSS_DOMAIN_INTERACTION_HEADROOM`
Analyze JOINT dimensions and earliest recurrent paired divergence only.

### If `V14A_SHADOW_UPPER_BOUND_NOT_REUSABLE`
V14B is not activated.

## Recurrence gate

A phenotype family is **recurrent** only if:

1. it appears in >=4 hard contexts;
2. spans >=2 unique source SHAs;
3. appears with the same direction/signature in >=75% of its occurrences;
4. can be expressed using legal candidate-visible state only;
5. does not require source/opponent identity.

For continuous quantities, family formation must use coarse predeclared buckets rather than fitted thresholds:

- quantity delta magnitude: `1`, `2`, `3-4`, `5+`;
- money gap: `<=-5000`, `-4999..-1000`, `-999..999`, `1000..4999`, `>=5000`;
- inventory count: `0`, `1`, `2-3`, `4+`;
- turn phase buckets defined above.

No post-hoc numeric threshold search.

## Decision

- >=1 recurrent legal phenotype:
  **`V14B_RECURRENT_DOMAIN_PHENOTYPE_READY`**
- divergences exist but none pass recurrence:
  **`V14B_DOMAIN_HEADROOM_NOT_COMPRESSIBLE`**
- mechanics invalid:
  **`V14B_MECHANICS_INVALID`**

If multiple recurrent phenotype families exist, do not rank by outcome because all rows derive from the same hard
population. Select the first family by deterministic ordering:
1. highest number of unique source SHAs;
2. then highest context support;
3. then earliest median turn;
4. then lexical phenotype key.

At most **one** first-party option family may be derived from V14B for the next causal gate.

## Next stage

A V14B-selected phenotype must be translated into a compact first-party candidate rule using only legal state,
frozen before evaluation, then tested on:
- the same hard contexts for causal discovery;
- untouched seeds for validation;
- broad regression controls.

No Kaggle submission is authorized by V14B.
