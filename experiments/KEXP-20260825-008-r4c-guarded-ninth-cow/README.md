# KEXP-20260825-008 — R4C guarded ninth cow

## Question

Does enabling the dormant, already-implemented guarded ninth-cow branch in the frozen COK V8 base improve development performance without destabilizing the policy?

## Why this is a clean experiment

R4A remains the exact hash-pinned COK V8 artifact. R4C changes only one upstream feature flag:

`_ENABLE_NINTH_COW = False` -> `True`

The underlying branch is already bounded by public-state conditions around step 289: eight owned cows, opponent herd pressure, at least three milk-demand shops, milk price >= 225, money >= 800, market-order capacity, and no conflicting cow order.

No route tape, worker count, crop mix, recovery rule, front-running rule, or terminal logic is modified.

## Candidate

`candidates/r4c_ninth_cow.py`

The wrapper loads the frozen `cok-v8-779caae` artifact after hash verification, asserts the upstream flag is still `False`, flips it to `True`, and delegates every action to that module.

## Protocol

Development seeds only. Validation and held-out remain sealed for this R4C hypothesis.

1. R4A vs Seyamalam V21, first 8 development seeds, both seats — control.
2. R4C vs Seyamalam V21, identical seeds/seats.
3. R4C vs R4A, identical seeds/seats.

## Promotion gate

R4C may advance only if all are true:

- zero runtime errors;
- R4C mean money delta vs Seyamalam >= the same-seed R4A control;
- R4C score rate vs Seyamalam >= the same-seed R4A control;
- direct R4C vs R4A score rate >= 0.50;
- direct mean R4C money delta vs R4A >= 0;
- at least one development episode shows a non-zero behavioral/performance difference attributable to the switch. If the guard never activates, record INCONCLUSIVE rather than PASS.

## Numbering note

This experiment was initially prepared under `KEXP-20260825-006`, which collided with the market-only terminal ablation. It was never executed under that identifier. It is renumbered to `KEXP-20260825-008`; `KEXP-007` is reserved for the frozen market-only validation gate.

## Execution

GitHub Actions run `32919545606`, first 8 frozen development seeds, both seats, `kaggle-environments==1.32.7`.

### R4A control vs Seyamalam V21

- 14 wins / 2 losses / 0 ties
- score rate: 0.875
- mean money delta: +21,063.875
- errors: 0

### R4C vs Seyamalam V21

- **14 wins / 2 losses / 0 ties**
- score rate: **0.875**
- mean money delta: **+21,063.875**
- errors: 0

The external matchup is exactly unchanged on all tested seeds/seats.

### R4C direct vs R4A

- 4 wins / 4 losses / 8 ties
- score rate: 0.500
- mean money delta: 0.000
- min delta: -218
- max delta: +218
- errors: 0

The switch can activate and create small differences, but the paired-seat effect cancels and produces no demonstrated external advantage.

## Decision

**NO PROMOTION / NEUTRAL.**

R4C meets the non-regression boundaries but provides no positive evidence: it leaves the Seyamalam matchup exactly unchanged and is exactly neutral against R4A in paired aggregate. The ninth-cow flag remains excluded from the validated hosted-submission candidate.

No validation or held-out seed was opened. Held-out remains sealed 32/32.
