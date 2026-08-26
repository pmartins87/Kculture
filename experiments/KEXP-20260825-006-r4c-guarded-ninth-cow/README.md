# KEXP-20260825-006 — R4C guarded ninth cow

## Question

Does enabling the dormant, already-implemented guarded ninth-cow branch in the frozen COK V8 base improve development performance without destabilizing the policy?

## Why this is a clean experiment

R4A remains the exact hash-pinned COK V8 artifact. R4C changes only one upstream feature flag:

`_ENABLE_NINTH_COW = False` -> `True`

The underlying branch is already bounded by public-state conditions around step 289: eight owned cows, opponent herd pressure, at least three milk-demand shops, milk price >= 225, money >= 800, market-order capacity, and no conflicting cow order.

No route tape, worker count, crop mix, recovery rule, front-running rule, or terminal logic is modified.

## Candidate

`candidates/r4c_ninth_cow.py`

The wrapper loads the frozen `cok-v8-779caae` artifact only after its SHA-256 is verified by `tools/fetch_public_opponents.py`, asserts that the upstream flag is still `False`, flips it to `True`, and delegates every action to that module.

## Protocol

Development seeds only. Validation and held-out remain sealed.

1. R4A vs Seyamalam V21, first 8 development seeds, both seats — control.
2. R4C vs Seyamalam V21, identical seeds/seats.
3. R4C vs R4A, identical seeds/seats.

Primary metrics: runtime errors, W/L/T, score rate and money delta.

## Promotion gate

R4C may advance only if all are true:

- zero runtime errors;
- R4C mean money delta vs Seyamalam >= the same-seed R4A control;
- R4C score rate vs Seyamalam >= the same-seed R4A control;
- direct R4C vs R4A score rate >= 0.50;
- direct mean R4C money delta vs R4A >= 0;
- at least one development episode shows a non-zero behavioral/performance difference attributable to the switch. If the guard never activates on the tested panel, record INCONCLUSIVE rather than PASS.

## Status

PREPARED. Do not start this workflow ahead of the already queued R4B terminal-liquidation gate; R4C is the next orthogonal one-variable branch if additional development evidence is needed.
