# ROADMAP — Kculture

## Objective

Maximize the probability of a **top-10 final finish** by combining accurate mechanics, strong long-horizon planning, opponent-aware adaptation, automated local tournaments, and disciplined final-agent selection.

## R0 — Intake and freeze official facts

- Capture rules, mechanics, timeline, action API, validation behavior, submission packaging, ladder behavior, and prize structure.
- Preserve versions/hashes of official starter assets where permitted.
- Separate documented mechanics from inferred behavior.

**Exit:** all competition-critical facts are traceable and current.

## R1 — Baseline reproduction

- Run official/simple baseline locally.
- Verify legal action handling, 720-turn episode completion, observations, state transitions, and terminal scoring.
- Log action counts, bank trajectory, inventory, crop/animal yields, expansion timing, and failures/no-ops.

**Exit:** repeatable legal baseline with deterministic diagnostics.

## R2 — Local tournament laboratory

- Build episode runner across fixed and randomized seeds.
- Maintain opponent pool: passive, simple crop loops, aggressive expansion, livestock-heavy, market-sensitive, and prior promoted agents.
- Capture win rate, profit delta, variance, failure rate, and matchup matrix.
- Fit local skill estimates only as a secondary summary; preserve raw episode outcomes.

**Exit:** strategy changes can be compared reliably before Kaggle submission.

## R3 — First ladder submission

- Package `main.py` correctly.
- Pass self-play validation.
- Reconcile hosted logs/behavior with local execution.
- Establish a conservative cadence for the 5-submission/day allowance.

**Exit:** first valid ladder agent and documented local↔hosted deltas.

## R4 — Strong economic baseline

- Optimize movement/action efficiency.
- Compare crop lifecycle economics, fertilizer use, harvesting cadence, storage, selling, land expansion, farm-hand hiring, and livestock pathways.
- Model opportunity cost per action and capital payback horizon.

**Exit:** one deterministic policy family robustly beats simple opponents.

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
- Maintain train/validation/held-out seed and opponent sets.

**Exit:** searched policies outperform hand-tuned champion on held-out evaluation.

## R8 — Metagame and final pair construction

- Analyze ladder episodes and public metagame without blindly fitting displayed rating.
- Build two final candidates with complementary matchup profiles.
- Avoid two nearly identical agents: the latest two submissions are strategically valuable portfolio slots.
- Stress against champion archive and adversarially selected opponents.

**Exit:** final pair selected from evidence across many controlled episodes.

## R9 — Final freeze

- Reproduce both final agents from clean environment.
- Verify packaging, imports, action legality, time/memory behavior, deterministic fallbacks, and zero-crash self-play.
- Freeze source/config/hashes and submission IDs.
- Submit both final tracked agents before 2026-09-30 23:59 UTC.

**Exit:** two robust final ladder agents accepted and preserved.
