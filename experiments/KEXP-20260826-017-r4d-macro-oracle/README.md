# KEXP-20260826-017 — R4D macro-oracle value-of-information test

Status: **COMPLETE / NO PROMOTION / SOLVER BRANCH DEPRIORITIZED**

## Why this experiment exists

The first hosted Kculture submission is valid and complete, but its live Kaggle rating fell from the first observed 161.6 to **135.7** in the user-visible 2026-08-26 snapshot. Local public-agent screening is therefore not sufficient as our only calibration mechanism.

KEXP-015 also showed that a universal default-route replacement is too crude. The user then asked whether Kaggriculture could be attacked like poker with a solver. That question was treated too quickly as a proposed direction. KEXP-017 is retained only as a **cheap value-of-information test** of that idea, not as a roadmap pivot.

An exact full-game equilibrium solver remains impractical for the current project: 720 recorded turns, multiple mobile actors, board construction, simultaneous market interaction, stochastic events, hidden opponent inventory and a very large combinatorial action space.

## Tested oracle branches

For every development seed, both seats, and each exact modern public opponent, the exact engine compared:

1. frozen `R4B-market-only-validated-v1`;
2. `R4D-A default→10C/4S`;
3. `R4D-B default→6C/8S`.

Competition-aligned oracle objective:

1. WIN > TIE > LOSS;
2. terminal money delta only breaks ties among branches with the same outcome class.

This is an ex-post upper bound over **only these three existing macro policies**. It is not a deployable solver and it is not evidence that a larger solver would share the same bound.

## Frozen execution

GitHub Actions run: **`32972566807`** — SUCCESS, development only.

96 contexts × 3 branches = **288 complete games**, zero reported execution errors. Validation and all 32 held-out seeds remained untouched.

Artifacts/digests:

- Kaito V27 artifact `9608766243`, ZIP SHA-256 `a6cfc86f4b00cb54fdb758ee666cfd4a7a341ad58b9b44424fef7597f589a5f4`;
- Rayk V11 artifact `9608750232`, ZIP SHA-256 `b4c07e4292ac8ae0c66e152401f9560bd5c447c6b5e7b8fcae9ea8435488ca0a`;
- Andrew V12 artifact `9608601559`, ZIP SHA-256 `81b8c44242bd7770028ab43cd6acf6a76af5518eef9b10154c16a611370a21ee`.

## Results

| Opponent | R4B baseline | fixed 10C/4S | fixed 6C/8S | perfect 3-branch oracle |
|---|---:|---:|---:|---:|
| Kaito V27 | 25-7 | 25-7 | 24-8 | **25-7** |
| Rayk V11 | 30-2 | **32-0** | 30-2 | **32-0** |
| Andrew V12 | **26-6** | 24-8 | 24-8 | **26-6** |
| **Combined** | **81-15** | **81-15** | **78-18** | **83-13** |

Mean terminal delta of the perfect three-branch oracle across the equally sized families is approximately **+6,182.22**, versus baseline +5,720.5. The competition-relevant gain is much smaller: only **two extra wins in 96 games**, both coming from the Rayk family.

Key facts:

- against Kaito, even perfect ex-post selection among the three branches cannot fix any of the seven losses;
- against Andrew, it cannot fix any of the six losses;
- against Rayk, the simple fixed 10C/4S branch already achieves the oracle's 32-0, so sophisticated selection is unnecessary for that gain;
- therefore the majority of current public-panel losses require **new strategic action families**, not a better selector among these three routes.

## Decision

**Do not pivot Kculture to a solver project.**

The experiment falsified the high-value version of the immediate solver hypothesis: perfect selection among our existing macro branches has only a 2/96 W/L ceiling on the current panel. That is too small to justify making solver construction the main use of engineering time while the hosted score is 135.7 and thirteen public-panel losses remain outside this action set.

Solver/search methods remain permitted as tools when they have a specific, cheap, testable role (for example, optimizing a bounded late-game subproblem). They receive no architectural privilege and must compete against simpler alternatives on expected prize value, evidence, engineering cost and hosted relevance.

## Prize-first continuation

1. Treat the **hosted/local mismatch** as the highest-priority calibration problem.
2. Diagnose mechanisms shared by Kaito/Andrew hard losses that no route choice fixes, especially the repeated late-horizon reversals.
3. Expand the modern opponent/state distribution rather than overfit the same 16 development seeds and three families.
4. Search new strategic action families with cheap falsification experiments first.
5. Require W/L improvement and cross-family robustness before validation or another Kaggle submission.
6. Keep all 32 held-out seeds sealed.
