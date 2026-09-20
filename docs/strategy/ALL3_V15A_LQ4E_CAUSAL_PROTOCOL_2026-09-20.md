# ALL3 V15A O-LQ4E Early Fertilizer-before-Hire Causal Protocol — 2026-09-20

## Status

Frozen before V15A outcomes.

## Candidate

**O-LQ4E — Early Fertilizer-before-Hire**.

Input:
exact ALL3 output (O-RW1 + O-TW1 + O-LQ2).

Eligibility:
- observation step < 336;
- market contains at least one `SELL FERTILIZER`;
- market contains at least one `HIRE`;
- among target slots, at least one HIRE currently precedes a SELL FERTILIZER.

Treatment:
- identify occupied slots whose order is either `SELL FERTILIZER` or `HIRE`;
- stable-sort only those target orders by priority:
  1. SELL FERTILIZER;
  2. HIRE;
- leave all non-target slots unchanged;
- preserve exact market multiset and all quantities;
- preserve exact farmer/hands.

No opponent identity, source SHA, seed, rating, exact observed turn whitelist, replay metadata or future state.

## Discovery population

All and only the 24 binding V13C hard contexts from:
`configs/all3_v14a_hard_contexts.json`.

For each context run:
- BASE exact ALL3;
- TREATMENT exact ALL3 + O-LQ4E.

Same source SHA, seed and seat.

Expected:
- 24 paired contexts;
- 48 episodes.

## Mechanical gate

PASS requires:
- 24/24 paired contexts;
- zero failures;
- BASE exactly reproduces frozen V13C score and margin in every context;
- treatment pre-fire action path equals BASE through the first fire;
- treatment never fires at step >=336;
- treatment never changes farmer/hands;
- market multiset is preserved on every fire.

## Strategic gate

Coverage requires:
- treatment fires in >=8 contexts;
- fires span >=2 unique source SHAs.

**`V15A_LQ4E_WL_HEADROOM`** if:
- mechanical PASS;
- coverage PASS;
- loss-to-win flips >=4;
- those flips span >=2 unique source SHAs;
- mean score delta >0;
- mean margin delta >0.

If mechanical+coverage pass, no loss-to-win threshold, but mean margin delta >0:
**`V15A_LQ4E_MARGIN_ONLY_CLOSE`**.

If mechanical+coverage pass and no positive mean margin:
**`V15A_LQ4E_NO_HEADROOM_CLOSE`**.

If coverage fails:
**`V15A_LQ4E_UNDERPOWERED`**.

If mechanics fail:
**`V15A_MECHANICS_INVALID`**.

Margin-only does not authorize validation or hosted candidate.

## Pre-registered fresh validation if V15A passes

Only `V15A_LQ4E_WL_HEADROOM` may activate V15B.

V15B frozen population:
- the same 10 unique hard-source SHAs represented in V13C;
- fresh seeds `78201..78204`;
- both seats;
- exact source hashes;
- BASE vs frozen O-LQ4E.

Fresh validation PASS will require:
- all expected pairs mechanically clean;
- >=8 treatment-fire contexts;
- >=2 positive-score contexts;
- mean score delta >0;
- zero negative-score contexts;
- zero BASE-win -> treatment-nonwin regressions;
- mean margin delta >=0.

No condition or transformation may change after V15A.

No Kaggle submission is authorized by V15A.
