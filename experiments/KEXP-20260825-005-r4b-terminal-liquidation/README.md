# KEXP-20260825-005 — R4B terminal-capacity liquidation

## Question

Can a route-independent terminal liquidation layer improve the frozen `R4A-public-base-v1` without changing its opening, production route, market timing, or recovery policy before the last executable step?

## Motivation

The upstream V8 failure analysis reports that 57 of 59 recorded losses had **less realized sale revenue after step 672** than the opponent. This is an observational late-game revenue deficit; it does **not** establish that inventory was stranded at the final action or that terminal liquidation is the causal fix. The weakest route loss cluster is `current:6c8s_3q`, and important product-revenue deficits include WHEAT, MILK, and TOMATO.

A separate static inspection in GitHub Actions run `32913552498` confirmed that the frozen route tapes use strongly route-dependent, fixed-quantity terminal actions. Current 3-quadrant routes share a fixed four-product sale bundle at step 718, while several legacy routes are substantially sparser at 718 and some perform cleanup on step 717. See `research/R4A_TERMINAL_INSPECTION_20260825.md`.

R4B therefore tested one deliberately narrow **causal hypothesis**: given the actual state reached after 718 earlier actions, does replacing only the final static route action with current-state, capacity-aware liquidation improve outcomes?

## Candidate

`candidates/r4b_terminal_liquidation.py`

The candidate wraps the hash-pinned Apache-2.0 COK V8 artifact selected as R4A. Kculture changes only step 718:

1. inspect the current shed and inventories carried by shed-adjacent actors;
2. solve a 0/1 knapsack over actor-level `DROP` choices under the 100-item shed cap, using current visible sale prices as approximate value;
3. suppress an existing low-value terminal `DROP` when it would crowd out a better selected actor;
4. project same-turn shed stock with the upstream execution-order model;
5. replace terminal market activity with complete sale orders for every projected sellable product.

All earlier steps call the frozen COK V8 policy unchanged.

## Predeclared development protocol

Only the first 8 `development` seeds were used, both seats.

A. Frozen COK V8 vs Seyamalam V21 (control rerun).
B. R4B vs Seyamalam V21.
C. R4B vs frozen COK V8.

Primary gates:

- zero runtime errors;
- R4B mean money delta vs Seyamalam >= the same-seed R4A control;
- R4B direct score rate vs R4A >= 0.50;
- direct mean money delta vs R4A >= 0.

## Result — REJECTED

GitHub Actions run `32913752287` completed the predeclared panel with zero runtime errors.

| Matchup | W-L-T | Score rate | Mean money delta |
|---|---:|---:|---:|
| R4A control vs Seyamalam V21 | 14-2-0 | 0.8750 | +21,063.875 |
| Full R4B vs Seyamalam V21 | 16-0-0 | 1.0000 | +22,541.500 |
| Full R4B vs R4A | 5-11-0 | 0.3125 | -1.625 |

The candidate improved the Seyamalam matchup but failed both direct promotion requirements against the frozen base: direct score rate was below 0.50 and direct mean delta was negative. The exact full R4B candidate is therefore **REJECTED** and must not be opened on validation or held-out seeds.

The failure localized the problem: changing physical unit actions to extra terminal `DROP`s is too aggressive. A separate market-only ablation (`KEXP-20260825-006`) preserves every physical COK action and tests final sale completeness independently.

Evidence artifact from run `32913752287`: artifact ID `9587959717`, archive SHA-256 `949e6bdf94c6356aae6af398c6bce17769997255f04a18c59eb5ba2c58245dcf`.

## Provenance boundary

COK V8 remains third-party Apache-2.0 code and is fetched by commit/hash. The terminal-capacity optimizer and wrapper logic in this experiment are Kculture changes.

## Status

**REJECTED — development gate failed. Validation and held-out were not opened for this candidate.**
