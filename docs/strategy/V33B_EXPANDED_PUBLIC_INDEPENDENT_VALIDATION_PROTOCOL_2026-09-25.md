# V33B — Expanded-Public Challenger Independent Validation Protocol — 2026-09-25

## Status
PRE-REGISTERED before any V33A R2 candidate outcome is observed.

This protocol activates only if V33A returns `V33A_EXPANDED_PUBLIC_CHALLENGER_READY`.

No V33B result authorizes automatic Kaggle mutation.

## Frozen candidate
Use exactly the single candidate selected by binding V33A R2:
- exact public ref;
- exact `main.py` SHA;
- exact acquired package bytes / snapshot provenance.

No fallback to second-best candidates is allowed if the selected candidate later fails.

## Baseline
Exact hosted V30B:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`.

## Independent validation population
Acquire a fresh V28B-style current public frontier after V33A selection is frozen.

Seeds exactly:
`80921,80922,80923,80924,80925,80926`.

Seats:
both 0 and 1.

Run exact candidate and exact V30B on all identical contexts.

## Package parity
Before scientific interpretation:
- construct deterministic submission-shaped package for selected candidate;
- exact packaged `main.py` SHA must equal V33A SHA;
- direct-vs-packaged parity exactly 8/8 on two frozen parity seeds and two fixed fresh opponents;
- failure => `V33B_MECHANICS_INVALID`.

## Frozen confirmation gate
Candidate confirms only if all:
1. mechanics PASS;
2. candidate score rate >= V30B + **0.08**;
3. mean paired score delta >= **+0.08**;
4. positive source breadth >=4;
5. positive seed breadth >=4/6;
6. positive paired contexts > negative;
7. positive support in both seats.

Decisions:
- `V33B_EXPANDED_PUBLIC_CHALLENGER_CONFIRMED`
- `V33B_EXPANDED_PUBLIC_CHALLENGER_NOT_CONFIRMED`
- `V33B_MECHANICS_INVALID`.

Routing:
CONFIRMED => perform read-only hosted-slot/quota preflight and request explicit user authorization before any submission.
NOT_CONFIRMED => close expanded-public route; no threshold lowering, no second-best fallback.
