# KEXP-20260827-028 — live-meta action-tape benchmark

Status: **RUNNING / BENCHMARK INFRASTRUCTURE ONLY**

## Prize-first problem

Frozen Kaito/Rayk/Andrew are useful regression controls but are poorly calibrated to the hosted field: R4B scores 81-15 locally while the hosted rating fell 161.6 → 135.7. Official Aug-26 top episodes show a much stronger, state-adaptive live frontier.

Public Kaggriculture episode datasets expose the complete official replay: environmental seed, both submitted action streams and terminal rewards. This experiment tests whether those public action streams can become a closer **development benchmark** without copying them into a submission.

## Phase A — exact replayability gate

Freeze the official **2026-08-26 top 10 episodes by manifest `avg_score`**.

For each episode:

1. extract both public action streams;
2. recreate the official environment using its public seed under the frozen Kaggriculture engine;
3. replay both tapes in their original seats;
4. require 720 recorded states, both statuses `DONE`, and **exact equality of both terminal rewards** with the public episode.

No R4B benchmark result is trusted for an episode unless Phase A reproduces it exactly.

### Infrastructure gate

- If at least **8/10** episodes reproduce exactly, the action-tape benchmark is eligible as a development calibration layer.
- If fewer than 8/10 reproduce exactly, reject/deprioritize this benchmark until the reproduction mismatch is explained.

## Phase B — R4B versus original winner tape

Only for Phase-A-exact episodes:

- keep the original winning tape in its original seat;
- replace the original loser with frozen `R4B-market-only-validated-v1`;
- run the same public environmental seed;
- record R4B W/L/T, terminal delta and how much the winner tape's reward changes under the counterfactual market interaction.

This is deliberately called a **counterfactual tape benchmark**, not an exact model of the live opponent: a fixed action stream cannot adapt to the new market trajectory created by R4B. Its value is calibration against much stronger recent behavior than the frozen notebook panel.

## Provenance and deployment boundary

- Source data: official public Kaggle episode datasets only.
- No validation or held-out seeds.
- Team name, episode ID, seed ID and action-tape identity are research provenance only and forbidden strategy features.
- Public opponent tapes are **benchmark-only** and are not copied, distilled or embedded in the submitted agent by this experiment.

Tool: `tools/live_meta_action_tape_benchmark.py`
Frozen tool blob: `f3bb56f9984c54c67c3538cb5cfc12db49199e03`
