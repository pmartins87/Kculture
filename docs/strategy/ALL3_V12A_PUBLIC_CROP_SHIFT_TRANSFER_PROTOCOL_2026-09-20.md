# ALL3 V12A Public Crop-Shift Regime Transfer Census Protocol — 2026-09-20

## Purpose

V11B found a strong hosted association between ALL3 losses and a legal public opponent crop regime.

V12A asks a narrower question **before any treatment is created**:

> Does that same public-state regime identify poor ALL3 outcomes against executable public agents on fresh exact-engine seeds?

This is still descriptive. It is a transfer gate for causal-option discovery, not a causal test.

## Frozen baseline

Exact ALL3:
- exact V47 host;
- O-RW1;
- O-TW1;
- O-LQ2.

No treatment or strategy modification.

Engine:
`kaggle-environments==1.32.7`.

## Frozen public league

Seven existing hash-pinned public families:

1. `v47_mirror`;
2. `ready_stock`;
3. `v48`;
4. `router_2715`;
5. `conditional_memory`;
6. `tactical_memory`;
7. `best_market`.

## Fresh seeds

`77001..77008`, both seats.

Total expected episodes:
**112**.

## Public regime measurement

At turns:
`456, 480, 504, 552, 600`

record own/opponent public:
- WHEAT;
- CARROT;
- TOMATO;
- STRAWBERRY;
- MELON;
- money.

Primary signal for an episode:

`opp_carrot_adv_any` =
at least one frozen checkpoint has opponent CARROT > own CARROT.

Strict diagnostic:

opponent CARROT - own CARROT >=4
AND
own WHEAT - opponent WHEAT >=4
at any frozen checkpoint.

Opponent identity is evaluation metadata only; it is forbidden as a future runtime condition.

## Mechanical gate

PASS requires:
- 112/112 episodes complete;
- zero failures;
- exact ALL3 action path only;
- all seven opponent families represented;
- both seats represented.

## Frozen transfer gate

Let signal-score rate use W/L score `loss=0, tie=0.5, win=1`.

**`V12A_PUBLIC_CROP_SHIFT_TRANSFER_READY`** only if all:

1. primary-signal support >= 8 episodes;
2. signal occurs in >= 2 opponent families with >=2 signal episodes each;
3. primary-signal loss rate >= 0.75;
4. primary-signal score rate <= 0.25;
5. non-signal support >= 16 episodes;
6. non-signal score rate - signal score rate >= 0.20.

If support exists but fails one or more outcome-separation criteria:
**`V12A_PUBLIC_CROP_SHIFT_NOT_DISCRIMINATIVE`**.

If support <8 or spans fewer than two families:
**`V12A_PUBLIC_CROP_SHIFT_TRANSFER_SPARSE`**.

If mechanics fail:
**`V12A_MECHANICS_INVALID`**.

## Next branch

Only `TRANSFER_READY` authorizes V12B causal macro-response oracle design.

V12B must:
- use only legal public state;
- never use opponent identity, seed, rating or future state;
- test bounded first-party response variants counterfactually;
- select a candidate by W/L, not margin alone;
- validate the frozen candidate on untouched seeds before option-library admission.

No automatic Kaggle submission.
