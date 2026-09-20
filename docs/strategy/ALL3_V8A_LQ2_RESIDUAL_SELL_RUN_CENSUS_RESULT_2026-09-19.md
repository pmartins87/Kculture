# ALL3 V8A LQ2 Residual SELL-Run Census — Result — 2026-09-19

## Binding execution

Workflow:
**`35479557496`**.

Mechanical:
- PASS;
- 4 frozen hard contexts;
- zero failures;
- exact ALL3 replay preserved.

## Verdict

**`V8A_ORDER_SEARCH_READY`**

Aggregate:
- LQ2-changed turns: **424**;
- eligible post-LQ2 multi-product SELL-run states: **170**;
- hard contexts with at least one eligible state: **4 / 4**;
- maximum distinct products in one SELL run: **6**.

Examples:
- step 673: FERTILIZER 10, MILK 2, WOOL 4, CARROT 2, WHEAT 2, EGG 4;
- step 577: STRAWBERRY 20, MILK 6, WOOL 1, FERTILIZER 9, EGG 6;
- step 673 in V48 contexts: 5-product WOOL/FERTILIZER/MILK/CARROT/WHEAT variants;
- step 600: 4-product MILK/STRAWBERRY/FERTILIZER/WOOL variants.

## Interpretation

LQ2 fixes quantity/compaction but preserves cross-product order. The hard contexts contain abundant
states where the order of multiple distinct SELLs could alter sequential market execution.

Therefore cross-product SELL order is structurally available and warrants a bounded causal oracle.

## Frozen V8B selection

Selection rule:
- per hard context rank by distinct products, non-empty SELL count, total quantity, earlier step;
- keep first state;
- keep at most one additional state separated by >=48 turns.

Frozen states:
- context 0: steps 673, 577;
- context 1: steps 673, 600;
- context 2: steps 673, 600;
- context 3: steps 673, 577.

Config:
`configs/all3_v8b_lq2_order_states.json`.

V8B tests every unordered pairwise transposition within each frozen run, changing only order and
preserving products/quantities/physical actions.

No Kaggle submission is authorized by V8A.
