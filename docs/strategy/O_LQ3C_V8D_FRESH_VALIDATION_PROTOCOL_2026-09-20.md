# O-LQ3C / V8D Fresh Paired Validation Protocol — 2026-09-20

## Frozen candidate

O-LQ3C is derived once from binding V8C `35516167350`.

Eligibility on exact ALL3 post-LQ2 action:
- O-LQ3 would change the market;
- exactly 4 nonempty SELL orders;
- exactly 6 HIRE orders;
- zero BUY operations;
- zero other nonempty market operations;
- MILK, WOOL and FERTILIZER all occur among SELL orders.

Treatment:
apply unchanged O-LQ3 priority `MILK -> WOOL -> FERTILIZER` for that turn only.
No thresholds, prices, opponent identity, seed or turn number are used.

## Fresh validation population

Opponents:
1. V48 — primary hard family;
2. V47 mirror — control;
3. Ready Stock — unrelated modern control.

Seeds:
`76001..76012`, both seats.

These seeds are frozen before execution.

## Paired design

For every opponent/seed/seat:
- exact ALL3 base;
- exact ALL3 + O-LQ3C treatment;
- identical seed and seat;
- pre-fire action parity required;
- exact engine `kaggle-environments==1.32.7`.

## Frozen gate

Mechanical PASS requires:
- all 72 paired contexts complete;
- zero failures;
- exact pre-fire parity;
- at least 4 V48 contexts where O-LQ3C fires;
- at least 2 combined control contexts where O-LQ3C fires.

Strategic PASS = **`V8D_CONDITIONAL_ORDER_FRESH_PASS`** only if all:
- V48 mean score delta > 0;
- V48 has >=1 positive-score context;
- overall win->nonwin regressions = 0;
- V47 mirror negative-score contexts = 0;
- Ready Stock negative-score contexts = 0.

If mechanics pass but activation coverage is below the frozen minimum:
`V8D_CONDITIONAL_ORDER_UNDERPOWERED`; the same frozen rule may only be evaluated on more untouched seeds, not changed.

If activation is sufficient but no W/L confirmation:
`V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION`; close O-LQ3C and activate pre-registered V9A.

Any score regression:
`V8D_CONDITIONAL_ORDER_REGRESSION_CLOSE`.

A PASS does not itself authorize Kaggle submission; it advances to broad seven-family regression/package readiness.

No automatic Kaggle submission.
