# ALL3 V24A Coupled Divergence Trace — Result — 2026-09-21

## Binding result

Workflow: **`35641081142`**  
Aggregate job: `106472979988`  
Artifact: `10658097764`  
Digest: `sha256:8b8599ea2c9a4ba884e78906aee388ef981a69983e179dee4f694cba68881222`

Mechanical:
- 4/4 trace shards PASS;
- 93/93 hard contexts reproduced;
- exact V23B FULL_SHADOW replay required and satisfied;
- 0 failures;
- immutable V23A source snapshot only.

Decision:

**`V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND`**

Eligible recurrent families: **19**.

Frozen selector chose:

**`M_TO_P|hands|2`**

Properties:
- topology: market-only divergence -> hands divergence;
- lag: 2 turns;
- median start step: 0;
- median end step: 2;
- interaction-exclusive contexts: **63/63**;
- source SHAs: **9**;
- functional clusters: **6** — F01, F02, F03, F04, F05, F08;
- seeds: **4** — 79302, 79304, 79305, 79306;
- OTHER_HARD contexts also containing the family: **30/30**.

## Action structure

Exact ALL3 turn-0 action is invariant across all 63 interaction-exclusive occurrences:

`market = [BUY_PRODUCT WHEAT 7, SELL WHEAT 2]`

The shadow first leg has two variants:

1. 49/63 overall:
   - BUY_PRODUCT WHEAT 20
   - SELL WHEAT 15
   - BUY_SEED WHEAT 1

2. 14/63 overall:
   - BUY_PRODUCT WHEAT 5
   - BUY_SEED WHEAT 1

At t+2, the physical hands leg is invariant across all 63 occurrences:

ALL3:
- [PICKUP COW]
- [PASS]
- [NORTH]
- [NORTH]
- [PICKUP COW]

Shadow:
- [PICKUP COW]
- [WEST]
- [NORTH]
- [NORTH]
- [PICKUP COW]

Thus the recurrent structure is real, but its first market leg is not globally invariant.

Next gate:
`V24B_INTERACTION_MECHANISM_DISTILLATION`.

No Kaggle submission is authorized.
