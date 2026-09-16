# Shadow Evaluator v0 — retrospective falsification

Date: 2026-09-15
Branch: `fix/kaggle-parity-v1`

## Question

Can the existing exact local H2H evaluator, without real Kaggle-population evidence, identify which of the frozen historical anchors transfers best to hosted Kaggriculture?

This is a falsification test. Its purpose is not to rescue the local league by tuning weights after seeing hosted results. If the local-only signal is directionally wrong on already-known anchors, a useful Shadow Kaggle Evaluator must add an external population layer based on real Kaggle episodes/results.

## Frozen hosted truth

Project checkpoints:

| Candidate | Hosted checkpoint |
|---|---:|
| CR053_REAL | ~2064.8 |
| CR052_REAL | ~1749.2 |
| CR083 | ~1619.9 |
| CR086 | ~1612.6 |

Hosted ordering: `CR053_REAL > CR052_REAL > CR083 > CR086`.

## Frozen exact local evidence

Source run: `34802917553`
Head: `a42b4589e568e3203ede7dad653e1c000f22b710`
Backend: `kaggle-environments==1.32.7`
Protocol: exact frozen packages, path-dependent official reference engine, 12 paired seeds, both seats, 24 games per edge, fresh spawned process per package per episode, zero execution errors.

| Edge (A vs B) | Local W-L | Local score rate A | Local direction | Hosted direction | Correct? |
|---|---:|---:|---|---|---|
| CR083 vs CR053_REAL | 20-4 | 0.833333 | CR083 > CR053 | CR083 < CR053 | NO |
| CR086 vs CR053_REAL | 20-4 | 0.833333 | CR086 > CR053 | CR086 < CR053 | NO |
| CR053_REAL vs CR052_REAL | 14-10 | 0.583333 | CR053 > CR052 | CR053 > CR052 | YES |
| CR083 vs CR052_REAL | 24-0 | 1.000000 | CR083 > CR052 | CR083 < CR052 | NO |
| CR086 vs CR052_REAL | 24-0 | 1.000000 | CR086 > CR052 | CR086 < CR052 | NO |

Directional accuracy on these five comparable edges: **1/5 = 20%**.

The strongest inversions are not marginal/noisy:

- CR083 beat CR053_REAL 20-4 locally, yet hosted checkpoint is ~444.9 lower.
- CR086 beat CR053_REAL 20-4 locally, yet hosted checkpoint is ~452.2 lower.
- CR083 and CR086 each swept CR052_REAL 24-0 locally, yet hosted checkpoints are ~129.3 and ~136.6 lower than CR052_REAL respectively.

CR053_REAL vs CR052_REAL is the only direction that agrees, and even that local edge was not decisive versus 0.5 (`CI95 [0.3333, 0.8333]`).

## Result

**FAIL_LOCAL_ONLY_SHADOW_REQUIRE_REAL_KAGGLE_POPULATION_LAYER**

The exact local engine is useful for mechanics, causal intervention tests, branch/invariant checks and catastrophic-regression filtering. It is not a sufficient competitive ranking oracle.

The failure cannot honestly be fixed by post-hoc weighting of these same four anchors: that would train on the answer. The missing variable is population transfer.

## Binding consequence

Shadow Evaluator v1 must begin from **real Kaggle population evidence**, not from a larger closed local league.

Minimum v1 layers, in order:

1. Acquire/publicly reconstruct recent Kaggle episode/result metadata and a player/submission interaction graph.
2. Build population-strength strata and a Bradley-Terry-style shadow rating from observed W/L where the data permits it.
3. Attach our hosted submissions to that graph and measure performance by opponent-strength stratum, recency and family/diversity rather than raw local H2H alone.
4. Use local exact simulation only as an intervention laboratory conditioned on states/strategic families actually observed hosted.
5. Only after v1 proves retrospective discrimination should opponent-policy imitation be added; do not start by overbuilding imitation models.

## Guardrails

- No hidden/private runtime feature is introduced into any competitor.
- Opponent identity/rating/EpisodeId remain forbidden runtime features.
- Hosted/population metadata may be used offline for analysis and training/evaluation labels, subject to competition rules.
- Original final holdout remains sealed.
- No automatic Kaggle submission is authorized by this document.

## Next gate

Before resuming CR093/H1B as a promoted competitive experiment, determine whether the repository's existing Kaggle forensic tooling can automatically collect enough real episode/result data to construct Shadow v1. If acquisition is viable, build the smallest retrospective population model and test whether it separates known good/bad hosted anchors better than the 20% local-only baseline. If acquisition is not viable or the population model does not improve discrimination, close the Shadow branch and return to short local-sanity -> hosted-sensor cycles.
