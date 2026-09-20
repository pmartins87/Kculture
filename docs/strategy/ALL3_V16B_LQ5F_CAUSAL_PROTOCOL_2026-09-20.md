# ALL3 V16B O-LQ5F W2 Fertilizer Queue +2 Causal Protocol — 2026-09-20

## Status

Frozen before V16B outcomes.

## Candidate

**O-LQ5F — W2 Fertilizer Queue +2**.

Input:
exact ALL3 after O-RW1 + O-TW1 + O-LQ2.

State:
one boolean `used`, initially false.

Eligibility:
- `used == false`;
- turn in `[336,503]`;
- ALL3 market contains at least one existing `SELL FERTILIZER` order.

Treatment:
- increase the quantity of the **first existing** SELL FERTILIZER order by exactly +2;
- preserve market order count;
- preserve all order positions;
- preserve every other order and quantity;
- preserve farmer/hands;
- set `used=true`.

No exact-turn whitelist.
No source/opponent identity, seed, rating, replay metadata or future state.

## Discovery population

All 24 binding V13C hard contexts from:
`configs/all3_v14a_hard_contexts.json`.

Paired:
- BASE exact ALL3;
- TREATMENT exact ALL3 + one-shot O-LQ5F.

Expected 24 pairs / 48 episodes.

## Mechanical gate

PASS requires:
- 24/24 pairs;
- zero failures;
- BASE exact frozen score/margin reproduction;
- pre-fire parity through first treatment fire;
- <=1 O-LQ5F fire per treatment episode;
- every fire in W2;
- treatment changes exactly one quantity field by +2;
- no physical change.

## Strategic gate

Coverage:
- fires in >=8 contexts;
- >=2 source SHAs.

**`V16B_LQ5F_WL_HEADROOM`** iff:
- mechanical PASS;
- coverage PASS;
- loss-to-win flips >=4;
- flips span >=2 source SHAs;
- mean score delta >0;
- mean margin delta >0.

If W/L threshold fails but mean margin delta >0:
**`V16B_LQ5F_MARGIN_ONLY_CLOSE`**.

If mean margin delta <=0:
**`V16B_LQ5F_NO_HEADROOM_CLOSE`**.

If insufficient coverage:
**`V16B_LQ5F_UNDERPOWERED`**.

Mechanics failure:
**`V16B_MECHANICS_INVALID`**.

## Fresh validation if PASS

Only `V16B_LQ5F_WL_HEADROOM` may activate V16C.

V16C is pre-frozen to:
- the same 10 exact hard-source SHAs;
- fresh seeds `78301..78304`;
- both seats;
- BASE vs the unchanged one-shot O-LQ5F.

Fresh PASS requires:
- all expected pairs mechanically clean;
- treatment fires in >=8 contexts;
- >=2 positive-score contexts;
- mean score delta >0;
- zero negative-score contexts;
- zero BASE-win -> treatment-nonwin regressions;
- mean margin delta >=0.

No candidate changes after V16B.

No Kaggle submission.
