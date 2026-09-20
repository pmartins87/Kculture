# ALL3 V16A W2 SELL-Quantity Phenotype — Binding Result — 2026-09-20

Workflow: **`35533351868`**.

Decision: **`V16A_W2_SELL_QUANTITY_PHENOTYPE_READY`**.

Eligible recurrent W2 SELL-quantity families: **11**.

Deterministically selected family:

**`W2|QTY|SELL|FERTILIZER|2`**

- direction: **INC**;
- selected increment: **+2**;
- contexts: **24/24**;
- source SHAs: **10/10**;
- dominant occurrences: **24**;
- direction share: **1.0**;
- median turn: **368**.

Event-level audit:
- exactly one selected-family occurrence per hard context;
- 20 contexts: ALL3 `SELL FERTILIZER 9` vs teacher `11`, turn 368;
- 4 contexts: ALL3 `SELL FERTILIZER 1` vs teacher `3`, turn 362.

No game outcome was used to select this family.

## Frozen candidate translation

Because the selected phenotype occurs exactly once per context, the causal candidate is **one-shot**:

**O-LQ5F — W2 Fertilizer Queue +2**

- active only during W2, turns 336..503;
- once per episode at the first eligible ALL3 action containing an existing `SELL FERTILIZER`;
- increase the quantity of the first existing `SELL FERTILIZER` order by exactly **+2**;
- do not add a new order;
- preserve order count and all order positions;
- preserve all other quantities;
- preserve farmer/hands;
- after one fire, never fire again that episode.

The exact descriptive turns 362/368 and quantities 1/9 are not runtime whitelists.

This is a discovery candidate only, not a promoted option.
