# O-LQ3C V8D-E1 Fresh Extension Protocol — 2026-09-20

## Trigger

Binding V8D workflow `35516560425` returned:
- `V8D_CONDITIONAL_ORDER_UNDERPOWERED`;
- mechanics PASS;
- 72/72 paired contexts complete;
- zero failures;
- zero negative-score contexts;
- V48 fire contexts = 2/24, below the frozen minimum of 4;
- controls already satisfy activation coverage.

This extension is therefore allowed by the frozen V8D protocol.

## Candidate

**O-LQ3C is byte-for-byte / semantics-for-semantics unchanged.**
No eligibility condition, ordering priority, threshold, opponent feature, seed feature or timing feature may change.

## Fresh extension E1

Opponents:
- V48;
- V47 mirror;
- Ready Stock.

Seeds:
- `76013..76024`;
- both seats.

Paired contexts:
- 24 per opponent;
- 72 total.

## Cumulative gate

Combine V8D + E1, yielding up to 48 paired contexts per opponent.

Mechanical validity requires:
- all E1 pairs complete;
- zero failures;
- exact pre-fire parity.

Then apply the **original V8D strategic gate cumulatively**:

PASS only if:
- cumulative V48 fire contexts >= 4;
- cumulative control fire contexts >= 2;
- cumulative V48 mean score delta > 0;
- cumulative V48 positive-score contexts >= 1;
- cumulative win->nonwin regressions = 0;
- cumulative negative-score contexts in V47 mirror = 0;
- cumulative negative-score contexts in Ready Stock = 0.

If cumulative activation coverage is met but there is still no W/L confirmation:
- `V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION`;
- close O-LQ3C;
- activate pre-registered V9A.

If any score regression occurs:
- `V8D_CONDITIONAL_ORDER_REGRESSION_CLOSE`;
- close O-LQ3C;
- activate V9A.

If cumulative V48 fire contexts remain <4:
- E1 remains underpowered;
- one **final** untouched extension E2 is pre-authorized on seeds `76025..76036`, both seats, same three opponents, unchanged O-LQ3C.
- If cumulative V48 activation is still <4 after E2, close O-LQ3C as operationally too rare for this line rather than extending indefinitely.

No automatic Kaggle submission.
