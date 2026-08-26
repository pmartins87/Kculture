# ROADMAP — Kculture

## Objective

Maximize the probability of a **top-10 final finish** by combining accurate mechanics, strong long-horizon planning, opponent-aware adaptation, automated local tournaments, and disciplined final-agent selection.

## Current gate summary

- R0 technical intake: complete; account-side Kaggle entry confirmation pending.
- **R1: PASS — 2026-08-25.**
- **R2: PASS — 2026-08-25.**
- R3: pending first hosted submission.
- **R4: ACTIVE — public strong-base screening and improvement.**

Public repository development is a deliberate decision, not a blocker. See `docs/DECISION_PUBLIC_DEVELOPMENT.md`.

## R0 — Intake and freeze official facts

- Capture rules, mechanics, timeline, action API, validation behavior, submission packaging, ladder behavior, and prize structure.
- Preserve versions/hashes of official starter assets where permitted.
- Separate documented mechanics from inferred behavior.

**Exit:** all competition-critical facts are traceable and current, including account entry.

**Status:** technical acquisition complete; account-side competition-rule acceptance / entered status still needs confirmation.

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

- Confirm account accepted competition rules / appears under entered competitions.
- Package `main.py` correctly.
- Pass self-play validation.
- Reconcile hosted logs/behavior with local execution.
- Establish a disciplined cadence inside the 5-submission/day allowance.

**Exit:** first valid ladder agent and documented local↔hosted deltas.

**Status:** pending account-side submission access. Local execution infrastructure is ready.

## R4 — Strong economic baseline

### R4A — select a strong public engineering base

- Screen multiple independent, public, licensed architectures on the frozen engine.
- Use development seeds only for base selection.
- Require hash/license provenance and both-seat execution.
- Choose on runtime safety + head-to-head outcomes first; bank margin is secondary.

Current experiment: `KEXP-20260825-004-r4-public-base-screen` compares COK V8 and Seyamalam V21. The winner is frozen as `R4A-public-base`.

### R4B+ — Kculture improvements

- Make one auditable strategic change at a time against the frozen R4A base.
- Test whether public-state expert routing is possible by measuring where strong bases first diverge and what information is observable at that point.
- Optimize movement/action efficiency and daily work scheduling.
- Evaluate land expansion, daily hiring, crop/livestock mix, fertilizer, inventory flow and market timing.
- Exploit shop/town demand only when the adaptation survives matched controls.
- Improve recovery for weeds, seed feasibility, animal placement, shed pressure and route divergence.
- Preserve terminal liquidation because only bank cash has terminal value.
- Add strong independent public policies and prior Kculture champions to the opponent archive.

**Exit:** one deterministic Kculture policy robustly beats the simple pool on validation and performs competitively against a diverse strong-public panel without runtime instability.

**Status:** active.

## R5 — Long-horizon planner

- Add state-value approximations for future cashflow and action scarcity.
- Optimize planting, harvest, expansion, labor, inventory movement and sales timing.
- Introduce tactical replanning when expected value changes materially.

**Exit:** planner beats R4 across validation/held-out seeds and diverse opponents.

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

**Exit:** searched policies outperform the hand-tuned champion on held-out evaluation.

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
