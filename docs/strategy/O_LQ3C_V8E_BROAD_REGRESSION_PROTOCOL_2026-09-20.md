# O-LQ3C V8E Broad Regression — Conditional Protocol — 2026-09-20

## Status

**DORMANT / PRE-REGISTERED BEFORE V8D RESULT.**

Activate only if V8D returns `V8D_CONDITIONAL_ORDER_FRESH_PASS`.
If V8D is underpowered, extend only V8D with untouched seeds and unchanged O-LQ3C.
If V8D closes/regresses, V8E remains dormant and pre-registered V9A activates.

## Frozen candidate

Use exact O-LQ3C bytes/semantics from V8D unchanged:

Eligibility on exact ALL3 post-LQ2 action:
- exactly 4 SELL;
- exactly 6 HIRE;
- zero BUY;
- zero other nonempty operations;
- MILK, WOOL and FERTILIZER all present;
- O-LQ3 actually changes their relative order.

Treatment:
`MILK -> WOOL -> FERTILIZER` stable ordering on the eligible turn only.

No retuning or additional condition is allowed after V8D.

## Broad population

Use all seven V2 public families:
- V47 mirror;
- Ready Stock;
- V48;
- router_2715;
- Conditional Memory;
- Tactical Memory;
- Best Market.

Fresh frozen seeds:
`76101..76106`, both seats.

Paired exact ALL3 vs ALL3+O-LQ3C.

## Gate

Mechanical PASS:
- all 84 paired contexts complete;
- zero failures;
- exact pre-fire parity.

Broad safety PASS requires:
- zero win->nonwin regressions overall;
- zero negative-score contexts in every opponent family;
- overall mean score delta >= 0;
- V48 mean score delta >= 0;
- at least one O-LQ3C fire in the broad matrix.

Decision:
- mechanics invalid -> `V8E_MECHANICS_INVALID`;
- any score regression -> `V8E_BROAD_REGRESSION_CLOSE`;
- mechanics/safety pass -> `V8E_BROAD_SAFE_PACKAGE_READY`;
- no fires -> `V8E_BROAD_NO_ACTIVATION_EXPAND_ONLY` (same frozen rule may be checked on more untouched seeds).

Margin-only changes are diagnostic and cannot override a score regression.

## Hosted policy if PASS

A V8E PASS authorizes package/readiness work, not an automatic submission.

If package parity also passes, preserve ALL3 as hosted control and use the other hosted slot for the new ALL3+O-LQ3C candidate rather than replacing the control immediately.

No automatic Kaggle submission.
