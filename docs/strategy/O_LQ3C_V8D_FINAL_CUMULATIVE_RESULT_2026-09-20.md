# O-LQ3C V8D Final Cumulative Result — 2026-09-20

## Executions

- V8D binding: `35516560425` — seeds 76001..76012;
- V8D-E1: `35516899185` — seeds 76013..76024;
- V8D-E2: `35517228393` — seeds 76025..76036.

All use the exact same frozen O-LQ3C candidate.

## Mechanical result

Across all three stages:
- 216 paired contexts total;
- 72 contexts per opponent;
- failures: 0;
- no score regressions;
- no candidate changes between stages.

## V48 cumulative

- contexts: 72;
- fire contexts: **6**;
- frozen minimum: 4 — coverage PASS;
- positive-score contexts: **0**;
- negative-score contexts: 0;
- nonwin->win: **0**;
- win->nonwin: 0;
- cumulative mean score delta: **0**.

Because all three stages have equal V48 context counts and each has mean score delta 0, cumulative mean score delta is exactly 0.

## Controls cumulative

V47 mirror:
- no negative-score contexts;
- no win->nonwin regressions.

Ready Stock:
- no negative-score contexts;
- no win->nonwin regressions.

E2 itself had:
- V47 mirror: 4 fire contexts, mean margin delta +25.9167, score delta 0;
- Ready Stock: 4 fire contexts, mean margin delta -11.4167, score delta 0;
- V48: 4 fire contexts, mean margin delta +17.5, score delta 0.

## Binding verdict

**`V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION`**

Coverage is now sufficient, so underpowered is no longer a valid interpretation.

The candidate is safe in this matrix but has no demonstrated W/L value on fresh V48 contexts. Margin-only effects cannot pass the frozen gate.

Therefore:
- **close O-LQ3C**;
- do not extend seeds;
- do not tune the 4-SELL+6-HIRE condition;
- keep V8E dormant;
- activate pre-registered V9A residual structural decomposition.

No automatic Kaggle submission.
