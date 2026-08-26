# KEXP-20260826-013 — current-meta hard-regime replays

## Purpose

Determine whether the late-collapse mechanism observed against exact Kaito V27 also appears in the hard regimes exposed by exact Rayk V11 and Andrew V12.

This is **diagnostic-only**. No code is promoted from this experiment and no validation/held-out seed is touched.

## Frozen candidate

`R4B-market-only-validated-v1`

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`

## Exact opponents

### Rayk V11

- `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
- `main.py` SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
- benchmark-only; no derivative use.

### Andrew V12

- `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`
- `main.py` SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
- Apache-2.0.

Every replay job must reacquire the exact notebook version and fail closed on the hash above.

## Predeclared hard-regime set

Rayk:

- `163219477`, both orientations — the only Rayk loss and also a symmetric Kaito V27 loss.

Andrew:

- `150614441`, both orientations — one Andrew seat loss / one win, and also seat-sensitive under V27;
- `393297156`, both orientations — symmetric Andrew loss;
- `598340816`, both orientations — one Andrew seat loss / one win, and symmetric V27 loss;
- `1422177419`, both orientations — symmetric Andrew loss.

Total: **10 complete development replays**.

## Diagnostic questions fixed before replay inspection

For each candidate-vs-opponent orientation, extract at minimum:

1. money delta at steps 120, 160, 192, 240, 360, 480, 600, 672, 700, 718 and terminal;
2. first checkpoint at which a lead that existed after step 480 is lost;
3. cows, sheep, hands and owned land at late checkpoints;
4. crop-board composition and shed inventory around 600/672/700/718;
5. late market quantities by product and HIRE activity;
6. whether the terminal result is already determined before the step-718 market-only controller can matter.

## Interpretation boundary

A mechanism is eligible to become an R4D hypothesis only if it is:

- observable from legal game state;
- not keyed to seed ID or opponent identity;
- present in more than one current public family or supported by an engine-economic theorem;
- expressible as one auditable change layered over R4B/COK;
- testable on the full 16-seed development panel before any new validation.

If hard regimes are architecturally different, do not force a universal patch. Prefer a state-dependent late-phase controller with explicit guard conditions or keep R4B frozen while moving toward R5 planning.

## Status

**PRE-REGISTERED — REPLAY CAPTURE PENDING.**
