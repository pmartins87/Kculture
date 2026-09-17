# Prize Solver S1 Hosted Result — 2026-09-17

## Hosted ablation

- S0: `R4D_PRIZE_SOLVER_S0_V4.tar.gz`
  - submission: `56294033`
  - hosted score: `475.3`
- S1: `R4D_PRIZE_SOLVER_S1_VALUE_V1.tar.gz`
  - submission: `56311025`
  - hosted score: `498.1`

Observed delta: `+22.8` points (`+4.8%` relative to S0), which is operationally near-flat compared with the ~3000+ prize target and should not be treated as meaningful transfer evidence from PS3.

## What this establishes

1. S1 executed correctly in the exact engine before submission: 720 steps, DONE/DONE, model valid, learned scorer invoked 44 times, max observed call latency ~1.53 ms.
2. The PS3 held-out counterfactual gain (~26.6% mean-regret reduction versus the V4 heuristic) did **not** translate into a material hosted gain.
3. Therefore the next stage must not be a blind scale-up of the same 5-plan contextual selector. The likely bottlenecks are limited decision leverage / coarse macro action space and distribution mismatch between self-play teacher states and hosted opponents.
4. Preserve V4/S0 and S1 as controls. Continue the frozen architecture toward PS4 Search+Value, but make search meaningful by increasing current-state candidate diversity rather than repeatedly choosing among the same five coarse macros.

## Decision

`S1_HOSTED_NEAR_FLAT_ADVANCE_TO_PS4`

Do not spend a larger rollout budget merely to retrain the same 5-plan selector. PS4 should retain the five V2 plans as anchors while opening a denser, state-conditioned candidate generator around them, then test whether bounded current-state search/value can create decisions that materially differ from S0/S1 before the next hosted submission.
