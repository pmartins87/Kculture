# KEXP-20260827-052 — fresh exploratory stress

Status: **COMPLETE — BOTH PASS / KEXP-050 PREFERRED BY FROZEN RULE**

## Purpose

KEXP-045 and KEXP-050 both produced positive W/L evidence against frozen R4B on previously used development/exploratory pools, but the observed effects were small enough that sampling variance remained material. Before opening validation, increase resolution on a completely fresh exploratory environmental distribution.

## Candidates

- KEXP-045: `candidates/r4d_jit_carrot_two.py`, blob `9d199b3c263254805c64f122367afe180027afeb`.
- KEXP-050: `candidates/r4d_reallocate_614_carrot.py`, blob `61b77be136836328917441cb03f89bc6665c4c27`.
- frozen R4B: `candidates/r4b_ablation_market_only.py`, blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Fresh seed protocol

`tools/run_fresh_exploratory_stress.py` deterministically generated 96 seeds from master seed `202608270052`, excluding all values in:

- development;
- validation;
- held-out;
- prior exploratory live-meta environmental pool.

Each candidate played frozen R4B on all 96 seeds in both seats: **192 games per candidate**.

Validation and held-out remained sealed.

## Predeclared gate

For each candidate independently:

- zero runtime/status errors;
- overall W/L/T score rate >= **0.53**;
- mean terminal delta > 0;
- score rate in each individual seat >= **0.48**.

If both pass and their overall score rates differ by less than 0.01, prefer KEXP-050 because it changes an existing WHEAT seed purchase into CARROT in the same market slot, has lower incremental cost, and is strategically less invasive. Otherwise prefer the materially stronger passing candidate.

## Result

Run: `33069453972` — **SUCCESS**.

### KEXP-045

Artifact `9646196500`; ZIP SHA-256 `d2513e1bb88e8ff5e1262347a60b2eeaa956afa0834423c0ce639802d894585a`.

- 192 games; zero errors;
- **86–46–60**;
- score rate **0.60417**;
- mean terminal delta **+88.71**;
- seat 0 score rate **0.58333**, mean delta **+27.53**;
- seat 1 score rate **0.62500**, mean delta **+149.90**.

### KEXP-050

Artifact `9646165805`; ZIP SHA-256 `157009b9fbc8661e48c495c959fb65cd3ecb0b9165d2644e47d255ab563bc9de`.

- 192 games; zero errors;
- **87–47–58**;
- score rate **0.60417**;
- mean terminal delta **+41.24**;
- seat 0 score rate **0.59896**, mean delta **−20.15**;
- seat 1 score rate **0.60938**, mean delta **+102.63**.

Both candidates pass the frozen stress gate. Their aggregate score rates are exactly tied, so the predeclared tie-break selects **KEXP-050** because it is the less invasive intervention.

## Decision

KEXP-052 correctly authorized KEXP-050 for fresh validation. The later hosted underperformance of KEXP-050 must not retroactively invalidate this result; instead it is evidence that even broad local environmental stress did not reproduce the hosted ladder distribution. Lab-to-host calibration remains a primary unresolved problem.
