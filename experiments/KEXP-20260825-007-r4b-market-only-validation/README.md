# KEXP-20260825-007 — R4B market-only validation

## Purpose

Test the exact market-only candidate frozen after `KEXP-20260825-006` on the untouched validation partition. This is the first opening of the 16 validation seeds for this candidate. The 32 held-out seeds remain sealed.

## Frozen candidate

- path: `candidates/r4b_ablation_market_only.py`
- development source commit: `148cc81fed390fd75c0cba00ceb779efaa17a46f`
- frozen candidate Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- freeze config: `configs/r4b_market_only_candidate.json`
- base: `R4A-public-base-v1` / COK V8, hash-pinned Apache-2.0 source

No candidate behavior may be changed after seeing validation outcomes. Any later code change creates a new development candidate and cannot reuse this validation result as if it applied to the changed code.

## Validation protocol

Use **all 16 validation seeds**, both candidate seats, on frozen `kaggle-environments==1.32.7`.

A. Frozen R4A vs Seyamalam V21 — validation control.
B. Frozen market-only candidate vs Seyamalam V21.
C. Frozen market-only candidate vs frozen R4A.

This produces 32 games per matchup, 96 total executions.

## Predeclared PASS gate

All conditions must hold:

1. zero runtime errors in all three matchup blocks;
2. market-only direct score rate vs R4A >= 0.50;
3. market-only direct mean money delta vs R4A >= 0;
4. market-only wins vs Seyamalam >= R4A-control wins vs Seyamalam;
5. market-only mean money delta vs Seyamalam >= R4A-control mean money delta vs Seyamalam.

A tie at the direct 0.50 boundary is acceptable because the intervention is deliberately minimal; the independent Seyamalam preservation/improvement gates must still pass.

## Decision rule

- **PASS:** preserve the exact evidence, promote this artifact to the next R4 engineering stage, and prepare a self-contained hosted-submission package. Held-out remains sealed until a later formal promotion/final-selection gate.
- **FAIL:** reject this candidate for promotion. Do not tune it on validation results; return to development-only hypotheses.

## Status

**PREDECLARED — validation not yet interpreted.**
