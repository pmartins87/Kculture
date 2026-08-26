# KEXP-20260825-010 — R4 development failure atlas

## Purpose

Build a higher-resolution failure map for the frozen `R4B-market-only-validated-v1` candidate before attempting another strategy modification.

This is **development-only diagnostic evidence**. It does not reopen or extend the completed validation claim and cannot promote a changed candidate by itself.

## Frozen candidate

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- status: `R4B-market-only-validated-v1`
- hosted package SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`

## Opponent panel

1. R4A / COK V8 — direct base-regression control.
2. Seyamalam V21 — independent mixed-farm architecture.
3. Kaito public V18 / C20 exact-replication mirror — third attributed public family.

All third-party artifacts are hash-pinned in `configs/public_opponents.json` and fetched through `tools/fetch_public_opponents.py`.

## Protocol

Use **all 16 frozen development seeds**, both candidate seats, `kaggle-environments==1.32.7`.

Candidate blocks:

- market-only vs R4A — 32 games;
- market-only vs Seyamalam V21 — 32 games;
- market-only vs Kaito V18 — 32 games.

Same-seed controls:

- R4A vs Seyamalam V21 — 32 games;
- R4A vs Kaito V18 — 32 games.

Total: **160 development games**.

Validation and all 32 held-out seeds remain sealed for this experiment.

## Diagnostic outputs

For each matchup record:

- W/L/T and tie-half score rate;
- mean/median/min/max money delta;
- zero-error status;
- exact losing seeds and seats;
- paired-seat aggregate by seed.

Then classify each remaining loss into a development hypothesis category before changing code. Avoid changing multiple economic mechanisms at once.

## Decision rule

This experiment has **no promotion gate**. It is a failure-atlas / hypothesis-generation run only.

A next candidate may be created only from a concrete pattern supported by this development evidence. Any changed candidate starts a new development experiment and does not inherit the previous validation result.

## Status

**PREDECLARED — RUNNING.**
