# KEXP-20260827-036 — terminal SELL impact ordering

Status: **COMPLETE / NO PROMOTION**

## Prize-first mechanism

The official market processes market-order **slots sequentially**: slot 0 from both players, then slot 1, etc. Within one slot, both players quote each unit from the same pre-commit market inventory. Therefore, when two players liquidate the same product in different slots, the player placing that product earlier receives the less-crashed price first.

Frozen R4B already solves terminal sale completeness, but its step-718 product ordering is not an explicit market-race optimization.

## Candidate

`candidates/r4d_terminal_sell_impact.py`

Everything in frozen R4B is preserved, including all physical actions and terminal SELL quantities. Only the order of existing step-718 SELL rows is changed. Products with larger self-price-impact exposure are placed earlier.

Candidate blob: `c3a21c93863f39c69ed7e8fe18852c5d4154b96a`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Frozen development gate

All 16 development seeds in both seats against Kaito V27, Rayk V11, Andrew V12 and frozen R4B directly.

Promotion required zero errors, modern-panel W/L no worse than 81-15, no meaningful family regression, direct score >=0.53125 and positive direct mean delta.

## Canonical result

GitHub Actions run **33043182635 — SUCCESS**.  
Artifact **9635044444**, ZIP digest **SHA-256 `26e6872363c8e25062f4e0ca34df5049604f1ba35589fdc9226b63c816dce51e`**.

Modern panel remained exactly unchanged in W/L:

- Kaito 25-7;
- Rayk 30-2;
- Andrew 26-6;
- combined **81-15**;
- zero errors.

Direct candidate vs R4B:

- **15-15-2**;
- score rate **0.50000**;
- mean terminal delta **+4.5625**;
- zero errors.

Seat split was strongly asymmetric (candidate seat0 10-5-1, seat1 5-10-1), reinforcing that the tiny money effect is market-order interaction rather than robust strength.

## Decision

**NO PROMOTION.** Reordering terminal SELL slots by self-impact does not improve prize-relevant W/L against R4B. The branch is closed as a standalone candidate.

No validation or held-out seeds were accessed.
