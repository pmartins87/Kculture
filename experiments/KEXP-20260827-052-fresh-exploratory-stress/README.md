# KEXP-20260827-052 — fresh exploratory stress

Status: **RUNNING**

## Purpose

KEXP-045 and KEXP-050 both produced positive W/L evidence against frozen R4B on previously used development/exploratory pools, but the observed effects are small enough that sampling variance remains material. Before opening validation, increase resolution on a completely fresh exploratory environmental distribution.

## Candidates

- KEXP-045: `candidates/r4d_jit_carrot_two.py`, blob `9d199b3c263254805c64f122367afe180027afeb`.
- KEXP-050: `candidates/r4d_reallocate_614_carrot.py`, blob `61b77be136836328917441cb03f89bc6665c4c27`.
- frozen R4B: `candidates/r4b_ablation_market_only.py`, blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Fresh seed protocol

`tools/run_fresh_exploratory_stress.py` deterministically generates 96 seeds from master seed `202608270052`, excluding all values in:

- development;
- validation;
- held-out;
- prior exploratory live-meta environmental pool.

Each candidate plays frozen R4B on all 96 seeds in both seats: **192 games per candidate**.

Validation and held-out remain sealed.

## Predeclared gate

For each candidate independently:

- zero runtime/status errors;
- overall W/L/T score rate >= **0.53**;
- mean terminal delta > 0;
- score rate in each individual seat >= **0.48**.

If both pass and their overall score rates differ by less than 0.01, prefer KEXP-050 because it changes an existing WHEAT seed purchase into CARROT in the same market slot, has lower incremental cost, and is strategically less invasive. Otherwise prefer the materially stronger passing candidate.

Passing KEXP-052 authorizes candidate freeze and fresh validation; it does not open held-out.
