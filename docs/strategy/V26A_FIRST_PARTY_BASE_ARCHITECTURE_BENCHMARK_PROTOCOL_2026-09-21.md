# V26A — First-Party Base Architecture Benchmark Protocol — 2026-09-21

## Status

PRE-REGISTERED after binding V25A returned
`V25A_PERSISTENT_POLICY_REQUIRED` and before any V26A competitive outcome.

## Question

Does the existing **PrizeSolverV4** end-to-end adaptive architecture show real current-frontier W/L headroom over exact V47+ALL3?

This is an architecture benchmark, not an option search.

## Contenders

### CONTROL — ALL3
Exact V47 plus the frozen ALL3 option host:
- O-RW1;
- O-TW1;
- O-LQ2.

### TREATMENT — PrizeSolverV4
`solver.prize_solver_v4.PrizeSolverV4`.

Current properties:
- end-to-end state-adaptive farmer/hands/market policy;
- no replay tape;
- public-state opponent pressure model;
- heuristic ValueModel only;
- no learned value model active;
- no runtime opponent identity;
- no future/private forbidden information.

No V26A code or parameter tuning may use benchmark outcomes.

## Current-frontier acquisition

At workflow start:

1. query the current public Kaggriculture Top-30 exactly once;
2. acquire refs serially with bounded retry/backoff;
3. SHA-deduplicate exact sources;
4. smoke each unique source in both seats against starter;
5. exclude exact V47 identity;
6. select up to 12 unique executable representatives by current representative rank only;
7. minimum selected representatives: 8;
8. persist exact selected packages to an immutable workflow artifact before benchmark episodes;
9. remove Kaggle credentials before third-party execution.

Unavailable non-selected refs are recorded but do not invalidate the benchmark.

## Fresh seeds

Frozen fresh seeds:
`79501, 79502, 79503, 79504, 79505, 79506`.

Both seats.

Expected paired contexts with 12 selected sources:
`12 × 6 × 2 = 144`.

Each context runs:
- CONTROL vs exact frozen source;
- TREATMENT vs the same exact frozen source.

## Mechanical validity

Require:
- >=8 selected unique executable sources;
- both-seat smoke PASS for every selected source;
- exact immutable snapshot SHA verification;
- every paired context complete;
- CONTROL and TREATMENT both DONE/DONE, 720 steps, finite rewards;
- no runtime exception;
- no source reacquisition after snapshot;
- no missing or duplicate context keys.

Any failure:
`V26A_MECHANICS_INVALID`.

## Primary paired metrics

For each context:

`score_delta = PrizeSolverV4_score - ALL3_score`.

Report:
- positive / neutral / negative score contexts;
- mean score delta;
- mean margin delta;
- source-SHA support;
- seed support;
- functional outcome-cluster support derived from CONTROL outcome vectors only.

Margin is secondary and cannot pass the architecture gate alone.

## Frozen architecture-headroom gate

PrizeSolverV4 passes only if all are true:

1. positive-score contexts >= **8**;
2. positive-score contexts span >= **3 source SHAs**;
3. positive-score contexts span >= **3 fresh seeds**;
4. mean score delta > 0;
5. negative-score contexts <= positive-score contexts / 2;
6. CONTROL-win -> TREATMENT-nonwin regressions <= positive-score contexts / 2;
7. at least 2 CONTROL functional outcome clusters contain a positive-score context.

Decision:

### `V26A_PRIZE_SOLVER_BASE_HEADROOM`
All conditions pass.

Route:
- select materially different first-party architecture;
- reopen Prize Solver roadmap at PS2/PS3;
- first task is exact rollout/value learning on PrizeSolverV4, not hosted submission;
- preserve ALL3 only as control.

### `V26A_PRIZE_SOLVER_BASE_NOT_READY`
Mechanics pass but architecture-headroom gate fails.

Route:
- do not train/scale PrizeSolverV4 merely because it is architecturally clean;
- open V26B teacher-derived persistent-policy reconstruction viability;
- preserve best proven hosted candidates / publication track in parallel;
- do not return to ALL3 option mining.

### `V26A_MECHANICS_INVALID`
Repair mechanics only; exact rerun.

## Anti-overfit rules

- no seed/source-specific route;
- no parameter tuning from V26A outcomes;
- no horizon/threshold sweep;
- no public leaderboard submission from V26A;
- no replacing PrizeSolverV4 with V1/V2/V3 after seeing outcomes;
- no changing the selected frontier population after outcomes.

## Kaggle

No automatic submission is authorized.
