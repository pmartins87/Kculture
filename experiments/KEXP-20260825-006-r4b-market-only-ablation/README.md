# KEXP-20260825-006 — R4B market-only terminal ablation

## Question

How much of any R4B terminal effect comes from completing final market sales, and how much comes from changing physical unit actions to `DROP`?

## Mechanistic basis

On the frozen Kaggriculture engine:

- terminal reward is exactly `farm.money`;
- market processing happens after farmer/hand actions;
- a valid `SELL` commits one unit at a time;
- every sold unit earns a positive price with official `PRICE_FLOOR = 1`;
- step 718 is the last executable action before `DONE`/reward assignment.

This makes final sale-completeness an important ablation. The full R4B additionally changes physical unit actions to capacity-aware `DROP`; that intervention can have an opportunity cost if it replaces another productive final action.

## Candidate

`candidates/r4b_ablation_market_only.py`

It delegates all physical actions to the frozen R4A COK V8 policy unchanged. Only on step 718 it:

1. projects same-turn shed stock using the upstream execution-order helper;
2. keeps the first-occurrence ordering of R4A's existing SELL product types;
3. expands those SELLs to the full projected quantity;
4. removes terminal non-SELL market investment orders;
5. appends sales for projected sellable products omitted by the fixed route tape.

There are only nine sellable product types, below the default/official ten market-order cap.

## Development-only panel

First 8 development seeds, both seats:

A. market-only vs Seyamalam V21;
B. market-only vs frozen R4A;
C. full R4B vs market-only.

No validation or held-out seed is opened.

## Interpretation

- Market-only > R4A: final sale completeness has measurable value.
- Full R4B > market-only: capacity-aware extra DROP choices add value beyond market completion.
- Market-only >= full R4B: physical-action replacement is unnecessary or harmful; prefer the simpler terminal controller.
- Neither > R4A: move the next hypothesis upstream into supply/midgame adaptation.

Primary evidence remains W/L/T/score rate; money delta diagnoses the magnitude and direction of the terminal effect.

## Status

PENDING CI at experiment creation.
