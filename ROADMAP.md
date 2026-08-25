# ROADMAP — Kculture

## Objective

Maximize the probability of a **top-10 final finish** by combining accurate mechanics, strong long-horizon planning, opponent-aware adaptation, automated local tournaments, and disciplined final-agent selection.

## Current gate summary

- R0 technical intake: complete; account-side Kaggle entry confirmation pending.
- **R1: PASS — 2026-08-25.**
- **R2: PASS — 2026-08-25.**
- R3: pending first hosted submission.
- R4: preparation active; competitive source development requires private storage because the current GitHub repository is public.

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

**Status:** **PASS.** `KEXP-20260825-001-official-starter-parity` established exact starter parity on fixed seeds and full self-play.

## R2 — Local tournament laboratory

- Build episode runner across fixed seeds and both seats.
- Maintain deterministic development/validation/held-out partitions.
- Maintain opponent pool: passive, simple crop loops, strong public references, and later prior promoted agents.
- Fresh-load file agents per episode to prevent state leakage.
- Capture win rate, profit delta, variance, failure rate, replay/summary artifacts, and provenance.
- Fit local skill estimates only as a secondary summary; preserve raw episode outcomes.

**Exit:** strategy changes can be compared reliably before Kaggle submission.

**Status:** **PASS.** `KEXP-20260825-003-r2-closure`: 64 disjoint seeds, 7 deterministic references, hash-pinned strong public benchmark, both-seat execution, zero closure-smoke errors.

## R3 — First ladder submission

- Confirm account has accepted competition rules / appears under entered competitions.
- Package `main.py` correctly.
- Pass self-play validation.
- Reconcile hosted logs/behavior with local execution.
- Establish a conservative cadence for the 5-submission/day allowance.

**Exit:** first valid ladder agent and documented local↔hosted deltas.

**Status:** pending account-side submission access. Local packaging/execution prerequisites are ready.

## R4 — Strong economic baseline

### Source-isolation prerequisite

Competitive candidate source must be developed in a **private** location during the active competition. The current `pmartins87/Kculture` repository is public; committing the serious policy here would expose it to competitors and may create Kaggle public-code-sharing obligations.

### Strategy work

- Replace the single-tile carrot reference with a genuinely scaled production architecture.
- Optimize movement/action efficiency and daily work scheduling.
- Compare crop lifecycle economics, fertilizer use, harvesting cadence, storage, selling, land expansion, farm-hand hiring, and livestock pathways.
- Model opportunity cost per action, marginal worker value, capital runway, and payback horizon.
- Condition production on public town/shop demand when the adaptation survives validation.
- Add retry/recovery logic for weeds, seed feasibility, purchase/placement reconciliation, shed overflow, and route divergence.
- Liquidate terminal inventory before the end because only bank cash determines reward.
- Benchmark against simple pool and hash-pinned strong public policies.

**Exit:** one deterministic policy family robustly beats simple opponents across validation seeds and closes a material fraction of the strong-public-benchmark cash gap without runtime instability.

**Status:** preparation active; private candidate storage is the immediate blocker to source implementation.

## R5 — Long-horizon planner

- Add state-value approximations for future cashflow and action scarcity.
- Optimize timing of planting, harvest, expansion, labor, inventory movement, and sales.
- Introduce tactical replanning when expected value changes materially.

**Exit:** planner beats R4 across held-out seeds/opponents.

## R6 — Dynamic market and opponent awareness

- Track observable market state and opponent farm state.
- Detect opponent strategy archetypes from early-game behavior.
- Test adaptive selling/production/expansion responses.
- Measure exploitability: every adaptation must also be tested against deceptive or mixed opponents.

**Exit:** adaptation adds robust value without destabilizing baseline play.

## R7 — Automated strategy search

- Parameter sweeps, evolutionary search, Bayesian/heuristic tuning, or policy search over compact strategy parameters.
- Multi-objective promotion: win rate, profit delta, low variance, robustness, and strategic coverage.
- Maintain strict development/validation/held-out separation.

**Exit:** searched policies outperform hand-tuned champion on held-out evaluation.

## R8 — Metagame and final pair construction

- Analyze ladder episodes and public metagame without blindly fitting displayed rating.
- Build two final candidates with complementary matchup profiles.
- Avoid two nearly identical agents: the latest two submissions are strategically valuable portfolio slots.
- Stress against champion archive and adversarially selected opponents.

**Exit:** final pair selected from evidence across many controlled episodes.

## R9 — Final freeze

- Reproduce both final agents from a clean environment.
- Verify packaging, imports, action legality, time/memory behavior, deterministic fallbacks, and zero-crash self-play.
- Freeze source/config/hashes and submission IDs.
- Submit both final tracked agents before 2026-09-30 23:59 UTC.

**Exit:** two robust final ladder agents accepted and preserved.
