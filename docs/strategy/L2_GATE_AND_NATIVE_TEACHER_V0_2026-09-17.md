# L2 gate PASS and native teacher v0 — 2026-09-17

## L2 result on Ryzen 9

The first vectorized exact interface passed its semantic gate and recovered enough of
the native simulator headroom to justify moving from infrastructure benchmarking into
actual search/learning work.

Observed on the user's 32-logical-CPU Ryzen / WSL2:

- semantic observation/action gate: PASS (24 observation checks)
- two-seat batch 256: 205.56 episodes/s, 147,797 sim-steps/s
- two-seat batch 1024: 559.43 episodes/s, 402,233 sim-steps/s
- two-seat batch 4096: **621.54 episodes/s, 446,886 sim-steps/s**
- speedup versus the old Python L1 V4 loop: **422.81x**

This is an infrastructure milestone, not competitive evidence. S0/S1 remain ~485
hosted-rating agents and are not development targets.

## Decision

Stop pure throughput benchmarking. The next consumer is a real search teacher.

## Native teacher v0

`native/teacher/kagteacher.cpp` keeps controller execution and exact simulation inside
C++. A candidate is a 32-dimensional factorized adaptive strategy, not one of the old
five macro plans. The dimensions separately control livestock, all five crops, labour,
land, reserve, feed runway, task priorities, nine product sale thresholds, opponent
pressure response, growth speed, terminal timing, density trigger and diversification.

The controller reads current legal state only. Offline evaluation supplies seeds, but
the controller never reads the hidden seed or future RNG.

`tools/prize_solver_native_teacher_cem_v0.py` performs CEM search against a diverse
population, evaluates both seat orientations on exact worlds, archives distinct elites,
and uses held-out worlds to compare the resulting champion with the initial broad prior.
Win rate dominates the objective; margin/robustness break ties; silent-loss/dead-action
telemetry only applies small anti-degeneracy penalties.

This v0 teacher is a bootstrap data generator for the later policy/value/search loop.
It is not itself claimed to be the final solver and its local objective is not treated
as a Kaggle rating oracle.

## Gate after this stage

The bootstrap must compile, finish without engine failures, produce finite metrics, and
show that the search loop can find at least a non-worse held-out candidate. After that,
scale the teacher and begin collecting state/action/value targets for the learned policy
and value network. Integrate stronger frozen/replay opponents as soon as their artifacts
are available, rather than allowing the native-controller family to become a closed
self-play universe.
