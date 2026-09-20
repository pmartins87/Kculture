# ALL3 V12B Bounded Competitive Crop Response Oracle — Conditional Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V12A RESULT.**

Activate only if V12A returns:
`V12A_PUBLIC_CROP_SHIFT_TRANSFER_READY`.

If V12A is sparse or not discriminative, this protocol remains dormant and no CARROT-response treatment is run.

## Motivation

V11B found a strong hosted association between ALL3 losses and a legal public regime where the opponent shifts toward more CARROT while ALL3 remains WHEAT-heavy.

O-PC1 previously failed and remains closed. V12B does **not** revive its profit trigger or unlimited rotation.

The new question is causal and bounded:

> After the public crop-shift regime appears, can a small, first-party reallocation of future ALL3 WHEAT planting capacity toward CARROT improve W/L?

## Trigger

Use only legal public farm state.

Latch once per episode at the first monitoring checkpoint in:
`456, 480, 504, 552, 600`

where:
`opponent CARROT plant count > own CARROT plant count`.

No opponent identity, seed, rating, replay metadata or future state.

The response window ends 96 turns after the trigger.

## Candidate response mechanics

Use exact ALL3 action first.

A candidate has an episode conversion budget `B`.

Budgets:
- **B1** = 1 crop unit;
- **B2** = 2 crop units;
- **B4** = 4 crop units.

Within the response window and while budget remains:

1. If exact ALL3 intends to PLANT WHEAT and an unreserved own CARROT seed is already available, rewrite at most the remaining budget of WHEAT plant commands to CARROT.
2. If additional CARROT seed supply is needed and exact ALL3 issues BUY_SEED WHEAT, redirect at most the remaining needed units from WHEAT seed demand to CARROT while preserving total purchased seed units and respecting the exact market-order cap.
3. Never change farmer/hand position or action type except the PLANT crop argument.
4. Never modify non-WHEAT seed orders.
5. Never add a market order if doing so would exceed the configured market-order cap.
6. The total number of WHEAT->CARROT plant conversions over the episode may not exceed B.
7. After the response window or exhausted budget, exact ALL3 resumes unchanged.

If a seed redirection does not ultimately produce a crop conversion inside the response window, record it separately; it is not counted as a completed conversion.

## Fresh discovery population

If activated, use fresh seeds:
`77101..77104`, both seats,

against the same seven hash-pinned V12A public families.

For every opponent/seed/seat, run:
- BASE exact ALL3;
- B1;
- B2;
- B4.

Expected paired contexts:
56 baseline contexts, 168 treatment contexts.

## Mechanical gate

PASS requires:
- all expected episodes complete;
- zero failures;
- exact pre-trigger BASE/treatment parity;
- treatment never fires before the frozen public trigger;
- total completed conversions never exceed budget;
- no invalid market-order count.

## Discovery selection gate

Evaluate W/L only.

A budget is **eligible** only if:
- trigger occurs in >=8 paired contexts;
- trigger spans >=2 opponent families;
- positive-score contexts >=2;
- mean score delta >0;
- win->nonwin regressions <=1;
- no opponent family has mean score delta < -0.125.

If multiple budgets are eligible:
1. highest mean score delta;
2. then highest positive-minus-negative score context count;
3. then smaller budget.

Decision:
- >=1 eligible budget:
  `V12B_BOUNDED_CROP_RESPONSE_HEADROOM`;
- triggers occur but no eligible budget:
  `V12B_CROP_RESPONSE_NO_WL_HEADROOM`;
- insufficient treatment firing:
  `V12B_CROP_RESPONSE_UNDERPOWERED`;
- mechanics fail:
  `V12B_MECHANICS_INVALID`.

## Next gate

A V12B-selected budget is discovery-only.

It must be frozen and validated on untouched seeds in V12C across:
- the same public league;
- broad regression controls;
- no condition or budget changes after V12B.

No Kaggle submission is authorized by V12B.
