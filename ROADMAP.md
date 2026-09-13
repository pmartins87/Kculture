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
10. Future promotion requires an independent high-strength population proxy before a hosted slot is spent.
11. **Do not enter polling loops.** Live state is checked only at predeclared/material decision boundaries.

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step state-conditioned teacher 1-NN.
- **CR084 critical late-livestock rescue.** Corrected Gate A barely passed, but frozen promotion failed and independent temporal high-strength evidence showed zero actual rescue opportunities. No window/risk/animal retuning.

Behavioral imitation remains closed. Public replays may be used offline to discover state/regime stressors, not to make identity-conditioned runtime policies.

## ACTIVE — CR083 hosted maturation

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**.

Kaggle submission: **`56199767`**.

Local promotion (`34715575445`) passed strongly: 45W–1L–18T versus CR071M, neutral guardrail deltas versus CR053/CR061/CR065.

Latest authenticated checkpoint already obtained in this work session:

- CR083: **1660.3**;
- CR071M: **1638.8**;
- observed CR083 lead: **+21.5**;
- about **76 public completed episodes** plus validation.

This is encouraging but not the final hosted verdict.

### Frozen maturity rule

Operational project heuristic, not Kaggle policy:

1. Keep the exact CR083 submission live and immutable.
2. Do not issue the final hosted verdict before **100 completed public episodes**.
3. Do **not** repeatedly poll between now and that boundary.
4. At 100+, make one frozen checkpoint of rating, W/L/T, seat split, opponent-strength bands and trend.
5. Crossing CR071M before 100 episodes is encouraging but not sufficient; upper-population transfer must also improve.
6. No CR083A/B/C and no tuning of the seed-clamp activation boundary, crop rules or formula from this hosted sample.
7. No new hosted submission solely to reroll rating convergence.

## CLOSED — CR084

Final record: `docs/strategy/CR084_FINAL_RESULT_2026-09-13.md`.

Corrected frozen SHA: `3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2`.

Key evidence:

- semantic audit valid: 23 exercised rescues, 0 market mismatches, 0 invalid physical differences;
- Gate A: 11W–7L–14T = `0.5625`, mean margin `+140.6875`;
- promotion master `9140842`: CR084 vs CR083 **12W–10L–42T = `0.515625`**, mean margin `-106.625`;
- CR071M guardrail delta versus CR083: `-0.125`;
- temporal high-strength proxy: 6 opponents `>=2300`, 5 CR083 losses, **0 rescue opportunities / 0 confirmed preventable escapes**.

Decision: `CLOSE_CR084_CRITICAL_FEED_RESCUE`.

## NEXT — CR085 architecture discovery

Do not build CR085 from a guessed patch. First decompose already-frozen high-strength losses into economic trajectories.

The discovery phase must compare CR083 and strong-opponent state evolution by coarse, legal economic families:

1. **cash / liquidity trajectory** by day;
2. **market prices and market inventory** for sellable products;
3. **productive inventory** — live animals, planted crops, harvested products;
4. **shed pressure / discarded overflow**;
5. **worker and land utilization**;
6. **input acquisition efficiency** — seed/product/animal/land/hire spending;
7. **route-switch aftermath** around the frozen CR083 switch points;
8. terminal conversion: which intermediate state variable best predicts the late money gap.

The discovery objective is not to imitate strong opponents. It is to find a repeatable causal bottleneck that:

- appears before terminal divergence;
- is observable from legal current state;
- recurs across multiple strong-opponent losses;
- can be converted into a narrow intervention with an explicit economic argument;
- can be stress-tested on a holdout cohort that did not motivate the intervention.

Only after this decomposition may a CR085 protocol be frozen.

## Frontier targets

Latest top-10 read-only checkpoint already obtained in this work session:

1. Majkel1337 `3239.9`
2. Mengfei Li `3065.9`
3. Artem The Farmer `3064.4`
4. ymg_aq `3020.9`
5. SpaTaro `3019.2`
6. Otter Vibe `3005.0`
7. redblackbst `2991.3`
8. feel the agi `2990.5`
9. binghua `2968.2`
10. Subramanya N `2965.4`

The strategic target remains far above mature CR071M/CR083 mid-1600s. We need a representation that keeps winning as matchmaking reaches the 2000s and eventually the ~3000 frontier.

## Escalation rule

A new architecture earns a hosted probe only after passing three independent layers:

1. fresh direct improvement versus the incumbent backbone;
2. broad legacy-anchor guardrails;
3. frozen high-strength population-regime stress evidence.

If hosted evidence contradicts the first two layers, improve the proxy, not the already-spent mechanism.
