# V32C — CHA22 Independent Primary Confirmation — 2026-09-24

## Status
PRE-REGISTERED after V32A completed with decision `V32A_NEW_PUBLIC_POLICIES_NO_ADVANTAGE`.

V32A remains binding and closed. This is a new independent confirmation of the single strongest V32A near-miss; no V32A threshold is lowered or reinterpreted.

No V32C result authorizes Kaggle mutation.

## Frozen candidate
Exact public policy:
- ref `abhinav0370/kaggriculture-cha22-agent`;
- SHA `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`.

V32A evidence motivating confirmation:
- score rate 0.9583333333;
- exact V30B baseline 0.8541666667;
- mean paired score delta +0.1041666667;
- 18 positive / 0 negative contexts;
- positive seed breadth 4/4;
- both seats;
- positive source breadth 3, below frozen V32A threshold 4.

## Baseline
Exact hosted V30B:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`.

## Independent population
Acquire a new current public frontier after this protocol is committed. It must be distinct from the V32A snapshot artifact.

Seeds exactly:
`80811,80812,80813,80814,80815,80816`.

Seats:
both 0 and 1.

Run exact V30B and exact CHA22 on every identical context.

## Frozen confirmation gate
CHA22 confirms only if all:
1. mechanics PASS;
2. candidate score rate >= V30B + 0.08;
3. mean paired score delta >= +0.08;
4. positive source breadth >=4;
5. positive seed breadth >=4/6;
6. positive paired contexts > negative paired contexts;
7. positive support in both seats.

Decisions:
- `V32C_CHA22_PRIMARY_CONFIRMED`
- `V32C_CHA22_PRIMARY_NOT_CONFIRMED`
- `V32C_MECHANICS_INVALID`

Routing:
CONFIRMED => freeze exact source/package, run package parity and a read-only hosted-slot preflight; then request explicit user authorization before any Kaggle submission.
NOT_CONFIRMED => close CHA22 path; do not tune or lower thresholds.
