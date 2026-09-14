# FP001 E2B — no-weed causal correction — 2026-09-14

## Purpose

Recover a valid matched causal estimate for E2 after discovering that default weed spawning uses an action-dependent RNG stream: occupying a tile changes which later empty tiles consume RNG draws, so same seed does not preserve common environmental randomness between crop and no-crop policies.

E2B changes **only the evaluation environment**, not the agent.

## Frozen candidate

Use `candidates/fp001_e2_dedicated_strawberry_hand.py` exactly as committed before E2 result inspection. No policy parameter, target, HIRE condition, fertilizer rule, crop rule, animal scheduler or market rule may change for E2B.

## Environment

- `kaggle-environments==1.32.7`;
- `episodeSteps=720`;
- `startingMoney=3000`;
- **`weedSpawnChance=0` for every treatment and control**;
- fresh seeds `69301..69306`;
- both seats;
- pass opponent, because this remains a causal production/economics gate rather than a population-strength test.

Six seeds × two seats gives 12 paired observations per architecture.

## Architectures

For each backbone:

- COW4_DAILY `S0H0`, `S1H0`, `S1H1`;
- COW5_SURVIVAL `S0H0`, `S1H0`, `S1H1`;
- COW5_DAILY `S0H0`, `S1H0`, `S1H1`.

## Required outputs

- per-case final-bank delta for auditability;
- paired S1H1−S1H0, S1H1−S0H0, S1H0−S0H0 summaries;
- full cow survival;
- crop planted;
- pre-productive crop death only;
- HIRE/WATER/FERTILIZE/HARVEST counts;
- berries, milk and fertilizer sold;
- main FEED/CARE/movement;
- hand movement/PASS utilization.

## Promotion rule

For a backbone to preserve one-hand/one-STRAWBERRY as a positive causal module:

1. S1H1−S1H0 mean > 0 and majority wins;
2. S1H1−S0H0 mean > 0 and majority wins;
3. full expected cow survival;
4. crop realizes the intended 8-berry H11 production in essentially all mechanically valid episodes.

If the total module is non-positive after removing weed RNG confounding, close one-hand/one-STRAWBERRY on that backbone. Do not threshold-retune it.

## Interpretation boundary

E2B is intentionally weed-free only for causal attribution. Any survivor must later prove robustness in the ordinary default environment during heterogeneous population testing. No E2B result alone authorizes hosted submission.
