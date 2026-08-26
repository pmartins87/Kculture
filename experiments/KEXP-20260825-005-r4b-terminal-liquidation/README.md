# KEXP-20260825-005 — R4B terminal-capacity liquidation

## Question

Can a route-independent terminal liquidation layer improve the frozen `R4A-public-base-v1` without changing its opening, production route, market timing, or recovery policy before the last executable step?

## Motivation

The upstream V8 failure analysis shows terminal-sale revenue deficit in 57 of 59 recorded losses. The weakest route cluster is `current:6c8s_3q`, and large product revenue gaps include WHEAT, MILK, and TOMATO. R4B therefore tests a deliberately narrow hypothesis rather than changing the full economic route.

## Candidate

`candidates/r4b_terminal_liquidation.py`

The candidate wraps the hash-pinned Apache-2.0 COK V8 artifact selected as R4A. Kculture changes only step 718:

1. inspect the current shed and inventories carried by shed-adjacent actors;
2. solve a 0/1 knapsack over actor-level `DROP` choices under the 100-item shed cap, using current visible sale prices as approximate value;
3. suppress an existing low-value terminal `DROP` when it would crowd out a better selected actor;
4. project same-turn shed stock with the upstream execution-order model;
5. replace terminal market activity with complete sale orders for every projected sellable product.

All earlier steps call the frozen base unchanged.

## Development protocol

Only the first 8 `development` seeds are used, both seats.

A. Frozen COK V8 vs Seyamalam V21 (control rerun).
B. R4B vs Seyamalam V21.
C. R4B vs frozen COK V8.

Primary gates:

- zero runtime errors;
- R4B mean money delta vs Seyamalam must be >= the same-seed R4A control;
- R4B direct score rate vs R4A must be >= 0.50;
- direct mean money delta vs R4A must be >= 0.

This development experiment does **not** open validation or held-out seeds. If the gates pass, the exact candidate is frozen before validation.

## Provenance boundary

COK V8 remains third-party Apache-2.0 code and is fetched by commit/hash. The terminal-capacity optimizer and wrapper logic in this experiment are Kculture changes. This file is research infrastructure, not yet a self-contained Kaggle submission.

## Status

PENDING CI at experiment creation.
