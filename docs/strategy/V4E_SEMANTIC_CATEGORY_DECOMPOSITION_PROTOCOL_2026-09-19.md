# V4E Exact Semantic-Category Decomposition Protocol — 2026-09-19

## Purpose

V4B/V4D proved that exact V48 market behavior from step 336 onward changes V47 from loss to tie.
O-LQ1 proved that a first-party projected clear/clamp approximation changes thousands of action
slots but changes **zero rewards**.

Therefore the next question is not "how do we imitate the visible queue cleanup?" but:

**Which exact V48 market-difference category is causally responsible for the W/L headroom?**

## Discovery population

Reuse V4B/V4D discovery seeds:
`74101..74106`, both seats.

This is mechanism discovery, not validation. Any first-party rule derived from V4E must later use
fresh seeds.

Binding interval:
**W2+ = steps 336–718**.

Before step 336, exact V47 market is always used.

Exact V47 farmer/hands are always executed.

V48 is an offline shadow proposal source only.

## Current-state slot classification

At each step inside W2+, compare the current exact V47 and exact V48 market lists by slot, padding
shorter lists with `[]`.

Each differing slot is classified as exactly one of:

- `CLEAR`: V47 has SELL, V48 has empty slot;
- `QTY_DOWN`: both SELL same product, V48 quantity is lower;
- `QTY_UP`: both SELL same product, V48 quantity is higher;
- `REPLACE`: both SELL, different product;
- `OTHER`: every remaining difference;
- unchanged slots stay V47.

## Frozen variants

Positive control:
- **FULL**: exact V48 market inside W2+.

Sufficiency variants:
- **ONLY_SANITATION** = CLEAR + QTY_DOWN;
- **ONLY_REPLACE** = REPLACE;
- **ONLY_QTY_UP** = QTY_UP;
- **ONLY_STRUCTURAL** = REPLACE + QTY_UP + OTHER.

Necessity ablations:
- **FULL_MINUS_SANITATION**;
- **FULL_MINUS_REPLACE**;
- **FULL_MINUS_QTY_UP**;
- **FULL_MINUS_STRUCTURAL**.

BASE exact V47 is also run.

No other variant may be introduced after seeing the result without opening a new named experiment.

## Mechanical requirements

- 6/6 seeds, both seats;
- all episodes DONE;
- exact V47 physical action preserved;
- no physical fallback is expected; any fallback is recorded;
- FULL should reproduce the known V4B/V4D loss->tie behavior. If FULL does not, the gate is invalid.

## Interpretation

For each variant, report:
- score rate;
- mean paired score delta vs BASE;
- mean margin delta;
- contexts reproducing loss->tie;
- physical fallback count;
- category-application counts.

A category is **sufficient** if its ONLY variant reproduces score headroom in >=10/12 contexts.

A category/bundle is **necessary** if removing it from FULL reduces reproduced contexts by >=4.

If ONLY_STRUCTURAL is sufficient and FULL_MINUS_SANITATION preserves headroom, close queue-clear/clamp
as causal and derive a first-party structural rule.

If no isolated/bundled category is sufficient but one ablation is necessary, inspect interactions
inside that necessary category.

No Kaggle submission is authorized by V4E.
