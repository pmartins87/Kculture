# ALL3 V21A Semantic Schedule Decomposition Protocol — 2026-09-21

## Status

PRE-REGISTERED after V20A closed and before any V21A episode outcome.

## Question

The frozen V19A O-TM1 schedule is a heterogeneous 102-turn market replacement policy. V21A asks which **semantic subset of scheduled turns**, if any, carries reproducible W/L headroom on the already-consumed V20A discovery population.

This is causal decomposition, not another predictor.

## Frozen population

Reuse only the already-consumed V20A discovery population:

- same 10 exact source SHAs;
- seeds 78711..78716;
- both seats;
- 120 contexts.

No V21 validation seed is used in V21A.

## Frozen schedule

Binding V19A schedule:
- workflow 35552885627;
- SHA256 `c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22`;
- P2 scope 464..591;
- 102 scheduled turns.

Each scheduled turn is assigned exactly one category from its frozen raw scheduled market:

1. **EMPTY** — no nonempty scheduled market order;
2. **HIRE_PRESENT** — at least one HIRE order;
3. **SELL_PRESENT** — at least one SELL and no HIRE;
4. **BUY_ONLY** — nonempty, no HIRE, no SELL.

Frozen expected category counts:
- EMPTY: 40;
- SELL_PRESENT: 33;
- BUY_ONLY: 22;
- HIRE_PRESENT: 7.

Category assignment is outcome-independent.

## Frozen modes

Run exact ALL3 except on scheduled turns whose category is active in the mode.

Modes:

- BASE — no scheduled replacement;
- FULL — all four categories;
- EMPTY_ONLY;
- SELL_ONLY;
- BUY_ONLY;
- HIRE_ONLY;
- FULL_MINUS_EMPTY;
- FULL_MINUS_SELL;
- FULL_MINUS_BUY;
- FULL_MINUS_HIRE.

When a category is active, use the **unchanged exact V19A scheduled market** and the existing O-TM1 projection semantics. Farmer/hands remain exact ALL3.

No order edit, threshold, turn list or schedule content may be changed after outcomes.

## Hard mechanical binding

Before strategic interpretation:

- 120 unique contexts;
- zero source/replay failures;
- exact schedule SHA;
- exact frozen category counts;
- all 10 modes completed per context;
- BASE must exactly reproduce the V20A binding BASE score and margin for all 120 contexts;
- FULL must exactly reproduce the V20A binding unconditional-treatment score and margin for all 120 contexts;
- zero BASE/FULL binding mismatches;
- no physical action change from O-TM1.

Failure => `V21A_MECHANICS_INVALID`.

## Per-mode metrics

For each non-BASE mode versus BASE compute:

- positive-score contexts;
- negative-score contexts;
- positive-score source SHAs;
- positive-score seeds;
- BASE-win -> treatment-nonwin regressions;
- mean score delta;
- mean margin delta;
- changed-market coverage.

Margin is diagnostic and tie-breaking only. A margin-only mode cannot pass.

## W/L eligibility

A mode is W/L-eligible iff:

- positive-score contexts >=4;
- positive-score contexts span >=2 source SHAs;
- positive-score contexts span >=2 seeds;
- negative-score contexts =0;
- BASE-win -> treatment-nonwin regressions =0;
- mean score delta >0;
- mean margin delta >=0;
- changed-market coverage >=8 contexts.

## Deterministic selection

Among eligible modes select by, in order:

1. most positive-score contexts;
2. most positive-score seeds;
3. most positive-score source SHAs;
4. highest mean score delta;
5. highest mean margin delta;
6. fewer active semantic categories;
7. lexical mode name.

If at least one mode is eligible:
`V21A_SEMANTIC_WL_HEADROOM`.

Otherwise:
`V21A_SEMANTIC_NO_WL_HEADROOM`.

No post-hoc combination is allowed.

## Promotion

Only `V21A_SEMANTIC_WL_HEADROOM` activates V21B with the exact selected mode unchanged.

No Kaggle submission is authorized by V21A.
