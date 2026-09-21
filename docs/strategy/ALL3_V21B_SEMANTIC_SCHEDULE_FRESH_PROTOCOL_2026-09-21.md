# ALL3 V21B Semantic Schedule Fresh Validation Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V21A OUTCOMES.

Activate only if V21A returns:
`V21A_SEMANTIC_WL_HEADROOM`.

## Candidate

The candidate is exactly the single V21A mode selected by the frozen deterministic rule.

No category membership, scheduled turn, order content, threshold or O-TM1 projection rule may change after the V21A result.

## Untouched population

Same 10 exact source SHAs.

Fresh seeds:
- 78901
- 78902
- 78903
- 78904

Both seats.

Expected:
- 10 × 4 × 2 = **80 paired BASE vs selected-mode contexts**.

These seeds are frozen before any V21A outcome and are not used in V20A/V21A discovery.

## Mechanical gate

PASS requires:
- 80/80 unique pairs;
- zero failures/source drift;
- exact binding V19A schedule SHA;
- exact V21A selected mode loaded from binding V21A artifact;
- exact semantic category function/counts;
- no treatment action difference before P2 scope;
- farmer/hands never changed by the treatment;
- changed-market treatment fires in >=8 contexts.

## Fresh strategic PASS

`V21B_SEMANTIC_FRESH_PASS` iff:
- mechanical PASS;
- positive-score contexts >=2;
- positive-score contexts span >=2 source SHAs;
- positive-score contexts span >=2 fresh seeds;
- negative-score contexts =0;
- BASE-win -> treatment-nonwin regressions =0;
- mean score delta across all 80 contexts >0;
- mean margin delta across all 80 contexts >=0.

Otherwise:
- `V21B_SEMANTIC_FRESH_FAIL_CLOSE`;
- `V21B_SEMANTIC_UNDERPOWERED`;
- `V21B_MECHANICS_INVALID`.

No Kaggle submission is authorized by V21B alone.
