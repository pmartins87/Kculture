# KEXP-20260825-004 — R4 public-base screen

## Question

Which attributed public architecture should become Kculture's first R4 economic baseline on the frozen `kaggle-environments==1.32.7` engine?

## Candidates

1. `cok-v8-779caae`
   - SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`
   - public-shop route controller with 3/4-quadrant mixed production, recovery controls and terminal market logic.
2. `seyamalam-v21-8b8c421`
   - SHA-256 `0cd14b653102d276c4f902fa3b8c6bd81d869b8ab64c422cb881b9d2346ec639`
   - 3-quadrant/12-hand mixed-farm route with public-state expert selection and late capital latch.

Both are public, attributed, hash-pinned artifacts. This experiment does not claim authorship over either policy.

## Protocol

Only `development` seeds are used.

- Each candidate versus the frozen seven-agent simple reference pool on the first 4 development seeds, both seats.
- Direct COK V8 versus Seyamalam V21 on the first 8 development seeds, both seats.
- Primary metrics: runtime errors, W/L/T, score rate with ties=0.5, and per-match bank delta.
- Selection priority: zero errors first; direct head-to-head score rate second; simple-pool robustness third; mean bank delta only as a tie-breaker.
- No validation or held-out seed may be opened for this base-selection screen.

## Promotion rule

The stronger public policy becomes `R4A-public-base`. It is a starting point, not the final Kculture contribution. Subsequent R4 experiments must make one auditable change at a time and compare against the frozen R4A base on identical seeds/opponents.

## Workflow

`.github/workflows/r4-public-base-screen.yml`

## Status

PENDING CI at experiment creation.
