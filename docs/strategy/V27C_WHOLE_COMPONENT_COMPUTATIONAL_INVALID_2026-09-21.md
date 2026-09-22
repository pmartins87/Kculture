# V27C Whole-Component Classification — Computational Mechanics Invalid — 2026-09-21

## Status

The original V27C representation is CLOSED as computationally invalid before any validation/holdout result was produced.

Binding data collection workflow:
`35678874775`.

Data collection:
- 12/12 collector shards PASS;
- 192 teacher episodes preserved;
- exact immutable V26A snapshot;
- fresh seeds `79901..79908`;
- both seats;
- no live Kaggle reacquisition.

Training attempt 1 and exact retry attempt 2 both failed at the same phase.

## Failure signature

The frozen representation treated:
- the complete MARKET list as one multiclass label;
- the complete HANDS list as one multiclass label;
- FARMER as one multiclass label.

The training matrix was:
- 57,520 retained training turns;
- 2,215 features;
- 881 MARKET classes;
- 50 FARMER classes;
- 1,765 HANDS classes.

Both attempts reached the same matrix and then the GitHub-hosted runner received a shutdown signal during ExtraTrees fitting, before any validation or holdout metrics or model artifact existed.

No V27C holdout performance has been observed.

## Interpretation

This is not evidence that 256-step legal-history distillation is weak.

It is evidence that representing an entire variable-length multi-worker action list as one multiclass target is a poor computational representation.

The game action schema is naturally structured:
- one farmer unit action;
- a legal number of hand/worker unit actions;
- up to 10 market order slots.

The existing programme action encoding reserves up to 40 unit actions total (farmer + hands) and 10 market orders.

## Allowed correction

A successor may change only the **label/action factorization and feature compression** while preserving:
- rank-1 teacher identity;
- immutable V26A opponent population;
- seeds `79901..79908`;
- train/validation/holdout split;
- no runtime opponent identity;
- no teacher call at inference;
- original V27C holdout parity thresholds.

The successor must be pre-registered before any holdout model score is observed.

No Kaggle submission is authorized.
