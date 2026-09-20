# O-LQ3C V8D-E2 Final Extension Protocol — 2026-09-20

## Trigger

V8D binding `35516560425`:
- V48 fire contexts 2/24.

V8D-E1 `35516899185`:
- V48 fire contexts 0/24.

Cumulative:
- V48 fire contexts = 2/48;
- zero score regressions;
- still below frozen minimum 4.

E2 was pre-authorized before E1 results and is the **final** extension.

## Candidate

Exact frozen O-LQ3C unchanged.

No change to:
- eligibility;
- SELL priority;
- operation counts;
- products;
- opponent handling;
- timing;
- thresholds.

## Fresh E2 population

Opponents:
- V48;
- V47 mirror;
- Ready Stock.

Seeds:
- `76025..76036`;
- both seats.

72 additional paired contexts.

## Final cumulative decision

Combine V8D + E1 + E2.

If cumulative V48 fire contexts < 4:
- **`V8D_CONDITIONAL_ORDER_RARE_CLOSE`**;
- close O-LQ3C;
- activate pre-registered V9A.

If cumulative V48 fire contexts >= 4:
apply original strategic gate:
- cumulative V48 mean score delta > 0;
- cumulative V48 positive-score contexts >=1;
- zero win->nonwin regressions overall;
- zero negative-score contexts in V47 mirror;
- zero negative-score contexts in Ready Stock.

All conditions true:
- `V8D_CONDITIONAL_ORDER_FRESH_PASS`;
- activate dormant V8E broad regression.

Coverage met but no W/L confirmation:
- `V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION`;
- close O-LQ3C;
- activate V9A.

Any score regression:
- `V8D_CONDITIONAL_ORDER_REGRESSION_CLOSE`;
- close O-LQ3C;
- activate V9A.

**No further seed extensions are permitted after E2.**

No automatic Kaggle submission.
