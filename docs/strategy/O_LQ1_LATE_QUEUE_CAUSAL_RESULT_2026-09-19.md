# O-LQ1 Late Queue Sanitation — Fresh Causal Result — 2026-09-19

## Binding execution

Parallel workflow: **`35450434666`**  
Head: `a560518402957280072df63dfc4e4da01d804111`.

The serial-equivalent workflow `35450394649` was still running when the parallel gate completed.
The first mechanically valid completed execution is binding by the frozen protocol.

Parallel mechanical PASS:
- 8/8 seed shards PASS;
- 16/16 paired contexts;
- zero failures;
- pre-trigger parity PASS everywhere;
- farmer/hands unchanged everywhere.

## Binding decision

**`O_LQ1_V48_CAUSAL_FAIL`**

Fresh seeds `74301..74308`, both seats:

- BASE score rate: **0.0**;
- O-LQ1 score rate: **0.0**;
- mean score delta: **0.0**;
- mean margin delta: **0.0**;
- positive-score contexts: **0**;
- negative-score contexts: **0**;
- loss->tie: **0**;
- loss->win: **0**.

Yet O-LQ1 fired heavily:
- mean fire count: **100.875 turns/context**;
- changed market slots: **3,480**;
- cleared SELL slots: **2,770**;
- same-product SELL quantity reductions: **710**.

Despite thousands of market-action changes, terminal rewards and margins were unchanged.

## Interpretation

This is strong causal evidence that the dominant visual V48 transformations
(`SELL` clear / projected quantity clamp) are mostly **engine-semantic no-ops** relative to exact V47.

Therefore:
- O-LQ1 is closed;
- do not broad-regression it;
- do not add it to the option library;
- do not tune its start step or inventory projection.

The V4B/V4D loss->tie headroom remains real, but it must come from the subset of exact V48 market
differences that are **semantically effective**:
- exact quantity reallocation not reproduced by O-LQ1;
- SELL product replacement / queue movement;
- rare quantity increases;
- or interactions among those transformations.

## Next experiment

Open **V4E exact semantic-category decomposition** on the V4B/V4D discovery seeds.

Inside the binding W2+ interval (336–718), classify each current V47->V48 market slot difference as:
- CLEAR;
- SAME_PRODUCT_QTY_DOWN;
- SAME_PRODUCT_QTY_UP;
- SELL_PRODUCT_REPLACE;
- OTHER.

Test both:
1. isolated sufficiency of each category;
2. FULL exact V48 market;
3. FULL-minus-category necessity ablations.

The objective is to identify which exact category or interaction carries the W/L headroom before
writing another first-party approximation.

No Kaggle submission is authorized by O-LQ1.
