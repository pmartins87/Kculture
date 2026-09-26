# V35A — Hosted-Score Public Agent Preflight Protocol — 2026-09-26

## Status

**PRE-REGISTERED BEFORE MECHANICAL RESULTS.**

This family is opened because two new facts invalidate the breadth interpretation of V33A without changing V33A's own result:

1. our strong offline V30B/V31C evidence transferred poorly to the live ladder;
2. V33A's `kaggle kernels list --sort-by scoreDescending` discovery population omitted public notebook artifacts with materially stronger observed hosted Public Scores.

This is a discovery-method correction, not threshold shopping.

## Purpose

Use the strongest directly observed **hosted-score evidence** still legally/publicly available before the final submission deadline.

V35A is intentionally a **mechanical / provenance / package preflight**, not another local tournament whose result can veto strong live-ladder evidence.

## Frozen candidate A — Barnyard Economist V7

- public notebook: `romanrozen/strong-barnyard-economist`;
- exact public version: **7**;
- Kaggle scriptVersion observed: `341074820`;
- observed Public Score on 2026-09-26: **3034.8**;
- observed Best Score: **3034.8 V7**;
- notebook license: **Apache-2.0**;
- acquisition handle: `romanrozen/strong-barnyard-economist/versions/7`.

## Frozen candidate B — Kaito Fast Routes V2

- public notebook: `kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes`;
- exact public version: **2**;
- Kaggle scriptVersion: `341206423`;
- observed Public Score for V2: **3009.0**;
- observed Best Score: **3009.0 V2**;
- notebook license: **Apache-2.0**;
- acquisition handle: `kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes/versions/2`.

The two candidates are not selected because of local V35 results. They are selected before execution from public hosted evidence.

## Frozen V35A checks

For each candidate:

1. download the exact versioned notebook output with KaggleHub;
2. require exactly one unique tar/tar.gz package containing root `main.py`;
3. preserve the original published archive bytes;
4. record archive SHA-256, `main.py` SHA-256, members and byte sizes;
5. load using the same last-callable semantics used by our existing hosted-faithful tooling;
6. run full 720-step smoke episodes on `kaggle-environments==1.32.7`:
   - seeds `81001, 81002`;
   - both seats;
   - opponent `starter`;
7. require statuses `DONE/DONE`, finite rewards and >=720 recorded steps in all 4 smoke contexts.

The smoke gate tests only **runnability and packaging**. Win/loss versus starter is diagnostic and cannot override the candidates' hosted-score evidence.

## Hosted read-only preflight

After package checks:

- list current team submissions;
- verify/record current latest-two;
- record UTC-day submission count and current submission-limit response;
- perform **no submission**.

Expected latest-two before any user-authorized mutation:
1. V31C `56528406`;
2. V30B `56509591`.

If both candidate packages pass and latest-two is unchanged, decision:
`V35A_BOTH_HOSTED_STRONG_PACKAGES_READY_FOR_USER_DECISION`.

If only one passes:
`V35A_ONE_HOSTED_STRONG_PACKAGE_READY_FOR_USER_DECISION`.

If latest-two drifted:
`V35A_PACKAGE_READY_SLOT_DRIFT_REVIEW_REQUIRED`.

If neither package is mechanically valid:
`V35A_NO_PACKAGE_READY`.

## Submission routing

**No automatic Kaggle submission is permitted.**

If both exact packages are ready, the default recommended hosted experiment is two sequential submissions, subject to a fresh explicit user authorization:

1. Barnyard V7 first — this would evict the currently older V30B;
2. Kaito V2 second — this would then evict V31C;

leaving both hosted-score-backed public candidates active.

The order may be revised only if the read-only slot state or package evidence changes before authorization.

## Why local high-upside gates are not repeated here

The project now has direct evidence that the previous local evaluator can rank policies very differently from the live ladder. A recent public Kaggriculture analysis independently reported essentially zero initial correlation between one local evaluator and its real ladder sample before replacing the opponent panel with realistic ladder agents.

In the final days, another broad offline tournament would consume time while applying a metric already shown to have weak transfer. V35A therefore limits local work to mechanics/integrity and lets hosted evidence drive the decision.
