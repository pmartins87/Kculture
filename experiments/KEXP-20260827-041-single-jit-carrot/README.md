# KEXP-20260827-041 — single JIT CARROT candidate

Status: **DEVELOPMENT PASS / EXPLORATORY FAIL — NO VALIDATION**

## Mechanism

KEXP-040 established a legal one-step JIT value rule for a mechanically safe late WHEAT slot:

`q * (CARROT_price - WHEAT_price) - 20 > 0`

For the 614→615 block, same-route yield is `q=3`. Candidate `candidates/r4d_jit_carrot_one.py` buys exactly one CARROT at state 614 when `3*(Pc-Pw)-20 > 0`, then converts exactly one actual R4B `PLANT WHEAT` at state 615 only if the added seed is observed to have arrived above the frozen-base expectation.

Candidate blob: `97e102933f96a85fcc586ec4a96500069902f035`.  
Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Mechanical execution audit — PASS

Run `33044850064`, artifact `9635413649`.

Across 36 development + exploratory episodes:

- trigger in 14/36 episodes;
- added purchase committed 14/14;
- exact `+1 PLANT CARROT / -1 PLANT WHEAT` 14/14;
- 22/36 non-trigger episodes had zero mutation;
- development 6/16 conversions;
- exploratory pool 8/20 conversions;
- zero errors.

Implementation therefore matches the intended policy.

## Development result — PASS

Run `33044755062`, artifact `9635541714`.

Modern public regression panel:

- Kaito V27: 25-7;
- Rayk V11: 30-2;
- Andrew V12: 26-6;
- combined **81-15**, exactly preserving R4B;
- zero errors.

Direct vs R4B:

- **20-12**;
- score **0.625**;
- mean terminal delta **+53.53125**.

This materially passed the predeclared development gate.

## Exploratory live-meta replication — FAIL

Run `33045892841`, artifact `9635804231`, artifact digest `sha256:843f8826e977f746ea030c34b033e1d8c5ec3a8d78d93ef32e1b87bbef5e65c5`.

Twenty exploratory live-meta environmental seeds × both seats, direct vs frozen R4B:

- **14 wins / 14 losses / 12 ties**;
- score rate **0.500**;
- mean terminal delta **-21.35**;
- seat 0: 10-4-6;
- seat 1: 4-10-6;
- zero errors.

The development edge does not generalize to this second distribution. This candidate is therefore **not eligible for validation or hosted submission**.

The strong seat asymmetry and the contradiction between development W/L and exploratory W/L motivate KEXP-046, which decomposes same-seed counterfactual own-farm value versus opponent/market externality.

## Decision

Keep KEXP-041 as an important scientific result: a state-adaptive value rule can beat R4B on one frozen development distribution and execute perfectly, but this exact one-conversion controller is not robust enough.

Do not open validation. Do not submit to Kaggle. KEXP-045 tests whether a second bounded conversion changes robustness; KEXP-046 diagnoses why KEXP-041 failed to generalize.

No seed, episode, opponent or team identity is a policy feature.
