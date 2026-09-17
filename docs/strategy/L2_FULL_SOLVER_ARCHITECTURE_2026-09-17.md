# L2 Full Solver Architecture — 2026-09-17

## Decision

The fast-engine gate is decisive:

- official `kaggle-environments==1.32.7`: ~0.444 adaptive episodes/s on the Ryzen host;
- kagsim L1 + current Python V4: ~1.470 adaptive episodes/s;
- kagsim L0 fixed-stream batch: ~91,955 episodes/s using all cores;
- ratio L0/L1: ~62,554x;
- exact final-bank parity passed on seeds 11, 23, 47.

Therefore the current bottleneck is not the game engine. It is the per-turn Python decision layer. The project must stop treating L1 Python callbacks as the long-term training architecture.

The target is a vectorized L2 actor interface that keeps thousands of exact `Sim` instances in C++, emits legal observation tensors in batches, accepts action tensors in batches, advances the environments with the GIL released, and later hosts a compact policy/value/search stack.

## What we are NOT doing

- no more five-macro-only learner as the development nucleus;
- no PPO-from-scratch commitment;
- no long-running V4 self-play campaign;
- no use of engine telemetry as runtime information available to the hosted agent;
- no acceptance of tiny hosted gains as project success.

S0/S1 remain engineering controls only.

## Architecture

```text
bit-exact kagsim 1.32.7
        |
        v
L2 VecGame (thousands of C++ Sims)
        |
        +--> legal observation tensors (public both farms + private own state)
        |
        +--> training-only diagnostics/telemetry (NEVER policy input)
        |
        v
hierarchical policy/value
        |
        +--> strategic/economic heads
        +--> tactical/logistics heads or deterministic constrained executor
        +--> legal masks / hard survival constraints
        |
        v
bounded search teacher (clone/fork exact states)
        |
        v
league actors: current, historical, exploiters, public/reference styles
        |
        v
replay / learner / checkpoint promotion
        |
        v
compact hosted policy + bounded online search
```

## Observation contract v0

The first L2 tensor contract is deliberately broad enough to avoid choosing a blind representation, but contains only runtime-legal information.

`global[B,37]` raw numeric values:

- step, day, hour;
- own/opponent money;
- own/opponent unit count;
- own/opponent unlocked quadrant count;
- own/opponent hires_today;
- market inventory[9];
- market prices[9];
- unlocked-shop multiplicity[8].

`tiles[B,2,10,10,12]` (`int16`):

- kind;
- what (crop/animal id, or -1);
- has_animal;
- watered_today;
- fed_today;
- cared_today;
- fertilizer_available;
- consecutive_dry/unfed;
- yield_units;
- planted/placed day;
- max_lifespan_step;
- fertilized_until_day.

`units[B,2,40,3]` (`int16`): x, y, present-mask for every public unit.

`private[B,497]` (`int16`) from the selected player's own private observation only:

- shed[12];
- seeds[5];
- inventories[40,12].

No opponent shed, opponent seeds, hidden seed, future state, or telemetry enters this observation.

## Action transport v0

L2 initially transports exact raw engine actions in fixed tensors:

- unit op/arg/n for up to 40 units;
- market op/item/n for up to 16 raw slots;
- explicit `n_units` and `n_orders`.

This is transport, not the final policy action space. The policy will be factorized/hierarchical and legality-masked; the first objective is to remove the 62k x Python callback bottleneck without changing game semantics.

## Why telemetry matters but must stay outside the policy

The gate exposed the current V4 as mechanically poor on seed 11, including:

- 3 escaped animals;
- 29 plants dried;
- 23 animal-shed days;
- 926+ hand PASS turns;
- dozens of dead harvest/water actions;
- >2k coins of silent capital/seed loss.

These counters are valuable as training diagnostics, constraint violations and auxiliary targets. They are not legal observations in the hosted game and therefore must never be policy inputs.

## L2 gates

L2 is accepted only when all of the following pass:

1. **semantic gate** — for a seed/action sequence, VecGame rewards match `kagsim.Game` and official engine controls;
2. **seat gate** — tensors for each player expose own private state and never opponent-private state;
3. **batch determinism** — same seeds/actions give identical results independent of thread count;
4. **throughput gate** — observe+step batching is at least 100x faster than current L1 V4 loop before neural inference;
5. **memory gate** — batches of at least 4096 environments fit stably on the Ryzen host;
6. **training gate** — learner can consume batches without per-environment Python callbacks.

The 100x threshold is intentionally modest relative to the 62,554x raw headroom. If L2 cannot recover at least two orders of magnitude before NN inference, its interface is wrong.

## Continuous campaign after L2

Once L2 passes, the Ryzen enters a continuous actor/learner campaign:

- actors never stop for ordinary analysis;
- checkpoint every 24h, plus emergency checkpoint on promotion events;
- promotion requires league improvement, not self-play-only improvement;
- search teacher, policy-only and policy+search are evaluated separately;
- opponent population includes frozen historical checkpoints and exploiters;
- PPO is optional and retained only if an ablation shows incremental value over search/distillation/value learning;
- hosted submissions are made for materially different checkpoints, not every local fluctuation.

## Competition objective

The project objective remains prize contention near the ~3000-strength region, not incremental improvement over ~485. S0/S1 are not competitive baselines; they are controls that proved packaging and engine integration.
