# CR071 anti-patterns — lessons that must not be repeated

## 1. Broadly “making CR053 adaptive” is already falsified

Hosted calibration on 2026-09-07 recorded:

- CR052 — `Adaptive Route Agent V2`, submission `56073867`: approximately **1703** near-stable hosted rating.
- CR053 — frozen static route from public episode `106309334`, submission `56073870`: approximately **2090** near-stable hosted rating.

The difference was roughly **387 rating points in favor of the static route**, despite CR052 passing the then-current local proxy and scoring 57.42% against CR029.

Source of record: `docs/HOSTED_CALIBRATION_2026-09-07_CR052_CR053.md` (commit `7230eafc874cfcde8d64b154ea51f52aa0bcf201`).

### Consequence for CR071

Do **not** take CR053 and add broad route adaptation, heuristic switching or multiple repairs at once. CR071 must preserve the chosen backbone exactly outside a small, observable intervention surface. Every intervention is an ablation with a corresponding no-intervention control.

## 2. Single-opponent proxies are not tournament proxies

CR052 and CR053 both passed the old CR029-centric local gate, while hosted reality separated them strongly. Therefore:

- no CR029-only promotion;
- no single H2H promotion;
- use the exact-reference historical league plus hosted reality checks;
- preserve strategically diverse candidates until broad evidence eliminates them.

## 3. Money-margin improvements are not promotion evidence

Old CR070 smoke tests produced dramatic mean-margin differences that did not correspond cleanly to W/L ordering or hosted ratings. Promotion metric is seat-balanced W/L on the exact Kaggle reference. Mean/median margin are diagnostic only.

## 4. Correlation-driven full-agent selectors are dangerous

A state observed after two strategies have already diverged is partly caused by those strategies. A selector learned from such a state can be non-causal and impossible to reproduce before committing to the route.

Forensics may support:

- exogenous signals (shop unlocks, genuinely shared market state);
- component-specific triggers;
- route switching only when candidate prefixes are mechanically compatible.

It must not justify arbitrary mid-game switching between unrelated trajectories.

## 5. No monolithic CR071 blend

CR061, CR065, CR068A/B and CR070A contain useful but overlapping logic around different route backbones. Combining all of it can introduce conflicts in market slots, funding order, shed inventory, hired-hand geometry and physical route timing.

Required sequence:

1. choose/falsify backbone with broad exact-reference evidence;
2. transplant **one** component;
3. exact-reference W/L ablation;
4. only then test component interactions;
5. hosted submission only after the package is a clear evidence-backed candidate.
