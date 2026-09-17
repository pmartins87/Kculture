# PS3 Value V1 — Result

Date: 2026-09-17

Source dataset: `runs/ps2_v4_2k_v2`

- branch states: 2,000
- exact counterfactual rollouts: 10,000
- rollout failures: 0
- train states: 1,608
- validation states: 392
- visible-state features: 55
- macro plans: 5

## Training

- early stop: epoch 63
- best normalized validation MSE: `0.7547963599283555`
- heuristic mean regret: `4947.21144278607`
- learned-policy mean regret: `2705.7904228855723`
- heuristic median regret: `2525.5`
- learned-policy median regret: `356.0`
- learned-policy oracle match rate: `0.4458955223880597`
- learned-policy p90 regret: `9010.5`

## Held-out validation

- heuristic mean regret: `4990.989795918367`
- learned-policy mean regret: `3665.0255102040815`
- mean-regret reduction: ~26.6%
- heuristic median regret: `2624.5`
- learned-policy median regret: `999.0`
- median-regret reduction: ~61.9%
- learned-policy oracle match rate: `0.3622448979591837`
- learned-policy p90 regret: `11408.2`

## Decision

`PS3_VALUE_V1_PASS_TO_S1_HOSTED`

The learned value policy generalizes imperfectly but materially reduces held-out macro regret versus the V4 heuristic. Per the frozen competition-first roadmap, do not delay for a larger training run before measuring transfer. Integrate the generated `models/prize_solver_value_v1.json` into Prize Solver S1 and submit hosted as the clean S0-vs-S1 value-learning ablation.

Hosted interpretation remains decisive: the local counterfactual improvement is a gate to submission, not evidence of leaderboard gain by itself.
