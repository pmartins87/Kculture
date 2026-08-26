# KEXP-20260825-006 — R4B market-only terminal ablation

## Question

How much of the terminal effect comes from completing final market sales, and how much comes from changing physical unit actions to `DROP`?

## Mechanistic basis

On the frozen Kaggriculture engine:

- terminal reward is exactly `farm.money`;
- market processing happens after farmer/hand actions;
- a valid `SELL` commits one unit at a time;
- every sold unit earns a positive price with official `PRICE_FLOOR = 1`;
- step 718 is the last executable action before `DONE`/reward assignment.

This makes final sale-completeness an important ablation. The rejected full R4B additionally changed physical unit actions to capacity-aware `DROP`; that intervention can replace another useful final action.

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

No validation or held-out seed was opened during this experiment.

## Results

GitHub Actions run `32915111893` completed all three jobs with zero runtime errors.

| Matchup | W-L-T | Score rate | Mean money delta |
|---|---:|---:|---:|
| Market-only vs Seyamalam V21 | 16-0-0 | 1.0000 | +22,541.500 |
| Market-only vs frozen R4A | 5-3-8 | 0.5625 | +12.000 |
| Full R4B vs market-only | 5-11-0 | 0.3125 | -3.125 |

The ablation isolates the useful component: **final sale completeness helps, while replacing physical actions with extra `DROP`s is harmful on this panel**. Market-only also preserves the 16-0 result against Seyamalam achieved by full R4B while avoiding the direct regression against R4A.

Evidence artifacts from run `32915111893`:

- market-only vs R4A: artifact ID `9587953165`, archive SHA-256 `ef0b9a89f364176fb7fabe77561fb79bcc3bb6a3564b08d0c68e4e37b239f15b`;
- market-only vs Seyamalam: artifact ID `9588135603`, archive SHA-256 `ef9ceb2d92f40ff87ea79b9ab3abb0bf38e3ffd7f248753c8d61eed736201a50`;
- full R4B vs market-only: artifact ID `9588042346`, archive SHA-256 `820ef27b8ad8c87d78f1b9bcd4f2501cdfbf949d233c32b052cb157b9eac52f1`.

## Decision

The exact market-only implementation is selected as a **frozen validation candidate**. This is an engineering selection from development evidence, not yet an R4 promotion. Its next test is predeclared separately as `KEXP-20260825-007-r4b-market-only-validation` using all 16 validation seeds and both seats. Held-out remains sealed.

## Status

**DEVELOPMENT SCREEN PASS — frozen for validation, not yet promoted.**
