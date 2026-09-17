# Prize Solver PS2 corrected 2k-state result

Date: 2026-09-17

## Run

Local Ryzen 9, 31 workers.

- runner: `tools/prize_solver_rollout_ryzen_v2.py`
- output: `runs/ps2_v4_2k_v2`
- seeds: 250
- branch days: 3,6,9,12,15,18,21,23
- branch states: 2,000
- macro plans per state: 5 (`PLANS_V2`)
- exact engine rollouts: 10,000
- failures: 0

## Aggregate result

- heuristic/oracle exact macro match rate: **0.247**
- heuristic mean regret: **4,955.792** final-margin units
- heuristic max regret: **47,030.0** final-margin units

Here `oracle` means the best of the five current `PLANS_V2` alternatives under the
PS2 counterfactual protocol (force the macro for the configured window, then continue
with the solver), not a globally optimal Kaggriculture policy.

## Decision

**PS2_CORRECTED_2K_PASS_ADVANCE_PS3**

The result is sufficient to train PS3 because:

1. all 10,000 counterfactual engine runs completed without failures;
2. the macro family exactly matches PrizeSolverV4's strategic action space;
3. the heuristic leaves substantial measurable counterfactual value on the table;
4. there are enough grouped states/seeds for a seed-disjoint train/validation split.

Do not enlarge the rollout dataset before measuring PS3 validation and hosted S1. The
next gate is whether learned macro selection materially lowers held-out regret relative
to the V4 heuristic, followed by Kaggle hosted S1 measurement.
