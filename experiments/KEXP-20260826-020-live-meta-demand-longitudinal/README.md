# KEXP-20260826-020 — longitudinal live-meta demand response

Status: **PREDECLARED / OBSERVATIONAL / DEVELOPMENT INTELLIGENCE ONLY**

## Prize-first question

KEXP-019 found a striking same-day association in the top-20 official 2026-08-25 ladder episodes: winners bought far more CARROT seed during steps 600–671, especially as public carrot-demand weight from the full eight-shop multiset increased. However, those 20 episodes were only Crop Dusta vs Ryo Hasegawa, so team identity is a serious confounder.

Before implementing any Kculture policy, repeat the exact same measurement on several preceding daily ladder datasets.

## Frozen protocol

Run the existing `tools/live_meta_demand_response.py` independently on:

- 2026-08-22, top 10 episodes by `avg_score`;
- 2026-08-23, top 10;
- 2026-08-24, top 10;
- 2026-08-25, top 10.

Each job records both players, so this yields up to 80 player-games total. Dates that do not exist in the official index must fail visibly rather than silently substitute another day.

Primary variables are identical to KEXP-019:

- complete public shop multiset at step 600;
- official carrot-demand weight = `2 * count(PET_CAFE) + count(FARMERS_MARKET)`;
- BUY_SEED CARROT during 600–671;
- final-day CARROT SELL during 696–718;
- W/L outcome;
- team name for confounding diagnosis only.

## Decision rule

A late-carrot R4D candidate becomes worth implementing only if the multi-day evidence is broadly consistent with the engine mechanics and not explained entirely by one team identity.

Strong support would include several of:

1. positive demand→late-carrot-buy relationship on multiple days;
2. winners tending to allocate more late carrot than losers at matched/similar demand levels on multiple days;
3. multiple distinct high-Elo teams using late carrot in high-demand shop regimes;
4. no evidence that the effect is simply a one-day artifact.

Failure to generalize means **reject/deprioritize** the candidate; do not rescue it by tuning thresholds to the original Aug-25 sample.

## Data discipline

Official public ladder episodes only. No frozen validation or held-out seeds are touched. Episode/team/seed identity may be used for research stratification, never as a deployable feature.

## Reproducibility

Tool: `tools/live_meta_demand_response.py`
Workflow: `.github/workflows/live-meta-demand-longitudinal.yml`
