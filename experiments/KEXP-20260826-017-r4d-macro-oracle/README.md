# KEXP-20260826-017 — R4D macro-oracle solver

Status: **PREDECLARED / DEVELOPMENT ONLY**

## Why this experiment exists

The first hosted Kculture submission is valid and complete, but its live Kaggle rating continued downward from the first observed 161.6 to **135.7** in the user-visible snapshot around 2026-08-26 12:00 UTC. Local current-meta screening is therefore not sufficient as our only strategy-development mechanism.

KEXP-015 also showed that a universal default-route replacement is too crude: default→10C/4S preserved the aggregate 81-15 development record and improved mean money, but the same change flipped the two Rayk losses on seed `163219477` into wins while turning two Andrew wins on that seed into losses. The required decision is contextual.

The user asked whether Kaggriculture can be attacked like poker with a solver. The answer is **yes in solver-inspired form**, but an exact full-game equilibrium solver is impractical because the game has 720 recorded turns, multiple mobile actors, board construction, simultaneous market interaction, stochastic future weeds/shop unlocks, hidden opponent inventory, and a large combinatorial action space.

This experiment starts the useful version of a solver: an **offline macro-policy oracle** that uses the exact frozen engine to exhaustively compare a small set of audited strategic continuations from the same state distribution, then distills the winning choice into a compact public-state policy.

## Oracle branches

For every development seed, both seats, and each exact modern public opponent, compare:

1. frozen `R4B-market-only-validated-v1`;
2. `R4D-A default→10C/4S`;
3. `R4D-B default→6C/8S`.

The competition objective is lexicographic:

1. WIN > TIE > LOSS;
2. terminal money delta breaks ties among branches with the same outcome class.

The oracle's ex-post choice is an **upper bound for this three-branch macro action set**, not a deployable policy. It is allowed to use future outcome only to create training labels.

## Public feature snapshot

At the first state where three shops are unlocked, capture only public/legal observables:

- first three shops and static COK route signal;
- our and opponent public money;
- public farm composition and signed layout differences;
- L1 layout distance;
- worker counts/positions;
- market prices;
- public town state.

Forbidden deployment features:

- seed ID;
- opponent identity;
- future result/actions;
- opponent private inventory;
- replay/submission IDs.

## Panel

Development only:

- 16 frozen development seeds;
- both seats;
- exact Kaito V27 V4;
- exact Rayk V11;
- exact Andrew V12.

Total: 96 state contexts × 3 macro branches = **288 complete games**.

Validation and all 32 held-out seeds remain closed to this oracle-building stage.

## Decision path

1. Measure the three-branch oracle upper bound over the 96 contexts.
2. Quantify how often each branch is optimal and where outcome flips occur.
3. Fit/search the smallest selector using only public observables.
4. Evaluate selector with grouped cross-validation by seed and, critically, leave-one-opponent-family-out tests so it cannot simply memorize public agents.
5. Only an auditable selector that beats the frozen 81-15 baseline on development without family collapse may become an R4D candidate.
6. Freeze exact code before any new validation access.

## Relationship to a future stronger solver

If the macro-oracle shows meaningful headroom, extend in stages:

- route-choice oracle;
- late-horizon production/harvest/sale macro search;
- receding-horizon model-predictive planning;
- opponent-belief ensemble for hidden inventory/action uncertainty;
- distillation of expensive offline search into a cheap submitted policy.

This preserves the best poker-solver idea: **do expensive optimization offline, deploy a compact strategy online**.
