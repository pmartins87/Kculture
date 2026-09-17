# Full Solver Campaign to 3000 — 2026-09-17

## Objective

The target is not incremental leaderboard improvement. The target is a prize-capable Kaggriculture agent, with ~3000 rating as the working competitive threshold.

The S0/S1 experiment established that a five-macro daily selector is far too low-bandwidth. S1 improved held-out counterfactual macro regret but moved hosted rating only from 475.3 to 498.1. Therefore the five-plan classifier is closed as the development nucleus. Its assets remain useful only as priors, controls, and warm-start demonstrations.

## Clock

Final submission deadline: 2026-09-30 23:59 UTC.

At 2026-09-17 ~20:00 UTC, about 13 days 4 hours remain.

## Compute evidence already measured on Ryzen 9

Corrected PS2 run:
- 250 seeds
- 8 branch states per seed
- 5 exact deep counterfactual rollouts per state
- 2,000 branch states
- 10,000 deep rollouts
- observed aggregate seed rate: ~0.241 seed/s

Equivalent observed deep-rollout throughput for that workload:
- 0.241 * 40 ~= 9.64 deep rollouts/s
- ~= 833,000 deep rollouts/day if run continuously at the same workload shape
- ~= 11 million deep rollouts over the remaining competition window if nothing else changed

This is already enough to justify continuous actor/rollout generation. However, the current Python exact engine and five-plan action space are not the final architecture.

## Strategic correction

Do not spend the remaining competition window tuning V4/V5 by hand in small increments.

Do not scale the current five-plan self-play dataset to 50k states and call that the solver.

Build a real hierarchical solver and keep the Ryzen saturated with useful experience generation.

## Architecture

### 1. Fast exact simulator

Highest-priority infrastructure task. We need a high-throughput simulator with proven parity to kaggle-environments 1.32.7.

Public competition work exists with Apache-2.0 fast C++ Kaggriculture engines, including kagsim / 2,000+ episodes-per-second claims and a later 24k-episodes-per-second notebook. We should ingest public licensed code only after source/license inspection and then prove transition parity against the official Python engine on randomized traces.

The Ryzen benchmark, not public claims, determines the production configuration.

Parity gates:
- same initial states for fixed seeds
- same transition after randomized legal joint actions
- same end-of-day RNG effects
- same market/town/shop behavior
- same terminal rewards
- thousands of randomized traces, zero unexplained mismatches

### 2. Hierarchical action space

The solver must not choose among five named plans.

Strategic/economic action representation should expose parameters directly, including at minimum:
- target livestock by species
- target crop mix by species
- worker/hiring schedule
- land expansion timing
- cash reserve / investment budget
- feed reserve / wheat production target
- harvest timing regime
- fertilizer allocation
- sell/hold thresholds by product
- market quantities and timing
- opponent-conditioned market responses

Low-level executor remains a deterministic legality/scheduling layer where that is useful. The learned/search layer controls economically meaningful decisions.

### 3. Policy + value + search

Train a policy/value system over legal visible state and explicit candidate action parameters.

Offline teacher:
- exact simulator rollouts
- beam / best-first / CEM-style candidate search
- multi-horizon value targets
- counterfactual action advantages

Runtime:
- compact policy/value model
- bounded search using remaining per-turn time bank
- deterministic legality mask and executor

The runtime budget is constrained by Kaggle to roughly 1 second per turn with a 60-second bank, 1.6 vCPU, CPU-only, <=100 MiB submission. Deep exact search belongs mainly offline; runtime search must be distilled/pruned and benchmarked.

### 4. Opponent population, not pure V4 self-play

Pure V4 x V4 training is closed as the primary distribution.

Population must include:
- frozen strong public/replay-derived strategies already collected
- historical CR families that are behaviorally distinct
- current learned checkpoints
- exploiters trained against current champion
- randomized strategic parameter agents
- self-play against recent checkpoint bank

Sampling should prevent one opponent family from dominating training.

### 5. Warm start from what already works

Do not throw away prior knowledge.

Use as demonstrations/priors:
- strong public replay trajectories
- frozen top-population macro patterns
- proven economic findings: livestock/care, wheat/feed, fertilizer, crop branches, sale timing
- CR086 latent supply estimator
- existing legal executor components

But none of these are the final policy.

### 6. Continuous learning loop

Ryzen should run continuously whenever the production trainer is ready.

Actor/learner loop:
1. generate trajectories / searched counterfactuals
2. append to replay buffer with versioned provenance
3. train/update policy and value
4. evaluate against fixed held-out opponent league
5. promote checkpoint only if it improves robust league metrics
6. add promoted checkpoint to league
7. continue without stopping actors

Checkpoint every 24 hours at minimum, with lighter internal checkpoints more frequently.

### 7. 24-hour checkpoint report

Every 24h checkpoint must report:
- total environment steps / episodes / searched branches
- simulator throughput
- policy/value losses
- held-out league W/D/L by opponent family and seat
- terminal-margin distribution
- exploitability/cycle diagnostics
- catastrophic legality/runtime failures
- model size and hosted inference timing
- delta from previous 24h checkpoint

Hosted Kaggle submission is used when a checkpoint represents a material policy generation, not for tiny hand edits.

## Training phases

### Phase A — fast-engine acquisition + parity

Time budget: hours, not days. Run in parallel with architecture work.

Exit: fast engine is trusted enough for training or explicitly rejected, in which case the Python exact engine remains fallback while optimization continues.

### Phase B — imitation / supervised warm start

Train policy from strong trajectories and searched expert actions so the learner starts from competent farming rather than rediscovering basic mechanics.

### Phase C — large-scale league self-play + counterfactual search

Continuous Ryzen workload. Millions of trajectories/branches, diverse opponent bank, policy/value updates.

### Phase D — runtime bounded search

Use learned policy to propose candidates and value to prune/evaluate. Measure exact hosted-time budget locally.

### Phase E — daily candidate promotion

At each 24h checkpoint, compare to the previous champion over a large fixed league and fresh seeds. If materially stronger and runtime-safe, package and submit. Continue training regardless.

## Anti-regression rules

- No more five-plan-only training as the main path.
- No architecture pivot from a single hosted game or single seed.
- No stopping Ryzen for routine analysis once the continuous pipeline is running.
- No scaling a dataset merely because it exists; scale the pipeline that has the highest competitive ceiling.
- No discarding proven historical mechanisms; use them as priors/features/opponents.
- No hidden seed, future state, or opponent-private state at runtime.
- Every public external code dependency must have license/provenance recorded and transition parity verified.

## Immediate next engineering tasks

1. Acquire and inspect the public Apache-2.0 fast Kaggriculture engine implementations/notebooks.
2. Build official-vs-fast-engine transition parity harness for 1.32.7.
3. Benchmark episodes/s and transitions/s on the Ryzen 9.
4. Replace named five-plan actions with explicit parametric strategic action encoding.
5. Build population opponent registry and replay buffer format.
6. Implement continuous actor/learner/checkpoint supervisor.
7. Start 24/7 Ryzen training.
8. Use the first 24h checkpoint as the first serious post-S1 evaluation point.

This campaign supersedes the incremental PS4 interpretation that merely expands the five macro plans. Search+Value remains part of the architecture, but only inside the full high-throughput hierarchical solver campaign.
