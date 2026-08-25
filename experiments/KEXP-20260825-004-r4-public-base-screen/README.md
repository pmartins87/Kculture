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

Only `development` seeds were used.

- Each candidate versus the frozen seven-agent simple reference pool on the first 4 development seeds, both seats.
- Direct COK V8 versus Seyamalam V21 on the first 8 development seeds, both seats.
- Primary metrics: runtime errors, W/L/T, score rate with ties=0.5, and per-match bank delta.
- Selection priority: zero errors first; direct head-to-head score rate second; simple-pool robustness third; mean bank delta only as a tie-breaker.
- No validation or held-out seed was opened.

## Results

GitHub Actions run: `32868407585` (PASS). Artifact: `9571507013`, archive SHA-256 `a376eced29b8595c39356436043fcddd407664e883b33535e506d0b1c170bcf6`.

### COK V8 vs simple pool

- 56 games: **56W-0L-0T**, zero errors.
- Mean bank delta: **+136,298.45**.
- Median bank delta: **+144,905**.
- Range: **+86,736 to +181,866**.

### Seyamalam V21 vs simple pool

- 56 games: **56W-0L-0T**, zero errors.
- Mean bank delta: **+151,034.84**.
- Median bank delta: **+153,663.5**.
- Range: **+88,302 to +168,390**.

V21 produced more cash against weak/simple opponents, which makes it a useful archived opponent and economic reference. This metric was deliberately secondary to direct head-to-head strength.

### Direct head-to-head — COK V8 vs Seyamalam V21

Across 8 development seeds × both seats:

- **COK V8: 14W-2L-0T**.
- Score rate / win rate: **0.875**.
- Zero runtime errors.
- Mean bank delta: **+21,063.875**.
- Median bank delta: **+21,797**.
- Range: **-1,365 to +38,860**.
- The only losses were seed `583180324`, both seats: `-1365` and `-1335`.

## Decision

**PASS. `cok-v8-779caae` is promoted as `R4A-public-base-v1`.**

This follows the pre-registered rule: both candidates were runtime-clean, and COK won the direct matchup decisively despite V21's higher simple-pool cash production.

This is an engineering base, not a claim that COK V8 is the strongest available public policy. During this experiment, fresher public Kaggle agents with higher reported/best ladder scores were discovered. They must be acquired and added to the strong-opponent panel before R4 is considered complete.

## Reproduction

Workflow: `.github/workflows/r4-public-base-screen.yml`. It is retained as a manual `workflow_dispatch` reproduction workflow after this experiment; it no longer runs on every push.

Structured metrics: `metrics.json`.
