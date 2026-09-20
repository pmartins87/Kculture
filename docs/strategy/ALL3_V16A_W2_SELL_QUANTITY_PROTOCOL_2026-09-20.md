# ALL3 V16A W2 SELL-Quantity Phenotype Translation Protocol — 2026-09-20

## Status

Frozen after V15A ordering-family causal closure and before any new causal treatment.

## Motivation

V14A established strong post-turn-336 market headroom:
- MARKET_W2PLUS improved 18/24 hard contexts;
- mean score delta +0.75;
- zero regressions.

V15A then falsified the selected ordering mechanism:
- 48/48 O-LQ4E fires;
- exact zero outcome/margin effect.

The next orthogonal market dimension is **SELL quantity**, not another reorder rule.

## Source

Use the binding V14B artifact from workflow `35526759114`.

Do not regenerate the atlas on a changed population.

## Eligible phenotype families

Filter V14B recurrent families to all and only:

- phase = `W2`;
- kind = `QTY`;
- side = `SELL`;
- product is a real product, never `EMPTY/_`;
- recurrent under the already-frozen V14B gate:
  - context support >=4;
  - source support >=2;
  - dominant direction share >=0.75.

No game outcomes from V15A/V14A may be used to rank eligible quantity families.

## Deterministic selection

Choose exactly one family by:

1. highest unique source support;
2. highest context support;
3. earliest median turn;
4. lexical group key.

Record:
- product;
- direction INC/DEC;
- quantity magnitude bucket;
- support;
- median turn.

## Decision

If at least one eligible family exists:
**`V16A_W2_SELL_QUANTITY_PHENOTYPE_READY`**.

Otherwise:
**`V16A_W2_SELL_QUANTITY_NOT_COMPRESSIBLE`**.

## Candidate translation rule

The selected family may produce at most one first-party candidate.

For an **INC** selected family:
- active only during W2 (turns 336..503);
- exact ALL3 market must already contain at least one SELL of the selected product;
- increase the aggregate SELL quantity for that product by the **minimum integer in the selected bucket**:
  - bucket 1 => +1;
  - bucket 2 => +2;
  - bucket 3-4 => +3;
  - bucket 5+ => +5;
- apply the increment to the first existing SELL order of that product;
- do not add a new order if no product SELL exists;
- preserve all other orders/quantities/order positions;
- preserve farmer/hands.

For a **DEC** family, symmetrically subtract the minimum bucket integer, floor at zero, without adding/removing unrelated orders.

This deterministic bucket-to-integer mapping is frozen before selection result.

No exact turn whitelist, source identity, opponent identity, seed, rating or future state.

## Next stage

The translated candidate must undergo a paired causal gate on all 24 V13C binding hard contexts.

Only real W/L improvement may advance to fresh validation.

No Kaggle submission.
