# ROADMAP — Kculture

## Objective

Maximize the probability of a **top-10 final finish** by combining accurate mechanics, strong long-horizon planning, opponent-aware adaptation, automated local tournaments, and disciplined final-agent selection.

## Current gate summary

- **R0: working intake complete** — technical intake complete; competition entry is user-confirmed and will be API-reconciled on first authenticated submission.
- **R1: PASS — 2026-08-25.**
- **R2: PASS — 2026-08-25.**
- **R3: READY TO SUBMIT** — validated deterministic package exists; first authenticated hosted upload/reconciliation remains.
- **R4: ACTIVE** — `R4B-market-only-validated-v1` is the first validated Kculture engineering candidate; further development continues on development-only evidence.

Public repository development is a deliberate decision, not a blocker. See `docs/DECISION_PUBLIC_DEVELOPMENT.md`.

## R0 — Intake and freeze official facts

- Capture rules, mechanics, timeline, action API, validation behavior, submission packaging, ladder behavior, and prize structure.
- Preserve versions/hashes of official starter assets where permitted.
- Separate documented mechanics from inferred behavior.

**Exit:** all competition-critical facts are traceable/current and competition entry is confirmed.

**Status:** **COMPLETE FOR WORKING PURPOSES.** Technical intake is frozen and the user confirmed competition enrollment. API-side entered-status evidence will be preserved during R3.

## R1 — Baseline reproduction

- Run official/simple baseline locally.
- Verify legal action handling, 720-turn episode completion, observations, state transitions, and terminal scoring.
- Log action counts and terminal behavior.

**Exit:** repeatable legal baseline with deterministic diagnostics.

**Status:** **PASS.** `KEXP-20260825-001-official-starter-parity` established exact starter parity.

## R2 — Local tournament laboratory

- Run fixed seeds and both player seats.
- Maintain deterministic development/validation/held-out partitions.
- Maintain passive/simple/strong-public/archive opponents.
- Fresh-load file agents per episode to prevent state leakage.
- Preserve raw outcomes, bank deltas, errors, replay/summary artifacts and provenance.

**Exit:** strategy changes can be compared reliably before Kaggle submission.

**Status:** **PASS.** `KEXP-20260825-003-r2-closure`: 64 disjoint seeds, 7 deterministic references, hash-pinned public benchmark, both-seat execution and zero closure-smoke errors.

## R3 — First ladder submission

- Confirm entered status through authenticated Kaggle API evidence.
- Submit the exact validated package.
- Pass hosted self-play validation.
- Reconcile hosted logs/behavior with local execution.
- Record ladder rating/episodes and exact submission ID/source/hash.
- Establish a disciplined cadence inside the 5-submission/day allowance.

**Exit:** first valid ladder agent and documented local↔hosted deltas.

**Status:** **READY TO SUBMIT.** `R4B-market-only-validated-v1` passed development, predeclared validation, deterministic packaging, and full-trajectory package parity. Archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`. `.github/workflows/r3-first-hosted-submission.yml` performs the authenticated upload after rebuilding/verifying the exact artifact.

## R4 — Strong economic baseline

### R4A — select a strong public engineering base

COK V8 is frozen as `R4A-public-base-v1` after a 14-2 same-seed development result over Seyamalam V21, with public source/license/hash provenance preserved.

**Status:** **COMPLETE / FROZEN BASE.**

### R4B — terminal market completeness

A broad terminal-capacity version was rejected because its physical `DROP` replacement regressed directly against R4A. Ablation isolated the useful component: preserve all physical COK behavior and only make final-step market liquidation complete.

`R4B-market-only-validated-v1` then passed the predeclared validation gate:

- 32-0 vs Seyamalam on 16 validation seeds × both seats;
- 8-6-18 vs R4A, score 0.53125, mean +165.03125;
- zero runtime errors;
- deterministic hosted package parity PASS.

A third public-family development check against Kaito V18 improved the same-seed R4A control from 14-2 / +20,732.75 to 16-0 / +22,210.375.

**Status:** **VALIDATED ENGINEERING CANDIDATE / HOSTED_SUBMISSION_READY.**

### R4C — guarded ninth cow

The dormant upstream ninth-cow flag was tested as a one-switch development hypothesis.

- vs Seyamalam: exactly matched R4A at 14-2 / +21,063.875;
- direct vs R4A: 4-4-8 / mean 0.

**Status:** **NO PROMOTION / NEUTRAL.**

### R4D+ — evidence-driven improvements

- Build a full development failure atlas before another strategy mutation.
- Use all 16 development seeds and both seats against COK/Seyamalam/Kaito.
- Change one auditable mechanism at a time from recurring failure patterns.
- Continue improving movement/action efficiency, daily work scheduling, expansion, labor, crop/livestock mix, fertilizer, inventory flow, market timing, recovery, and route decisions only when matched controls justify the change.
- Preserve final liquidation behavior because only bank cash has terminal value.
- Add newer strong public agents and prior Kculture champions to the opponent archive.

Current diagnostic: `KEXP-20260825-010-r4-development-failure-atlas`, 160 development games. It has no promotion gate; it exists to generate the next hypothesis.

**R4 exit:** one deterministic Kculture policy robustly beats diverse strong-public controls on predeclared validation without runtime instability, with a hosted ladder result consistent enough to justify moving deeper into planner/search work.

## R5 — Long-horizon planner

- Add state-value approximations for future cashflow and action scarcity.
- Optimize planting, harvest, expansion, labor, inventory movement and sales timing.
- Introduce tactical replanning when expected value changes materially.

**Exit:** planner beats R4 across a newly frozen validation protocol and later held-out evidence.

## R6 — Dynamic market and opponent awareness

- Track observable market and opponent farm state.
- Detect opponent strategy archetypes from early behavior.
- Test adaptive selling/production/expansion responses.
- Stress adaptations against deceptive and mixed opponents.

**Exit:** adaptation adds robust value without destabilizing baseline play.

## R7 — Automated strategy search

- Parameter sweeps, evolutionary search, Bayesian/heuristic tuning, or policy search over compact strategy parameters.
- Multi-objective promotion: W/L/T, bank delta, low variance, robustness and matchup coverage.
- Maintain strict development/validation/held-out separation.

**Exit:** searched policies outperform the hand-tuned champion on a formal final-selection evaluation.

## R8 — Metagame and final pair construction

- Analyze ladder episodes and public metagame without blindly fitting displayed rating.
- Build two final candidates with complementary matchup profiles.
- Avoid two nearly identical agents: the latest two submissions are strategic portfolio slots.
- Stress against champion archive and adversarially selected opponents.

**Exit:** final pair selected from controlled evidence across diverse matchups.

## R9 — Final freeze

- Reproduce both final agents from a clean environment.
- Verify packaging, imports, action legality, time/memory behavior, deterministic fallbacks and zero-crash self-play.
- Freeze source/config/hashes and submission IDs.
- Submit both final tracked agents before 2026-09-30 23:59 UTC.

**Exit:** two robust final ladder agents accepted and preserved.
