# ROADMAP — Kculture live plan

Updated: 2026-09-13

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before validation results are interpreted.
4. Invalid evaluations are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.
9. Strong local H2H against CR071M/legacy anchors is necessary but not sufficient for hosted metagame value.
10. Future promotion requires an independent **high-strength population proxy** before a hosted slot is spent.

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step state-conditioned teacher 1-NN.

Behavioral imitation remains closed. Public replays may be used offline to discover state/regime stressors, not to make identity-conditioned runtime policies.

## ACTIVE — CR083 hosted maturation

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**.

Kaggle submission: **`56199767`**.

Local promotion (`34715575445`) passed strongly: 45W–1L–18T versus CR071M, neutral guardrail deltas versus CR053/CR061/CR065.

Hosted evidence now has the correct interpretation:

- Kaggle initializes a new valid simulation submission at `mu_0 = 600`; its rating is still converging during early episodes;
- CR083 moved from `1563.9` to **`1596.2`** while CR071M moved to `1642.4`, reducing the apparent gap from `83.3` to **`46.2`**;
- frozen 36-replay forensics: **27W–9L**, 75.0% raw win rate;
- however, fresh population cross-match is **0–4 versus current >=2300 / roughly top-1000 opponents**.

Full checkpoint: `docs/strategy/CR083_HOSTED_PROBE_CHECKPOINT_2026-09-13.md`.

### Frozen maturity rule

Operational project heuristic, not Kaggle policy:

1. Keep the exact CR083 submission live and immutable.
2. Do not issue the final hosted verdict before **100 completed public episodes**.
3. At 100+, freeze a new checkpoint of rating, rating trend, all public W/L/T, seat split and opponent-strength bands.
4. Crossing CR071M before 100 episodes is encouraging but not sufficient; upper-population transfer must also improve.
5. No CR083A/B/C and no tuning of the seed-clamp activation boundary, crop rules or formula from this hosted sample.
6. No new hosted submission solely to reroll rating convergence.

## ACTIVE IN PARALLEL — rebuild the promotion proxy

The old gate asked whether a candidate improved CR071M and preserved legacy anchors. The missing question is whether it survives **high-strength live population regimes**.

Next evaluation layer must therefore:

1. freeze a current high-strength population cohort, prioritizing roughly top-1000 (`rating >= ~2300`) and top-500 (`>= ~2578`) opponents;
2. obtain only public/legal replay evidence through authenticated Kaggle interfaces;
3. extract current-observation/economic-regime stressors and mechanics-level differences — not opponent identity as a runtime feature and not replay-action imitation;
4. identify which economic states are systematically absent from CR071M/CR053/CR061/CR065 local validation;
5. turn those regimes into a frozen offline stress protocol;
6. only then build the next genuinely independent economic-value architecture;
7. require that candidate to pass CR071M direct, legacy guardrails **and** high-strength population-proxy evidence before any hosted probe.

## Frontier targets

Fresh full leaderboard snapshot `2026-09-13T07:47:09 UTC`:

- top 10 cutoff: **2970.8**;
- rank 100: `2782.8`;
- rank 500: `2578.1`;
- rank 1000: `2300.8`;
- rank 2000: `1679.7`.

The strategic target is not merely to exceed mature CR071M around the mid-1600s. We need a representation that continues winning as matchmaking moves upward through the 2000s toward the 3000 frontier.

## Escalation rule

A new architecture earns a hosted probe only after passing three independent layers:

1. fresh direct improvement versus the incumbent backbone;
2. broad legacy-anchor guardrails;
3. frozen high-strength population-regime stress evidence.

If hosted evidence contradicts the first two layers, improve the proxy, not the already-spent mechanism.
