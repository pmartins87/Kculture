# KEXP-20260825-007 — R4B market-only validation

## Purpose

Test the exact market-only candidate frozen after `KEXP-20260825-006` on the untouched validation partition. The 32 held-out seeds remain sealed.

## Frozen candidate

- path: `candidates/r4b_ablation_market_only.py`
- development source commit: `148cc81fed390fd75c0cba00ceb779efaa17a46f`
- frozen candidate Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- freeze config: `configs/r4b_market_only_candidate.json`
- base: `R4A-public-base-v1` / COK V8, hash-pinned Apache-2.0 source

The validation workflow independently verified that exact Git blob before every candidate matchup.

## Predeclared protocol

All 16 validation seeds, both candidate seats, frozen `kaggle-environments==1.32.7`:

A. R4A vs Seyamalam V21 — validation control.
B. Frozen market-only candidate vs Seyamalam V21.
C. Frozen market-only candidate vs frozen R4A.

96 total executions.

PASS required all of:

1. zero runtime errors in all blocks;
2. direct score rate vs R4A >= 0.50;
3. direct mean money delta vs R4A >= 0;
4. candidate wins vs Seyamalam >= R4A-control wins;
5. candidate mean delta vs Seyamalam >= R4A-control mean.

## Result — PASS

GitHub Actions run `32918640409`, workflow source commit `c629328bc0282a778a42e8b61923a18c8d13ce6c`.

| Matchup | W-L-T | Score rate | Mean money delta | Errors |
|---|---:|---:|---:|---:|
| R4A control vs Seyamalam V21 | 30-2-0 | 0.9375 | +18,053.625 | 0 |
| Market-only vs Seyamalam V21 | 32-0-0 | 1.0000 | +18,885.875 | 0 |
| Market-only vs R4A | 8-6-18 | 0.53125 | +165.03125 | 0 |

Every predeclared condition passed. The candidate improved the independent Seyamalam control by two wins and +832.25 mean money delta while also finishing above 0.50 direct score and above zero direct mean against its own R4A base.

### Preserved artifacts

- R4A control vs Seyamalam: artifact `9589171677`, ZIP SHA-256 `d2486970897fa80d73614893110c45c3c3a684e1105dd9812c8ea19ce6b1b336`.
- Market-only vs Seyamalam: artifact `9589181975`, ZIP SHA-256 `f2c7081adf8028369d8990f8a3d1b5d47c0d5d907e189a47a2c540e84e1f7827`.
- Market-only vs R4A: artifact `9589181047`, ZIP SHA-256 `45f34954c0122409f1197294faf7bd273b9eba689bad063d72b36b8c02cf0564`.

## Decision

**VALIDATION PASS.** Promote this exact artifact to `R4B-market-only-validated-v1`, suitable for self-contained package parity and the first hosted-ladder submission candidate.

This does **not** declare R4 overall complete or top-10 strength. Stronger public opponents are still to be acquired/evaluated and hosted ladder evidence is still missing.

The 32 held-out seeds remain sealed. Validation results must not be used to tune a changed version and then be attributed to that changed code.

## Status

**PASS — validated engineering candidate; package parity / R3 hosted submission next.**
